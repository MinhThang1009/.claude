---
name: code-review
description: Review code thay đổi trong working tree, branch hiện tại, hoặc PR. Tìm bug, vấn đề security, performance, style, test coverage. Dùng khi user nói "review code", "review pr", "kiểm tra code", hoặc gọi /code-review.
allowed-tools: Read Grep Glob Bash(git diff:*) Bash(git log:*) Bash(git status:*) Bash(gh pr view:*) Bash(gh pr diff:*)
argument-hint: "[tùy chọn — số PR hoặc đường dẫn cụ thể]"
---

# Skill: Code Review

Bạn được gọi để review code một cách kỹ lưỡng nhưng có ưu tiên.

## Bước 1: Xác định scope

Tùy theo `$ARGUMENTS`:

- **Không có argument**: review thay đổi chưa commit (`git diff` + `git diff --staged`)
- **Số (123)**: review PR #123 (`gh pr diff 123`)
- **Đường dẫn (`src/foo.ts`)**: review nội dung file đó
- **`branch <name>`**: review tất cả thay đổi của branch so với `main` (`git diff main...<name>`)

Hiển thị scope đã chọn cho user trước khi tiếp tục.

## Bước 2: Đọc context

- Đọc file liên quan trong diff để hiểu đầy đủ context (không chỉ đọc hunk).
- Đọc file test tương ứng (nếu có).
- Kiểm tra commit message và PR description (nếu có) để hiểu intent.

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
- Function có quá dài không?
- Code có duplicate đoạn nào trong codebase không (gợi ý: dùng Grep tìm pattern)?
- Comment giải thích WHY hay chỉ lặp lại WHAT?

### 6. Style (Low)
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
- KHÔNG nitpick style nếu có formatter — formatter chạy tự động xử lý.
- KHÔNG đề xuất rewrite kiểu "làm khác đi" nếu chỉ là preference.
- Nếu mọi thứ ổn → nói rõ "Không có vấn đề blocking, có thể merge". Đừng bịa lỗi.

## Bước 5: Hỏi tiếp

Sau khi đưa kết quả, hỏi: "Có cần diff cụ thể cho các issue 🔴 không, hay dừng ở mức liệt kê?"

Skill này read-only (frontmatter `allowed-tools` không có Edit/Write). Output diff là **text suggestion** trong chat — user tự copy/apply. Nếu muốn auto-apply, dùng skill `/refactor` hoặc subagent có Edit/Write.

## Gotchas

- **Race condition, off-by-one, memory leak**: không obvious từ diff. Đọc CONTEXT xung quanh, không chỉ dòng thay đổi.
- **Security holes** (SQLi, XSS, IDOR, SSRF): check input validation + auth check, không tin diff "trông OK".
- **Test coverage ≠ quality**: test có thể test sai thứ. Đọc test assertion, không chỉ count coverage %.
- **Style nit priority THẤP NHẤT**: flag nhưng không block PR nếu logic OK. Ưu tiên fix bug + security trước.
