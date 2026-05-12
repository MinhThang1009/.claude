---
name: full-review
description: "Multi-agent review — adaptively dispatches 1-3 agents (code-review + security-audit + test-analyzer) based on complexity, validates findings, consolidates report. Use for comprehensive review before deploy or merging large PRs."
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
   - Scope all: `git ls-files | wc -l` (đếm tracked files, tự respect `.gitignore`) + `git ls-files | xargs wc -l` → đếm LOC codebase. Nếu không có git → `find . -type f | wc -l` (adjust exclude theo project)
   - Scope PR: `gh pr diff <N> --stat` (GitHub). Nếu không có `gh` CLI hoặc dùng platform khác (GitLab, Bitbucket) → hỏi user cung cấp diff
3. Collect file list: `git diff --name-only` hoặc `find` → liệt kê file names
4. Nếu clean (0 changes cho diff scope) → báo user, dừng
5. Nếu scope mơ hồ → hỏi user, KHÔNG đoán

**Dispatch pre-check subagent** (`model: haiku` trong Agent tool call) với data đã collect (inject diff stats + file list vào prompt):
- Subagent nhận **số liệu thực** (không cần tự count) + file names (thấy sensitive areas)
- Check: PR closed/draft? Trivial change (≤5 dòng, chỉ format/typo)? → "skip"
- **Chọn scale tier** dựa trên data thực (xem Bước 2)

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

**Agent 1: code-reviewer** (model + tools theo agent definition)
- Prompt: "Review code changes trong [scope]. Tìm bugs, logic errors, performance, maintainability. Rate mỗi issue confidence 0-100. Chỉ report confidence ≥ 80."

**Agent 2: security-auditor** (model + tools theo agent definition)
- Prompt: "Security audit code changes trong [scope]. Tìm injection, auth flaws, secrets, insecure crypto, SSRF, XSS. Report theo CVSS severity."

**Agent 3: test-analyzer** (model + tools theo agent definition)
- Prompt: "Phân tích test coverage cho code changes trong [scope]. Kiểm tra: có test cho logic mới không? Edge cases đã cover? Có test bị break không? Chạy test suite nếu có."

### Bước 3 — Consolidate (adaptive theo số agents)

**Nếu chỉ 1 agent** (Simple tier): skip dedup + validate — output trực tiếp findings của agent đó. Không cần consolidate 1 source.

**Nếu 2+ agents**:
1. **Đếm findings mỗi agent** (tự đếm, không tin self-count).
2. **Deduplicate**: nếu 2+ agents báo cùng issue → giữ 1, lấy severity cao hơn, ghi "confirmed by N agents".
3. **KHÔNG drop finding ngầm** — mọi finding phải xuất hiện trong report hoặc ghi rõ lý do drop.

### Bước 4 — Validate findings (adaptive)

**Nếu 0 findings Critical/High**: skip validation — không có gì cần validate.

**Nếu có Critical/High**:
- Launch **1 fresh subagent** (không nhận context về intent) verify mỗi finding.
- Subagent chỉ nhận: file path + line number + issue description + instruction "verify xem issue này có thật không".
- Finding không validate → đánh dấu "unverified", vẫn giữ trong report nhưng ghi rõ.

### Bước 5 — Output (scale theo complexity)

**Simple** (1 agent, ít findings): output ngắn gọn — list findings + 1-2 câu summary. Không cần headers phức tạp.

**Moderate/Complex** (2-3 agents): output đầy đủ:

```markdown
# Full Review Report

**Scope**: [mô tả scope]
**Agents**: [agents đã dispatch] (N findings mỗi agent)
**Tổng raw**: X findings → Y sau dedup → Z validated

## 🔴 Critical / High (validated)
[findings]

## 🟡 Medium
[findings]

## 🟢 Low / Info
[findings]

## ⚠️ Unverified (cần user confirm)
[findings chưa validate — bỏ section nếu không có]

## ✅ Điểm tốt
[những thứ làm đúng]

## Test Coverage
[phân tích từ test-analyzer — bỏ section nếu không dispatch test-analyzer]
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
