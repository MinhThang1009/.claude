# Verification Techniques

Reference for Phases 3–6 of the audit-logic skill.

---

## Verifying a Finding is Real (Not False Positive)

Before adding an issue to the confirmed list:

1. **Trace the call chain.** Who calls this function? Under what conditions? Can the buggy branch actually be reached from a production code path? If only a test can reach it, it may not be a production bug.
2. **Check if the test already covers it.** Grep test files for the function name and the specific condition. If an existing test exercises this exact path and passes, the behavior may be intentional — revisit the analysis.
3. **Check similar code elsewhere.** If the codebase has 5 similar functions and 4 do it correctly, the 5th is almost certainly a bug. If all 5 do it the same "wrong" way, it might be an intentional design choice.
4. **Construct a minimal reproduction mentally.** Can you describe a specific input that triggers the wrong behavior? If you can't construct a concrete example, the bug is likely theoretical.

---

## Independent Verification Agent Prompt

When spawning an independent verifier (Phase 5, step 6), give the agent **exactly this prompt** with no additional context about what you changed or why:

> The canonical copy of this template lives in SKILL.md Phase 5 step 6 — if the two ever diverge, SKILL.md wins.

```
Read these files: [list changed files]

For each file, determine:
1. Is the logic correct? Are all business rules properly enforced?
2. Are there race conditions, data integrity risks, or missing validation?
3. Are there edge cases where the code produces incorrect output?

Do NOT look at git history, commit messages, or any description of what was changed.
Read the current code only.
Report findings with specific file and line number references.
```

**The agent must not know what you fixed.** That context creates confirmation bias — the agent converges toward "your fix looks correct" instead of finding remaining issues. The point is independent eyes, not a rubber stamp.

---

## Test Strategy for Bug Fixes

> Canonical criteria live in SKILL.md Phase 5 step 2 — if the two ever diverge, SKILL.md wins.

A good bug-fix test:
- **Fails** on the unfixed code (reproduces the bug) — or is explicitly labeled DOCUMENTATION per SKILL.md Phase 5 step 2 (INFO-severity, behavior-unchanged fixes only)
- **Passes** on the fixed code
- Asserts the **outcome**, not the implementation detail (do not test internal state)
- Is **named** to describe the scenario, not the code path

**Test naming examples:**
```
// Bad:  "test variant.stockQuantity field check"
// Good: "adding out-of-stock variant to cart throws 400 even if other variants have stock"

// Bad:  "test null check branch"
// Good: "getUser returns null when userId is not found, not an empty object"
```

**When no test runner is available:**
- Document the expected behavior as a comment in the fix commit
- Note in the Phase 7 summary that the fix needs environment-level verification
- Do not claim the fix is verified — it is not

**Code snippets for Phase 5** (canonical rules live in SKILL.md Phase 5; these are only the format examples):

Call-signature assertion grep (Phase 5 step 1 pre-flight):
```
grep -r "<assertion_matcher>" <test_dirs> | grep "<function_name>"
```

Integration/API test placeholder for `[UNIT-TEST-BLIND]` fixes (Phase 5 step 2):
```js
// Verifies [BUG-X]: [description of what the test proves]
test.skip('[BUG-X] integration test — requires real DB/service', async () => { ... });
```

**For race conditions:**
- Unit tests can mock concurrency order but cannot prove atomicity
- The authoritative verification is examining the transaction boundaries in the code
- Note in the commit: "Atomicity verified by code review — transaction wraps X, Y, Z operations"

---

## Discovering Stale Documentation

After fixing bugs, find documentation that now states incorrect behavior:

1. **Search by function or method name.** Grep all documentation files (`.md`, `.txt`, docs directories) for the name of every function you changed.

2. **Search by old behavior keywords.** If you added a check, grep for phrases like "does not check", "no validation", "accepted without". If you removed a field, grep for its name.

3. **Check module-level docs.** Always look for a `CLAUDE.md`, `README.md`, or equivalent in:
   - The same directory as the changed files
   - The parent directory
   - The project root

4. **Check any centrally maintained metrics.** Some projects maintain test counts, coverage percentages, or API endpoint counts in documentation. If your fix added or removed tests, search for these numbers and update them.

**Update only factually wrong content:**
- Rewrite descriptions that state the old, incorrect behavior
- Update business rule descriptions that no longer match the code
- Do **not** rewrite accurate sections as a "refresh" — unnecessary churn obscures the meaningful change

---

## Severity Classification

> The canonical rubric — including the race-condition calibration (wrong data persisted = HIGH; failed request/500 with no wrong data = MEDIUM at most) — lives in SKILL.md Phase 3. If this section and SKILL.md ever diverge, SKILL.md wins.

**🔴 HIGH — fix immediately:**
- Data written to the database can be wrong, duplicated, or missing
- Security: authentication bypass, privilege escalation, sensitive data exposed
- Race condition that produces inconsistent state under concurrent load
- Business rule not enforced that directly affects financial, inventory, or order accuracy

**🟡 MEDIUM — fix before shipping:**
- Feature behaves differently than documented in a way users will notice
- Validation enforced on one code path but missing on an equivalent path (same operation, different entry point)
- Partial cleanup on failure that accumulates over time (orphaned files, dangling records)
- Inconsistency with how the same pattern is handled elsewhere in the codebase, with potential user-visible or risk-bearing impact (purely cosmetic inconsistency with no user-visible impact is INFO per SKILL.md)
- Race condition whose worst case is a failed request / 500 with no wrong data persisted

**🔵 INFO — document, defer if appropriate:**
- Dead code with no production caller (remove, or document explicitly as intentional)
- Comment that describes the old, wrong behavior (update the comment)
- Minor inconsistency with no user-visible impact
- Design limitation that is known and accepted by the team

**NOT a bug — do not report:**
- Style or formatting that violates no logic
- Missing test coverage for a branch that is genuinely unreachable in production
- "Could be more efficient" without a measured or demonstrated performance problem
- Theoretical edge case with no realistic trigger path in the target environment

---

## Commit Message Format

Each fix commit answers three questions: what was wrong, why it was wrong, what changed.

Follow the **target project's** commit conventions (language, scope format, footer). The examples below use English subjects — if the project's convention mandates another language or format, the project wins.

```
fix(<module>): <what was wrong — short, present tense>

<why it was wrong — root cause, 1-2 sentences>
<what the fix changes>
```

**Examples:**
```
fix(cart): addToCart checks total stock but not per-variant stock

totalStock > 0 doesn't guarantee the requested variant has stock.
Blue(stock=0) + Red(stock=5) → totalStock=5 → allowed incorrectly.
Now checks variant.stockQuantity when variantId is specified.
```

```
fix(auth): getUserById returns empty object instead of null when not found

Caller pattern `if (!user)` evaluates to false for `{}`, bypassing auth guard.
Returns null explicitly when findByPk yields no result.
```

**Doc-update commit format:**
```
docs(<module>): update after <bug-name> fix

<which behavior description was stale and what it says now>
```
