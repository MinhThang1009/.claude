---
name: logic-audit
description: This skill should be used when the user asks to "audit logic bugs", "read all source files and find bugs", "gate tầng 0", "logic check a module", "verify module correctness", "find business logic bugs", "audit this module before drawing diagrams", or says "read every line of code". Works on any module, language, or framework — discovers tests, docs, and project structure at runtime.
version: 0.1.0
argument-hint: [module-path-or-directory]
allowed-tools: Read Grep Glob Bash Edit Write
---

# Logic Audit Skill

Perform a systematic, line-by-line logic audit of the target module. Find real bugs — not style issues, not theoretical edge cases — bugs that cause wrong behavior, data corruption, race conditions, or incorrect business rule enforcement.

**This skill is language-agnostic and framework-agnostic.** Adapt to whatever stack is in the target directory.

## Phase 1 — Discover

1. List every source file in the target (exclude test files, generated files, lock files). Print the list so the user sees scope.
2. Find the project's primary docs (CLAUDE.md, README.md, or equivalent) and read the section describing what this module does and what business rules it enforces.
3. Run the existing tests for this module to establish a **green baseline**. If tests are already failing before any changes, stop and report — don't proceed on a broken baseline.

## Phase 2 — Read Everything (No Gaps)

Read **every single line** of every source file from Phase 1. Not excerpts. Not grep summaries. Full files.

Apply these rules while reading:

- **Distrust comments.** Comments describe intent. Code describes reality. When a comment says "this never happens" or "X is always Y" — verify it in the actual code logic.
- **Distrust module documentation.** CLAUDE.md and README descriptions may be stale. The source is the source of truth.
- **Read the corresponding test file** for each source file to understand what's already asserted and what's assumed but untested.
- **Maintain a running issue list** as you read. Do not fix yet — complete the full read first.

For large modules (>10 files), read the most critical files first: service/business logic layer, then repository/data layer, then controllers/routes last.

## Phase 3 — Analyze Findings

For each issue on the running list, determine:

1. **Is it a real logic bug?** Would it cause incorrect behavior, data corruption, security vulnerability, race condition, or meaningful UX confusion in production?
2. **Is it testable?** Can it be triggered through the public API or an exported function?
3. **What is the minimal fix?** State the exact change before touching any file.

Classify severity:
- 🔴 HIGH — data integrity, security, incorrect business rule, race condition
- 🟡 MEDIUM — UX confusion, inconsistency with how similar code elsewhere works, missing validation that the module claims to enforce
- 🔵 INFO — dead code, misplaced comment, minor inconsistency

**Present findings to the user and wait for confirmation before fixing anything.**

## Phase 4 — Fix (One Bug Per Commit)

For each confirmed bug, in order of severity:

1. Apply the **minimal surgical fix** — change only what fixes the bug. Do not refactor adjacent code.
2. Write or update tests that:
   - Would have caught the bug before the fix
   - Assert the correct behavior after the fix
3. Run the test suite. Fix any test failures caused by the fix (updated assertions are expected; broken unrelated tests are not).
4. Run the full test suite to confirm no regressions.
5. Run the project's linter if one exists.
6. **Spawn an independent verification agent**: give it only the changed files, no description of what was fixed or why. Ask it "does this code behave correctly? find any issues." Compare its findings against the fix.
7. Commit with a clear message: bug name, why it was wrong, what changed.

Repeat for each confirmed bug. **One bug = one commit.**

## Phase 5 — Update Stale Documentation

After all bug fixes are committed:

1. Search for documentation files that reference the changed behavior: module CLAUDE.md or README, parent-level CLAUDE.md, architecture docs, test-count tables.
2. For each doc found: check whether descriptions of the changed behavior are now factually wrong.
3. Update only what is factually stale. Do not rewrite sections that are still accurate.
4. If the project maintains test-count metrics anywhere, update them.
5. Commit doc updates separately from code fixes.

## Phase 6 — Summary

Print a final summary:
- Bugs found and fixed (with short description and commit hash)
- Files read (count)
- Docs updated
- Items deferred (known issues not fixed, with reason)

---

## Ground Rules (Apply Throughout)

- **Read code, not descriptions** — when behavior is unclear, read the implementation.
- **No assumption of correctness** — "it looks right" is not verification. Run the test.
- **No shortcuts on reading** — a 500-line file requires reading 500 lines.
- **Verify before and after every fix** — run tests before touching anything, run again after.
- **One bug = one commit** — resist batching. Each commit must be independently revertable.
- **Document what you don't fix** — if something is wrong but out of scope or by design, say so explicitly.

## Additional Resources

For detailed patterns on reading code systematically and verifying findings:
- **`references/reading-patterns.md`** — how to read different code patterns (async, transactions, guard clauses, caching)
- **`references/verification-techniques.md`** — independent verification, test strategies, doc discovery
