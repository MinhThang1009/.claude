---
name: build-mcp-app
description: This skill should be used when the user wants to build an "MCP app", add "interactive UI" or "widgets" to an MCP server, "render components in chat", build "MCP UI resources", make a tool that shows a "form", "picker", "dashboard" or "confirmation dialog" inline in the conversation, or mentions "apps SDK" in the context of MCP. Use AFTER the build-mcp-server skill has settled the deployment model, or when the user already knows they want UI widgets.
version: 0.1.0
---

# Xây dựng MCP App (Interactive UI Widgets)

MCP app là MCP server tiêu chuẩn **cộng thêm UI resources** — các interactive component được render inline trong chat surface. Build một lần, chạy trong Claude *và* ChatGPT và bất kỳ host nào implement apps surface.

UI layer là **bổ sung thêm**. Về cơ bản vẫn là tools, resources, và cùng wire protocol. Nếu bạn chưa build plain MCP server trước đây, skill `build-mcp-server` bao gồm base layer. Skill này thêm widgets lên trên.

> **Test trong Claude:** Thêm server như custom connector trên claude.ai (qua Cloudflare tunnel cho local dev) — điều này sẽ chạy thực tế iframe sandbox và `hostContext`. Xem https://claude.com/docs/connectors/building/testing.

## Các đặc điểm riêng của Claude host

| `_meta.ui.*` key | Nơi dùng | Tác dụng |
|---|---|---|
| `resourceUri` | tool | UI resource `ui://` nào host render cho kết quả của tool này. |
| `visibility: ["app"]` | tool | Ẩn widget-only helper tool (ví dụ geometry/image fetcher gọi qua `callServerTool`) khỏi tool list của Claude. |
| `prefersBorder: false` | resource | Bỏ outer card border của host (mobile). |
| `csp.{connectDomains, resourceDomains, baseUriDomains}` | resource | Khai báo external origins; mặc định là block-all. `frameDomains` hiện bị giới hạn trong Claude. |

- `hostContext.safeAreaInsets: {top, right, bottom, left}` (px) — tuân thủ điều này cho notches và composer overlay.
- Directory submission yêu cầu OAuth hoặc **authless** (`none`) — static bearer chỉ dùng private-deploy và bị block khi listing — cộng với tool `annotations` và 3–5 PNG screenshots; xem `references/directory-checklist.md`.

---

## Khi nào widget tốt hơn plain text

Đừng thêm UI chỉ vì có thể — hầu hết tools dùng text trả về là ổn. Thêm widget khi một trong các điều sau là đúng:

| Tín hiệu | Loại widget |
|---|---|
| Tool cần structured input mà Claude không thể suy ra đáng tin cậy | Form |
| User phải chọn từ list mà Claude không thể xếp hạng (files, contacts, records) | Picker / table |
| Action destructive hoặc billable cần xác nhận rõ ràng | Confirm dialog |
| Output là spatial hoặc visual (charts, maps, diffs, previews) | Display widget |
| Job chạy lâu mà user muốn theo dõi | Progress / live status |

Nếu không có điều nào áp dụng, bỏ qua widget. Text build nhanh hơn và nhanh hơn cho user.

---

## Widgets vs Elicitation — chọn đúng hướng

Trước khi build widget, kiểm tra xem **elicitation** có đáp ứng không. Elicitation là native theo spec, zero UI code, hoạt động trong bất kỳ compliant host nào.

| Nhu cầu | Elicitation | Widget |
|---|---|---|
| Xác nhận yes/no | ✅ | overkill |
| Chọn từ enum ngắn | ✅ | overkill |
| Điền flat form (tên, email, ngày) | ✅ | overkill |
| Chọn từ list lớn/có search | ❌ (không scroll/search) | ✅ |
| Visual preview trước khi chọn | ❌ | ✅ |
| Chart / map / diff view | ❌ | ✅ |
| Progress live-updating | ❌ | ✅ |

Nếu elicitation đáp ứng được, dùng nó. Xem `../build-mcp-server/references/elicitation.md`.

