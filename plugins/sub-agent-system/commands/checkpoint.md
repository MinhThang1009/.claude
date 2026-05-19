---
description: Saves current phase state to disk and creates a git commit to enable session recovery if interrupted.
---

Use the checkpoint-writer skill to save the current phase state.

**Steps:**

1. Determine the current phase number from the most recent checkpoint file in `.claude/checkpoints/` or from context (Phase 1 if no checkpoints exist yet)
2. Use the checkpoint-writer skill to:
   - Write `.claude/checkpoints/phase-[N]-[timestamp].md` with phase ID, description, files modified, key decisions, next phase prerequisites, and Status: COMPLETE
   - Run `git add [checkpoint-file] [chain-start-commit if phase 1] && git commit -m "checkpoint: phase N complete — [description]"` — list each file explicitly, never use `git add -A` or `git add .`
3. Report the checkpoint file path and git commit hash

Use this command after every significant phase completes. It is required before running `/compact` or ending a session in a multi-phase workflow — without a checkpoint, the session cannot be resumed from a known state.
