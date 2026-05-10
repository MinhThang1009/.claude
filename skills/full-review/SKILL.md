---
name: full-review
description: Multi-agent review dispatch 3 agents song song (code-review + security-audit + test-analysis), validate findings, consolidate report. Dùng khi cần review toàn diện trước deploy, merge PR lớn, hoặc audit codebase.
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git log:*), Bash(git status:*), WebFetch
argument-hint: "[scope: PR #N | branch | files | all]"
---

# Orchestration: Full Review

Skill này dispatch 3 subagents song song, validate findings, rồi consolidate — theo pattern Anthropic code-review command.

## Quy trình

### Bước 1 — Pre-check (Haiku-level, nhanh)

Trước khi dispatch agents, kiểm tra:
- `git status` / `git diff --stat` → có changes không? Nếu clean → báo user, dừng.
- Scope: `$ARGUMENTS` xác định review gì (PR, branch, files, hoặc all unstaged).
- Nếu scope mơ hồ → hỏi user, KHÔNG đoán.

### Bước 2 — Dispatch 3 agents song song

Launch **3 subagents đồng thời**:

**Agent 1: code-reviewer** (Sonnet)
- Prompt: "Review code changes trong [scope]. Tìm bugs, logic errors, performance, maintainability. Rate mỗi issue confidence 0-100. Chỉ report confidence ≥ 80."
- Tools: Read, Grep, Glob, Bash

**Agent 2: security-auditor** (Opus)
- Prompt: "Security audit code changes trong [scope]. Tìm injection, auth flaws, secrets, insecure crypto, SSRF, XSS. Report theo CVSS severity."
- Tools: Read, Grep, Glob, Bash, WebFetch

**Agent 3: test-analysis** (Sonnet)
- Prompt: "Phân tích test coverage cho code changes trong [scope]. Kiểm tra: có test cho logic mới không? Edge cases đã cover? Có test bị break không? Chạy test suite nếu có."
- Tools: Read, Grep, Glob, Bash

### Bước 3 — Consolidate (đếm trước, không drop ngầm)

Sau khi 3 agents trả kết quả:

1. **Đếm findings mỗi agent** (tự đếm, không tin self-count).
2. **Deduplicate**: nếu 2+ agents báo cùng issue → giữ 1, lấy severity cao hơn, ghi "confirmed by N agents".
3. **KHÔNG drop finding ngầm** — mọi finding phải xuất hiện trong report hoặc ghi rõ lý do drop.

### Bước 4 — Validate findings (2-pass review)

Với mỗi finding **Critical/High**:
- Launch **1 fresh subagent** (không nhận context về intent) verify finding đó.
- Subagent chỉ nhận: file path + line number + issue description + instruction "verify xem issue này có thật không".
- Finding không validate → đánh dấu "unverified", vẫn giữ trong report nhưng ghi rõ.

### Bước 5 — Output

```markdown
# Full Review Report

**Scope**: [mô tả scope]
**Agents**: code-reviewer (N findings) + security-auditor (N findings) + test-analysis (N findings)
**Tổng raw**: X findings → Y sau dedup → Z validated

## 🔴 Critical / High (validated)
[findings]

## 🟡 Medium
[findings]

## 🟢 Low / Info
[findings]

## ⚠️ Unverified (cần user confirm)
[findings chưa validate]

## ✅ Điểm tốt
[những thứ làm đúng]

## Test Coverage
[phân tích từ agent 3]
```

### Bước 6 — Hỏi user

Sau report, hỏi:
- "Fix Critical/High ngay?" → nếu OK, lập plan và sửa
- "Commit as-is?" → nếu OK, gọi `/commit`
- "Cần review thêm?" → dispatch thêm agents nếu cần

## KHÔNG làm

- KHÔNG tự fix mà không hỏi user
- KHÔNG drop findings vì "false positive" mà chưa validate
- KHÔNG merge Critical/High với Low — giữ riêng
- KHÔNG chạy nếu scope không rõ ràng
