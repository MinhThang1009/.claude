---
description: Save phase state and create a recovery commit.
---

Use the checkpoint-writer skill to save the current phase state.

**Steps:**

1. Determine the current phase number from the most recent checkpoint file in `.claude/checkpoints/` or from context (Phase 1 if no checkpoints exist yet)
2. Use the checkpoint-writer skill to:
   - Write `.claude/checkpoints/phase-[N]-[timestamp].md` with phase ID, description, files modified, key decisions, next phase prerequisites, and Status: COMPLETE
   - If the project is a git repo (GIT_REPO: YES in PIPELINE_CONFIG.md): the skill commits **both** the checkpoint file AND the code files listed in "Files modified" — this ensures `git diff [start-commit]` in chain-verifier sees all pipeline changes.
   - If NOT a git repo: skip the git commit step — the checkpoint file is still written and usable within the session, but cannot be restored via git after a session ends.
   - **Note:** The skill commits code files. If you call checkpoint-writer after code has already been committed separately, the commit will only include the checkpoint metadata file.
3. Report the checkpoint file path and git commit hash (or "no git commit — non-git project")

Use this command after every significant phase completes. It is required before running `/compact` or ending a session in a multi-phase workflow — without a checkpoint, the session cannot be resumed from a known state.
