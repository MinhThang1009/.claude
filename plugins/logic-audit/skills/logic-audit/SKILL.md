---
name: logic-audit
description: This skill should be used when the user asks to "audit logic bugs", "read all source files and find bugs", "gate tầng 0", "logic check a module", "verify module correctness", "find business logic bugs", "audit this module before drawing diagrams", or says "read every line of code". Works on any module, language, or framework — discovers tests, docs, and project structure at runtime.
version: 0.2.0
argument-hint: [module-path-or-directory]
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write]
---

# Logic Audit Skill

Perform a systematic, line-by-line logic audit of the target module. The goal is to find **real bugs** — not style issues, not theoretical edge cases — bugs that cause wrong behavior, data corruption, race conditions, or incorrect business rule enforcement in production.

**Language-agnostic and framework-agnostic.** Adapt discovery, test commands, and doc search to whatever stack exists in the target directory.

---

## Phase 1 — Discover

1. List every source file in the target directory (exclude test files, generated files, build artifacts, lock files). Print the full list so the user sees the audit scope before proceeding.

2. Find the project's primary documentation (CLAUDE.md, README.md, architecture docs, or equivalent). Read the section describing what this module does and what business rules it must enforce. This establishes the expected behavior to audit against.

3. Identify and run the existing test suite for this module to establish a **green baseline**:
   - Find the test runner and config (jest.config, pytest.ini, go test, etc.)
   - Run only the tests relevant to this module if possible
   - If tests are **already failing before any changes** → stop, report the failures, and ask the user whether to continue with code-only analysis
   - If tests **cannot be run** (missing environment, requires external services, CI-only) → note this explicitly and proceed with code-only analysis. Flag at the end that fixes should be verified in the appropriate environment.

---

## Phase 2 — Read Everything (No Gaps)

Read **every single line** of every source file listed in Phase 1. Not excerpts. Not grep summaries. Not subagent delegation. Full files, read directly.

**Critical rule: Do NOT use subagents or Explore agents to do the reading for you.** Subagents read code from a fresh context without the accumulated understanding built across files — they miss cross-file invariants and subtle inconsistencies. Read every file yourself.

Apply these rules while reading:

- **Distrust comments.** Comments describe intent, not reality. When a comment says "this never happens" or "X is always guaranteed" — verify it by tracing the actual code logic. The comment was likely added to justify a guard that CAN fail.
- **Distrust module documentation.** CLAUDE.md and README descriptions can be stale. The source code is the source of truth.
- **Read the corresponding test file** for each source file. Understand what is already asserted, what is assumed-but-untested, and what scenarios have no test at all.
- **Maintain a running issue list** as you read. Do not stop to fix. Complete the full read of all files first — later files often reveal whether an earlier suspicious pattern is actually a bug or an intentional invariant.

**Reading order for large modules (>10 files):**
1. Business logic / service layer first (highest bug density)
2. Data access / repository layer (transaction and integrity bugs)
3. Controllers / routes / handlers last (validation gaps)

**What to look for** — consult `references/reading-patterns.md` while reading each file. Key patterns: race conditions, missing transactions, aggregate-vs-per-item checks, null/undefined boundary failures, guard clauses that can be bypassed, dead code, type coercion bugs, off-by-one errors, and business rules enforced in one path but missing in another.

---

## Phase 3 — Analyze Findings

After reading all files, review the running issue list. For each item, determine:

1. **Is it a real logic bug?** Would it cause incorrect behavior, data corruption, a security vulnerability, a race condition, or meaningful user-facing confusion in production? If the answer is "maybe, theoretically" — it is not a bug yet.
2. **Is it reachable?** Can the buggy branch actually be triggered from a production code path? Trace the call chain.
3. **Is it already tested?** Grep test files for the condition. If an existing test exercises the path and it passes, revisit the analysis — maybe the "bug" is intentional behavior.
4. **What is the minimal fix?** State the exact change before touching any file.