---

## Kiến trúc: hai hình thức deployment

### Remote MCP app (phổ biến nhất)

Hosted streamable-HTTP server. Widget templates được phục vụ như **resources**; kết quả tool tham chiếu đến chúng. Host fetch resource, render trong iframe sandbox, và broker messages giữa widget và Claude.

```
┌──────────┐  tools/call   ┌────────────┐
│  Claude  │─────────────> │ MCP server │
│   host   │<── result ────│  (remote)  │
│          │  + widget ref │            │
│          │               │            │
│          │ resources/read│            │
│          │─────────────> │  widget    │
│ ┌──────┐ │<── template ──│  HTML/JS   │
│ │iframe│ │               └────────────┘
│ │widget│ │
│ └──────┘ │
└──────────┘
```

### MCPB-packaged MCP app (local + UI)

Cơ chế widget giống như trên, nhưng server chạy local trong MCPB bundle. Dùng khi widget cần drive **local** application — ví dụ file picker duyệt disk thực, dialog điều khiển desktop app.

Về mechanics MCPB packaging, xem skill **`build-mcpb`**. Tất cả nội dung phía dưới áp dụng cho cả hai hình thức.

---

## Widget gắn với tools như thế nào

Widget-enabled tool có **hai đăng ký riêng biệt**:

1. **The tool** khai báo UI resource qua `_meta.ui.resourceUri`. Handler của nó trả về plain text/JSON — KHÔNG phải HTML.
2. **The resource** được đăng ký riêng và phục vụ HTML.

Khi Claude gọi tool, host thấy `_meta.ui.resourceUri`, fetch resource đó, render trong iframe, và pipe return value của tool vào iframe qua event `ontoolresult`.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerAppTool, registerAppResource, RESOURCE_MIME_TYPE }
  from "@modelcontextprotocol/ext-apps/server";
import { z } from "zod";

const server = new McpServer({ name: "contacts", version: "1.0.0" });

// 1. The tool — trả về DATA, khai báo UI nào sẽ hiển thị
registerAppTool(server, "pick_contact", {
  description: "Open an interactive contact picker",
  annotations: { title: "Pick Contact", readOnlyHint: true },
  inputSchema: { filter: z.string().optional() },
  _meta: { ui: { resourceUri: "ui://widgets/contact-picker.html" } },
}, async ({ filter }) => {
  const contacts = await db.contacts.search(filter);
  // Plain JSON — widget nhận qua ontoolresult
  return { content: [{ type: "text", text: JSON.stringify(contacts) }] };
});

// 2. The resource — phục vụ HTML
registerAppResource(
  server,
  "Contact Picker",
  "ui://widgets/contact-picker.html",
  {},
  async () => ({
    contents: [{
      uri: "ui://widgets/contact-picker.html",
      mimeType: RESOURCE_MIME_TYPE,
      text: pickerHtml,  // HTML string của bạn
    }],
  }),
);
```

URI scheme `ui://` là quy ước. MIME type PHẢI là `RESOURCE_MIME_TYPE` (`"text/html;profile=mcp-app"`) — đây là cách host biết render nó như interactive iframe, không chỉ hiển thị source.

---

## Widget runtime — class `App`

Trong iframe, script của bạn nói chuyện với host qua class `App` từ `@modelcontextprotocol/ext-apps`. Đây là **kết nối hai chiều liên tục** — widget giữ hoạt động chừng nào conversation còn active, nhận kết quả tool mới và gửi hành động của user.

```html
<script type="module">
  /* Bundle ext-apps inline lúc build time → globalThis.ExtApps */
  /*__EXT_APPS_BUNDLE__*/
  const { App } = globalThis.ExtApps;

  const app = new App({ name: "ContactPicker", version: "1.0.0" }, {});

  // Đặt handlers TRƯỚC khi connect
  app.ontoolresult = ({ content }) => {
    const contacts = JSON.parse(content[0].text);
    render(contacts);
  };

  await app.connect();

  // Sau, khi user click:
  function onPick(contact) {
    app.sendMessage({
      role: "user",
      content: [{ type: "text", text: `Selected contact: ${contact.id}` }],
    });
  }
</script>
```

