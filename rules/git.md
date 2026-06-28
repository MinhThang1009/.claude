# Git Workflow

> Auto-imported every session via `rules/`.

## Commit Messages

**Format**: Conventional Commits, **subject in VIETNAMESE**.

```text
<type>(<scope>): <short description in Vietnamese, no trailing period, ≤50 chars>

<body: explain WHY, can be multiple paragraphs, wrap lines at ~72 chars, Vietnamese>

<footer: issue/breaking change references, in English>
```

**Type** (keep in English so tools can parse): `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

**Breaking change**: append `!` after the type/scope (`feat(api)!: …`) and/or add a `BREAKING CHANGE: <mô tả>` footer (in English). Signals a major version bump under SemVer.

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

- **PR title**: Vietnamese, Conventional Commits format — keep the `type(scope):` prefix in English so tools (Linear/Jira/GitHub) can parse it (`feat`, `fix`, `ci`…), write the subject in Vietnamese with full diacritics (same convention as commit messages).
- **PR title doubles as the squash-merge commit subject**: with "Squash and merge", GitHub uses the PR title (plus the PR number) as the squashed commit's subject when the PR has multiple commits, so a clean title lands directly in `main`'s history.
- **PR description**: Vietnamese (reviewed within a Vietnamese team). Include: purpose (1–2 sentences), key changes (bullets), how to test, screenshots/video for UI changes, breaking changes if any.
- **Auto-close issues**: a closing keyword (`Closes` / `Fixes` / `Resolves`, also `close/closed`, `fix/fixed`, `resolve/resolved`) followed by `#N` in the PR description (or in a commit) auto-closes the linked issue, but ONLY when the PR is merged into the repository's **default branch**.

## Workflow

- **Work on a feature branch + open a PR** (GitHub Flow: branch from `main` → commit → open PR → review → merge → **delete the branch**). Do NOT push directly to `main` or any protected branch. Direct pushes to `main` are acceptable only on a throwaway solo scratch repo; even then a PR keeps `main` always-green.
- **Protect `main` to enforce the flow**: requiring CI-green or approvals BEFORE merge is NOT part of GitHub Flow itself; it comes from **branch protection rules** or the newer **rulesets** (GitHub's modern alternative: multiple rulesets can apply at once, are viewable with read access, and can also restrict commit metadata). Rulesets and classic branch protection coexist; the most restrictive rule wins.
- **Before committing**: `git diff --staged` to review what's about to be committed. Never commit blind. Unrelated file found staged → unstage it immediately and tell the user before continuing.
- **Stage files individually**, NOT `git add .` (easy to include junk files).
- **Small, frequent commits** > one large end-of-day commit. Each commit should be one logical unit that can be reverted independently.
- **Pull/rebase before push**. `git pull --rebase` on feature branches.
- **Keep the feature branch current**: rebase (or merge) `main` into it regularly to avoid drift and to satisfy a `strict` / "up to date before merge" protection rule. Rebase only while the branch is unshared.
- **Merge strategy**: default to **squash** for feature PRs (one clean commit on `main`; the PR title becomes the subject). Use a **merge commit** to preserve the branch's individual commits; avoid **rebase-and-merge** when commits are signed (it does not preserve signatures). Always squash away "WIP" / "fix typo" noise.
- **After a PR merges**, prune stale refs: `git fetch --prune` removes remote-tracking refs deleted on the remote; then delete the local branch (`git branch -d <name>`).
- **Switch context mid-change** without committing: `git stash` (alias `git stash push`) saves uncommitted work and reverts the tree to HEAD; `git stash pop` restores it and removes the entry (`git stash drop` discards without applying).
- **Backport one commit** (e.g. a fix onto a `hotfix/` branch) without merging the whole branch: `git cherry-pick <sha>` applies that commit's change as a new commit; needs a clean working tree.

## Tags & Releases

- **Tag with SemVer**: `vMAJOR.MINOR.PATCH` (e.g. `v1.2.0`). Use **annotated** tags — `git tag -a v1.2.0 -m "Mô tả bản phát hành"` — not lightweight tags.
- **Push tags explicitly**: `git push origin v1.2.0`. A plain `git push` does NOT push tags.
- Tag only from a merged, CI-green `main` commit, never from a feature branch.
- If a release-on-tag workflow builds artifacts/GitHub Releases, bump the version in the manifest (e.g. `version.php`) and commit it BEFORE tagging so the tag matches the shipped version.

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
- `git commit --amend` on a commit that's already been pushed (it replaces the tip with a new SHA = rewriting history). Amending a local/unpushed commit is fine; on your own pushed feature branch, follow with `--force-with-lease`.

## Recovery & Debugging

- **`git reflog` is the safety net** for "lost" commits: it records every move of `HEAD` and branch tips in the local repo. After a mistaken `reset --hard`, `rebase`, or `branch -D`, find the prior state (`HEAD@{2}`, `<branch>@{1}`, …) and recover with `git reset --hard HEAD@{2}` or `git branch <name> <reflog-sha>`. Always try reflog BEFORE concluding work is gone.
- **Undo a merged PR on `main`** without rewriting history: a squash/normal commit reverts with `git revert <sha>`; a merge commit needs `git revert -m 1 <merge-sha>` (`-m 1` keeps the first parent = `main` as the mainline). Safer than force-pushing `main`.
- **Find the commit that introduced a regression**: `git bisect start` → `git bisect bad` (current) → `git bisect good <old-sha>`, test each step and mark `good`/`bad`, then `git bisect reset` to finish.

## Attribution

- Do NOT add `Co-Authored-By: Claude` to commits (disabled via `attribution.commit: ""` in `~/.claude/settings.json`) (see [settings docs](https://code.claude.com/docs/en/settings)).
- Do NOT add the `🤖 Generated with [Claude Code]` tagline to commits or PR descriptions. Note: `attribution.commit` only controls commit messages — PR description attribution from plugins (e.g., `/commit-push-pr`) requires setting `attribution.pr: ""` separately.
- If it still appears → it's a bug; tell the user to check both `attribution.commit` and `attribution.pr` in settings.

## Commit Signing

- Prefer **signed commits** (`git commit -S`, or set `commit.gpgsign true`) so GitHub shows the **Verified** badge. GitHub accepts **GPG, SSH, and S/MIME** signatures.
- Caveat: **"Rebase and merge" does NOT preserve signatures** (commits are replayed); use a merge commit or squash if the Verified signature must survive.
- Only when a signing key is configured. If the user has no key set up, do NOT block or fail commits on signing → ask first.

## Safe Hook Behavior

- Respect pre-commit hooks in the project (`.husky/`, `.git/hooks/`) — do not bypass with `--no-verify` unless the user explicitly asks.
- Lint/format/type-check failures → fix them, don't bypass.

## Merge Conflicts

- `git merge` conflict → read both sides carefully, do NOT auto-resolve by pattern. Ask the user if unsure which side is correct.
- `git rebase` conflict → fix the files, `git add` them, then `git rebase --continue` (NOT `git commit`). `git rebase --abort` restores the pre-rebase state; `git rebase --skip` drops the current conflicting commit (use with care).
- After resolving → run tests before committing the merge.
