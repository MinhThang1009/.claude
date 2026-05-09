# <TÊN PROJECT> — Note cá nhân

> **GITIGNORE**. Note cá nhân về project (per-user), không chia sẻ trong team. Cộng dồn với `<project>/CLAUDE.md` (team) và `~/.claude/CLAUDE.md` (global).
>
> 📝 **Quy ước first-person**: Đây là personal note template — đại từ "tôi" trong placeholder examples = USER (người sở hữu file). Khi copy template vào project, tự thay placeholder `<vd: ...>` bằng nội dung thực tế.

## Môi trường local

- Node version đang dùng: <vd: 20.11>
- Database local: <vd: PostgreSQL chạy trong Docker port 5433>
- Branch đang làm: <vd: feat/google-oauth>
- Issue tracker reference: <vd: tôi quản lý task qua linear @yourname>

## Pattern Claude lưu ý cho user này

- <vd: Tôi prefer dùng `vitest` thay `jest`. Nếu thấy file test cũ dùng jest → đề xuất migrate dần>
- <vd: Khi sửa Tailwind, tôi muốn class theo thứ tự: layout → spacing → typography → color → state>
- <vd: Tôi không quen Redux. Nếu cần state management, đề xuất Zustand trước>

## Thử nghiệm cá nhân (không ảnh hưởng team)

- <vd: Đang test branch `experiment/edge-runtime` để xem có nên migrate sang edge function>

## Liên hệ

- <vd: PM của project này: @ten-pm — hỏi PM về business logic>
- <vd: Lead BE: @ten-lead — hỏi lead về DB schema>

## Snippet thường dùng

```bash
# Reset DB local
<command>

# Restart Docker
<command>

# Tạo seed data
<command>
```