Classify each confirmed issue:
- 🔴 **HIGH** — data integrity, security, race condition, incorrect business rule that affects money/stock/orders
- 🟡 **MEDIUM** — UX confusion, validation missing in one code path but present in equivalent paths, partial cleanup on failure
- 🔵 **INFO** — dead code, misplaced/stale comment, minor inconsistency with no user-visible impact

**Present the classified findings to the user and wait for confirmation before touching any file.** The user decides which severity levels to fix, and in what order.

---

## Phase 4 — Fix (One Bug Per Commit)

For each confirmed bug, in severity order (HIGH first):

1. Apply the **minimal surgical fix** — change only what is necessary to fix this specific bug. Do not refactor adjacent code, rename variables, or improve style in the same commit.

2. Write or update tests that:
   - Would have **failed** with the old code (reproduces the bug)
   - **Pass** with the fix (verifies the correct behavior)
   - Assert the outcome, not the implementation detail
   - Are named to describe the scenario, not the code path

3. Run the test suite for this module. Expected: previously passing tests still pass, the new/updated test passes. If unrelated tests break, investigate before continuing — a fix that breaks other tests may have incorrect scope.

4. Run the **full** project test suite to confirm no regressions.

5. Run the project's linter/formatter if one exists and is configured.

6. **Spawn an independent verification agent.** Give it only the list of changed files — no description of what was fixed or why. Use the exact prompt template in `references/verification-techniques.md` (Independent Verification Agent Prompt section). The agent must not know your intent; that context biases it toward confirming rather than finding remaining issues. Compare its findings against your fix.

7. Commit with a message that answers three questions: what was wrong, why it was wrong, what changed. Use the commit format in `references/verification-techniques.md`.

**Repeat for each bug. One bug = one commit. Do not batch multiple bugs into a single commit.**

---

## Phase 5 — Update Stale Documentation

After all bug fixes are committed:

1. Search for documentation files that reference the changed behavior. Use the doc-discovery patterns in `references/verification-techniques.md` (Discovering Stale Documentation section): search by function name, by old behavior keywords, and by checking module-level docs in the same and parent directories.

2. For each doc file found: check whether descriptions of the changed behavior are now factually wrong.
   - Update descriptions that state the old incorrect behavior
   - Update business rule descriptions that no longer match the code
   - Do **not** rewrite accurate sections just to refresh them

3. If the project maintains test-count metrics or coverage summaries in documentation, update those numbers.

4. Commit doc updates **separately** from code fixes with a message like `docs(<module>): update after <bug-name> fix`.

---

## Phase 6 — Summary

Print a final summary:
- Bugs found and fixed, with short description and commit hash for each
- Files read (total count)
- Documentation files updated
- Items deferred: issues found but not fixed, with explicit reason for each (out of scope, by design, requires environment to verify, user decision to defer)

---

## Ground Rules (Apply Throughout)

- **Read code, not descriptions.** When behavior is unclear, read the implementation — not the CLAUDE.md, not the README, not the test names.
- **Read yourself — no subagent delegation.** Delegating file reading to subagents produces shallow, context-free analysis. Every file must be read directly in this session.
- **No assumption of correctness.** "It looks right" is not verification. If you think it's correct, run the test that proves it.
- **No shortcuts on reading.** A 600-line file requires reading 600 lines. There is no representative sample.
- **Verify before and after every fix.** Run the test suite before touching the code (baseline), and again after (regression check).
- **One bug = one commit.** Each commit must be independently revertable. If you discover two bugs, fix them in two separate commits.
- **Document what you don't fix.** If something is wrong but out of scope, confirmed by design, or requires an environment you don't have — say so explicitly in the Phase 6 summary. Silence is not acceptable.

---

## Additional Resources

Load these references when needed — they contain detailed patterns and techniques that are too long to include here:

- **`references/reading-patterns.md`** — Concrete patterns to look for while reading: race conditions, transaction boundaries, guard clause bypasses, null/undefined failures, type coercion, off-by-one, business rule coverage, dead code
- **`references/verification-techniques.md`** — False-positive filtering, independent verification agent prompt, test strategy, doc discovery, severity classification, commit message format
