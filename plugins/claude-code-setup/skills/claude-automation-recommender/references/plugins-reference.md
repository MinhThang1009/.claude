# Gợi Ý Plugin

Plugin là các bộ sưu tập có thể cài đặt, bao gồm skill, command, agent và hook. Cài đặt qua `/plugin install`.

**Lưu ý**: Đây là các plugin từ repository chính thức. Dùng web search để khám phá thêm plugin từ cộng đồng.

---

## Plugin Chính Thức

### Phát Triển & Chất Lượng Code

| Plugin | Phù hợp nhất cho | Tính năng chính |
|--------|----------|--------------|
| **plugin-dev** | Xây dựng plugin Claude Code | Skill để tạo skill, hook, command, agent |
| **pr-review-toolkit** | Workflow review PR | Các agent review chuyên biệt (code, test, kiểu) |
| **code-review** | Review code tự động | Multi-agent review với điểm độ tin cậy |
| **code-simplifier** | Refactoring code | Đơn giản hóa code trong khi giữ nguyên chức năng |
| **feature-dev** | Phát triển tính năng | Workflow tính năng end-to-end với agent |

### Git & Workflow

| Plugin | Phù hợp nhất cho | Tính năng chính |
|--------|----------|--------------|
| **commit-commands** | Workflow Git | Các command /commit, /commit-push-pr |
| **hookify** | Quy tắc tự động hóa | Tạo hook từ pattern hội thoại |

### Frontend

| Plugin | Phù hợp nhất cho | Tính năng chính |
|--------|----------|--------------|
| **frontend-design** | Phát triển UI | UI chất lượng production, tránh thiết kế chung chung |

### Học Tập & Hướng Dẫn

| Plugin | Phù hợp nhất cho | Tính năng chính |
|--------|----------|--------------|
| **explanatory-output-style** | Học tập | Giải thích có tính giáo dục về các lựa chọn code |
| **learning-output-style** | Học tương tác | Yêu cầu đóng góp tại các điểm quyết định |
| **security-guidance** | Nhận thức bảo mật | Cảnh báo về vấn đề bảo mật khi chỉnh sửa |

### Language Server (LSP)

| Plugin | Ngôn ngữ |
|--------|----------|
| **typescript-lsp** | TypeScript/JavaScript |
| **pyright-lsp** | Python |
| **gopls-lsp** | Go |
| **rust-analyzer-lsp** | Rust |
| **clangd-lsp** | C/C++ |
| **jdtls-lsp** | Java |
| **kotlin-lsp** | Kotlin |
| **swift-lsp** | Swift |
| **csharp-lsp** | C# |
| **php-lsp** | PHP |
| **lua-lsp** | Lua |

---

## Tham Khảo Nhanh: Codebase → Plugin

| Dấu hiệu Codebase | Plugin Khuyến Nghị |
|-----------------|-------------------|
| Đang xây dựng plugin | plugin-dev |
| Workflow theo PR | pr-review-toolkit |
| Commit git | commit-commands |
| React/Vue/Angular | frontend-design |
| Muốn quy tắc tự động hóa | hookify |
| Project TypeScript | typescript-lsp |
| Project Python | pyright-lsp |
| Project Go | gopls-lsp |
| Code nhạy cảm về bảo mật | security-guidance |
| Học tập/onboarding | explanatory-output-style |

---

## Quản Lý Plugin

```bash
# Cài đặt plugin
/plugin install <plugin-name>

# Liệt kê plugin đã cài
/plugin list

# Xem chi tiết plugin
/plugin info <plugin-name>
```

---

## Khi Nào Nên Khuyến Nghị Plugin

**Khuyến nghị cài đặt plugin khi:**
- Người dùng muốn cài automation cho Claude Code từ repository chính thức của Anthropic hoặc marketplace chia sẻ khác
- Người dùng cần nhiều tính năng liên quan với nhau
- Team muốn workflow chuẩn hóa
- Lần đầu cài đặt Claude Code
