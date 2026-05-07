# Quy tắc Git

> KHÔNG auto-import. Reference khi cần (`@~/.claude/references/git-workflow.md`).

## Commit message

**Format**: Conventional Commits, **subject TIẾNG VIỆT**.

```
<type>(<scope>): <mô tả ngắn bằng tiếng Việt, không chấm cuối, ≤72 ký tự>

<body — giải thích WHY, có thể nhiều đoạn, tiếng Việt>

<footer — tham chiếu issue/breaking change, tiếng Anh chuẩn>
```

**Type** (giữ tiếng Anh để tool parse được): `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

**Ví dụ đúng**:
```
feat(auth): thêm đăng nhập bằng Google OAuth

Tích hợp passport-google-oauth20 để hỗ trợ SSO. Người dùng
có thể chọn login bằng email hoặc Google account.

Closes #142
```

```
fix(api): sửa lỗi 500 khi user không có avatar

S3 trả về NoSuchKey khi avatar key không tồn tại. Fallback
về default avatar URL thay vì throw.

Refs #218
```

**Ví dụ sai**:
- `fix: bug` (không scope, không mô tả)
- `Update auth.ts` (không type, không mô tả vấn đề)
- `feat(auth): add Google OAuth login` (subject tiếng Anh — quy ước project là tiếng Việt)

## Branch name

**TIẾNG ANH**, kebab-case, theo prefix:
- `feat/<short-description>` — feature mới
- `fix/<issue-id>-<short-description>` — bug fix
- `refactor/<area>` — refactor
- `docs/<topic>` — chỉ docs
- `chore/<task>` — task vặt
- `hotfix/<issue-id>` — fix gấp lên prod

Ví dụ: `feat/google-oauth`, `fix/218-avatar-fallback`, `refactor/auth-middleware`.

## PR title & description

- **PR title**: tiếng Anh, format giống commit message. Tool như Linear/Jira parse được.
- **PR description**: tiếng Việt OK (review trong team Việt). Bao gồm: mục đích (1-2 câu), thay đổi chính (bullet), cách test, screenshot/video nếu UI, breaking change nếu có.

## Workflow

- **Trước khi commit**: `git diff --staged` review thay đổi mình sắp commit. Đừng commit "blind".
- **Add từng file** cụ thể, KHÔNG `git add .` (dễ commit file rác).
- **Commit nhỏ và thường xuyên** > commit lớn cuối ngày. Mỗi commit là 1 đơn vị logic revert được.
- **Pull/rebase** trước push. `git pull --rebase` trên feature branch.
- **Squash** trước merge nếu PR có nhiều commit "WIP", "fix typo".

## Lệnh CẤM TUYỆT ĐỐI (không tự ý chạy)

- `git push --force` (hay `-f`) lên branch chia sẻ: `main`, `master`, `develop`, `release/*`. Trên feature branch của riêng mình → cần dùng `--force-with-lease`.
- `git reset --hard` khi chưa stash/commit work hiện tại.
- `git clean -fdx` trên repo mà mình không 100% biết những gì sẽ bị xóa.
- `git rebase` khi commit đã được người khác pull về.
- `git filter-repo` / `filter-branch` trên branch chia sẻ.
- Sửa `.git/` trực tiếp.

## Lệnh nên xác nhận trước khi chạy

- `git checkout <file>` (mất work uncommitted của file đó).
- `git stash drop`.
- `git branch -D <name>` (force delete unmerged).
- `git tag -d` + `git push --delete tag`.
- `git revert <commit>` trên public history.

## Attribution

- KHÔNG thêm `Co-Authored-By: Claude <noreply@anthropic.com>` vào commit (đã tắt qua `attribution.commit: ""` trong `~/.claude/settings.json`).
- KHÔNG thêm tagline `🤖 Generated with [Claude Code]` vào commit/PR description.
- Nếu vẫn xuất hiện → bug, báo người dùng để check setting.

## Hooks an toàn

- Pre-commit hook trong project (`.husky/`, `.git/hooks/`) → tôn trọng, không bypass `--no-verify` trừ khi tôi yêu cầu rõ.
- Lint/format/type-check fail → sửa, không bypass.

## Khi xung đột

- `git merge` conflict → đọc kỹ cả 2 phía, KHÔNG auto-resolve theo pattern. Hỏi tôi nếu không chắc bên nào đúng.
- Sau resolve → chạy test trước khi commit merge.
