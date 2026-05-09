---
name: commit
description: Tạo Conventional Commit thông minh (subject tiếng Việt, type tiếng Anh) sau khi review staged diff. Gọi khi user muốn commit work hiện tại — đảm bảo commit message rõ ràng, đúng convention, không tự thêm attribution Claude.
allowed-tools: Bash(git status:*) Bash(git diff:*) Bash(git log:*) Bash(git add:*) Bash(git commit:*) Read
disable-model-invocation: true
argument-hint: "[chỉ thị riêng nếu có, vd: 'gộp 2 file kia thành 1 commit']"
model: inherit
---

# Skill: Commit thông minh

Mục đích: tạo 1 commit chuẩn Conventional Commits với subject **tiếng Việt**, type **tiếng Anh**, KHÔNG attribution Claude.

## Quy trình 5 bước

### Bước 1 — Đọc trạng thái

```bash
!`git rev-parse --git-dir >/dev/null 2>&1 && git status --short || echo "(không phải git repo — không thể commit)"`
!`git rev-parse --git-dir >/dev/null 2>&1 && git diff --stat || true`
!`git rev-parse --git-dir >/dev/null 2>&1 && git log --oneline -5 || true`
```

Phân loại file thành nhóm logic (ví dụ: file auth, file test, file docs). 1 commit = 1 chủ đề.

### Bước 2 — Đề xuất grouping

Nếu nhiều file thuộc nhiều chủ đề khác nhau → đề xuất tách commit:

> Tôi thấy 3 nhóm thay đổi:
> 1. `src/auth/*` — feature OAuth (5 files)
> 2. `tests/auth/*` — test cho OAuth (2 files)
> 3. `README.md`, `CHANGELOG.md` — docs
>
> Đề xuất 2 commits: (1+2 chung), (3 riêng). Bạn đồng ý?

Nếu user không có instruction đặc biệt → 1 commit/PR scope nhỏ thì gộp, lớn thì tách.

### Bước 3 — Phân tích diff để chọn type & scope

Đọc `git diff --staged` chi tiết, suy ra:

| Type       | Tình huống áp dụng                                        |
| ---------- | --------------------------------------------------------- |
| `feat`     | Thêm chức năng người dùng cảm nhận được                   |
| `fix`      | Sửa bug có ảnh hưởng đến hành vi                          |
| `refactor` | Sửa code KHÔNG đổi behavior                               |
| `perf`     | Tối ưu performance                                        |
| `docs`     | Chỉ docs (`*.md`, comment, JSDoc)                         |
| `test`     | Chỉ test                                                  |
| `style`    | Format, lint (không đổi logic)                            |
| `build`    | Build system, dependency                                  |
| `ci`       | CI/CD config                                              |
| `chore`    | Task vặt khác (rename file, dọn comment, update lockfile) |
| `revert`   | Revert commit                                             |

`<scope>` = module/component bị ảnh hưởng (`auth`, `api`, `ui`, `db`, `parser`...). Optional nếu thay đổi rộng.

### Bước 4 — Soạn message

Format:
```text
<type>(<scope>): <mô tả tiếng Việt, ≤72 ký tự, không chấm cuối>

<body tiếng Việt — giải thích WHY (không phải WHAT). Có thể nhiều đoạn.>

<footer — references issue: Closes #123, Refs #456, BREAKING CHANGE: ...>
```

**Ví dụ commit nhỏ**:
```text
fix(api): trả về 404 khi user không tồn tại thay vì 500

Trước đây service throw NoSuchKey khi gọi getUser với id không
tồn tại, controller bắt thành 500. Đổi thành ném UserNotFoundError
được catch trong middleware → trả 404.

Closes #218
```

**Ví dụ commit feature**:
```text
feat(auth): thêm đăng nhập bằng Google OAuth 2.0

Tích hợp passport-google-oauth20:
- Endpoint mới: GET /auth/google, GET /auth/google/callback
- User được tạo tự động lần đầu login (lookup theo email)
- Avatar đồng bộ từ Google profile

Cần thêm GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET vào .env.

Closes #142
```

**Ví dụ breaking change**:
```text
refactor(api)!: đổi format response /users từ array sang paginated

BREAKING CHANGE: GET /users trước trả về array users, giờ trả
{ items, total, page, pageSize }. Frontend cần cập nhật.

Lý do: client gặp OOM khi user >10k. Pagination giúp ổn định.

Refs #305
```

### Bước 5 — Xác nhận và commit

In message ra cho user **xác nhận** trước:

```text
Tôi sẽ commit với message:

[message ở đây]

OK chứ?
```

Nếu OK → chạy (Claude tự generate command thực với value cụ thể):

**Cho message ngắn, ASCII (1 dòng):**
```bash
git add <files cụ thể>
git commit -m "<subject>"
```

**Cho message multiline hoặc có Unicode (tiếng Việt, emoji)**, dùng `-F` file để tránh lỗi encoding (đặc biệt trên Windows + PowerShell):
```bash
git add <files cụ thể>
# Tạo file message tạm — Linux/macOS/Git Bash dùng /tmp/, Windows PowerShell dùng $env:TEMP\
cat > /tmp/commit-msg.txt <<'EOF'
<subject>

<body>

<footer>
EOF
git commit -F /tmp/commit-msg.txt
rm /tmp/commit-msg.txt
```

> **Lưu ý OS**:
> - Trên Git Bash (Windows) `/tmp/` map tới `C:\tmp\` — tạo dir trước nếu chưa có (`mkdir -p /tmp`).
> - Trên PowerShell native (không có Git Bash) dùng `$env:TEMP\commit-msg.txt` thay `/tmp/...`.
> - `git commit -m "subj" -m "body"` qua PowerShell here-string có thể garbled Unicode. Dùng `-F` an toàn cross-platform.

## Quy tắc bắt buộc

- **KHÔNG `git add .`** — chỉ add file đã review.
- **KHÔNG thêm `Co-Authored-By: Claude`** hay tagline `🤖 Generated with Claude Code` (đã tắt qua settings).
- **KHÔNG commit** nếu lint/test/typecheck fail (trừ khi user yêu cầu rõ với lý do hợp lý).
- **KHÔNG `--no-verify`** trừ khi user yêu cầu.
- **KHÔNG `--amend`** commit của người khác.
- **KHÔNG commit secret** — quét diff tìm pattern: chuỗi 32+ hex, JWT, AWS key, Bearer, Basic auth.
- File mới có vẻ là binary lớn (>1MB) → cảnh báo trước khi add.

## Khi không chắc

- Subject không quá 72 ký tự nhưng vẫn rõ → ưu tiên rõ.
- Không chắc type giữa `feat` vs `fix` → nghĩ "Hành vi user thấy có khác trước không?". Có → `feat`/`fix`. Không → `refactor`/`chore`.
- Không chắc scope → bỏ scope.

## $ARGUMENTS

Nếu user đưa argument (ví dụ `/commit gộp tất cả thành 1 commit duy nhất`), tuân theo. Mặc định: tự đề xuất grouping.
