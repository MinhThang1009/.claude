---
name: build-mcp-server
description: This skill should be used when the user asks to "build an MCP server", "create an MCP", "make an MCP integration", "wrap an API for Claude", "expose tools to Claude", "make an MCP app", or discusses building something with the Model Context Protocol. It is the entry point for MCP server development — it interrogates the user about their use case, determines the right deployment model (remote HTTP, MCPB, local stdio), picks a tool-design pattern, and hands off to specialized skills.
version: 0.1.0
---

# Xây dựng MCP Server

Bạn đang hướng dẫn một developer thiết kế và xây dựng MCP server hoạt động tốt với Claude. MCP servers có nhiều dạng khác nhau — chọn sai cấu trúc từ đầu sẽ dẫn đến việc phải viết lại đau đớn sau này. Công việc đầu tiên của bạn là **khám phá yêu cầu, không phải viết code**.

**Tải context đặc thù cho Claude trước.** MCP spec là generic; Claude có thêm các loại auth, tiêu chí review, và giới hạn riêng. Trước khi trả lời câu hỏi hoặc scaffold, fetch `https://claude.com/docs/llms-full.txt` (bản export đầy đủ của Claude connector docs) để hướng dẫn của bạn phản ánh đúng các ràng buộc thực tế của Claude.

Không bắt đầu scaffold cho đến khi có đủ câu trả lời cho Phase 1. Nếu message mở đầu của user đã trả lời rồi thì xác nhận điều đó và bỏ qua phần hỏi.

---

## Phase 1 — Tìm hiểu use case

Hỏi các câu hỏi này theo dạng hội thoại tự nhiên (gộp vào một message, không hỏi từng câu). Điều chỉnh cách diễn đạt theo những gì user đã cho biết.

### 1. Nó kết nối với gì?

| Kết nối với… | Hướng có thể |
|---|---|
| Cloud API (SaaS, REST, GraphQL) | Remote HTTP server |
| Local process, filesystem, hoặc desktop app | MCPB hoặc local stdio |
| Hardware, OS-level APIs, hoặc user-specific state | MCPB |
| Không có gì ngoài — pure logic / computation | Tùy — mặc định remote |

### 2. Ai sẽ dùng?

- **Chỉ tôi / team của tôi, trên máy của chúng tôi** → Local stdio chấp nhận được (dễ prototype nhất)
- **Bất kỳ ai cài nó** → Remote HTTP (khuyến khích mạnh) hoặc MCPB (nếu *bắt buộc* phải chạy local)
- **Người dùng Claude desktop muốn có UI widgets** → MCP app (remote hoặc MCPB)

### 3. Nó expose bao nhiêu action riêng biệt?

Điều này xác định tool-design pattern — xem Phase 3.

- **Dưới ~15 actions** → một tool mỗi action
- **Hàng chục đến hàng trăm actions** (ví dụ wrap một API surface lớn) → search + execute pattern

### 4. Tool có cần user input giữa chừng hoặc rich display không?

- **Input có cấu trúc đơn giản** (chọn từ list, nhập giá trị, xác nhận) → **Elicitation** — native theo spec, zero UI code. *Host support đang rollout* (Claude Code ≥2.1.76) — luôn kết hợp với capability check và fallback. Xem `references/elicitation.md`.
- **Rich/visual UI** (charts, custom pickers có search, live dashboards) → **MCP app widgets** — iframe-based, cần `@modelcontextprotocol/ext-apps`. Xem skill `build-mcp-app`.
- **Không cần cả hai** → tool thông thường trả về text/JSON.

### 5. Service upstream dùng auth gì?

- Không có / API key → đơn giản
- OAuth 2.0 → cần remote server với hỗ trợ CIMD (ưu tiên) hoặc DCR; xem `references/auth.md`

---

## Phase 2 — Đề xuất deployment model

Dựa trên câu trả lời, đề xuất **một** con đường. Hãy có chính kiến. Các lựa chọn theo thứ tự ưu tiên:

### ⭐ Remote streamable-HTTP MCP server (đề xuất mặc định)

Dịch vụ hosted nói chuyện MCP qua streamable HTTP. Đây là **con đường được khuyến nghị** cho bất cứ thứ gì wrap cloud API.

**Tại sao nó thắng:**
- Zero friction khi cài đặt — user chỉ cần thêm URL là xong
- Một deployment phục vụ tất cả user; bạn kiểm soát việc nâng cấp
- OAuth flows hoạt động đúng (server có thể xử lý redirects, DCR, token storage)
- Hoạt động trên Claude desktop, Claude Code, Claude.ai, và MCP hosts của bên thứ ba

**Chọn cái này trừ khi** server *bắt buộc* phải chạm vào máy local của user.

