---
description: Post-run audit of a completed multi-agent pipeline. Runs completion-checker, git diff verification, coverage-verifier, and fact-checker in sequence. Pass your project's test command as an argument — e.g., /audit-output "npm test" or /audit-output "pytest -q".
---

**Required argument:** `$ARGUMENTS` = the project's test command (e.g., `npm test`, `pytest -q`, `cargo test`). If not provided, Level 4 regression tests will be SKIPPED and the audit report will be marked incomplete.

Run the following checks in order. Each level must complete before the next begins.

**Level 1 — Structural checks (automated):**
1. Use the completion-checker skill: verify all tasks in the pipeline's COMPLETION_CHECKLIST were processed
2. Resolve `[start-commit]` from `.claude/checkpoints/chain-start-commit`:
   ```bash
   Bash("cat .claude/checkpoints/chain-start-commit 2>/dev/null || echo MISSING")
   ```
   If MISSING: skip git diff and note "chain-start-commit not found — scope violation check skipped."
3. Run `Bash("git diff --name-only [start-commit]")`: compare files changed against files assigned to each agent
4. Report any files modified outside the assigned scope (scope violations)

**Level 2 — Content sampling:**
5. Use the coverage-verifier skill: spot-check 2–3 randomly selected files per agent for actual coverage
6. Use the fact-checker skill: verify the top 5 findings by severity against source code
7. Run `git diff [file]` for every file claimed as edited: count real edits vs claimed edits

**Level 2.5 — Severity gate:**
First verify FINDINGS_REPORT.md exists:
```bash
Bash("test -f .claude/FINDINGS_REPORT.md && echo EXISTS || echo MISSING")
```
If MISSING: set `PIPELINE_STATUS: NEEDS_RERUN` and note "FINDINGS_REPORT.md not found — consolidate-findings must run before audit-output." Skip the severity-gate and proceed directly to Level 3.

If EXISTS: run the severity-gate skill — it reads `.claude/FINDINGS_REPORT.md` directly (the consolidated report from consolidate-findings, NOT the fact-checker output). Do NOT pass fact-checker output as injected text to severity-gate. If any CRITICAL findings are verified:
- Set `PIPELINE_STATUS: NEEDS_RERUN` immediately
- List all CRITICAL findings in `ACTION_REQUIRED`
- Skip Level 3 and Level 4 — no point running further checks if critical issues exist

**Level 3 — Semantic review:**
8. Assess goal alignment: does the pipeline output address the original objectives?
9. Note any findings from the pipeline-reviewer if it ran as part of the pipeline

**Level 4 — Regression:**
10. Run the project's test command if available
11. Run the project's lint and type-check commands if available

Write the results to `AUDIT_REPORT.md`:

```markdown
# AUDIT_REPORT — [timestamp]

## Level 1 — Structural
- Tasks: [PROCESSED]/[TOTAL]
- Files modified: [N] (expected [M])
- Scope violations: [list or NONE]

## Level 2 — Content
- Coverage: [THOROUGH/SUPERFICIAL/FABRICATED] for [N] agents sampled
- Fact check: VERIFIED [N] / CONTRADICTED [N] / UNVERIFIED [N]
- Git diff verify: [N] real edits / [N] claimed edits

## Level 3 — Semantic
- Goal alignment: YES | PARTIAL | NO

## Level 4 — Regression
- Tests: PASS | FAIL | SKIPPED
- Lint: CLEAN | ERRORS | SKIPPED

## Verdict
PIPELINE_STATUS: CLEAN | ISSUES_FOUND | NEEDS_RERUN
ACTION_REQUIRED:
- [specific action if ISSUES_FOUND, or NONE]
```
