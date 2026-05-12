---
name: handoff
description: "Creates a handoff brief to compact the current session OR transition to a new session. Use when session shows signs of high context usage or before clearing history."
allowed-tools: Read Write Bash(git status:*) Bash(git log:*) Bash(git diff:*)
argument-hint: "[--save | --inject]"
model: inherit
---

# Skill: Handoff between sessions

Per guidance from Anthropic ([Using Claude Code session management and 1M context](https://claude.com/blog/using-claude-code-session-management-and-1m-context)) and community experience: **resuming a long session is often worse than brief-injection into a new session** — because resuming drags in stale environment data (old tool output, old file content) whereas a brief carries only decisions and current state.

## When to apply

| Situation                                                  | Action                                             |
| ---------------------------------------------------------- | -------------------------------------------------- |
| About to `/compact` (context 60-77% wrap-up zone) — continuing the same task | `/handoff` then `/compact <instructions>` |
| About to `/clear` — switching to a new task but need to remember a few things | `/handoff --save` then `/clear` |
| Starting a new session after a break                        | Open new session, paste handoff into first prompt  |
| After crash / session error                                 | `claude --continue` → `/handoff` to check state    |

## Process

### Step 1 — Check current context

```bash
# User checks via /context themselves. I (Claude) read git to know code state (skip if not a git repo):
!`git rev-parse --git-dir >/dev/null 2>&1 && git status --short || echo "(not a git repo — skip git context)"`
!`git rev-parse --git-dir >/dev/null 2>&1 && git log --oneline -5 || true`
!`git rev-parse --git-dir >/dev/null 2>&1 && git diff --stat HEAD || true`
```

### Step 2 — Draft the handoff brief

I write a **SHORT** brief (≤300 words of content, not counting headings) in the format below. Omit any section that does not apply. The brief must be self-contained without requiring the session history.

```markdown
# Handoff — <task name> — <YYYY-MM-DD HH:MM>

## Current session goal
<1 sentence — what problem is being solved>

## Done
- <short bullet — what was accomplished, with file path if applicable>
- ...

## In progress
- <work in progress, where it stopped>
- File being edited: `path/to/file.ts:120` — <note>

## Decisions made (with 1-sentence rationale)
- <Decision 1>: <rationale>
- <Decision 2>: <rationale>

## Constraints / things to remember
- <perf, compat, security, business rule>

## Things to avoid / tried but didn't work
- <approach X — rejected because of reason Y>

## Next steps
1. <specific action>
2. <specific action>

## Useful commands for this project
- Build: `<command>`
- Test: `<command>`
- Lint: `<command>`
```

### Step 3 — Save or inject

**If user runs `/handoff` without a flag** → print the brief to chat. User will:
- Copy it manually into a new session, OR
- I continue with `/compact <brief>` to maintain continuity.

**If user runs `/handoff --save`** → write brief to `<project>/HANDOFF.md` (project root, not `.claude/` — `.claude/` is a config directory). Before writing: check `.gitignore` for a `HANDOFF.md` entry — if absent, add it (avoid committing internal notes).
- New session will read it when user says "read HANDOFF.md".

**If user runs `/handoff --inject`** → print 1 paste-ready line for user to paste into a new session:
```text
Continuing from handoff: [inline brief 5-7 lines]. Main files: <list>. Next step: <action>.
```

## Rules for writing the brief

- **Decisions, not process**: write "Decided to use JWT RS256 because legal requires it", NOT "Tried HS256, then tried RS256, then discussed...".
- **Closed paths = skip** unless it is important for the next session to know NOT to try them again.
- **Absolute paths or repo-root-relative paths** for files. Not "that other file".
- **Exact commands** — copy-paste ready, not "run the build command".
- **Skip long tool output** (build logs, detailed test results). Keep only the result: pass/fail/skip.

## Integration with `/compact`

After drafting the brief, user can run:
```text
/compact Keep the brief just drafted, drop debugging history and old tool output.
```
This guided compact instruction helps Claude compact with direction, giving the brief a higher chance of surviving auto-summary.

## Anti-patterns — Do NOT

- Do NOT paste entire modified code into the brief. Just write path + summary.
- Do NOT write a brief longer than 1 terminal screen. Too long → becomes noise.
- Do NOT include secrets/tokens/keys in the brief.
- Do NOT guess next steps when direction is unclear. Write "Needs user confirmation on direction".
