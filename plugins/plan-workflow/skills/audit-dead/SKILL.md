---
name: audit-dead
description: This skill should be used when the user asks to "audit for dead code", "check for unused imports", "find cascade effects", "run post-implementation audit", or at Phase 7 of the /plan-refactor workflow after implementation completes. Finds dead imports, dead parameters, schema gaps, structural misplacements, and stale documentation created by changes.
version: 1.0.0
---

# Post-Implementation Audit

Run after completing any implementation plan to find cascade effects that planning cannot predict (P5). Implementation changes the code; the changed code has properties — newly dead dependencies, newly broken contracts, newly inconsistent parallel paths — that no pre-implementation analysis could have foreseen.

## When to Use

- At Phase 7 of the `/plan-refactor` workflow, after all implementation phases pass
- After any batch of code changes (>3 files modified)
- When the user suspects dead code or stale references exist after changes
- Before signing off on a refactoring to confirm the codebase is clean

## Audit Checks

Run all six checks in order. Report all findings before suggesting fixes.

### Check 1 — Dead Import Scan

For each file in scope:
1. Extract every destructured symbol from `require()` / `import` statements.
2. Search the file body (excluding the import line itself) for each symbol.
3. Flag any symbol with zero usages in the body as `DEAD_IMPORT`.

**Verification requirement:** Verify every candidate manually — do not trust automated scan output. Read the relevant lines. Automated dead-import scripts have high false positive rates because they cannot distinguish between code usage, comment mentions, and string literals.

**False positive traps — do NOT flag these:**
- Symbol used only in a JSDoc comment or inline comment → not dead code (but note it for documentation accuracy)
- Symbol used only in test files → alive (tests are callers, not dead weight)
- Symbol inside a string literal (log message, error message) → alive at runtime
- Symbol in test `describe()`/`it()` block → behavior description, not a variable reference
- Symbol accessed via bracket notation `obj[varName]` or template literal → alive but invisible to grep

**Example:** After renaming `parseAIResponse` → `parseLLMOutput`, the old import `const { parseAIResponse } = require(...)` may still exist in a file that was missed by the rename plan. This is a genuine `DEAD_IMPORT` — the symbol is imported but never called because all call sites now use the new name.

### Check 2 — Dead Parameter Cascade

For every function/method that had a parameter removed or made unused in this change:
1. Find all direct callers of that function.
2. Ask: was the caller collecting a value **only to pass it to this function**? If yes, that value collection is now dead in the caller too.
3. Repeat upward through the call chain until reaching a function that genuinely uses the value for something other than passing it on.

Report the full chain: `A collects X → passes to B → passes to C (param removed) → X is now dead in A and B`.

**Mid-implementation emergence:** A parameter may be alive when the plan is written but become dead mid-implementation. For example, if Phase 1 removes a parameter from function C, and function B only collected that value to pass to C, then B's parameter became dead — but this was not in the original plan because B's parameter was alive at planning time. Check after each implementation phase, not only at the end.

**YAGNI antipattern:** Any parameter documented as "not currently used, kept for future extension" is a YAGNI violation. It will never be filled in. Remove it and trace the cascade upward. This is a common source of dead parameter chains that grow over time.

**Example:** Removing `context` from `buildAugmentedPrompt(msg, products, context)` made `context` in `augmentAndGenerate(msg, products, context, history)` dead (it was only collected to pass downstream). And `context` in `handleMessage(msg, userId, sessionId, context)` was only collected to pass to `augmentAndGenerate`. Full cascade: 3 functions cleaned.

### Check 3 — Schema Consistency Across Parallel Paths

Identify all functions that return the same logical type (e.g., "product card", "search result", "API response", "chat reply"). These are the most dangerous gaps because parallel paths are developed and maintained independently.

Common parallel path pairs:
- Happy path (LLM response parser) vs. fallback path (keyword matcher)
- Success handler vs. error handler
- Main code path vs. cache path
- Online mode vs. offline mode

For each group:
1. List every return site across all execution paths.
2. List the fields in each returned object.
3. Diff the field sets — every field must be present in every path.
4. Flag any field present in some paths but absent in others as `SCHEMA_GAP`.

The missing field causes a silent bug that only appears when the happy path fails — which is exactly when reliability matters most. Unit tests typically only cover the happy path.

**Example:** `response-parser.js` returns `{ id, name, slug, price, stockQuantity, ... }` but `keyword-fallback.js` returns `{ id, name, slug, price, ... }` — missing `stockQuantity`. Frontend code accessing `product.stockQuantity` gets `undefined` only when LLM is down.

### Check 4 — Documentation Staleness