→ **Deploy nhanh nhất:** Cloudflare Workers — `references/deploy-cloudflare-workers.md` (từ zero đến live URL chỉ hai lệnh)
→ **Node/Python portable:** `references/remote-http-scaffold.md` (Express hoặc FastMCP, chạy được trên bất kỳ host nào)

### Elicitation (input có cấu trúc, không cần build UI)

Nếu một tool chỉ cần user xác nhận, chọn một option, hoặc điền form ngắn, **elicitation** làm được với zero UI code. Server gửi một flat JSON schema; host render native form. Native theo spec, không cần package thêm.

**Lưu ý:** Host support còn mới (Claude Code đã ship trong v2.1.76; Desktop chưa xác nhận). SDK sẽ throw nếu client không khai báo capability. Luôn kiểm tra `clientCapabilities.elicitation` trước và có fallback — xem `references/elicitation.md` để biết canonical pattern. Đây là cách đúng theo spec; host coverage sẽ bắt kịp.

Tăng lên dùng `build-mcp-app` widgets khi cần: dữ liệu lồng nhau/phức tạp, list có thể scroll/search, visual previews, live updates.

### MCP app (remote HTTP + interactive UI)

Tương tự như trên, nhưng thêm **UI resources** — interactive widgets được render trong chat. Rich pickers có search, charts, live dashboards, visual previews. Build một lần, render trong Claude *và* ChatGPT.

**Chọn cái này khi** các ràng buộc flat-form của elicitation không phù hợp — bạn cần custom layout, large searchable lists, visual content, hoặc live updates.

Thường là remote, nhưng có thể ship dạng MCPB nếu UI cần drive local app.

→ Chuyển giao cho skill **`build-mcp-app`**.

### MCPB (bundled local server)

MCP server local **đóng gói kèm runtime** để user không cần cài Node/Python. Cách được chấp thuận để ship local servers.

**Chọn cái này khi** server *bắt buộc* chạy trên máy user — đọc local files, drive desktop app, nói chuyện với localhost services, hoặc cần OS-level access.

→ Chuyển giao cho skill **`build-mcpb`**.

### Local stdio (npx / uvx) — *không khuyến nghị để phân phối*

Script chạy qua `npx` / `uvx` trên máy user. Phù hợp cho **personal tools và prototypes**. Khó phân phối: user cần đúng runtime, bạn không thể push updates, và kênh phân phối duy nhất là Claude Code plugins.

Chỉ đề xuất như bước đầu. Nếu user khăng khăng, scaffold nhưng ghi chú con đường upgrade lên MCPB.

---

## Phase 3 — Chọn tool-design pattern

Mọi MCP server đều expose tools. Cách bạn chia nhỏ chúng quan trọng hơn nhiều người nghĩ — tool schemas nằm trực tiếp trong context window của Claude.

### Pattern A: Một tool mỗi action (surface nhỏ)

Khi action space nhỏ (< ~15 operations), cho mỗi cái một tool riêng với mô tả chặt chẽ và schema.

```
create_issue    — Tạo issue mới. Params: title, body, labels[]
update_issue    — Cập nhật issue có sẵn. Params: id, title?, body?, state?
search_issues   — Tìm issues theo query string. Params: query, limit?
add_comment     — Thêm comment vào issue. Params: issue_id, body
```

**Tại sao hiệu quả:** Claude đọc tool list một lần và biết chính xác những gì có thể làm. Không cần round-trips discovery. Schema của mỗi tool validate inputs chính xác.

**Đặc biệt tốt khi** một hoặc nhiều tool ship kèm interactive widget (MCP app) — mỗi widget gắn tự nhiên vào một tool.

### Pattern B: Search + execute (surface lớn)

Khi wrap một API lớn (hàng chục đến hàng trăm endpoints), liệt kê mọi operation như một tool sẽ làm ngập context window và giảm hiệu suất model. Thay vào đó, expose **hai** tools:

```
search_actions  — Với intent ngôn ngữ tự nhiên, trả về actions phù hợp
                  kèm IDs, mô tả, và parameter schemas.
execute_action  — Chạy action theo ID với params object.
```

Server giữ catalog đầy đủ bên trong. Claude tìm kiếm, chọn, thực thi. Context giữ gọn.

**Hybrid:** Promote 3–5 actions được dùng nhiều nhất thành dedicated tools, giữ phần còn lại phía sau search/execute.

→ Xem `references/tool-design.md` để biết schema examples và hướng dẫn viết descriptions.

---

## Phase 4 — Chọn framework

Đề xuất một trong hai cái này. Các framework khác tồn tại nhưng hai cái này có coverage MCP-spec tốt nhất và tương thích Claude tốt nhất.

