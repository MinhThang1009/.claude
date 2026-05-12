# Remote Streamable-HTTP MCP Server — Scaffold

Các server hoạt động tối giản trong cả hai framework được khuyến nghị. Bắt đầu từ đây, sau đó thêm tool.

---

## TypeScript SDK (`@modelcontextprotocol/sdk`)

```bash
npm init -y
npm install @modelcontextprotocol/sdk zod express
npm install -D typescript @types/express @types/node tsx
```

**`src/server.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { z } from "zod";

const server = new McpServer(
  { name: "my-service", version: "0.1.0" },
  { instructions: "Prefer search_items before calling get_item directly — IDs aren't guessable." },
);

// Pattern A: một tool cho một action
server.registerTool(
  "search_items",
  {
    description: "Search items by keyword. Returns up to `limit` matches ranked by relevance.",
    inputSchema: {
      query: z.string().describe("Search keywords"),
      limit: z.number().int().min(1).max(50).default(10),
    },
    annotations: { readOnlyHint: true },
  },
  async ({ query, limit }, extra) => {
    // extra.signal là AbortSignal — kiểm tra nó trong vòng lặp dài để xử lý cancellation
    const results = await upstreamApi.search(query, limit);
    return {
      content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
    };
  },
);

server.registerTool(
  "get_item",
  {
    description: "Fetch a single item by its ID.",
    inputSchema: { id: z.string() },
    annotations: { readOnlyHint: true },
  },
  async ({ id }) => {
    const item = await upstreamApi.get(id);
    return { content: [{ type: "text", text: JSON.stringify(item) }] };
  },
);

// Streamable HTTP transport (chế độ stateless — đơn giản nhất)
const app = express();
app.use(express.json());

app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined, // stateless
  });
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

app.listen(process.env.PORT ?? 3000);
```

**Stateless vs stateful:** Đoạn code trên tạo transport mới cho mỗi request (stateless). Ổn cho hầu hết server bọc API. Nếu các tool cần chia sẻ state qua nhiều call trong một session (hiếm gặp), dùng session-keyed transport map — xem `examples/server/simpleStreamableHttp.ts` trong SDK.

---

## FastMCP 3.x (Python)

```bash
pip install fastmcp
```

**`server.py`**

```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="my-service",
    instructions="Prefer search_items before calling get_item directly — IDs aren't guessable.",
)

@mcp.tool(annotations={"readOnlyHint": True})
def search_items(query: str, limit: int = 10) -> list[dict]:
    """Search items by keyword. Returns up to `limit` matches ranked by relevance."""
    return upstream_api.search(query, limit)

@mcp.tool(annotations={"readOnlyHint": True})
def get_item(id: str) -> dict:
    """Fetch a single item by its ID."""
    return upstream_api.get(id)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=3000)
```

FastMCP tự suy ra JSON schema từ type hint và docstring trở thành mô tả tool. Giữ docstring ngắn gọn và hướng đến hành động — chúng được đưa vào context window của Claude nguyên văn.

---

## Pattern search + execute (API surface lớn)

Khi bọc 50+ endpoint, đừng đăng ký tất cả. Dùng hai tool:

```typescript
const CATALOG = loadActionCatalog(); // { id, description, paramSchema }[]

server.registerTool(
  "search_actions",
  {
    description: "Find available actions matching an intent. Call this first to discover what's possible. Returns action IDs, descriptions, and parameter schemas.",
    inputSchema: { intent: z.string().describe("What you want to do, in plain English") },
    annotations: { readOnlyHint: true },
  },
  async ({ intent }) => {
    const matches = rankActions(CATALOG, intent).slice(0, 10);
    return { content: [{ type: "text", text: JSON.stringify(matches, null, 2) }] };
  },
);

server.registerTool(
  "execute_action",
  {
    description: "Execute an action by ID. Get the ID and params schema from search_actions first.",
    inputSchema: {
      action_id: z.string(),
      params: z.record(z.unknown()),
    },
  },
  async ({ action_id, params }) => {
    const action = CATALOG.find(a => a.id === action_id);
    if (!action) throw new Error(`Unknown action: ${action_id}`);
    validate(params, action.paramSchema);
    const result = await dispatch(action, params);
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  },
);
```

`rankActions` có thể bắt đầu đơn giản bằng keyword matching. Nâng cấp lên embedding nếu độ chính xác quan trọng.

---

## Kiểm thử

MCP Inspector kết nối tới bất kỳ transport nào và cho phép bạn thao tác với tool theo cách tương tác.

```bash
# Tương tác — mở UI tại localhost:6274
npx @modelcontextprotocol/inspector
# → chọn "Streamable HTTP", dán http://localhost:3000/mcp, Connect
```

Để kiểm tra tự động (CI, smoke test):

```bash
npx @modelcontextprotocol/inspector --cli http://localhost:3000/mcp \
  --transport http --method tools/list

npx @modelcontextprotocol/inspector --cli http://localhost:3000/mcp \
  --transport http --method tools/call --tool-name search_items --tool-arg query=test
```

---

## Kết nối user

Sau khi deploy, user thêm URL trực tiếp — không cần bước install.

| Bề mặt | Cách làm |
|---|---|
| **Claude Code** | `claude mcp add --transport http <name> <url>` (thêm `--scope user` để global, `--header "Authorization: Bearer ..."` để auth) |
| **Claude Desktop / Claude.ai** | Settings → Connectors → Add custom connector. **Không** dùng `claude_desktop_config.json` — remote server được cấu hình ở đó sẽ bị bỏ qua. |
| **Connector directory** | Anthropic có hướng dẫn nộp để được liệt kê trong public connector directory. |

---

## Deploy

**Con đường nhanh nhất:** Cloudflare Workers — hai lệnh từ zero đến URL `https://` live trên free tier. Dùng scaffold native của Workers (không phải Express). → `deploy-cloudflare-workers.md`

**Express scaffold này** chạy trên bất kỳ Node host nào — Render, Railway, Fly.io, VPS. Container hóa nó (`node:20-slim`, copy, `npm ci`, `node dist/server.js`) và ship. FastMCP là câu chuyện tương tự với Python base image.

---

## Checklist trước khi deploy

- [ ] `POST /mcp` phản hồi `initialize` với server capabilities
- [ ] `tools/list` trả về tool của bạn với schema đầy đủ
- [ ] Lỗi trả về MCP error có cấu trúc, không phải HTTP 500 với body HTML
- [ ] CORS header được set nếu browser client sẽ kết nối
- [ ] Header `Origin` được validate trên `/mcp` (MUST theo spec — ngăn DNS rebinding)
- [ ] Header `MCP-Protocol-Version` được tôn trọng (trả về 400 với version không hỗ trợ)
- [ ] Field `instructions` được set nếu việc dùng tool cần gợi ý
- [ ] Health check endpoint tách biệt với `/mcp` (host poll endpoint này)
- [ ] Secret lấy từ env var, không bao giờ hardcode
- [ ] Nếu dùng OAuth: CIMD hoặc DCR endpoint đã được implement — xem `auth.md`
