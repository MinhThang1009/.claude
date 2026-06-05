---
name: debug
description: "Systematic debugging workflow: reproduce first, write failing test, then fix. Use when encountering bugs, unexplained errors, or unexpected behavior."
allowed-tools: Read Grep Glob Bash Edit
argument-hint: "[bug description or error message]"
---

# Skill: Systematic Debugging

You have been called to debug. **DO NOT** make random fixes until you understand the problem.

## Principles

> "A bug you can reproduce reliably is half-fixed."

## Step 1: Gather symptoms

Ask the user (if not yet clear):
- What exactly are the symptoms? (what error, what wrong output, where does it crash)
- When does it occur? (always, randomly, only in certain environments)
- Did it work before? If so, what is the most recent change?
- Is there an error message / stack trace? Paste it in.

## Step 2: Reproduce

Before guessing the cause, **reproduce in the local environment**:
- Run the command the user described
- Open the file, call the function, send the request — recreate the conditions that trigger the error
- Capture the full output

If **CANNOT reproduce**:
- Tell the user clearly
- Suggest steps to gather more information (add more logging, try different env, different version)
- DO NOT make guesses and fix blindly when reproduction has not been achieved.

## Step 3: Narrow down the cause

Apply the scientific method:

1. **Observe**: what exactly is the wrong output compared to the expected correct output?
2. **Hypothesize**: list 2-4 plausible causes, ranked by confidence.
3. **Verify**: for each hypothesis, identify the **experiment** to validate it (which file to read, which command to run, what to log). Start with the hypothesis that has the lowest verification cost.
4. **Narrow down**: bisect — split the suspicious space in half (commit, file, function, input range) until the smallest component causing the error is found.

Tools:
- `git bisect` for regressions
- Binary search in code: comment/uncomment to split in half
- Add logging at key points (remember to remove after fixing)
- Reproduce with the smallest possible input that triggers the error (minimal reproducer)

## Step 4: Understand the cause (root cause, NOT the symptom)

When the error location is found:
- Why does this code cause the error? (specific mechanism, not just "it's wrong")
- Why was it written this way? (read git blame, read old PRs)
- Are there other places in the codebase with a similar pattern? (use Grep — fixing one place is usually not enough)

## Step 5: Write a failing test

Before fixing:
- Write a test that reproduces the bug. This test MUST **FAIL** on the current code.
- The test must be minimal, only testing the bug, not other things.
- Name the test to describe the bug: `it('does not crash when input is an empty array', ...)`.

If the project has no test framework, or the bug is hard to test (UI bug, race condition) → create a **manual reproduction script** instead.

## Step 6: Fix

- Fix the root cause, DO NOT patch the symptom.
- If there are multiple ways to fix → choose the least invasive with the fewest side effects.
- Fix ALL other places with a similar pattern (found in step 4).

## Step 7: Verify

- Re-run the failing test → it must now PASS.
- Run the full test suite → it must not break other tests.
- Manually reproduce the original bug → it must no longer occur.

## Step 8: Report

```markdown
## Bug: <short description>

**Cause**: <specific root cause, 1-3 sentences>

**Fix**: <how it was fixed, 1-3 sentences>

**Files changed**:
- src/foo.ts (line 42-45) — fixed empty check logic
- tests/foo.test.ts — added reproduction test

**Verify**:
- ✓ failing test now passes
- ✓ full test suite passes
- ✓ manual reproduction no longer errors
```

## When the bug cannot be reproduced

Difficult cases (race condition, different env, "works-on-my-machine"):
- DO NOT guess a fix and say "probably done". Be direct: "Cannot reproduce. The following fix is based on hypothesis X. Needs verification via [method Y]."
- Suggest adding logging/telemetry to capture the next occurrence.

## When two fixes have failed

STOP. Suggest: "Tried 2 approaches without success. Recommending `/clear` then describe the bug again with better context — something may be getting missed."

## Gotchas

- **Bug disappears** = not actually reproduced yet. Run 5-10 times to confirm reproducibility before guessing the cause.
- **Failing test MUST fail via the project's test runner** (pytest, jest, go test, cargo test, etc.) — not just manually. An irreproducible test = bug not yet understood.
- **Race condition / async**: bug occurs intermittently = suspect a race. Do not fix with a retry loop — find the actual shared state.
- **Fixing the symptom ≠ fixing the root cause**: log/print the cause before fixing. If you cannot explain "why", the fix is not complete.
