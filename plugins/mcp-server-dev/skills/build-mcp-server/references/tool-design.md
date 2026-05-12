# Tool Design — Viết Tool mà Claude Dùng Đúng

Schema và mô tả tool là prompt engineering. Chúng được đưa thẳng vào context của Claude và quyết định Claude có chọn đúng tool với đúng argument không. Hầu hết lỗi tích hợp MCP đều bắt nguồn từ mô tả mơ hồ hoặc schema lỏng lẻo.

## Yêu cầu bắt buộc của Anthropic Directory

Nếu server này sẽ được nộp lên Anthropic Directory, những điều sau là tiêu chí review pass/fail (danh sách đầy đủ: https://claude.com/docs/connectors/building/review-criteria):

- Mỗi tool **phải** có annotation `readOnlyHint`, `destructiveHint`, và `title` — chúng quyết định auto-permission trong Claude.
- Tên tool **phải** ≤64 ký tự.
- Thao tác đọc và ghi **phải** nằm trong các tool riêng biệt. Một tool duy nhất chấp nhận cả GET lẫn POST/PUT/PATCH/DELETE sẽ bị từ chối — ghi chú safe vs unsafe trong mô tả của một tool không đáp ứng yêu cầu này.
- Mô tả tool **không được** hướng dẫn Claude cách hành xử (ví dụ: "luôn làm X", "bạn phải gọi Y trước", ghi đè system instruction, quảng bá sản phẩm) — bị coi là prompt injection khi review.
- Tool chấp nhận endpoint/param API tự do **phải** tham chiếu đến documentation của API mục tiêu trong mô tả.

---

## Mô tả

**Mô tả là hợp đồng.** Đó là thứ duy nhất Claude đọc trước khi quyết định có gọi tool không. Viết nó như một dòng manpage cộng với gợi ý phân biệt.

### Tốt

```
search_issues — Search issues by keyword across title and body. Returns up
to `limit` results ranked by recency. Does NOT search comments or PRs —
use search_comments / search_prs for those.
```

- Nói rõ nó làm gì
- Nói rõ nó trả về gì
- Nói rõ nó *không* làm gì (ngăn việc gọi sai tool)

### Kém

```
search_issues — Searches for issues.
```

Claude sẽ gọi tool này cho bất cứ thứ gì trông có vẻ search, kể cả những thứ nó không làm được.

### Phân biệt các tool tương tự

Khi hai tool giống nhau, mỗi mô tả nên nói khi nào dùng *tool kia*:

```
get_user      — Fetch a user by ID. If you only have an email, use find_user_by_email.
find_user_by_email — Look up a user by email address. Returns null if not found.
```

---

## Parameter schema

**Schema chặt ngăn bad call.** Mọi ràng buộc bạn thể hiện trong schema là một thứ ít hơn có thể sai lúc runtime.

| Thay vì | Dùng |
|---|---|
| `z.string()` cho ID | `z.string().regex(/^usr_[a-z0-9]{12}$/)` |
| `z.number()` cho limit | `z.number().int().min(1).max(100).default(20)` |
| `z.string()` cho lựa chọn | `z.enum(["open", "closed", "all"])` |
| optional không có gợi ý | `.optional().describe("Defaults to the caller's workspace")` |

**Mô tả mọi parameter.** Text `.describe()` xuất hiện trong schema mà Claude thấy. Bỏ qua nó là bỏ phí cơ hội.

```typescript
{
  query: z.string().describe("Keywords to search for. Supports quoted phrases."),
  status: z.enum(["open", "closed", "all"]).default("open")
    .describe("Filter by status. Use 'all' to include closed items."),
  limit: z.number().int().min(1).max(50).default(10)
    .describe("Max results. Hard cap at 50."),
}
```

---

## Hình dạng return

Claude đọc bất cứ thứ gì bạn đặt trong `content[].text`. Làm cho nó dễ parse.

**Nên:**
- Trả JSON cho dữ liệu có cấu trúc (`JSON.stringify(result, null, 2)`)
- Trả xác nhận ngắn cho mutation (`"Created issue #123"`)
- Bao gồm ID mà Claude sẽ cần cho các call tiếp theo
- Cắt bớt payload lớn và nói rõ (`"Showing 10 of 847 results. Refine the query to narrow down."`)

**Không nên:**
- Trả raw HTML
- Trả megabyte API response chưa lọc
- Trả thành công trống không có identifier (`"ok"` sau khi create — Claude không thể tham chiếu đến thứ nó vừa tạo)

---

## Bao nhiêu tool?

| Số lượng tool | Hướng dẫn |
|---|---|
| 1–15 | Một tool cho một action. Lý tưởng. |
| 15–30 | Vẫn ổn. Audit tìm cặp gần giống có thể gộp lại. |
| 30+ | Chuyển sang search + execute. Tùy chọn đưa top 3–5 lên thành tool riêng. |

Giới hạn không phải là hard limit của protocol — đó là kinh tế context window. Mỗi schema tool là token Claude tiêu tốn *mỗi lượt*. Ba mươi tool với schema phong phú có thể ngốn 3–5k token trước khi cuộc hội thoại thậm chí bắt đầu.

---

## Lỗi

Trả MCP tool error, không phải exception làm crash transport. Bao gồm đủ chi tiết để Claude có thể recover hoặc retry theo cách khác.

```typescript
if (!item) {
  return {
    isError: true,
    content: [{
      type: "text",
      text: `Item ${id} not found. Use search_items to find valid IDs.`,
    }],
  };
}
```

Gợi ý ("use search_items…") biến ngõ cụt thành bước tiếp theo.

---

## Tool annotation

Gợi ý host dùng cho UX — nút confirm màu đỏ cho destructive, tự động approve cho readonly. Tất cả mặc định là chưa set (host giả định trường hợp xấu nhất).

| Annotation | Ý nghĩa | Hành vi của host |
|---|---|---|
| `readOnlyHint: true` | Không có side effect | Có thể tự động approve |
| `destructiveHint: true` | Xóa/ghi đè | Hộp thoại xác nhận |
| `idempotentHint: true` | An toàn để retry | Có thể retry khi lỗi tạm thời |
| `openWorldHint: true` | Giao tiếp với thế giới ngoài (web, API) | Có thể hiển thị network indicator |

```typescript
server.registerTool("delete_file", {
  description: "Delete a file",
  inputSchema: { path: z.string() },
  annotations: { destructiveHint: true, idempotentHint: false },
}, handler);
```

```python
@mcp.tool(annotations={"destructiveHint": True, "idempotentHint": False})
def delete_file(path: str) -> str:
    ...
```

Kết hợp với hướng dẫn tách read/write trong `build-mcpb/references/local-security.md` — đánh dấu mọi read tool là `readOnlyHint: true`.

---

## Structured output

`JSON.stringify(result)` trong một text block hoạt động được, nhưng spec có typed output first-class: `outputSchema` + `structuredContent`. Client có thể validate.

```typescript
server.registerTool("get_weather", {
  description: "Get current weather",
  inputSchema: { city: z.string() },
  outputSchema: { temp: z.number(), conditions: z.string() },
}, async ({ city }) => {
  const data = await fetchWeather(city);
  return {
    content: [{ type: "text", text: JSON.stringify(data) }],  // backward compat
    structuredContent: data,                                    // typed output
  };
});
```

Luôn bao gồm text fallback — không phải tất cả host đều đọc `structuredContent` ở thời điểm hiện tại.

---

## Các content type ngoài text

Tool có thể trả về nhiều hơn string:

| Type | Shape | Dùng cho |
|---|---|---|
| `text` | `{ type: "text", text: string }` | Mặc định |
| `image` | `{ type: "image", data: base64, mimeType }` | Screenshot, chart, diagram |
| `audio` | `{ type: "audio", data: base64, mimeType }` | TTS output, recording |
| `resource_link` | `{ type: "resource_link", uri, name?, description? }` | Con trỏ — client fetch sau |
| `resource` (embedded) | `{ type: "resource", resource: { uri, text\|blob, mimeType } }` | Inline toàn bộ nội dung |

**`resource_link` vs embedded:** dùng link cho payload lớn hoặc khi client có thể không cần (để họ quyết định). Embed khi nội dung nhỏ và luôn cần.
