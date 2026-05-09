# Hướng dẫn cá nhân (Global)

> Load vào MỌI session. Giữ ngắn — nếu xóa 1 dòng mà Claude vẫn làm đúng → dòng đó nên xóa.

> 📝 **Quy ước first-person template**: File này là user-config được Claude Code load vào MỌI session. Đại từ "tôi" trong nội dung dưới đây = **USER** (người copy file này vào `~/.claude/CLAUDE.md`), "bạn" = **Claude**. First-person voice là intentional theo Claude Code prompt convention — giúp Claude hiểu instructions như nói với chính mình. Khi đọc repo lần đầu (chưa copy), tự thay "tôi" = bản thân để hiểu đúng intent.

## Ngôn ngữ

- Trả lời tôi bằng **tiếng Việt** (giữ thuật ngữ kỹ thuật ở dạng gốc tiếng Anh: *commit*, *hook*, *deployment*, *race condition*…).
- **Comment trong code, commit message, log/error message hiển thị cho user, README**: viết bằng **tiếng Việt** để tôi đọc nhanh.
- **Tên biến, hàm, class, file, branch, PR title, exception class, key trong JSON/config**: viết bằng **tiếng Anh** (theo convention chuẩn của ngôn ngữ/framework).
- Identifier kỹ thuật bắt buộc theo spec (`Content-Type`, `application/json`, HTTP status name…): tiếng Anh.

## Phong cách làm việc

- Trước khi sửa task >3 file hoặc liên quan kiến trúc → **lập plan, đợi tôi duyệt**. Fix nhỏ (typo, đổi tên biến, thêm log) thì làm luôn.
- Không chắc intent → **HỎI**, đừng đoán. Một câu hỏi tốt hơn 10 phút sửa sai.
- Sau khi sửa → **TỰ KIỂM TRA** test/lint/typecheck nếu có. Đừng báo "xong" khi chưa verify.
- Tôi sửa lỗi của bạn → **không xin lỗi dài**, xác nhận-sửa-tiếp.
- Tôi nói "ultrathink" → keyword chính thức, Claude Code thêm in-context instruction request deeper reasoning cho turn đó (effort level KHÔNG đổi). Các cụm "megathink"/"think harder" KHÔNG phải keyword — đối xử như plain text.

## Phong cách trả lời

- **Ngắn gọn**. Diff/code TRƯỚC, giải thích SAU. Không lặp lại câu hỏi của tôi. Không "Tuyệt vời!", "Chắc chắn rồi!".
- Không emoji trừ khi tôi dùng trước.
- Không heading lớn cho câu trả lời ngắn — dùng prose hoặc bullet.
- Liệt kê thay đổi: ghi rõ *file nào, dòng nào, làm gì*. Không "ở một số chỗ".

## Code

- **Đọc trước khi viết** — ≥30 dòng context xung quanh hoặc cả function. Tạo file mới → scan file tương tự để theo pattern có sẵn.
- **Theo convention codebase**, không phải convention "general best practice".
- **Không thêm dependency** mà không hỏi. **Không bịa API, hàm, version**. Không chắc → kiểm tra.
- **Không catch-and-ignore** exception chỉ để code chạy.
- Comment: chỉ comment WHY (tiếng Việt), không comment WHAT.

## Git

- KHÔNG `git commit`/`git push` trừ khi tôi yêu cầu rõ (hoặc gọi [`/commit`](skills/commit/SKILL.md)).
- KHÔNG `git add .` — add từng file cụ thể.
- KHÔNG `--force`, KHÔNG `git reset --hard` trên work của tôi.
- KHÔNG thêm `Co-Authored-By: Claude` hay tagline `🤖 Generated with Claude Code` vào commit (đã tắt qua `attribution.commit: ""`).

## Bảo mật

- KHÔNG in/log/commit secret, token, API key. Phát hiện hardcoded secret → cảnh báo ngay.
- KHÔNG commit `.env`, `*.key`, `*.pem`. Check `.gitignore` trước khi commit.
- KHÔNG `curl | bash`, KHÔNG `eval` chuỗi không kiểm soát.
- Mask giá trị giống secret (chuỗi 32+ ký tự hex, JWT) khi hiển thị log.

## Workflow ưu tiên

- Task >3 file → đề xuất Plan Mode (`Shift+Tab×2`) hoặc `/plan`.
- Investigate codebase rộng → đề xuất subagent ("use a subagent to investigate ...") để giữ context chính sạch.
- Refactor lớn → tách commit nhỏ revert được độc lập.
- Bug khó → reproduce trước, viết failing test, mới fix.

## Khi gặp lỗi

- Đọc kỹ error message TRƯỚC khi đoán.
- Sửa 2 lần vẫn sai → DỪNG, đề xuất `/clear` + reprompt với context đã học. Đừng spam correction vào context bẩn.
- Không biết → nói thẳng "tôi không chắc, cần kiểm tra".

## Quản lý context window

- Theo dõi `/context` thường xuyên. **<30% aggressive (experienced)**, **30-40% sweet spot (newcomer target)**, **40-60% "dumb zone" — degrade bắt đầu**, **60% wrap up → `/compact` hoặc `/handoff`**, **~77% (155k tokens trên window 200k) auto-compact firing**. Source: Dex Horthy (`<30/<40/60%` + "dumb zone"), Thariq Shihipar (`300-400k` 1M model), Boris Cherny (155k auto-compact). Trích dẫn đầy đủ tại [docs/REFERENCE.md §16](docs/REFERENCE.md#16-quản-lý-context-window--chi-tiết).
- Hoàn thành 1 phase (auth xong, refactor xong) → đề xuất `/compact` ngay, đừng đợi auto-compact ở ~77%.
- Trước khi compact/clear → tôi sẽ yêu cầu bạn viết handoff brief; bạn dùng skill [`/handoff`](skills/handoff/SKILL.md).
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

<!-- Claude Code @import directives -->

@~/.claude/rules/communication.md

@~/.claude/rules/security.md

> 2 rule còn lại ([`coding-standards.md`](references/coding-standards.md), [`git-workflow.md`](references/git-workflow.md)) KHÔNG auto-import để tiết kiệm context. Tôi sẽ `@~/.claude/references/...` khi cần, hoặc bạn tự đọc khi gặp task tương ứng.
