---
name: verify-plan
description: This skill should be used when the user asks to "verify the plan", "check the plan", "validate plan claims", or at Phase 5 of the /plan-refactor workflow before implementation begins. Independently verifies every factual claim in a plan against the actual codebase. Catches wrong locations, missed files, and incorrect counts before they cause failures. For gap-tracking plans (### Gap entries + cleanup grep checklist) use /audit-plan:audit-plan instead.
---

# Plan Verification

Adversarial verification of an implementation plan. The verifier did not write the plan and has no context from the planning session. Every claim is checked against the actual codebase — not against memory or summaries.

## When to Use

- At Phase 5 of the `/plan-refactor` workflow, before the first code edit
- When a plan was created in a previous session and needs re-validation before resuming
- When the user asks to double-check a plan's factual claims
- After a plan is updated to fix blockers found in a previous verification round

## Verification Procedure

Read the plan document provided by the user. For every factual claim in the plan, verify it against the actual codebase by performing the checks below. Do not trust the plan — verify everything.

### 1. File Path Verification

For each file path stated in the plan:
- Confirm the file exists at the stated path using the Read or Glob tool.
- If the file has been renamed or moved since the plan was written, report the new location.
- Check both the "Implementation Phases" and the "Files Touched" sections — sometimes a file appears in one but not the other.

Common failure: a file was renamed or deleted between plan creation and verification. This is a BLOCKER because the implementation phase referencing it will fail.

### 2. Location Verification

For each code location stated in the plan (line numbers, symbol positions, function definitions):
- Read the file at the stated location. Confirm the stated code actually appears there.
- If the file has been edited since the plan was written (e.g., by Phase 1 of a multi-phase plan), locations will have shifted. Use grep to find the current location.
- Report any location that does not match what the plan claims.

Common failure: plans often contain line numbers from the time of exploration. After any edit, every line number below the edit point shifts. Treat all plan line numbers as approximate — grep for the symbol to find the real location.

### 3. Count Verification (if plan states counts)

For each reference count or occurrence count stated in the plan:
- Use **occurrence counts**, not line counts. One line may contain the symbol multiple times.
  ```bash
  grep -ro "symbol" src/ | wc -l    # occurrence count (correct)
  # NOT: grep -r "symbol" | wc -l   # line count (undercounts)
  ```
- Compare the actual occurrence count to the plan's stated count.
- Report any mismatch, including both the expected and actual values.
- Verify the file extension used in the grep matches this codebase (not hardcoded to one language).

Common failure: plans that used `grep | wc -l` (line counts) during creation will systematically undercount when a symbol appears multiple times on one line. A plan claiming "41 references" may actually have 57 occurrences.

### 4. Missed File Detection

For each change described in the plan:
- Search the **entire codebase** for relevant content, not just the files listed in the plan.
- Flag any file with a match that is NOT in the plan's "Files Touched" list.
- **Explicitly check these commonly missed categories:**
  - Test files (with this codebase's naming pattern: `*.test.js`, `*_test.py`, `*.spec.ts`, etc.)
  - Documentation files (`**/*.md`, especially CLAUDE.md at any directory depth)
  - Configuration or fixture files that may contain symbol strings

Common failure: test files and CLAUDE.md files are missed in every first-pass inventory. This is the single most common source of post-implementation grep failures.

### 5. "What Does NOT Change" Validation

For each entry in the plan's "What Does NOT Change" section:
- Confirm the stated reason for exclusion is valid — read the actual code to verify.
- Confirm the excluded item is genuinely out of scope (not accidentally omitted).
- If a FINAL DECISION tag exists on an entry, do not re-litigate it — verify only that the decision is correctly recorded.
- Flag any entry where the reason is unclear, outdated, or potentially incorrect.

Common failure: an item marked "does not change" was actually renamed in a different scope, and the exclusion is based on a misidentification of which scope is affected.

### 6. Cross-Phase Dependency Check

If the plan has multiple phases:
- Verify that Phase N's changes will not break Phase M's stated locations (for all M > N).
- If Phase 1 renames a symbol that Phase 3 also references, confirm Phase 3's plan accounts for the rename.
- Flag any phase that depends on a location or count from a prior phase without acknowledging that it may shift.

Common failure: Phase 1 renames a variable, which shifts line numbers in the file. Phase 3 references a specific line number in the same file — that line number is now wrong.

### 7. Test Baseline Plausibility

Verify the stated BASELINE test count:
- If possible, run the test suite to confirm the exact count.
- If not possible, note the uncertainty — do not silently accept an unverified baseline.
- Check if the test configuration file has been modified recently (which could change the count).

## Output Format

Report findings grouped by severity:

```
[Phase N — Item description]
STATUS: VERIFIED | WRONG | STALE | MISSED
Expected: <what the plan claims>
Actual:   <what the code shows>
Fix:      <what needs to change in the plan>
```

**BLOCKER** — Wrong location, missed file, incorrect count. Will cause implementation failure. Must fix before proceeding.
**WARNING** — Stale comment, minor inconsistency, unclear exclusion reason. Should fix but will not cause implementation failure.
**OK** — Verified correct. No action needed.

End with a summary:
```
Blockers: N  |  Warnings: N  |  OK: N
Ready to implement: YES / NO (fix blockers first)
```

If blockers are found: return to Phase 4 of /plan-refactor to fix the specific claims, then re-run this verification.

## Edge Cases

Patterns that standard checks will not catch:

- **Same-name symbols in different scopes:** Confirm the plan's "DO NOT RENAME" list (if present) correctly identifies local variables with the same name as renamed symbols in different files.
- **Interleaved JSDoc blocks:** Two methods' JSDoc can appear adjacent in a file (one method's closing `*/` immediately followed by another's `/**`). Verify the plan assigns each JSDoc block to the correct method — a partial read will miss this.
- **Dynamic references:** Symbols accessed via bracket notation (`obj[varName]`) or template literals are invisible to grep. If the plan relies solely on grep to count references, dynamic references will be missed.
