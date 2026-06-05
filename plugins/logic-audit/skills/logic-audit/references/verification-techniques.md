# Verification Techniques

Reference for Phases 3–5 of the logic-audit skill. Load when verifying findings or planning fixes.

## Verifying a Finding is Real (Not False Positive)

**Before reporting a bug, verify:**

1. **Trace the call chain** — who calls this function? Under what conditions? Can the buggy branch actually be reached from production code paths?
2. **Check if the test already covers it** — grep test files for the function name and the specific condition. If a test already exercises the path and passes, revisit the analysis.
3. **Check similar code elsewhere** — if the codebase has 5 similar functions and 4 do it correctly, the 5th is likely a bug. If all 5 do it the same "wrong" way, it might be intentional.
4. **Construct a minimal reproduction** — can you write a test that fails with the current code and passes after the proposed fix? If yes, the bug is confirmed.

## Independent Verification Agent Prompt

When spawning an independent verifier agent (Phase 4, step 6), give it this and only this:

```
Read these files: [list of changed files]

For each file, determine:
1. Is the logic correct? Are all business rules properly enforced?
2. Are there race conditions, data integrity risks, or missing validation?
3. Any edge cases not handled?

Do NOT look at git history or ask what was changed. Read the current code only.
Report findings with specific file:line references.
```

The agent must not know what you fixed or why — that context would bias toward confirming your fix rather than finding remaining issues.

## Test Strategy for Bug Fixes

**A good bug-fix test must:**
- Reproduce the bug (fail before the fix, pass after)
- Assert the outcome, not the implementation detail
- Cover both the buggy case AND the correct behavior after fix
- Be named to describe the scenario, not the code path

**Example for a stock check bug:**
```
// Bad test name: "test variant.stockQuantity check"
// Good test name: "adding out-of-stock variant to cart throws 400 even if other variants have stock"
```

**For race conditions** — unit tests can mock time/order, but the real fix should be verifiable via integration test or by examining the transaction scope in the code.

## Discovering Stale Documentation

After fixing bugs, find stale docs by:

1. **Search by function/method name** changed — grep all `.md` files for the function name
2. **Search by behavior description** — grep for keywords from the old behavior (e.g., if a check was added, grep for "does not check", "no validation for", "accepted without")
3. **Search module-level docs** — always check `<module>/CLAUDE.md` or `<module>/README.md` in the same directory as changed files, and parent-level docs
4. **Check test count tables** — grep for numbers like "5349 tests", "215 suites" and update if tests were added/removed

**Update only factually wrong content:**
- Change descriptions that say the old incorrect behavior
- Update business rule descriptions that no longer match the code
- Do not rewrite accurate sections just to "refresh" them

## Severity Classification Guide

**🔴 HIGH — fix immediately:**
- Data written to DB can be wrong or duplicated
- Security: userId spoofing, privilege escalation, sensitive data exposure
- Race condition that can cause inconsistent state in production
- Business rule not enforced that directly affects financial/stock/order accuracy

**🟡 MEDIUM — fix before shipping:**
- Feature behaves differently than documented and user-facing (confusing UX)
- Check enforced in one code path but missing in an equivalent path
- Partial cleanup on failure (temp files, orphaned records) that accumulates over time
- Inconsistency with how the same pattern is handled elsewhere in the codebase

**🔵 INFO — document, defer if needed:**
- Dead code with no production caller (remove or explicitly document as intentional)
- Comment that describes old behavior (update the comment)
- Minor inconsistency with no user-visible impact
- Design limitation that's known and accepted

**NOT a bug (do not report):**
- Style or formatting issues
- Missing test coverage for a branch that's genuinely unreachable
- "Could be more efficient" without evidence of actual performance problem
- Theoretical edge case with no realistic trigger path

## Commit Message Format

Each fix commit should answer three questions:
1. What was wrong?
2. Why was it wrong (root cause)?
3. What changed?

```
fix(<module>): <what was wrong>

<why it was wrong — root cause in 1-2 sentences>
<what the fix changes>
```

Example:
```
fix(ai): addToCart checks total stock but not per-variant stock

totalStock > 0 doesn't guarantee the requested variant has stock.
Blue(stock=0) + Red(stock=5) → totalStock=5 → allowed incorrectly.
Now checks variant.stockQuantity when variantId is specified.
```
