---
name: checkpoint-writer
description: >
  Saves phase results to disk and creates a git commit after each phase completes. Use at
  the end of every implementation phase to enable session recovery if the session is
  interrupted.
allowed-tools: Write Bash
---

After a phase completes, execute these steps in order:

**Step 0 — Locate project root and record chain start commit (first phase only).**
```bash
Bash("git rev-parse --show-toplevel 2>/dev/null || pwd")   # → PROJECT_ROOT
```
If result is NOT a git repo (git rev-parse fails, falls back to pwd): note "No git repo detected — skipping chain-start-commit and git commit steps. Checkpoint file will be written to .claude/checkpoints/ but not committed."

If git repo found:
```bash
Bash("mkdir -p $(git rev-parse --show-toplevel)/.claude/checkpoints")
```
If Phase 1, record start commit:
```bash
Bash("git rev-parse HEAD > $(git rev-parse --show-toplevel)/.claude/checkpoints/chain-start-commit")
```
This file is the anchor for `chain-verifier`. Skip for phases 2+.

**Step 1 — Write the checkpoint file.**
```bash
# TIMESTAMP cross-platform: date -u +%Y%m%dT%H%M%S (macOS/Linux/Git Bash on Windows)
# Add $RANDOM suffix to prevent filename collision when two phases complete in the same second
Bash("TIMESTAMP=$(date -u +%Y%m%dT%H%M%S); ROOT=$(git rev-parse --show-toplevel); cat > \"$ROOT/.claude/checkpoints/phase-N-${TIMESTAMP}-$RANDOM.md\" << 'CPEOF'\n[checkpoint content]\nCPEOF")
```
Write `.claude/checkpoints/phase-[N]-[timestamp].md` with the following content:

```markdown
# Checkpoint: Phase [N]

## Phase description
[One-sentence summary of what this phase accomplished]

## Status
COMPLETE

## Files modified
- [file path]: [one-line description of change]
- [file path]: [one-line description of change]

## Key decisions
- [Decision]: [one-sentence rationale]

## Prerequisites for next phase
- [What Phase N+1 needs to know or have available]

## Timestamp
[ISO 8601 timestamp]
```

**Step 2 — Create a git commit.**
Add only the specific files listed in "Files modified" above — never use `git add -A` or `git add .`:
```bash
Bash("git add [file1] [file2] ...")  # list each file explicitly from the Files modified section
Bash("git status --short")           # preview what will be committed — verify no unexpected files
Bash("git commit -m 'checkpoint: phase N complete — [description]'")
```

Keep the commit message under 72 characters. If `git status` shows unexpected files, do NOT proceed — report them and let the main agent decide.

**Step 3 — Report.**

```
CHECKPOINT_WRITTEN:
File: .claude/checkpoints/phase-N-[timestamp].md
Git commit: [hash from commit output]
Next phase can resume from: [one sentence describing the current state]
```

If the git commit fails (e.g., nothing to commit), report the checkpoint file path and note "No changes to commit — working tree clean."

If not in a git repo: skip Step 2 entirely. Report:
```
CHECKPOINT_WRITTEN:
File: [path]
Git commit: SKIPPED (not a git repository)
Next phase can resume from: [description]
```
