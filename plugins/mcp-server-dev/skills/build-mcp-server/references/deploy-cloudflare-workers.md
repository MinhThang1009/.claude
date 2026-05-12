# Deploy lên Cloudflare Workers

Con đường nhanh nhất từ zero đến một MCP URL `https://` live. Free tier, không cần thẻ tín dụng để bắt đầu, hai lệnh để deploy.

**Đánh đổi:** Đây là scaffold native của Workers, không phải deploy target cho Express scaffold trong `remote-http-scaffold.md`. Runtime khác nhau. Nếu bạn cần portability qua nhiều host, hãy dùng Express. Nếu bạn chỉ muốn nó live, bắt đầu ở đây.

---

## Bootstrap

```bash
npm create cloudflare@latest -- my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-authless
cd my-mcp-server
```

Lệnh này kéo một template tối giản với các dep đúng (`agents`, `zod`) và một `wrangler.jsonc` hoạt động được.

---

## `src/index.ts`

Thay thế ví dụ calculator của template bằng tool của bạn. Dùng `registerTool()` (cùng API với Express scaffold — instance `McpServer` là giống hệt nhau):

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { McpAgent } from "agents/mcp";
import { z } from "zod";

export class MyMCP extends McpAgent {
  server = new McpServer(
    { name: "my-service", version: "0.1.0" },
    { instructions: "Prefer search_items before get_item — IDs aren't guessable." },
  );

  async init() {
    this.server.registerTool(
      "search_items",
      {
        description: "Search items by keyword. Returns up to `limit` matches.",
        inputSchema: {
          query: z.string().describe("Search keywords"),
          limit: z.number().int().min(1).max(50).default(10),
        },
        annotations: { readOnlyHint: true },
      },
      async ({ query, limit }) => {
        const results = await upstreamApi.search(query, limit);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
      },
    );
  }
}

export default {
  fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const url = new URL(request.url);
    if (url.pathname === "/mcp") {
      return MyMCP.serve("/mcp").fetch(request, env, ctx);
    }
    return new Response("Not found", { status: 404 });
  },
};
```

`McpAgent` là wrapper của Cloudflare — nó xử lý streamable-HTTP transport, session routing, và Durable Object plumbing. Code của bạn chỉ chạm vào `this.server`, vốn là class `McpServer` giống nhau từ SDK. Mọi thứ trong `tool-design.md` và `server-capabilities.md` áp dụng không thay đổi.

---

## `wrangler.jsonc`

Template đi kèm với file này. Block Durable Objects là **boilerplate** — `McpAgent` dùng DO cho session state. Bạn không tương tác trực tiếp với nó.

```jsonc
{
  "name": "my-mcp-server",
  "main": "src/index.ts",
  "compatibility_date": "2025-03-10",
  "compatibility_flags": ["nodejs_compat"],
  "migrations": [{ "new_sqlite_classes": ["MyMCP"], "tag": "v1" }],
  "durable_objects": {
    "bindings": [{ "class_name": "MyMCP", "name": "MCP_OBJECT" }]
  }
}
```

Nếu bạn đổi tên class `MyMCP`, hãy cập nhật cả `new_sqlite_classes` và `class_name` cho khớp.

---

## Chạy và deploy

```bash
npx wrangler dev     # → http://localhost:8787/mcp
npx wrangler deploy  # → https://my-mcp-server.<account>.workers.dev/mcp
```

`wrangler deploy` in ra URL live. Đó là URL user dán vào Claude.

Secret (upstream API key): `npx wrangler secret put UPSTREAM_API_KEY`, sau đó đọc `env.UPSTREAM_API_KEY` bên trong `init()`.

---

## OAuth

Cloudflare cung cấp `@cloudflare/workers-oauth-provider` — một drop-in xử lý phía authorization server (CIMD/DCR endpoint, phát hành token, consent UI). Nó wrap `McpAgent` của bạn và chặn `/mcp` sau khi kiểm tra token. Xem `auth.md` để biết chi tiết giao thức; template CF `cloudflare/ai/demos/remote-mcp-github-oauth` cho thấy cách nối dây.
