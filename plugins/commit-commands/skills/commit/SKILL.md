---
name: commit
description: Creates smart Conventional Commits following the project's commit conventions. Analyzes staged changes and generates appropriate commit messages.
allowed-tools: Bash(git status:*) Bash(git diff:*) Bash(git log:*) Bash(git add:*) Bash(git commit:*) Read
disable-model-invocation: true
argument-hint: "[optional custom instructions, e.g.: fix #123]"
model: inherit
---

# Skill: Smart Commit

Purpose: create 1 Conventional Commits-compliant commit with a **Vietnamese subject**, **English type**, NO Claude attribution.

## 5-step process

### Step 1 — Read state

```bash
!`git rev-parse --git-dir >/dev/null 2>&1 && git status --short || echo "(not a git repo — cannot commit)"`
!`git rev-parse --git-dir >/dev/null 2>&1 && git diff --stat || true`
!`git rev-parse --git-dir >/dev/null 2>&1 && git log --oneline -5 || true`
```

Group files into logical groups (e.g., auth files, test files, docs files). 1 commit = 1 topic.

### Step 2 — Propose grouping

If multiple files span multiple topics → propose splitting commits:

> I see 3 groups of changes:
> 1. `src/auth/*` — OAuth feature (5 files)
> 2. `tests/auth/*` — OAuth tests (2 files)
> 3. `README.md`, `CHANGELOG.md` — docs
>
> Proposing 2 commits: (1+2 together), (3 separately). Agree?

If user has no special instruction → 1 commit for small/focused PRs, split for larger ones.

### Step 3 — Analyze diff to choose type & scope

Read `git diff --staged` in detail, infer:

| Type       | When to apply                                             |
| ---------- | --------------------------------------------------------- |
| `feat`     | Adds user-visible functionality                           |
| `fix`      | Fixes a bug that affects behavior                         |
| `refactor` | Code changes that do NOT change behavior                  |
| `perf`     | Performance optimization                                  |
| `docs`     | Docs only (`*.md`, comments, docstrings)                  |
| `test`     | Tests only                                                |
| `style`    | Formatting, linting (no logic changes)                    |
| `build`    | Build system, dependencies                                |
| `ci`       | CI/CD config                                              |
| `chore`    | Other miscellaneous tasks (rename files, clean comments, update lockfile) |
| `revert`   | Revert a commit                                           |

`<scope>` = module/component affected (`auth`, `api`, `ui`, `db`, `parser`...). Optional if the change is broad.

### Step 4 — Draft the message

Format:
```text
<type>(<scope>): <Vietnamese description, ≤72 chars, no trailing period>

<Vietnamese body — explains WHY (not WHAT). Can be multiple paragraphs.>

<footer — issue references: Closes #123, Refs #456, BREAKING CHANGE: ...>
```

**Small commit example**:
```text
fix(api): return 404 when user does not exist instead of 500

Previously the service threw NoSuchKey when calling getUser with a
non-existent id; the controller caught it as 500. Changed to throw
UserNotFoundError caught in middleware → returns 404.

Closes #218
```

**Feature commit example**:
```text
feat(auth): add Google OAuth 2.0 login

Integrated passport-google-oauth20:
- New endpoints: GET /auth/google, GET /auth/google/callback
- User is auto-created on first login (lookup by email)
- Avatar synced from Google profile

Requires GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET in .env.

Closes #142
```

**Breaking change example**:
```text
refactor(api)!: change /users response format from array to paginated

BREAKING CHANGE: GET /users previously returned an array of users,
now returns { items, total, page, pageSize }. Frontend needs updating.

Reason: client hit OOM with >10k users. Pagination stabilizes memory.

Refs #305
```

### Step 5 — Confirm and commit

Print the message for user **confirmation** first:

```text
I will commit with this message:

[message here]

OK?
```

If OK → run (Claude generates the actual command with specific values):

**For short, ASCII messages (1 line):**
```bash
git add <specific files>
git commit -m "<subject>"
```

**For multiline messages or those containing Unicode (Vietnamese, emoji)**, use `-F` file to avoid encoding errors (especially on Windows + PowerShell):
```bash
git add <specific files>
# Create a temporary message file — Linux/macOS/Git Bash use /tmp/, Windows PowerShell use $env:TEMP\
cat > /tmp/commit-msg.txt <<'EOF'
<subject>

<body>

<footer>
EOF
git commit -F /tmp/commit-msg.txt
rm /tmp/commit-msg.txt
```

> **OS note**:
> - On Git Bash (Windows) `/tmp/` maps to `%TEMP%` (usually `C:\Users\<user>\AppData\Local\Temp\`) — this directory already exists, no need to create it.
> - On native PowerShell (without Git Bash) use `$env:TEMP\commit-msg.txt` instead of `/tmp/...`.
> - `git commit -m "subj" -m "body"` via PowerShell here-string may garble Unicode. Using `-F` is safe cross-platform.

## Mandatory rules

- **NO `git add .`** — only add files that have been reviewed.
- **NO `Co-Authored-By: Claude`** or `🤖 Generated with Claude Code` tagline (disabled via settings).
- **NO commit** if lint/test/typecheck fails. Exception only when user explicitly states one of: (1) WIP commit on personal branch (not yet in CI), (2) test failure due to infrastructure (DB down, network), (3) commit for bisect/debug. "In a hurry" / "fix later" → NOT sufficient, ask again.
- **NO `--no-verify`** unless user explicitly requests it.
- **NO `--amend`** on someone else's commit.
- **NO committing secrets** — scan diff for patterns: 32+ hex strings, JWT, AWS key, Bearer, Basic auth.
- New file that looks like a large binary (>1MB) → warn before adding.

## When uncertain

- Subject under 72 chars but still clear → prioritize clarity.
- Unsure between `feat` vs `fix` → think "Does the user-visible behavior differ from before?". Yes → `feat`/`fix`. No → `refactor`/`chore`.
- Unsure about scope → omit scope.

## Extended modes

### `/commit push-pr` — Commit + Push + Create PR

When `$ARGUMENTS` contains `push-pr` or `push pr`:

1. Run Steps 1→5 as above (normal commit).
2. If on `main`/`master`/`develop` → create a new branch first: `git checkout -b <type>/<scope>-<short-desc>`.
3. `git push -u origin HEAD`.
4. Create PR with `gh pr create --fill` (requires GitHub CLI). If `gh` is absent → provide install instructions + stop.
5. Display PR URL to user.

### `/commit clean` — Clean stale branches

When `$ARGUMENTS` contains `clean` or `clean-gone`:

1. `git fetch --prune`
2. Find branches with `[gone]` upstream: `git branch -vv | grep ': gone]'`
3. If branch is linked to a worktree → `git worktree remove <path>` first.
4. List branches to be deleted, **ask user for confirmation**.
5. `git branch -d <branch>` for each branch (use `-d` not `-D` — safer, fails if unmerged).

## $ARGUMENTS

If user provides an argument (e.g., `/commit combine everything into 1 commit`), follow it. Default: auto-propose grouping.
