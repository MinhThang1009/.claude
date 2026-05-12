---
name: code-review
description: Review code thay đổi trong working tree, branch hiện tại, hoặc PR. Tìm bug, vấn đề security, performance, style, test coverage. Dùng khi user nói "review code", "review pr", "kiểm tra code", hoặc gọi /code-review.
allowed-tools: Read Grep Glob Bash(git diff:*) Bash(git log:*) Bash(git status:*) Bash(gh pr view:*) Bash(gh pr diff:*)
context: fork
agent: code-reviewer
argument-hint: "[tùy chọn — số PR hoặc đường dẫn cụ thể]"
---

# Skill: Code Review

Bạn được gọi để review code một cách kỹ lưỡng nhưng có ưu tiên.

## Context tự động inject

```!
git diff HEAD 2>/dev/null || echo "No git diff available"
```

## Bước 1: Xác định scope

Tùy theo `$ARGUMENTS`:

- **Không có argument**: review diff đã inject ở trên (unstaged + staged changes)
- **Số (123)**: review PR #123 (`gh pr diff 123` — yêu cầu GitHub CLI; nếu không có `gh` → hỏi user cung cấp diff)
- **Đường dẫn (`src/foo.ts`)**: review nội dung file đó
- **`branch <name>`**: review thay đổi của branch so với default branch (auto-detect: `git symbolic-ref refs/remotes/origin/HEAD` → fallback `main` → `master`)

Hiển thị scope đã chọn cho user trước khi tiếp tục.

## Bước 2: Đọc context

- Đọc file liên quan trong diff để hiểu đầy đủ context (không chỉ đọc hunk).
- Đọc file test tương ứng (nếu có).
- Kiểm tra commit message và PR description (nếu có) để hiểu intent.
- **Git history**: `git blame` cho các dòng thay đổi — hiểu ai viết, khi nào, commit nào. Nếu có `gh` → check PR comments/reviews cũ trên file đó (`gh pr list --search "file:path" --state merged --limit 3`).
- **CLAUDE.md + REVIEW.md**: đọc nếu tồn tại — dùng làm baseline cho compliance check ở Bước 3.

## Bước 3: Review theo 6 góc nhìn

Theo thứ tự ưu tiên:

### 1. Correctness (Critical)
- Logic có đúng intent không? Có edge case nào miss?
- Off-by-one, null/undefined, race condition, type coercion sai?
- Error handling có nuốt lỗi không?

### 2. Security (Critical)
- Có hardcode secret/token không?
- Có injection (SQL, command, XSS, SSRF, path traversal) không?
- Validate input ở boundary?
- Auth/authz check trên endpoint mới?

### 3. Tests (High)
- Code mới có test không? Test có thực sự verify behavior không?
- Test có đủ edge case không (boundary, null, empty, error path)?
- Có thay đổi behavior nào làm test cũ thành sai semantic không?

### 4. Performance (Medium)
- N+1 query?
- Loop lồng có cần thiết?
- Cache miss cho thứ đáng cache?
- Bundle size impact (frontend)?

### 5. Maintainability (Medium)
- Naming có rõ không?
- Function có quá dài không? (Reference: [`coding-standards.md` dòng 11](../../../../rules/coding-standards.md) — <50 lý tưởng, >100 đề xuất tách)
- Code có duplicate đoạn nào trong codebase không (gợi ý: dùng Grep tìm pattern)?
- Comment giải thích WHY hay chỉ lặp lại WHAT?
- **Code comments compliance**: đọc comments trong files bị sửa — verify thay đổi không contradict guidance trong existing comments (vd: comment nói "must be called before X" nhưng diff bỏ call đó).

### 6. CLAUDE.md / REVIEW.md Compliance (Low)
- Nếu CLAUDE.md hoặc REVIEW.md có quy tắc cụ thể → kiểm tra diff có vi phạm không.
- Chỉ flag khi guideline **explicitly mention** issue đó (không suy diễn rộng).
- Vi phạm compliance → severity 🟡 (non-blocking), trừ khi guideline nói rõ là blocking.

### 7. Style (Low)
- Theo convention codebase?
- Format đúng (formatter của project)?
- Lint pass?

## Bước 4: Trình bày kết quả

Format chuẩn:

```markdown
## Tóm tắt
[1-2 câu: code này làm gì, có nên merge không, mức độ thay đổi]

## 🔴 Phải sửa (blocking)
- **<file>:<line>** — <vấn đề ngắn>
  → <gợi ý fix cụ thể, có code nếu được>

## 🟡 Nên sửa (non-blocking nhưng đáng làm)
- ...

## 🟢 Gợi ý (optional)
- ...

## ✅ Điểm tốt
- [Khen ngắn gọn — quan trọng để cân bằng feedback]
```

Quy tắc:
- Mỗi finding phải có **vị trí cụ thể** (file:line) và **gợi ý fix**.
- **Confidence scoring**: chỉ report finding có confidence ≥80%. Tự đánh giá theo rubric: 100 = chắc chắn bug/vulnerability, 75 = rất có thể sai, 50 = có thể sai nhưng cần context thêm, 25 = chỉ là gợi ý style, 0 = không chắc. Finding <80% → bỏ hoặc gộp vào 🟢 Gợi ý.
- KHÔNG nitpick style nếu có formatter — formatter chạy tự động xử lý.
- KHÔNG đề xuất rewrite kiểu "làm khác đi" nếu chỉ là preference.
- KHÔNG flag pre-existing issues (code cũ không nằm trong diff) trừ khi diff làm nó trở thành vấn đề.
- KHÔNG flag issues mà linter/typecheck sẽ bắt (đã có CI).
- KHÔNG flag intentional behavior changes đã giải thích trong commit message/PR description.
- KHÔNG flag code có lint-ignore comment (đã được acknowledge).
- Nếu mọi thứ ổn → nói rõ "Không có vấn đề blocking, có thể merge". Đừng bịa lỗi.

## Bước 5: Hỏi tiếp

Sau khi đưa kết quả, hỏi: "Có cần diff cụ thể cho các issue 🔴 không, hay dừng ở mức liệt kê?"

Skill này read-only (frontmatter `allowed-tools` không có Edit/Write). Output diff là **text suggestion** trong chat — user tự copy/apply. Nếu muốn auto-apply, dùng skill `/refactor` hoặc subagent có Edit/Write.

## Gotchas

- **Race condition, off-by-one, memory leak**: không obvious từ diff. Đọc CONTEXT xung quanh, không chỉ dòng thay đổi.
- **Security holes** (SQLi, XSS, IDOR, SSRF): check input validation + auth check, không tin diff "trông OK".
- **Test coverage ≠ quality**: test có thể test sai thứ. Đọc test assertion, không chỉ count coverage %.
- **Style nit priority THẤP NHẤT**: flag nhưng không block PR nếu logic OK. Ưu tiên fix bug + security trước.
