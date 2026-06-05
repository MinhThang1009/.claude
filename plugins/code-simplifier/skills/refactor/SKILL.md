---
name: refactor
description: "Refactors code without changing behavior. Requires tests first, refactors step by step, verifies after each step."
allowed-tools: Read Grep Glob Edit Bash
argument-hint: [file or function to refactor]
---

# Skill: Safe Refactor

> Refactor = changing code structure WITHOUT changing behavior. If behavior changes → that is a feature/fix, not a refactor.

## Step 1: Pre-flight check

Do NOT start refactoring if any of the following is true:
- Working tree is not clean (uncommitted changes) → suggest committing first.
- Current test suite is failing → suggest fixing tests first.
- No tests exist for the code about to be refactored → suggest writing characterization tests first (tests that capture current behavior, even if that behavior may not be correct).

Ask the user if needed:
- Refactor scope: just 1 file, 1 module, or across the codebase?
- Goal: easier to read? Separate responsibility? Remove duplication? Change pattern?
- Are there public API constraints? (Which functions are exported and MUST NOT have their signatures changed?)

## Step 2: Analyze & plan

Read the code, understand what it does. Then:

1. **List code smells** present:
   - Long function/class
   - Duplicate code
   - Magic numbers, magic strings
   - Unclear naming
   - High coupling between modules
   - Implicit side effects
   - Inconsistent error handling

2. **Propose a refactor plan** as small steps, each step:
   - Atomic (independently committable)
   - Reversible (easy to roll back)
   - Verifiable by tests after each step

   Example:
   ```text
   Step 1: Extract function `validateEmail` from `signupUser`
   Step 2: Rename `data` → `userInput` (4 locations)
   Step 3: Split type `User` into 2 types: `UserInput` and `UserRecord`
   Step 4: Replace magic number 86400 with const `SECONDS_PER_DAY`
   ```

3. **Present the plan to the user**, ask: "OK with this plan? Do all steps, or only some?"

## Step 3: Execute step by step

For EACH step:

1. **Apply the change** (Edit file).
2. **Run tests** immediately after. If tests fail → revert immediately, do not continue.
3. **Run lint/format** if the project has it.
4. **Brief report**: "Step N done, tests pass" or "Step N failed because X, reverted".
5. Suggest a commit checkpoint: `refactor: extract validateEmail function`.

Do NOT combine multiple steps into one large edit. The urge to do it all at once is tempting — but a mistake in a large batch is hard to find. Small steps + small commits = easy to revert.

## Step 4: Final verify

After all steps are done:
- Full test suite PASSES
- Lint/format clean
- Build succeeds
- (If applicable) Manual smoke test: run the app, click through a main flow, ensure nothing is broken.
- Does the final diff match the original plan? Did any behavior changes sneak in? If so → move them to a separate commit.

## Red rules

Do NOT do these during a refactor:
- Add new features
- Fix bugs (even obvious ones — note them as TODO, do them later)
- Change a public API signature without notification
- Change behavior even "just a little" (e.g., "throw the error earlier here for safety") — that is a behavior change, put it in a separate commit
- Mix format-only changes with logic changes in the same diff
- Refactor unrelated files "while I'm at it"

## When dealing with difficult legacy code

If code is too tangled, has no tests, and the author has left:
- Suggest the **strangler pattern**: write new code in parallel, gradually migrate callers, delete old code last.
- Or suggest **characterization tests**: run the old code with many inputs, capture outputs, use as tests. The tests will look ugly (they don't assert "correct" behavior, only assert "same as today") — but that is the only safe option when the original intent is unknown.

## Output format

When done, report:

```text
Refactor complete: [scope]

Steps executed:
1. ✓ Extract validateEmail (commit abc123)
2. ✓ Rename data → userInput (commit def456)
3. ✗ Step 3 (split type) — test failed, reverted. Reason: ...
4. ✓ Replace magic number (commit ghi789)

Ran:
- Test suite: pass (124 tests)
- Lint: clean
- Build: success

[If applicable] Notes for follow-up:
- Found a bug in foo.ts:42 during refactor — not fixed, open an issue?
```

## Gotchas

- **Refactor = preserve behavior**. Tests must pass BEFORE and AFTER. If different → it's a feature/fix, not a refactor.
- **No tests → write characterization tests first**. Blind refactoring is very dangerous with legacy code.
- **Renaming files/symbols** = changing many imports. Use Grep to find all references before renaming — do not naively search & replace (easy to miss case-sensitive, comments, string literals). If the project has an LSP rename script, prefer using it.
- **Performance changes = optimize, not refactor**. Keep the 2 types of commits separate for easy revert.
