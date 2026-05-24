---
name: fact-checker
description: This skill should be used when an agent's claims are suspect — either content claims (finding X at line Y) that may be hallucinated, or state claims (claimed to edit file Z) where git diff should confirm. Use this skill — not validator — when the concern is whether the agent fabricated its narrative. Use validator when findings are trusted and only code-location confirmation is needed. Also trigger when user asks to "check for hallucinations", "verify agent claims", or "fact-check findings".
version: 0.1.0
allowed-tools: Read Grep Bash
---

**Input:** List of claims from the subagent + file paths + claim type (content or state).

Two verification paths:

**Content claims** — claims about what the code contains (e.g., "function X lacks a null check at line 42"):
1. Read the file at the cited location.
2. Check whether the claim matches the actual code.
3. Check ±20 lines for context that might invalidate or confirm the claim.

**State claims** — claims about actions taken (e.g., "fixed the bug in file Y", "added error handling to function Z"):
1. Try `Bash("git diff HEAD -- [file]")` — compares working tree to HEAD, catches both committed and uncommitted changes.
2. If empty, try committed diff — resolve project root, read start commit, then diff:
   ```bash
   Bash("git rev-parse --show-toplevel 2>/dev/null || echo '.'")   # → PROJECT_ROOT
   Bash("cat \"[PROJECT_ROOT]/.claude/checkpoints/chain-start-commit\" 2>/dev/null || echo NO_CHECKPOINT")   # → start-commit
   Bash("git diff [start-commit] -- [file]")
   ```
   If still empty and NO_CHECKPOINT: try `Bash("git diff HEAD~1 -- [file]")` as last resort.
3. If all diffs are empty: the claimed action did not occur — this is state hallucination.
4. If a diff exists: verify the diff content matches the claim intent.

**Output per claim:**

```
FACT_CHECK_REPORT:
Claim: "[exact quote of the claim]"
Type: CONTENT | STATE
Evidence: "[verbatim quote from file, or git diff output]"
Verdict: VERIFIED | CONTRADICTED | UNVERIFIED
Action: ACCEPT | DISCARD | RE_EXECUTE
```

- `VERIFIED` — evidence confirms the claim
- `CONTRADICTED` — evidence directly contradicts the claim
- `UNVERIFIED` — cannot confirm or deny with available tools (note why)
- `DISCARD` — do not use this finding; it is not supported by evidence
- `RE_EXECUTE` — the claimed action did not happen; re-dispatch the task
