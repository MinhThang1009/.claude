---
name: full-review
description: Multi-agent review dispatch 3 agents song song (code-review + security-audit + test-analyzer), validate findings, consolidate report. Dùng khi cần review toàn diện trước deploy, merge PR lớn, hoặc audit codebase.
allowed-tools: Read Grep Glob Bash(git diff:*) Bash(git log:*) Bash(git status:*) WebFetch
argument-hint: "[scope: PR #N | branch | files | all]"
---

# Orchestration: Full Review

Skill này dispatch 3 subagents song song, validate findings, rồi consolidate — theo pattern Anthropic code-review command.

## Quy trình

### Bước 1 — Pre-check (dispatch Haiku agent, tiết kiệm tokens)

Launch **1 Haiku agent** kiểm tra nhanh:
- `git status` / `git diff --stat` → có changes không? Nếu clean → báo user, dừng.
- Scope: `$ARGUMENTS` xác định review gì (PR, branch, files, hoặc all unstaged).
- Nếu scope = PR: check PR closed? draft? Claude đã comment chưa? (`gh pr view <N> --json state,isDraft --comments`)
- Diff quá nhỏ (≤5 dòng, chỉ format/typo) → báo user "trivial change, skip full review?" thay vì dispatch 3 agents.
- Nếu scope mơ hồ → hỏi user, KHÔNG đoán.

Nếu Haiku agent trả về "skip" → **dừng ngay**, không dispatch Bước 2.

### Bước 2 — Dispatch agents (adaptive scaling)

**Scale số agents theo complexity** (theo [Anthropic multi-agent research pattern](https://www.anthropic.com/engineering/multi-agent-research-system): "Simple fact-finding requires just 1 agent... complex research might use more than 10 subagents"):

Haiku pre-check (Bước 1) đánh giá complexity và chọn scale. Guidelines (qualitative labels + quantitative bounds, criteria tự thiết kế cho code review):

| Tier | Label | Bounds (guidelines, không hard cutoff) | Agents |
|------|-------|---------------------------------------|--------|
| 1 | **Simple** | ~1-20 dòng, 1-2 files, không đụng auth/payment/crypto | **1** (code-reviewer only) |
| 2 | **Moderate** | ~20-200 dòng, 3-10 files, hoặc có security concern | **2** (code-reviewer + security-auditor) |
| 3 | **Complex** | >200 dòng, >10 files, sensitive areas, hoặc architectural change | **3** (full) |

Haiku dùng bảng trên làm **guideline**, có thể adjust nếu context cho thấy complexity khác bounds (vd: 15 dòng nhưng đụng auth → Moderate, không phải Simple).

"all" scope chỉ define phạm vi review, KHÔNG override scaling — Haiku vẫn judge complexity dựa trên nội dung thực tế.

Launch subagents theo scale đã chọn:

**Agent 1: code-reviewer** (Sonnet)
- Prompt: "Review code changes trong [scope]. Tìm bugs, logic errors, performance, maintainability. Rate mỗi issue confidence 0-100. Chỉ report confidence ≥ 80."
- Tools: Read, Grep, Glob, Bash

**Agent 2: security-auditor** (Opus)
- Prompt: "Security audit code changes trong [scope]. Tìm injection, auth flaws, secrets, insecure crypto, SSRF, XSS. Report theo CVSS severity."
- Tools: Read, Grep, Glob, Bash, WebFetch

**Agent 3: test-analyzer** (Sonnet)
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
**Agents**: code-reviewer (N findings) + security-auditor (N findings) + test-analyzer (N findings)
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
