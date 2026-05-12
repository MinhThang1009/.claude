# Checklist nộp connector directory

Kiểm tra trước khi nộp một remote MCP app lên connector directory của Claude. Mỗi mục là một tiêu chí review bắt buộc.

| Hạng mục | Yêu cầu |
|---|---|
| **Auth** | OAuth (DCR hoặc CIMD) hoặc **`none`** (không xác thực). Static bearer token chỉ dành cho private-deploy và sẽ bị chặn listing. Authless hợp lệ cho server dữ liệu công khai — server giữ mọi API key upstream. |
| **Tool annotations** | Mọi tool phải đặt `annotations.title` cộng với các hint liên quan: `readOnlyHint: true` cho tool fetch/search, `destructiveHint` / `idempotentHint` cho write, `openWorldHint: true` nếu tool tiếp cận hệ thống bên ngoài. |
| **Tên tool** | ≤ 64 ký tự, snake/kebab case. |
| **Layout widget** | Chiều cao inline ≤ 500px, không có nested scroll container, target cảm ứng tối thiểu 44pt, độ tương phản WCAG-AA trong cả hai theme. |
| **Theming** | `html, body { background: transparent }`, `<meta name="color-scheme" content="light dark">`, áp dụng CSS token của host qua `applyHostStyleVariables`. |
| **External link** | Dùng `app.openLink`. Khai báo từng origin (ví dụ: `https://api.example.com`) trong *Allowed link URIs* của connector để link bỏ qua modal xác nhận. |
| **Helper tool** | Tool chỉ dùng cho widget (geometry/image fetcher) mang `_meta.ui.visibility: ["app"]` để không xuất hiện trong danh sách tool của Claude. |
| **Screenshot** | 3–5 file PNG, rộng ≥ 1000px, crop vào phần response của app thôi — không có prompt text trong khung hình. |

Xem `abuse-protection.md` để biết hướng dẫn rate-limit và IP-tiering sau khi endpoint authless được công khai.
