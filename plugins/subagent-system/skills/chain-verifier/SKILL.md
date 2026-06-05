---
name: chain-verifier
description: This skill should be used at the final step of any multi-phase pipeline to verify the complete working-tree state satisfies the original requirements. Trigger after all fix agents and pipeline-reviewer have completed. Also invoke when user asks to "run chain-verifier", "verify the pipeline output", or "confirm requirements are met".
allowed-tools: Read Grep Glob Bash
---

Do not attempt to reconstruct the pipeline's history. Treat this as an independent audit — evaluate only what is present in the provided files and git diff. Requesting chain history defeats the purpose of this skill.

**Input:** Original requirements (verbatim) + final affected file paths + optional TEST_COMMAND.

**Step 0 — Verify git repo and read chain start commit.**

First, confirm this is a git repository:
```bash
Bash("git rev-parse --is-inside-work-tree 2>/dev/null || echo NOT_GIT")
```
If the result is `NOT_GIT`: output `CHAIN_VERIFICATION_BLOCKED: not a git repository — chain-verifier requires git to compute diffs. Run chain-verifier only in git-managed projects.` and stop.

Resolve working dir and read the chain start commit:
```bash
Bash("git rev-parse --show-toplevel 2>/dev/null || echo '.'")   # → WORKING_DIR
Bash("cat \"[WORKING_DIR]/.claude/checkpoints/chain-start-commit\" 2>/dev/null || echo NO_CHECKPOINT")   # → start-commit
```
This file is written by `checkpoint-writer` at the start of Phase 1. If the result is `NO_CHECKPOINT`, set start-commit to `HEAD~1` and report: "chain-start-commit not found — checkpoint-writer may not have run. Falling back to HEAD~1 as approximate start commit — run `git log --oneline -10` to verify the correct range, then diff with `git diff HEAD~1`."

Verify independently in this order:

**1. Read the affected files.**
Use Read to examine every file in the affected file paths list. Do not skim — read enough to assess whether the requirements are met.

**2. Verify requirements are satisfied.**
Compare the current code state against the original requirements text. Do not compare against any intermediate agent output.

**3. Review all changes made by the chain.**
Resolve working dir first: `Bash("git rev-parse --show-toplevel 2>/dev/null || echo '.'")` → WORKING_DIR. Then run `Bash("git -C [WORKING_DIR] diff [start-commit]")` to see every change the pipeline made. Check for unexpected modifications outside the stated scope.

**4. Check for unexpected changes.**
List any files modified that were not in the affected file paths list. Flag any behavior changes that the original requirements did not call for.

**5. Run tests if a TEST_COMMAND was provided.**
Execute it with Bash and record the result.

**Output format:**

```
CHAIN_VERIFICATION:
Original requirement: "[verbatim quote]"
Actual code state: [summary of what the code currently does]
Changes made: [summary of git diff — files changed, lines added/removed]
Requirement met: YES | PARTIAL | NO
  Detail: [what is or is not satisfied]
Unexpected changes: [list of files or behaviors outside stated scope, or NONE]
Tests: PASS | FAIL | N/A
  Detail: [test output summary or "no TEST_COMMAND provided"]

VERDICT: APPROVED | NEEDS_REVERT | NEEDS_FIX
  Reason: [one sentence]
```

- `APPROVED` — requirements met, no unexpected changes, tests pass
- `NEEDS_REVERT` — cascaded errors make the changes unsafe; include the git log for revert target selection
- `NEEDS_FIX` — requirements partially met or tests fail, but revert is not necessary
