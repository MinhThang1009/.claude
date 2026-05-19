---
name: handoff-validator
description: >
  Validates a phase's output before passing it to the next phase in an agent chain. Use
  between every phase transition to prevent error cascades. Checks objective alignment,
  edit verification, and test results.
allowed-tools: Read Grep Bash
---

**Input:** Phase N output + original phase objectives + affected file paths + TEST_COMMAND (injected by the main agent, e.g., `"npm test"`, `"pytest"`, `"cargo test"`).

Verify four things:

**1. Objectives met.**
Read the affected files and check whether the stated phase objectives are satisfied by the current state of the code. Compare against the objectives text, not against the agent's self-report.

**2. Claimed edits are real.**
For each file the phase claimed to modify, run `Bash("git diff [file]")`. Count the files with non-empty diffs versus the total files claimed.

**3. Tests pass.**
If TEST_COMMAND was injected, run it with Bash. Record the result. If no TEST_COMMAND was provided, record SKIPPED.

**4. Output is sufficient for the next phase.**
Assess whether the phase output contains enough information for Phase N+1 to proceed — interface changes documented, constraints noted, required context present.

**Output format:**

```
HANDOFF_CHECK:
Phase: N → N+1
Objectives met: YES | PARTIAL | NO
  Detail: [which objectives are satisfied or missing]
Edits verified: [real count] real / [claimed count] claimed
  Unverified files: [list if any]
Tests: PASS | FAIL | SKIPPED
  Detail: [test output summary or "no TEST_COMMAND provided"]
Handoff quality: SUFFICIENT | INSUFFICIENT
  Detail: [what is missing if INSUFFICIENT]

DECISION: PROCEED | REVERT_AND_RETRY | ESCALATE
```

When DECISION is `REVERT_AND_RETRY`:
- **Interactive mode (human in loop):** Run `Bash("git log --oneline -5")` and report hashes so the human can choose a revert target.
- **Automated mode (unattended pipeline):** Read the chain-start-commit and validate before reverting:
  ```bash
  # Step 1: read and validate hash
  HASH=$(Bash("cat .claude/checkpoints/chain-start-commit"))
  VALID=$(Bash("git cat-file -t [HASH] 2>/dev/null"))
  # Only proceed if VALID == "commit"
  
  # Step 2: stash current work — ABORT if stash fails
  STASH_OUT=$(Bash("git stash push -m 'auto-stash before handoff revert' 2>&1; echo EXIT:$?"))
  # Case A: EXIT:0 AND output contains "No local changes to save"
  #   → tree is already clean (no uncommitted tracked-file changes). Safe to proceed.
  #   Note: untracked files (.claude/, etc.) are not stashed — they persist after checkout (intended).
  # Case B: EXIT:0 AND output does NOT contain "No local changes to save"
  #   → stash entry was created. Proceed.
  # Case C: EXIT: followed by non-zero
  #   → output REVERT_BLOCKED: git stash failed ([stash output]) and escalate to human.
  #   Do NOT run git checkout.
  
  # Step 3: revert files (NOT HEAD — preserves commit history) — only if stash succeeded
  Bash("git checkout [HASH] -- .")
  # Note: git checkout only reverts tracked files. Untracked files created by the pipeline
  # (e.g., .claude/checkpoints/, .claude/progress/) remain on disk after this revert.
  # If a clean state is required, manually remove these with:
  # Bash("rm -rf [PROJECT_ROOT]/.claude/checkpoints/ [PROJECT_ROOT]/.claude/progress/")
  # Only do this if you are certain these directories contain only pipeline artifacts.
  ```
  If `VALID` is not "commit" (hash missing, truncated, or invalid): do NOT run git checkout. Instead output `REVERT_BLOCKED: invalid hash in chain-start-commit` and escalate to human.

When DECISION is `ESCALATE`: write to `.claude/alerts/[timestamp]-handoff-escalation.md` and halt the pipeline. The main agent should not proceed to Phase N+1 until the escalation is resolved.
