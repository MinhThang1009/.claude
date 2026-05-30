---
name: handoff-validator
description: This skill should be used when the user asks to "validate phase handoff", "check phase output before next phase", "verify phase completion", or at every phase transition in a pipeline. Verifies objectives, real edits (git diff HEAD), tests (120s timeout), and handoff sufficiency. Supports automated surgical revert on failure.
allowed-tools: Read Grep Bash Write
---

**Input:** Phase N output + original phase objectives + affected file paths + TEST_COMMAND (injected by the main agent, e.g., `"npm test"`, `"pytest"`, `"cargo test"`).

Verify four things:

**1. Objectives met.**
Read the affected files and check whether the stated phase objectives are satisfied by the current state of the code. Compare against the objectives text, not against the agent's self-report.

**2. Claimed edits are real.**
For each file the phase claimed to modify, run `Bash("git rev-parse --verify -q HEAD >/dev/null 2>&1 && git diff HEAD -- [file] || git status --porcelain -- [file]")`. Count the files with non-empty output versus the total files claimed.
Note: always use `git diff HEAD` (not bare `git diff`) — bare `git diff` compares working tree to index only and returns empty for staged-but-not-committed files, producing false "no edits" verdicts. Guard for a repo with no commits yet (`git rev-parse HEAD` fails) — fall back to `git status --porcelain -- [file]` so the initial-commit case is not misread as "0 edits".

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
- **Automated mode (unattended pipeline):** make each step below as a SEPARATE `Bash(...)` tool call and keep the result in your reasoning. Do NOT write `$(Bash(...))` into a shell — that is not valid shell and will fail with `Bash: command not found`. Use `<VAR>` to mean "the value you got from the earlier call".
  - **Step 1 — resolve PROJECT_ROOT:** call `Bash("git rev-parse --show-toplevel 2>/dev/null || echo '.'")`; call the result `<PROJECT_ROOT>`.
  - **Step 2 — read hash:** call `Bash("cat \"<PROJECT_ROOT>/.claude/checkpoints/chain-start-commit\" 2>/dev/null || echo NO_CHECKPOINT")`; call the result `<HASH>`. If `<HASH>` is `NO_CHECKPOINT` → output `REVERT_BLOCKED: chain-start-commit not found` and escalate. Do NOT run git checkout.
  - **Step 3 — validate hash:** call `Bash("git cat-file -t <HASH> 2>/dev/null")`. Proceed ONLY if the result is exactly `commit`; otherwise output `REVERT_BLOCKED: invalid hash in chain-start-commit` and escalate. Do NOT run git checkout.
  - **Step 4 — stash current work:** call `Bash("git stash push -m 'auto-stash before handoff revert' 2>&1; echo EXIT:$?")`.
    - EXIT:0 AND output contains `No local changes to save` → tree already clean, proceed (untracked files like `.claude/` are not stashed — they persist after checkout, intended).
    - EXIT:0 without that message → a stash entry was created, proceed.
    - non-zero EXIT → output `REVERT_BLOCKED: git stash failed (<stash output>)` and escalate. Do NOT run git checkout.
  - **Step 5 — surgical revert (only this phase's files):** call `Bash("git checkout <HASH> -- <file1> <file2> ...")` using the `affected_file_paths` passed as input to this skill, NOT `"."` — a full-tree revert wipes ALL phases' work, including phases that already passed validation. If no `affected_file_paths` were passed → output `REVERT_BLOCKED` and escalate; do NOT use `"."`. (git checkout reverts only tracked files; untracked pipeline files in `.claude/checkpoints/`, `.claude/progress/` remain on disk — intended.)

When DECISION is `ESCALATE`: first resolve PROJECT_ROOT and get a timestamp:
```bash
Bash("cat .claude/PIPELINE_CONFIG.md 2>/dev/null | sed -n 's/^PROJECT_ROOT:[[:space:]]*//p' || git rev-parse --show-toplevel 2>/dev/null || echo '.'")   # → PROJECT_ROOT
Bash("date -u +%Y%m%dT%H%M%S")   # → TIMESTAMP
```
Then write alert using the Write tool (not Bash heredoc — Write is cross-platform and reliable):
```
Write("[PROJECT_ROOT]/.claude/alerts/[TIMESTAMP]-handoff-escalation.md", content)
```
Content: phase number, objectives not met, unverified files, test failure details, and recommended action.
Then halt — the main agent must not proceed to Phase N+1 until the escalation is resolved.