Placeholder `/*__EXT_APPS_BUNDLE__*/` được server thay bằng nội dung của `@modelcontextprotocol/ext-apps/app-with-deps` lúc startup — xem `references/iframe-sandbox.md` để biết tại sao cần làm vậy và đoạn code rewrite. **Không** dùng `import { App } from "https://esm.sh/..."` — CSP của iframe block các transitive dependency fetches và widget render trắng.

| Method | Hướng | Dùng cho |
|---|---|---|
| `app.ontoolresult = fn` | Host → widget | Nhận return value của tool |
| `app.ontoolinput = fn` | Host → widget | Nhận input args của tool (Claude truyền vào) |
| `app.sendMessage({...})` | Widget → host | Inject message vào conversation |
| `app.updateModelContext({...})` | Widget → host | Cập nhật context im lặng (không có visible message) |
| `app.callServerTool({name, arguments})` | Widget → server | Gọi tool khác trên server của bạn |
| `app.openLink({url})` | Widget → host | Mở URL trong tab mới (sandbox block `window.open`) |
| `app.getHostContext()` / `app.onhostcontextchanged` | Host → widget | Theme, host CSS vars, `containerDimensions`, `displayMode`, `deviceCapabilities` |
| `app.requestDisplayMode({mode})` | Widget → host | Yêu cầu `inline` / `pip` / `fullscreen` |
| `app.downloadFile({name, mimeType, content})` | Widget → host | Download qua host (base64 content) |
| `new App(info, caps, {autoResize: true})` | — | Iframe height theo nội dung được render |

`sendMessage` là con đường thông thường "user đã chọn gì đó, báo Claude". `updateModelContext` dùng cho state mà Claude nên biết nhưng không nên làm bẩn chat. `openLink` là **bắt buộc** cho bất kỳ outbound navigation nào — `window.open` và `<a target="_blank">` bị block bởi sandbox attribute.

**Widgets không thể làm:**
- Truy cập DOM, cookies, hoặc storage của host page
- Thực hiện network calls đến arbitrary origins (CSP-restricted — route qua `callServerTool`)
- Mở popups hoặc navigate trực tiếp — dùng `app.openLink({url})`
- Load remote images đáng tin cậy — inline như `data:` URLs phía server

Giữ widgets **nhỏ và single-purpose**. Một picker thì chọn. Một chart thì hiển thị. Đừng build cả sub-app trong iframe — tách thành nhiều tools với focused widgets.

---

## Scaffold: minimal picker widget

**Cài đặt:**

```bash
npm install @modelcontextprotocol/sdk @modelcontextprotocol/ext-apps zod express
```

**Server (`src/server.ts`):**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { registerAppTool, registerAppResource, RESOURCE_MIME_TYPE }
  from "@modelcontextprotocol/ext-apps/server";
import express from "express";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { z } from "zod";

const require = createRequire(import.meta.url);
const server = new McpServer({ name: "contact-picker", version: "1.0.0" });

// Inline ext-apps browser bundle vào widget HTML.
// CSP của iframe block CDN script fetches — bundling là bắt buộc.
const bundle = readFileSync(
  require.resolve("@modelcontextprotocol/ext-apps/app-with-deps"), "utf8",
).replace(/export\{([^}]+)\};?\s*$/, (_, body) =>
  "globalThis.ExtApps={" +
  body.split(",").map((p) => {
    const [local, exported] = p.split(" as ").map((s) => s.trim());
    return `${exported ?? local}:${local}`;
  }).join(",") + "};",
);
const pickerHtml = readFileSync("./widgets/picker.html", "utf8")
  .replace("/*__EXT_APPS_BUNDLE__*/", () => bundle);

