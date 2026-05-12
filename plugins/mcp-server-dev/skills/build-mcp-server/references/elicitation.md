# Elicitation — nhập liệu từ user theo spec native

Elicitation cho phép server tạm dừng giữa chừng một tool call và hỏi user nhập dữ liệu có cấu trúc. Client render một form native (không phải iframe, không phải HTML). User điền vào, server tiếp tục.

**Đây là câu trả lời đúng cho input đơn giản.** Widget (`build-mcp-app`) dành cho khi bạn cần UI phong phú — chart, danh sách có tìm kiếm, preview trực quan. Nếu bạn chỉ cần xác nhận, chọn option, hoặc vài trường form, elicitation đơn giản hơn, native theo spec, và hoạt động trên mọi host tuân thủ.

---

## ⚠️ Kiểm tra capability trước — hỗ trợ còn mới

Hỗ trợ của host rất mới:

| Host | Trạng thái |
|---|---|
| Claude Code | ✅ từ v2.1.76 (cả hai chế độ `form` và `url`) |
| Claude Desktop | Chưa xác nhận — có thể chưa hoặc rất gần đây |
| claude.ai | Chưa rõ |

**SDK throws `CapabilityNotSupported` nếu client không quảng bá elicitation.** Không có graceful degradation tích hợp sẵn. Bạn PHẢI kiểm tra và có fallback.

### Pattern chuẩn

```typescript
server.registerTool("delete_all", {
  description: "Delete all items after confirmation",
  inputSchema: {},
}, async ({}, extra) => {
  const caps = server.getClientCapabilities();
  if (caps?.elicitation) {
    const r = await server.elicitInput({
      mode: "form",
      message: "Delete all items? This cannot be undone.",
      requestedSchema: {
        type: "object",
        properties: { confirm: { type: "boolean", title: "Confirm deletion" } },
        required: ["confirm"],
      },
    });
    if (r.action === "accept" && r.content?.confirm) {
      await deleteAll();
      return { content: [{ type: "text", text: "Deleted." }] };
    }
    return { content: [{ type: "text", text: "Cancelled." }] };
  }
  // Fallback: trả về text yêu cầu Claude chuyển tiếp câu hỏi
  return { content: [{ type: "text", text: "Confirmation required. Please ask the user: 'Delete all items? This cannot be undone.' Then call this tool again with their answer." }] };
});
```

```python
# fastmcp
from fastmcp import Context
from fastmcp.exceptions import CapabilityNotSupported

@mcp.tool
async def delete_all(ctx: Context) -> str:
    try:
        result = await ctx.elicit("Delete all items? This cannot be undone.", response_type=bool)
        if result.action == "accept" and result.data:
            await do_delete()
            return "Deleted."
        return "Cancelled."
    except CapabilityNotSupported:
        return "Confirmation required. Ask the user to confirm deletion, then retry."
```

---

## Giới hạn schema

Schema elicitation bị giới hạn có chủ đích — giữ form đơn giản:

- **Chỉ flat object** — không nesting, không mảng object
- **Chỉ kiểu primitive** — `string`, `number`, `integer`, `boolean`, `enum`
- Các string format giới hạn ở: `email`, `uri`, `date`, `date-time`
- Dùng `title` và `description` trên mỗi property — chúng trở thành label của form

Nếu dữ liệu của bạn không vừa với các ràng buộc này, đó là tín hiệu để chuyển lên dùng widget.

---

## Response ba trạng thái

| Action | Ý nghĩa | `content` có không? |
|---|---|---|
| `accept` | User đã submit form | ✅ đã validate theo schema của bạn |
| `decline` | User chủ động từ chối | ❌ |
| `cancel` | User đóng (escape, click ra ngoài) | ❌ |

Xử lý `decline` và `cancel` khác nhau nếu cần — `decline` là cố ý, `cancel` có thể là vô tình.

`server.elicitInput()` của TS SDK tự động validate response `accept` theo schema của bạn qua Ajv. `ctx.elicit()` của fastmcp trả về một typed discriminated union (`AcceptedElicitation[T] | DeclinedElicitation | CancelledElicitation`).

---

## Shorthand response_type của fastmcp

```python
await ctx.elicit("Pick a color", response_type=["red", "green", "blue"])  # enum
await ctx.elicit("Enter email", response_type=str)                         # string
await ctx.elicit("Confirm?", response_type=bool)                           # boolean

@dataclass
class ContactInfo:
    name: str
    email: str
await ctx.elicit("Contact details", response_type=ContactInfo)             # flat dataclass
```

Chấp nhận: kiểu primitive, `list[str]` (trở thành enum), dataclass, TypedDict, Pydantic BaseModel. Tất cả phải là flat.

---

## Bảo mật

**KHÔNG ĐƯỢC yêu cầu password, API key, hoặc token qua elicitation** — yêu cầu của spec. Những thứ đó đi qua OAuth hoặc `user_config` với `sensitive: true` (MCPB), không phải runtime form.

---

## Khi nào chuyển lên dùng widget

Elicitation xử lý được: confirm dialog, enum picker, flat form ngắn.

Hãy dùng `build-mcp-app` widget khi bạn cần:
- Cấu trúc dữ liệu lồng nhau hoặc phức tạp
- Danh sách cuộn được/tìm kiếm được (100+ mục)
- Preview trực quan trước khi chọn (thumbnail ảnh, file tree)
- Progress cập nhật live hoặc nội dung streaming
- Layout tùy chỉnh, chart, map