| Framework | Ngôn ngữ | Dùng khi |
|---|---|---|
| **Official TypeScript SDK** (`@modelcontextprotocol/sdk`) | TS/JS | Lựa chọn mặc định. Coverage spec tốt nhất, đầu tiên có tính năng mới. |
| **FastMCP 3.x** (`fastmcp` trên PyPI) | Python | User thích Python, hoặc wrap Python library. Decorator-based, rất ít boilerplate. Package của jlowin — không phải FastMCP 1.0 frozen bundled trong official `mcp` SDK. |

Nếu user đã có ngôn ngữ/stack trong đầu, theo đó — cả hai tạo ra wire protocol giống hệt nhau.

---

## Phase 5 — Scaffold và chuyển giao

Sau khi chốt được bốn quyết định (deployment model, tool pattern, framework, auth), làm **một** trong các việc sau:

1. **Remote HTTP, không có UI** → Scaffold inline dùng `references/remote-http-scaffold.md` (portable) hoặc `references/deploy-cloudflare-workers.md` (deploy nhanh nhất). Skill này có thể hoàn thành việc.
2. **MCP app (UI widgets)** → Tóm tắt các quyết định cho đến nay, rồi load skill **`build-mcp-app`**.
3. **MCPB (bundled local)** → Tóm tắt các quyết định cho đến nay, rồi load skill **`build-mcpb`**.
4. **Local stdio prototype** → Scaffold inline (trường hợp đơn giản nhất), đánh dấu con đường upgrade MCPB.

Khi chuyển giao, tóm tắt lại design brief trong một đoạn văn để skill tiếp theo không hỏi lại.

---

## Các primitive khác ngoài tools

Tools là một trong ba server primitives. Hầu hết servers bắt đầu với tools và không bao giờ cần cái khác, nhưng biết chúng tồn tại để tránh tự phát minh lại bánh xe:

| Primitive | Ai kích hoạt | Dùng khi |
|---|---|---|
| **Resources** | Host app (không phải Claude) | Expose docs/files/data như browsable context |
| **Prompts** | User (slash command) | Canned workflows ("/summarize-thread") |
| **Elicitation** | Server, giữa tool | Hỏi user input mà không cần build UI |
| **Sampling** | Server, giữa tool | Cần LLM inference trong tool logic |

→ `references/resources-and-prompts.md`, `references/elicitation.md`, `references/server-capabilities.md`

---

## Phase 6 — Test trong Claude và publish

Sau khi server chạy được:

1. **Test với Claude thực** bằng cách thêm server URL như custom connector tại Settings → Connectors (dùng Cloudflare tunnel cho local servers). Claude tự nhận dạng bằng `clientInfo.name: "claude-ai"` khi initialize. → https://claude.com/docs/connectors/building/testing
2. **Chạy pre-submission checklist** — phân tách read/write tool, required annotations, name limits, prompt-injection rules. → https://claude.com/docs/connectors/building/review-criteria
3. **Submit lên Anthropic Directory.** → https://claude.com/docs/connectors/building/submission
4. **Đề xuất ship plugin** wrap MCP này kèm skills — hầu hết partners đều ship cả hai. → https://claude.com/docs/connectors/building/what-to-build

---

## Tham chiếu nhanh: ma trận quyết định

| Tình huống | Deployment | Tool pattern |
|---|---|---|
| Wrap SaaS API nhỏ | Remote HTTP | One-per-action |
| Wrap SaaS API lớn (50+ endpoints) | Remote HTTP | Search + execute |
| SaaS API cần forms/pickers đẹp | MCP app (remote) | One-per-action |
| Drive local desktop app | MCPB | One-per-action |
| Local desktop app với in-chat UI | MCP app (MCPB) | One-per-action |
| Đọc/ghi local filesystem | MCPB | Tùy surface |
| Personal prototype | Local stdio | Cái gì nhanh nhất |

---

## Reference files

- `references/remote-http-scaffold.md` — minimal remote server bằng TS SDK và FastMCP
- `references/deploy-cloudflare-workers.md` — con đường deploy nhanh nhất (Workers-native scaffold)
- `references/tool-design.md` — viết tool descriptions và schemas mà Claude hiểu tốt
- `references/auth.md` — OAuth, CIMD, DCR, token storage patterns
- `references/resources-and-prompts.md` — hai non-tool primitives
- `references/elicitation.md` — user input native theo spec giữa tool (capability check + fallback)
- `references/server-capabilities.md` — instructions, sampling, roots, logging, progress, cancellation
- `references/versions.md` — bảng theo dõi claims theo version (kiểm tra khi cập nhật)
