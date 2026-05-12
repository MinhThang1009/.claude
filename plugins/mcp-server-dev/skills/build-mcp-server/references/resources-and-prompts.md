# Resources & Prompts — hai primitive còn lại

MCP định nghĩa ba primitive phía server. Tool do model điều khiển (Claude quyết định khi nào gọi chúng). Hai cái còn lại khác nhau:

- **Resource** do ứng dụng điều khiển — host quyết định cái gì được kéo vào context
- **Prompt** do user điều khiển — được hiển thị dưới dạng slash command hoặc menu item

Hầu hết server chỉ cần tool. Hãy dùng đến hai thứ này khi shape của integration không vừa với "Claude gọi một function."

---

## Resources

Resource là dữ liệu được xác định bằng URI. Không giống tool, nó không được *gọi* — nó được *đọc*. Host duyệt qua các resource có sẵn và quyết định cái nào được tải vào context.

**Khi resource tốt hơn tool:**
- Dữ liệu tham chiếu lớn (docs, schema, config) mà Claude nên có thể duyệt qua
- Nội dung thay đổi độc lập với cuộc hội thoại (log file, live data)
- Bất cứ thứ gì mà "Claude quyết định fetch" là mental model sai

**Khi tool tốt hơn:**
- Thao tác có side effect
- Kết quả phụ thuộc vào tham số Claude chọn
- Bạn muốn Claude (không phải host UI) quyết định khi nào kéo nó vào

### Static resource

```typescript
// TypeScript SDK
server.registerResource(
  "config",
  "config://app/settings",
  { name: "App Settings", description: "Current configuration", mimeType: "application/json" },
  async (uri) => ({
    contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify(config) }],
  }),
);
```

```python
# fastmcp
@mcp.resource("config://app/settings")
def get_settings() -> str:
    """Current application configuration."""
    return json.dumps(config)
```

### Dynamic resource (URI template)

Template RFC 6570 cho phép một lần đăng ký phục vụ nhiều URI:

```typescript
import { ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";

server.registerResource(
  "file",
  new ResourceTemplate("file:///{path}", { list: undefined }),
  { name: "File", description: "Read a file from the workspace" },
  async (uri, { path }) => ({
    contents: [{ uri: uri.href, text: await fs.readFile(path, "utf8") }],
  }),
);
```

```python
@mcp.resource("file:///{path}")
def read_file(path: str) -> str:
    return Path(path).read_text()
```

### Subscription

Resource có thể thông báo cho client khi chúng thay đổi. Khai báo `subscribe: true` trong capabilities, sau đó emit `notifications/resources/updated`. Host đọc lại. Hữu ích cho log tail, live dashboard, watched file.

---

## Prompt

Prompt là message template có tham số. Host hiển thị nó dưới dạng slash command hoặc menu item. User chọn nó, điền tham số, và các message kết quả được đưa vào cuộc hội thoại.

**Khi nào dùng:** các workflow đóng gói sẵn mà user chạy lặp lại — `/summarize-thread`, `/draft-reply`, `/explain-error`. Code gần như không có, đổi lại UX cao.

```typescript
server.registerPrompt(
  "summarize",
  {
    title: "Summarize document",
    description: "Generate a concise summary of the given text",
    argsSchema: { text: z.string(), max_words: z.string().optional() },
  },
  ({ text, max_words }) => ({
    messages: [{
      role: "user",
      content: { type: "text", text: `Summarize in ${max_words ?? "100"} words:\n\n${text}` },
    }],
  }),
);
```

```python
@mcp.prompt
def summarize(text: str, max_words: str = "100") -> str:
    """Generate a concise summary of the given text."""
    return f"Summarize in {max_words} words:\n\n{text}"
```

**Ràng buộc:**
- Argument chỉ là **string** (không có number, boolean, object) — convert bên trong handler
- Trả về mảng `messages[]` — có thể bao gồm embedded resource/image, không chỉ text
- Không có side effect — handler chỉ build message, không *làm* bất cứ điều gì

---

## Bảng quyết định nhanh

| Bạn muốn... | Dùng |
|---|---|
| Để Claude fetch thứ gì đó theo yêu cầu, với tham số | **Tool** |
| Expose context có thể duyệt được (file, doc, schema) | **Resource** |
| Expose một họ dynamic (`db://{table}`) | **Resource template** |
| Cho user một workflow một click | **Prompt** |
| Hỏi user điều gì đó giữa chừng tool | **Elicitation** (xem `elicitation.md`) |
