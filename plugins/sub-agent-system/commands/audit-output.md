---
description: Post-run audit of a completed multi-agent pipeline. Runs completion-checker, git diff verification, coverage-verifier, and fact-checker in sequence. Pass your project's test command as an argument — e.g., /audit-output "npm test" or /audit-output "pytest -q".
---

**Required argument:** `$ARGUMENTS` = the project's test command (e.g., `npm test`, `pytest -q`, `cargo test`). If not provided, Level 4 regression tests will be SKIPPED and the audit report will be marked incomplete.

Run the following checks in order. Each level must complete before the next begins.

**Level 1 — Structural checks (automated):**
1. Use the completion-checker skill: verify all tasks in the pipeline's COMPLETION_CHECKLIST were processed
2. Run `Bash("git diff --name-only [start-commit]")`: compare files changed against files assigned to each agent
3. Report any files modified outside the assigned scope (scope violations)

**Level 2 — Content sampling:**
4. Use the coverage-verifier skill: spot-check 2–3 randomly selected files per agent for actual coverage
5. Use the fact-checker skill: verify the top 5 findings by severity against source code
6. Run `git diff [file]` for every file claimed as edited: count real edits vs claimed edits

**Level 3 — Semantic review:**
7. Assess goal alignment: does the pipeline output address the original objectives?
8. Note any findings from the pipeline-reviewer if it ran as part of the pipeline

**Level 4 — Regression:**
9. Run the project's test command if available
10. Run the project's lint and type-check commands if available

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
