---
name: context-check
description: Kiểm tra mức tiêu thụ context window và đề xuất hành động (compact/clear/subagent/handoff). Gọi khi user nói "context bao nhiêu rồi", "có cần compact không", "kiểm tra token", hoặc tự động khi thấy phản hồi của Claude xuống chất lượng.
allowed-tools: Read
model: inherit
---

# Skill: Kiểm tra context window

Mục đích: chủ động đánh giá context và đề xuất hành động đúng, **trước khi quality degrade**.

## Quy trình

### Bước 1 — Đọc trạng thái

Claude **không thể tự chạy `/context`** vì đó là [slash command chỉ user invoke](https://code.claude.com/docs/en/skills). Đề nghị user:

> Cần chạy `/context` ở terminal và gửi lại output (% và breakdown).

Sau khi user gửi output `/context`, phân tích theo các bước dưới.

### Bước 2 — Phân tích theo ngưỡng

> Source ngưỡng % (multi-author, verified):
> - `<30/<40/60%` + "dumb zone": [Dex Horthy at MLOps Community](https://youtu.be/YwZR6tc7qYg?t=1541) (2026-03-24)
> - `300-400k tokens` context rot (1M model): Thariq Shihipar (Anthropic Claude Code team) via [howborisusesclaudecode.com](https://howborisusesclaudecode.com/)
> - `155k tokens` auto-compact (200k window): [Boris Cherny X tweet](https://x.com/bcherny/status/1977163445205450783)
> - Trích dẫn đầy đủ + nuance theo task complexity: [docs/REFERENCE.md §16](../../docs/REFERENCE.md#16-quản-lý-context-window--chi-tiết). Anthropic không publish % chính thức.

| % context | Trạng thái                          | Hành động đề xuất                                                        |
| --------- | ----------------------------------- | ------------------------------------------------------------------------ |
| `<30%`    | 🟢 Aggressive zone                  | Mục tiêu experienced users                                                |
| `30-40%`  | 🟢 Sweet spot                       | Newcomer target — "shoot to keep it under 40%" (Dex)                   |
| `40-60%`  | 🟡 "Dumb zone" bắt đầu              | Performance degrade — plan wrap-up phase hiện tại                        |
| `60-77%`  | 🟠 Wrap up actively                 | `/compact` HOẶC `/handoff` → `/clear` + brief mới                        |
| `~77%`    | 🔴 Auto-compact firing (155k tokens)| Đã muộn — ưu tiên `/handoff --save` trước khi mất chi tiết               |
| `>90%`    | ⛔ Hard limit                        | DỪNG task lớn ngay, brief + new session                                   |

### Bước 3 — Phân tích từng nhóm

`/context` chia output theo nhóm (system, memory/CLAUDE.md, skills, MCP tools, conversation, file content). Tìm nhóm tiêu thụ cao bất thường:

| Nhóm tiêu thụ cao               | Nguyên nhân                         | Cách giảm                                                 |
| ------------------------------- | ----------------------------------- | --------------------------------------------------------- |
| Memory (CLAUDE.md + rules) >10% | CLAUDE.md / rules quá dài           | Prune lại, tách phần ít dùng vào REFERENCE.md             |
| MCP tools >15%                  | Bật quá nhiều MCP server không dùng | `claude mcp` list rồi disable cái không cần cho phiên này |
| Skill descriptions >5%          | Quá nhiều skill auto-discover       | Set `disable-model-invocation: true` cho skill ít dùng    |
| Conversation history >40%       | Nhiều tool output / dead-end        | `/compact` ngay                                           |
| File content >25%               | Đã `@` quá nhiều file lớn           | `/clear` + chỉ ref file cần thiết                         |

### Bước 4 — Đề xuất hành động

Đưa ra **1 đề xuất chính** kèm lý do, KHÔNG list 5 option để user chọn:

Ví dụ output:
> Context đang ở 73%. Conversation history chiếm 45% — chủ yếu do tool output dài từ phiên debug trước. **Đề xuất**: chạy `/handoff` để tóm tắt 5 dòng key decision, rồi `/compact giữ lại brief, drop debug log`. Sau đó tiếp tục task hiện tại trong session này. Estimate context sau compact: ~25%.

## Lựa chọn `/compact` vs `/clear`

| Tình huống dùng `/compact`                     | Tình huống dùng `/clear`                |
| ---------------------------------------------- | --------------------------------------- |
| Đang giữa 1 task, cần giữ thread               | Hoàn thành 1 task, chuyển task khác hẳn |
| Quyết định và file path quan trọng cần survive | Không cần lịch sử                       |
| Context 40-60% ("dumb zone")                   | Context >77% (auto-compact zone) hoặc đã rối |
| Nhiều dead-end debugging cần dọn               | Đã commit xong, sang feature mới        |

**Nguyên tắc vàng**: `/compact` = nén, `/clear` = xóa hẳn. Nhầm `/clear` với `/compact` = mất context phải re-explain. Nhầm `/compact` với `/clear` = giữ rác cho task mới.

## Khi context corrupt / Claude lú

Triệu chứng:
- Claude nhắc đi nhắc lại file/quyết định cũ.
- Claude quên rule trong CLAUDE.md (ví dụ vẫn dùng tiếng Anh comment dù đã set tiếng Việt).
- Sửa 2 lần vẫn không đúng.
- Lỗi `Internal server error` / `ECONNRESET` / "Chat has reached its limit".

→ KHÔNG `/compact` (compact context bẩn = bẩn tiếp). Phải:
1. `/handoff --save` (hoặc copy paste brief ra ngoài).
2. `/clear` hoặc thoát mở session mới.
3. Inject brief vào prompt đầu tiên.

## Tip dài hạn

- Đặt status line custom hiển thị % context: [code.claude.com/docs/en/statusline](https://code.claude.com/docs/en/statusline).
- Audit `~/.claude/CLAUDE.md` định kỳ (mỗi tháng): xóa dòng không còn cần.
- Project lớn: dùng subagent (`use a subagent to investigate ...`) để giữ main context sạch.
- Tool output lớn (build log, JSON dump >5KB): redirect vào file thay vì dump vào chat: `npm test > /tmp/test.log 2>&1 && tail -50 /tmp/test.log`.
