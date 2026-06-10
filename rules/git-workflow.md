# Git Workflow

> Auto-imported every session via `rules/`.

## Commit Messages

**Format**: Conventional Commits, **subject in VIETNAMESE**.

```text
<type>(<scope>): <short description in Vietnamese, no trailing period, ≤72 chars>

<body — explain WHY, can be multiple paragraphs, Vietnamese>

<footer — issue/breaking change references, in English>
```

**Type** (keep in English so tools can parse): `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

**Good examples**:
```text
feat(auth): thêm đăng nhập bằng Google OAuth

Tích hợp passport-google-oauth20 để hỗ trợ SSO. Người dùng
có thể chọn login bằng email hoặc Google account.

Closes #142
```

```text
fix(api): sửa lỗi 500 khi user không có avatar

S3 trả về NoSuchKey khi avatar key không tồn tại. Fallback
về default avatar URL thay vì throw.

Refs #218
```

**Bad examples**:
- `fix: bug` (no scope, no description)
- `Update auth.ts` (no type, no problem description)
- `feat(auth): add Google OAuth login` (subject in English — project convention is Vietnamese)

## Branch Names

**ENGLISH**, kebab-case, with prefix:
- `feat/<short-description>` — new feature
- `fix/<issue-id>-<short-description>` — bug fix
- `refactor/<area>` — refactoring
- `docs/<topic>` — docs-only
- `chore/<task>` — housekeeping
- `hotfix/<issue-id>` — urgent production fix

Examples: `feat/google-oauth`, `fix/218-avatar-fallback`, `refactor/auth-middleware`.

## PR Title & Description

- **PR title**: English, Conventional Commits format (unlike commit messages, subject is in English so tools like Linear/Jira can parse it).
- **PR description**: Vietnamese is fine (reviewed within a Vietnamese team). Include: purpose (1–2 sentences), key changes (bullets), how to test, screenshots/video for UI changes, breaking changes if any.

## Workflow

- **Before committing**: `git diff --staged` to review what's about to be committed. Never commit blind. Unrelated file found staged → unstage it immediately and tell the user before continuing.
- **Stage files individually**, NOT `git add .` (easy to include junk files).
- **Small, frequent commits** > one large end-of-day commit. Each commit should be one logical unit that can be reverted independently.
- **Pull/rebase before push**. `git pull --rebase` on feature branches.
- **Squash before merging** if the PR has many "WIP" or "fix typo" commits.

## Forbidden Commands (never run without explicit user request)

- `git push --force` (or `-f`) to shared branches: `main`, `master`, `develop`, `release/*`. On your own feature branch → use `--force-with-lease` instead.
- `git reset --hard` when current work is not stashed/committed.
- `git clean -fdx` on a repo where you don't know 100% of what will be deleted.
- `git rebase` when commits have already been pulled by someone else.
- `git filter-repo` / `filter-branch` on shared branches.
- Direct edits to `.git/`.

## Commands That Require Confirmation

- `git checkout <file>` (loses uncommitted changes to that file).
- `git stash drop`.
- `git branch -D <name>` (force-delete unmerged branch).
- `git tag -d` + `git push --delete tag`.
- `git revert <commit>` on public history.

## Attribution

- Do NOT add `Co-Authored-By: Claude` to commits (disabled via `attribution.commit: ""` in `~/.claude/settings.json`) (see [settings docs](https://code.claude.com/docs/en/settings)).
- Do NOT add the `🤖 Generated with [Claude Code]` tagline to commits or PR descriptions. Note: `attribution.commit` only controls commit messages — PR description attribution from plugins (e.g., `/commit-push-pr`) requires setting `attribution.pr: ""` separately.
- If it still appears → it's a bug; tell the user to check both `attribution.commit` and `attribution.pr` in settings.

## Safe Hook Behavior

- Respect pre-commit hooks in the project (`.husky/`, `.git/hooks/`) — do not bypass with `--no-verify` unless the user explicitly asks.
- Lint/format/type-check failures → fix them, don't bypass.

## Merge Conflicts

- `git merge` conflict → read both sides carefully, do NOT auto-resolve by pattern. Ask the user if unsure which side is correct.
- After resolving → run tests before committing the merge.
