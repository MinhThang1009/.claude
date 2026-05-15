# Hướng dẫn cá nhân (Global)

> Load vào MỌI session. Giữ ngắn — nếu xóa 1 dòng mà Claude vẫn làm đúng → dòng đó nên xóa.

> 📝 **Quy ước first-person template**: File này là user-config được Claude Code load vào MỌI session. Đại từ "tôi" trong nội dung dưới đây = **USER** (người copy file này vào `~/.claude/CLAUDE.md`), "bạn" = **Claude**. First-person voice là intentional theo Claude Code prompt convention — giúp Claude hiểu instructions như nói với chính mình. Khi đọc repo lần đầu (chưa copy), tự thay "tôi" = bản thân để hiểu đúng intent.

## Ngôn ngữ

- Mặc định **tiếng Việt**, thuật ngữ kỹ thuật giữ tiếng Anh. Chi tiết tại [`communication.md` §Tiếng Việt vs Anh](rules/communication.md).

## Phong cách làm việc

- Sắp sửa **>3 file có thay đổi logic** hoặc đụng **kiến trúc** (thêm module, đổi DB schema, refactor public API, đổi pattern xuyên codebase) → **lập plan, đợi tôi duyệt**. Plan mỗi bước có dạng: `[Step] → verify: [check]`. Batch trivial (format, rename, version bump) thì làm luôn dù nhiều file. Fix nhỏ (typo, đổi tên biến, thêm log, sửa 1-2 file isolated) cũng làm luôn.
- Không chắc intent → **HỎI**, đừng đoán. Một câu hỏi tốt hơn 10 phút sửa sai.
- Sau khi sửa → **TỰ KIỂM TRA** test/lint/typecheck nếu có. Đừng báo "xong" khi chưa verify.
- Tôi nói "ultrathink" → keyword chính thức, Claude Code thêm in-context instruction request deeper reasoning cho turn đó (effort level KHÔNG đổi). Các cụm "think"/"think hard"/"think more" KHÔNG phải keyword — đối xử như plain text.
- Subagent results, git state, external deps → xem chi tiết [`verification.md`](rules/verification.md).

## Phong cách trả lời

- **Ngắn gọn**. Diff/code TRƯỚC, giải thích SAU. Chi tiết tại [`communication.md`](rules/communication.md).

## Code

- Chi tiết tại [`coding-standards.md`](rules/coding-standards.md). Tóm tắt: đọc trước khi viết, theo convention codebase, YAGNI, surgical changes, không thêm dependency mà không hỏi.

## Git

- KHÔNG `git commit`/`git push` trừ khi tôi yêu cầu rõ — phải có động từ explicit: `commit`, `push`, `ship`, `merge`, hoặc gọi [`/commit`](plugins/commit-commands/skills/commit/SKILL.md). Câu mơ hồ như "save it", "looks good", "done" → KHÔNG đủ, hỏi lại.
- Chi tiết (add, force, reset, attribution, branch) tại [`git-workflow.md`](rules/git-workflow.md).

## Bảo mật

- Chi tiết tại [`security.md`](rules/security.md).

## Workflow ưu tiên

- Khi cần plan (theo rule ["Phong cách làm việc"](#phong-cách-làm-việc) ở trên) → ưu tiên đề xuất Plan Mode (`Shift+Tab×2 từ default mode`) hoặc `/plan` thay vì viết plan inline trong response.
- Investigate codebase rộng → đề xuất subagent ("use a subagent to investigate ...") để giữ context chính sạch. Nếu không dùng subagent → scope narrow (chỉ đọc file/dir cần thiết, không explore toàn bộ).
- Refactor lớn → tách commit nhỏ revert được độc lập.
- Bug khó → reproduce trước, viết failing test, mới fix (chi tiết tại coding-standards.md §Test, §Verification khi refactor).

## Khi gặp lỗi

- Đọc kỹ error message TRƯỚC khi đoán.
- Sửa 2 lần vẫn sai → DỪNG, đề xuất `/clear` + reprompt với context đã học. Đừng spam correction vào context bẩn.

## Quản lý context window

- Theo dõi `/context` thường xuyên. **<40% sweet spot**, **40-60% dumb zone bắt đầu**, **60-77% wrap up actively**, **>77% sau auto-compact PHẢI act**. Ngưỡng community-curated, chi tiết + source tại [`docs/REFERENCE.md` §16.2](docs/REFERENCE.md).
- Hoàn thành 1 phase (auth xong, refactor xong) → đề xuất `/compact` ngay, đừng đợi auto-compact firing (~77% của 200k window = ~155k tokens, theo [Boris Cherny — Anthropic, Claude Code lead](https://x.com/bcherny/status/1977163445205450783); docs mới ghi default ~95% — có thể đã thay đổi qua versions).
- Trước khi compact/clear → tôi sẽ yêu cầu bạn viết handoff brief; bạn dùng skill [`/handoff`](plugins/session/skills/handoff/SKILL.md).
- Câu hỏi nhanh không cần lưu history → tôi dùng `/btw`.

## Compact Instructions

Khi `/compact` chạy (manual hoặc auto), summary PHẢI giữ lại:

1. **Files đã sửa** (full path) và **lý do sửa** từng file.
2. **Quyết định kiến trúc** đã chốt (kèm rationale 1 câu).
3. **Lệnh build/test/lint** đã xác định work với project này.
4. **Constraint** (performance, compatibility, security) đã được thiết lập.
5. **Việc đang dở dang** + **bước tiếp theo** rõ ràng.
6. Bỏ: tool output dài, dead-end debugging, các đoạn rephrase qua lại.

## Tham chiếu rule mở rộng

> Tất cả file trong `~/.claude/rules/` (coding-standards.md, communication.md, git-workflow.md, security.md, verification.md) auto-load mọi session — không cần `@import`.
