---
name: handoff
description: "Creates a handoff brief to compact the current session OR transition to a new session. Use when session shows signs of high context usage or before clearing history."
disable-model-invocation: false
allowed-tools: Read Write Bash(git *) Bash(find *)
argument-hint: "[--save | --inject]"
---

Generate a concise handoff brief for session continuity or context compaction. Per Anthropic guidance ([session management blog](https://claude.com/blog/using-claude-code-session-management-and-1m-context)): **brief-injection into a new session is often better than resuming** — resuming drags in stale data whereas a brief carries only decisions and current state.

## When to use

| Situation | Action |
| --------- | ------ |
| About to `/compact` (context 60-77%) | `/handoff` then `/compact <instructions>` |
| About to `/clear` — need to remember things | `/handoff --save` then `/clear` |
| Starting a new session after a break | Open new session, paste handoff into first prompt |
| After crash / session error | `claude --continue` → `/handoff` to check state |

## Instructions

When invoked, follow these steps every time:

1. **Examine current git state** (skip if not a git repo): run `git status --short`, `git log --oneline -5`, `git diff --stat HEAD`.
2. **Draft the brief** using the template below. Keep it ≤300 words (not counting headings). Omit sections that don't apply. The brief must be self-contained without requiring session history.
3. **Deliver based on flag**:
   - **No flag** → print the brief to chat. User will copy it or follow up with `/compact <brief>`.
   - **`--save`** → write `HANDOFF.md` to every project root in the workspace. Find projects via `find . -maxdepth 3 -name ".git" -type d -not -path "*/node_modules/*" -not -path "*/.git/modules/*"`, take parent dir of each `.git/`. Fallback to cwd if none found. For each project: write `HANDOFF.md` (not inside `.claude/`), ensure `.gitignore` has a `HANDOFF.md` entry. Report: `Saved HANDOFF.md to: <list>`. **IMPORTANT: use the `Write` tool to write the file — never use Bash (`cat >`, `echo >`, `tee`). The Write tool triggers a PostToolUse hook that automatically moves the file to `.claude/handoff.md`.**
   - **`--inject`** → print a single paste-ready line: `Continuing from handoff: [5-7 line inline brief]. Main files: <list>. Next step: <action>.`

## Brief template

```markdown
# Handoff — <task name> — <YYYY-MM-DD HH:MM>

## Current session goal
<1 sentence — what problem is being solved>

## Done
- <short bullet — what was accomplished, with file path if applicable>

## In progress
- <work in progress, where it stopped>
- File being edited: `path/to/file.ts:120` — <note>

## Decisions made (with 1-sentence rationale)
- <Decision>: <rationale>

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

## Rules for writing the brief

- **Decisions, not process**: "Decided JWT RS256 because legal requires it", NOT "Tried HS256, then RS256, then discussed…".
- **Closed paths = skip** unless the next session must know NOT to try them again.
- **Absolute paths or repo-root-relative paths** for files. Not "that other file".
- **Exact commands** — copy-paste ready, not "run the build command".
- **Skip long tool output** (build logs, test results). Keep only the result: pass/fail/skip.

## Integration with `/compact`

After the brief is drafted, user can run:
```text
/compact Keep the brief just drafted, drop debugging history and old tool output.
```

## Anti-patterns

- Do NOT paste entire modified code. Just write path + summary.
- Do NOT write a brief longer than 1 terminal screen.
- Do NOT include secrets/tokens/keys.
- Do NOT guess next steps when direction is unclear. Write "Needs user confirmation on direction".