registerAppTool(server, "pick_contact", {
  description: "Open an interactive contact picker. User selects one contact.",
  annotations: { title: "Pick Contact", readOnlyHint: true },
  inputSchema: { filter: z.string().optional().describe("Name/email prefix filter") },
  _meta: { ui: { resourceUri: "ui://widgets/picker.html" } },
}, async ({ filter }) => {
  const contacts = await db.contacts.search(filter ?? "");
  return { content: [{ type: "text", text: JSON.stringify(contacts) }] };
});

registerAppResource(server, "Contact Picker", "ui://widgets/picker.html", {},
  async () => ({
    contents: [{ uri: "ui://widgets/picker.html", mimeType: RESOURCE_MIME_TYPE, text: pickerHtml }],
  }),
);

const app = express();
app.use(express.json());
app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});
app.listen(process.env.PORT ?? 3000);
```

Cho widget apps chỉ local (drive desktop app, đọc local files), swap transport sang `StdioServerTransport` và đóng gói qua skill `build-mcpb`.

**Widget (`widgets/picker.html`):**

```html
<!doctype html>
<meta charset="utf-8" />
<style>
  body { font: 14px system-ui; margin: 0; }
  ul { list-style: none; padding: 0; margin: 0; max-height: 300px; overflow-y: auto; }
  li { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #eee; }
  li:hover { background: #f5f5f5; }
  .sub { color: #666; font-size: 12px; }
</style>
<ul id="list"></ul>
<script type="module">
/*__EXT_APPS_BUNDLE__*/
const { App } = globalThis.ExtApps;
(async () => {
  const app = new App({ name: "ContactPicker", version: "1.0.0" }, {});
  const ul = document.getElementById("list");

  app.ontoolresult = ({ content }) => {
    const contacts = JSON.parse(content[0].text);
    ul.innerHTML = "";
    for (const c of contacts) {
      const li = document.createElement("li");
      li.innerHTML = `<div>${c.name}</div><div class="sub">${c.email}</div>`;
      li.addEventListener("click", () => {
        app.sendMessage({
          role: "user",
          content: [{ type: "text", text: `Selected contact: ${c.id} (${c.name})` }],
        });
      });
      ul.append(li);
    }
  };

  await app.connect();
})();
</script>
```

Xem `references/widget-templates.md` để biết thêm các widget shapes.

---

## Lưu ý thiết kế tránh phải viết lại

**Một widget mỗi tool.** Cưỡng lại cám dỗ build một mega-widget làm tất cả mọi thứ. Một tool → một focused widget → một result shape rõ ràng. Claude lý luận về những cái này tốt hơn nhiều.

**Tool description phải đề cập widget.** Claude chỉ thấy tool description khi quyết định gọi cái gì. "Opens an interactive picker" trong description là thứ khiến Claude chọn nó thay vì đoán ID.

**Widgets là optional khi runtime.** Hosts không hỗ trợ apps surface chỉ đơn giản bỏ qua `_meta.ui` và render text content của tool bình thường. Vì tool handler đã trả về text/JSON có nghĩa (dữ liệu của widget), degradation là tự động — Claude thấy dữ liệu trực tiếp thay vì qua widget.

**Đừng block trên widget results cho read-only tools.** Widget chỉ *hiển thị* dữ liệu (chart, preview) không nên yêu cầu user action để hoàn thành. Trả về display widget *và* text summary trong cùng result để Claude có thể tiếp tục lý luận mà không cần chờ.

**Phân chia layout theo số lượng item, không theo số tool.** Nếu một use case là "hiển thị một kết quả chi tiết" và cái khác là "hiển thị nhiều kết quả cạnh nhau", đừng tạo hai tools — tạo một tool nhận `items[]`, và để widget chọn layout: `items.length === 1` → detail view, `> 1` → carousel. Giữ server schema đơn giản và để Claude quyết định count tự nhiên.

**Đặt reasoning của Claude trong payload.** Field `note` ngắn trên mỗi item (tại sao Claude chọn nó) render như callout trên card giúp user thấy reasoning inline với lựa chọn. Đề cập field này trong tool description để Claude điền vào.

**Normalize image shapes phía server.** Nếu data source của bạn trả về images với aspect ratios rất khác nhau, rewrite về dạng biến thể có thể đoán trước (ví dụ square-bounded) *trước khi* fetch để data-URL inline. Sau đó đặt container image của widget có `aspect-ratio` cố định + `object-fit: contain` để mọi thứ ngồi ở giữa.

**Theo theme của host.** `app.getHostContext()?.theme` (sau `connect()`) cộng `app.onhostcontextchanged` cho live updates. Toggle class `.dark` trên `<html>`, giữ màu trong CSS custom props với override block `:root.dark {}`, đặt `color-scheme`. Tắt `mix-blend-mode: multiply` trong dark — nó làm ảnh biến mất.

---

## Testing

**Claude Desktop** — các bản build hiện tại vẫn yêu cầu config shape `command`/`args` (không có `"type": "http"` native). Wrap bằng `mcp-remote` và force `http-only` transport để probe SSE không nuốt mất widget-capability negotiation:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:3000/mcp",
               "--allow-http", "--transport", "http-only"]
    }
  }
}
```

Desktop cache UI resources tích cực. Sau khi edit widget HTML, **quit hoàn toàn** (⌘Q / Alt+F4, không phải đóng window) và relaunch để force cold resource re-fetch.

**Headless JSON-RPC loop** — iterate nhanh mà không cần click qua Desktop:

```bash
# test.jsonl — một JSON-RPC message mỗi dòng
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"your_tool","arguments":{...}}}

(cat test.jsonl; sleep 10) | npx mcp-remote http://localhost:3000/mcp --allow-http
```

`sleep` giữ stdin mở đủ lâu để thu thập tất cả responses. Parse jsonl output bằng `jq` hoặc Python one-liner.

**Widget dev loop** — tránh hoàn toàn vòng lặp ⌘Q-relaunch bằng cách serve inlined widget HTML tại GET route đơn giản với fake `ExtApps` shim fire `ontoolresult` từ query param:

```ts
app.get("/widget-preview", (_req, res) => {
  const shim = `globalThis.ExtApps={applyHostStyleVariables:()=>{},App:class{
    constructor(){this.h={}} ontoolresult;onhostcontextchanged;
    async connect(){const p=new URLSearchParams(location.search).get("payload");
      if(p)this.ontoolresult?.({content:[{type:"text",text:p}]});}
    getHostContext(){return{theme:"light"}}
    sendMessage(m){console.log("sendMessage",m)} updateModelContext(){}
    callServerTool(){return Promise.resolve({content:[]})} openLink(){} downloadFile(){}
  }};`;
  res.type("html").send(widgetHtml.replace("/*__EXT_APPS_BUNDLE__*/", shim));
});
```

Mở `http://localhost:3000/widget-preview?payload={"rows":[...]}` trong browser tab bình thường và iterate với devtools thông thường.

**Host fallback** — dùng host không có apps surface (hoặc MCP Inspector) và xác nhận text content của tool degraded đúng cách.

**CSP debugging** — mở devtools console của chính iframe. CSP violations là lý do #1 tại sao widgets fail im lặng (hình chữ nhật trắng, không có lỗi trong main console). Xem `references/iframe-sandbox.md`.

---

## Reference files

- `references/iframe-sandbox.md` — CSP/sandbox constraints, bundle-inlining pattern, image handling, host theming
- `references/widget-templates.md` — reusable HTML scaffolds cho picker / confirm / progress / display
- `references/apps-sdk-messages.md` — App class API: widget ↔ host ↔ server messaging, lifecycle & supersession
- `references/payload-budgeting.md` — giới hạn tool-result size của host, prune-then-truncate, heavy assets qua `callServerTool`
- `references/abuse-protection.md` — Anthropic egress CIDRs, tiered rate limiting, `trust proxy`, response caching
- `references/directory-checklist.md` — pre-flight cho connector-directory submission
