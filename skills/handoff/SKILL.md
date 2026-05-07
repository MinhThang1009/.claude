---
name: handoff
description: Tạo handoff brief để compact session hiện tại HOẶC chuyển sang session mới. Gọi khi user nói "handoff", "chuyển session", "compact với note", "ghi lại trước khi clear", hoặc context >70%.
allowed-tools: Read, Write, Bash(git status:*), Bash(git log:*), Bash(git diff:*)
disable-model-invocation: false
user-invocable: true
argument-hint: "[--save | --inject]"
model: inherit
---

# Skill: Handoff giữa các session

Theo nghiên cứu của Anthropic (`claude.com/blog/using-claude-code-session-management-and-1m-context`) và kinh nghiệm cộng đồng: **resume một session dài thường tệ hơn brief-injection vào session mới** — vì resume kéo theo stale environment data (tool output cũ, file content cũ) còn brief chỉ mang quyết định và trạng thái hiện tại.

## Khi nào dùng skill này

| Tình huống | Cách dùng |
|---|---|
| Sắp `/compact` (context >60%) — vẫn làm tiếp cùng task | `/handoff` rồi `/compact <chỉ dẫn>` |
| Sắp `/clear` — chuyển sang task mới nhưng cần nhớ vài thứ | `/handoff --save` rồi `/clear` |
| Bắt đầu session mới sau khi nghỉ | Mở session mới, paste handoff vào prompt đầu tiên |
| Sau crash / session lỗi | `claude --continue` → `/handoff` để xem state |

## Quy trình

### Bước 1 — Kiểm tra context hiện tại

```bash
# Người dùng tự xem qua /context. Tôi (Claude) tự đọc git để biết state code:
!`git status --short`
!`git log --oneline -5`
!`git diff --stat HEAD`
```

### Bước 2 — Soạn handoff brief

Tôi viết brief **NGẮN** (5-10 dòng, ≤300 từ) theo format dưới đây. Brief phải tự đọc được mà không cần history.

```markdown
# Handoff — <task name> — <YYYY-MM-DD HH:MM>

## Mục tiêu phiên hiện tại
<1 câu — đang giải quyết vấn đề gì>

## Đã xong
- <bullet ngắn — gì đã làm được, kèm path file nếu có>
- ...

## Đang dở
- <việc đang dở dang, dừng ở bước nào>
- File đang sửa: `path/to/file.ts:120` — <ghi chú>

## Quyết định đã chốt (kèm lý do 1 câu)
- <Quyết định 1>: <lý do>
- <Quyết định 2>: <lý do>

## Constraint / điều cần nhớ
- <perf, compat, security, business rule>

## Việc tránh / đã thử nhưng không work
- <approach X — bị reject vì lý do Y>

## Bước tiếp theo
1. <hành động cụ thể>
2. <hành động cụ thể>

## Lệnh hữu ích cho project này
- Build: `<command>`
- Test: `<command>`
- Lint: `<command>`
```

### Bước 3 — Lưu hoặc inject

**Nếu user chạy `/handoff` không kèm flag** → in brief ra chat. User sẽ:
- Copy thủ công vào session mới, HOẶC
- Tôi tiếp tục với `/compact <brief>` để giữ continuity.

**Nếu user chạy `/handoff --save`** → ghi brief vào `<project>/.claude/HANDOFF.md` (đã được gitignore qua `.claude/settings.local.json`).
- Session mới sẽ tự đọc khi user nói "đọc HANDOFF.md".

**Nếu user chạy `/handoff --inject`** → in 1 dòng paste-ready để user paste vào session mới:
```
Tiếp tục từ handoff: [brief inline 5-7 dòng]. File chính: <list>. Bước tiếp: <action>.
```

## Quy tắc viết brief

- **Quyết định, không quá trình**: ghi "Chốt dùng JWT RS256 vì legal yêu cầu", KHÔNG ghi "Đã thử HS256, sau đó thử RS256, sau đó thảo luận với...".
- **Đường đi đã đóng = bỏ qua** trừ khi quan trọng để session sau biết KHÔNG thử lại.
- **Path tuyệt đối hoặc rel-from-repo-root** cho file. Không "file kia".
- **Lệnh chính xác** — copy paste chạy được, không "chạy lệnh build".
- **Bỏ qua tool output dài** (build log, test result chi tiết). Chỉ giữ kết quả: pass/fail/skip.

## Tích hợp với `/compact`

Sau khi tôi soạn brief, người dùng có thể chạy:
```
/compact Giữ lại brief tôi vừa cho, drop debugging history và tool output cũ.
```
Câu chỉ dẫn này giúp Claude compact có hướng, brief survives cao hơn auto-summary.

## Anti-pattern — KHÔNG làm

- KHÔNG copy-paste lại toàn bộ code đã sửa vào brief. Chỉ ghi path + tóm tắt.
- KHÔNG viết brief dài hơn 1 màn hình terminal. Quá dài → trở thành noise.
- KHÔNG đưa secret/token/key vào brief.
- KHÔNG đoán bước tiếp theo nếu chưa rõ. Ghi "Cần user xác nhận hướng đi".
