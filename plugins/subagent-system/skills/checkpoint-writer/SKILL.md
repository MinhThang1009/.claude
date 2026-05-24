---
name: checkpoint-writer
description: This skill should be used when saving current pipeline phase state to disk and creating a recovery commit. Trigger at the end of every implementation phase, when the user asks to "save a checkpoint", "commit this phase", or before any /compact or session end. Enables resume-from-checkpoint to reconstruct pipeline state after interruption.
version: 0.1.0
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
If Phase 1, record start commit — only if file does not already exist (guard against overwrite on restart):
```bash
Bash("ROOT=$(git rev-parse --show-toplevel); CSC=\"$ROOT/.claude/checkpoints/chain-start-commit\"; [ -f \"$CSC\" ] || git rev-parse HEAD > \"$CSC\"")
```
This file is the anchor for `chain-verifier`. Skip for phases 2+.
**Why guard with `[ -f ]`:** If the pipeline is interrupted and restarted from Phase 1 after new commits exist, overwriting chain-start-commit would lose the original revert anchor. The guard ensures the anchor always points to the true pipeline start.

**Step 1 — Write the checkpoint file.**
Use the `Write` tool directly — do NOT use Bash heredoc (heredoc newline escaping is unreliable on Windows Git Bash and can produce a single-line or malformed file):
```
# Get timestamp and path first:
Bash("date -u +%Y%m%dT%H%M%S")   # → TIMESTAMP
Bash("git rev-parse --show-toplevel")  # → ROOT

# Then use Write tool:
Write("[ROOT]/.claude/checkpoints/phase-[N]-[TIMESTAMP].md", [content below])
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

## Checkpoint commit
Checkpoint commit: [git commit hash written by Step 2, or SKIPPED if non-git]

## Timestamp
[ISO 8601 timestamp]
```

**Step 2 — Create a git commit.**
Add only the specific files listed in "Files modified" above — never use `git add -A` or `git add .`:
```bash
Bash("git add [file1] [file2] ...")  # list each file explicitly from the Files modified section
Bash("git status --short")           # preview what will be committed — verify no unexpected files
Bash("git commit -m 'checkpoint: phase N complete — [description]'")
Bash("git rev-parse HEAD")           # → COMMIT_HASH
```

Keep the commit message under 72 characters. If `git status` shows unexpected files, do NOT proceed — report them and let the main agent decide.

**Step 2.5 — Backfill commit hash into checkpoint file.**
Replace the placeholder with the real hash using Edit:
```
Edit("[ROOT]/.claude/checkpoints/phase-[N]-[TIMESTAMP].md",
  old: "Checkpoint commit: [git commit hash written by Step 2, or SKIPPED if non-git]",
  new: "Checkpoint commit: [COMMIT_HASH]")
```

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
