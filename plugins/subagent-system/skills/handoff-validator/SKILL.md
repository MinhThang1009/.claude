---
name: handoff-validator
description: This skill should be used when the user asks to "validate phase handoff", "check phase output before next phase", "verify phase completion", or at every phase transition in a pipeline. Verifies objectives, real edits (git diff HEAD), tests (120s timeout), and handoff sufficiency. Supports automated surgical revert on failure.
version: 0.1.0
allowed-tools: Read Grep Bash Write
---

**Input:** Phase N output + original phase objectives + affected file paths + TEST_COMMAND (injected by the main agent, e.g., `"npm test"`, `"pytest"`, `"cargo test"`).

Verify four things:

**1. Objectives met.**
Read the affected files and check whether the stated phase objectives are satisfied by the current state of the code. Compare against the objectives text, not against the agent's self-report.

**2. Claimed edits are real.**
For each file the phase claimed to modify, run `Bash("git diff HEAD -- [file]")`. Count the files with non-empty diffs versus the total files claimed.
Note: always use `git diff HEAD` (not bare `git diff`) — bare `git diff` compares working tree to index only and returns empty for staged-but-not-committed files, producing false "no edits" verdicts.

**3. Tests pass.**
If TEST_COMMAND was injected, run it with a timeout to prevent pipeline hangs:
```bash
Bash("timeout 120 [TEST_COMMAND] 2>&1 | tail -80; echo EXIT:$?")
```
Record: PASS (exit 0), FAIL (non-zero exit), or TIMEOUT (exit code 124 — the test suite exceeded 120 seconds).
If TIMEOUT: record as FAIL with note "test suite timed out at 120s — check for hanging tests or increase timeout."
If no TEST_COMMAND was provided, record SKIPPED.

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
  PROJECT_ROOT=$(Bash("git rev-parse --show-toplevel 2>/dev/null || echo '.'"))
  HASH=$(Bash("cat \"[PROJECT_ROOT]/.claude/checkpoints/chain-start-commit\" 2>/dev/null || echo NO_CHECKPOINT"))
  # If HASH == NO_CHECKPOINT → REVERT_BLOCKED: chain-start-commit not found
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
  
  # Step 3: revert ONLY the files from this phase (surgical — preserves other phases' work)
  # Use the affected file paths passed as input to this skill, NOT "." (full tree revert).
  # Full tree revert wipes ALL phases' work, including phases that already passed validation.
  Bash("git checkout [HASH] -- [file1] [file2] [file3]")
  # Replace [file1] [file2] [file3] with the actual affected_file_paths from the skill input.
  # If no affected_file_paths were passed: output REVERT_BLOCKED and escalate — do NOT use "."
  # Note: git checkout only reverts tracked files. Untracked pipeline files
  # (.claude/checkpoints/, .claude/progress/) remain on disk — this is intentional.
  ```
  If `VALID` is not "commit" (hash missing, truncated, or invalid): do NOT run git checkout. Instead output `REVERT_BLOCKED: invalid hash in chain-start-commit` and escalate to human.

When DECISION is `ESCALATE`: first resolve PROJECT_ROOT and get a timestamp:
```bash
Bash("cat .claude/PIPELINE_CONFIG.md 2>/dev/null | grep '^PROJECT_ROOT:' | cut -d' ' -f2- || git rev-parse --show-toplevel 2>/dev/null || echo '.'")   # → PROJECT_ROOT
Bash("date -u +%Y%m%dT%H%M%S")   # → TIMESTAMP
```
Then write alert using the Write tool (not Bash heredoc — Write is cross-platform and reliable):
```
Write("[PROJECT_ROOT]/.claude/alerts/[TIMESTAMP]-handoff-escalation.md", content)
```
Content: phase number, objectives not met, unverified files, test failure details, and recommended action.
Then halt — the main agent must not proceed to Phase N+1 until the escalation is resolved.
