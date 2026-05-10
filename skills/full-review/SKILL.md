---
name: full-review
description: Multi-agent review dispatch 3 agents song song (code-review + security-audit + test-analyzer), validate findings, consolidate report. Dùng khi cần review toàn diện trước deploy, merge PR lớn, hoặc audit codebase.
allowed-tools: Read Grep Glob Bash(git diff:*) Bash(git log:*) Bash(git status:*) WebFetch
argument-hint: "[scope: PR #N | branch | files | all]"
---

# Orchestration: Full Review

Skill này dispatch 3 subagents song song, validate findings, rồi consolidate — theo pattern Anthropic code-review command.

## Quy trình

### Bước 1 — Collect data + Pre-check (hybrid: lead collect → Haiku judge)

**Lead agent** chạy trước (deterministic, không cần subagent):
1. Xác định scope từ `$ARGUMENTS` (PR, branch, files, hoặc all)
2. Collect diff stats:
   - Scope diff: `git diff --stat` → đếm dòng thay đổi, số files
   - Scope all: `find . -name "*.py" -o -name "*.ts" ... | xargs wc -l` → đếm LOC codebase
   - Scope PR: `gh pr diff <N> --stat`
3. Collect file list: `git diff --name-only` hoặc `find` → liệt kê file names
4. Nếu clean (0 changes cho diff scope) → báo user, dừng
5. Nếu scope mơ hồ → hỏi user, KHÔNG đoán

**Dispatch Haiku agent** với data đã collect (inject diff stats + file list vào prompt):
- Haiku nhận **số liệu thực** (không cần tự count) + file names (thấy sensitive areas)
- Haiku check: PR closed/draft? Trivial change (≤5 dòng, chỉ format/typo)? → "skip"
- Haiku **chọn scale tier** dựa trên data thực (xem Bước 2)

Nếu Haiku trả về "skip" → **dừng ngay**, không dispatch Bước 2.

### Bước 2 — Dispatch agents (adaptive scaling)

**Scale số agents theo complexity** (theo [Anthropic multi-agent research pattern](https://www.anthropic.com/engineering/multi-agent-research-system): "Simple fact-finding requires just 1 agent... complex research might use more than 10 subagents"):

Haiku chọn scale dựa trên **data thực đã inject** ở Bước 1. Guidelines (qualitative labels + quantitative bounds, criteria tự thiết kế cho code review):

| Tier | Label | Bounds (guidelines, không hard cutoff) | Agents |
|------|-------|---------------------------------------|--------|
| 1 | **Simple** | ~1-20 dòng, 1-2 files, không đụng auth/payment/crypto | **1** (code-reviewer only) |
| 2 | **Moderate** | ~20-200 dòng, 3-10 files, hoặc có security concern | **2** (code-reviewer + security-auditor) |
| 3 | **Complex** | >200 dòng, >10 files, sensitive areas, hoặc architectural change | **3** (full) |

Haiku dùng bảng trên làm **guideline**, có thể adjust nếu context cho thấy complexity khác bounds (vd: 15 dòng nhưng đụng auth → Moderate, không phải Simple).

"all" scope chỉ define phạm vi review, KHÔNG override scaling — Haiku judge dựa trên **data thực** (LOC, file count, file names), không phải scope label.

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