Search explicitly for stale references — do not rely on having updated documentation during implementation:

```bash
grep -r "OldConcept" --include="*.md"         # CLAUDE.md, README
grep -r "OldConcept" --include="*.[ext]"      # JSDoc in source files
```

Specific patterns to check:
- `@param` tags referencing a parameter that was removed → `STALE_DOC`
- Function signatures shown in CLAUDE.md that no longer match actual code → `STALE_DOC`
- Comments saying "calls X()" where X was renamed → `STALE_DOC`
- File-level JSDoc listing old export names → `STALE_DOC`

**JSDoc block integrity:** When updating JSDoc, read the full surrounding context as a unit — do not edit just one `@param` line in isolation. Adjacent methods' JSDoc blocks can appear interleaved (one method's closing `*/` immediately followed by another method's `/**`). A partial read will miss this and editing the wrong block corrupts both.

### Check 5 — Structural Misplacement

Not all misplaced code is dead code. A function can be correctly used and referenced yet placed at the wrong structural level:

- **Module-level function** that operates exclusively on a class's data and is only called from within that class → should be a `static` method on the class. It passes all dead-code checks but has wrong structural ownership.

For each module-level function in the changed files: check whether all its callers are within a single class. If yes, flag as `MISPLACED_FUNCTION` and propose converting to a class static method.

**Example:** `buildEmbeddingText(product)` defined at module level in `vector-store.js` but only called by `HybridVectorStore.upsertProduct()` → moved to `static buildEmbeddingText(product)` inside the class.

### Check 6 — Unreachable Code

For each file changed, look for:
- Code after an unconditional `return` / `throw` / `continue` / `break` in the same branch → `UNREACHABLE`
- A condition that is structurally always true or always false given the current code
- `try/catch` blocks where the guarded code cannot actually throw the caught exception type
- `continue` statements that appear reachable but are actually dead because a prior `return` already exits the function in all cases

## Output Format

For finding type definitions, see the "Finding Type Reference" table below.

```
[FILE:LINE] TYPE | Description | Confidence (HIGH/MED/LOW)
```

Types: `DEAD_IMPORT` · `DEAD_VAR` · `DEAD_PARAM` · `DEAD_CASCADE` · `YAGNI_PARAM` · `SCHEMA_GAP` · `MISPLACED_FUNCTION` · `STALE_DOC` · `UNREACHABLE`

Report findings at all confidence levels — HIGH/MED directly, LOW prefixed with `(needs-verify)` — and let the user decide. (This is a single-pass finder feeding HUMAN GATE 3 with no automated verifier downstream, so surface everything rather than self-filtering — per the single-pass exception in `evidence-based-findings.md`.)

End with:
```
Confirmed issues: N
Needs verification: N
Clean: YES / NO
```

**★ HUMAN GATE 3:** Present the above summary to the user before signing off. Include: (1) what was in the original plan and is now complete, (2) what this audit found that was NOT in the plan, (3) current test count vs BASELINE. Wait for the user to decide whether any findings require additional action before the workflow closes.

## Finding Type Reference

| Type | Description | Example |
|------|------------|---------|
| `DEAD_IMPORT` | Imported symbol with no usage in file body | `const { X } = require(...)` but X never called |
| `DEAD_VAR` | Declared variable never read after assignment | `const x = compute(); // x never used` |
| `DEAD_PARAM` | Function parameter never used inside function | `function f(a, b) { return a; } // b unused` |
| `DEAD_CASCADE` | Param/var dead because downstream consumer removed | `A passes X to B; B's param removed → X dead in A` |
| `YAGNI_PARAM` | Param documented as "not used yet, kept for future" | YAGNI violation — remove and trace cascade |
| `SCHEMA_GAP` | Field present in some execution paths but not others | LLM path returns `stockQuantity`, fallback doesn't |
| `MISPLACED_FUNCTION` | Module-level function belonging as class static method | Function only called from within one class |
| `STALE_DOC` | CLAUDE.md or JSDoc referencing old/removed symbol | `@param context` for a removed parameter |
| `UNREACHABLE` | Code after unconditional return/throw | `return x; doSomething(); // never reached` |

## Common False Positives (All Check Types)

| Pattern | Why it's NOT dead |
|---------|-------------------|
| Symbol in JSDoc `@param` comment | Documentation, not dead code |
| Symbol in test `describe()`/`it()` string | Behavior description |
| Symbol used only in test files | Tests are callers — alive |
| Symbol in log/error message string | Runtime usage — alive |
| Same name in different file/scope | Different entity entirely |
| Symbol accessed via `obj[varName]` | Dynamic reference invisible to grep |
