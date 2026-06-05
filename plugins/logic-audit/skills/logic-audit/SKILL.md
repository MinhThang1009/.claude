---
name: logic-audit
description: This skill should be used when the user asks to "audit logic bugs", "read all source files and find bugs", "gate tầng 0", "logic check a module", "verify module correctness", "find business logic bugs", "audit this module before drawing diagrams", or says "read every line of code". Works on any module, language, or framework — discovers tests, docs, and project structure at runtime.
version: 0.4.5
argument-hint: <module-path-or-directory>
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write]
---

# Logic Audit Skill

Perform a systematic, line-by-line logic audit of the target module. The goal is to find **real bugs** — not style issues, not theoretical edge cases — bugs that cause wrong behavior, data corruption, race conditions, or incorrect business rule enforcement in production.

**Language-agnostic and framework-agnostic.** Adapt discovery, test commands, and doc search to whatever stack exists in the target directory.

---

## Phase 1 — Discover

1. List every source file in the target directory (exclude test files, generated files, build artifacts, lock files). Print the full list so the user sees the audit scope before proceeding.

2. Find the project's primary documentation (CLAUDE.md, README.md, architecture docs, or equivalent). Read the section describing what this module does and what business rules it must enforce. This establishes the expected behavior to audit against.

3. **Create gate state file** — use the Write tool to create `.claude/logic-audit-state.json` at the project root:
   ```json
   {"phase4_gate": false, "phase5_gate": false}
   ```
   The Stop hook reads this file and blocks if gates are incomplete. Delete the file at the end of Phase 6.

4. Identify and run the existing test suite for this module to establish a **green baseline**:
   - Find the test runner and config (jest.config, pytest.ini, go test, etc.)
   - Run only the tests relevant to this module if possible
   - If **no test files exist** → note this explicitly. Proceed with code-only analysis. All fixes will be unverified by automated tests — flag this prominently in the Phase 6 summary.
   - If tests are **already failing before any changes** → stop, report the failures, and ask the user whether to continue with code-only analysis
   - If tests **cannot be run** (missing environment, requires external services, CI-only) → note this explicitly and proceed with code-only analysis. Flag at the end that fixes should be verified in the appropriate environment.

---

## Phase 2 — Read Everything (No Gaps)

Read **every single line** of every source file listed in Phase 1. Not excerpts. Not grep summaries. Not subagent delegation. Full files, read directly.

**Critical rule: Do NOT use subagents or Explore agents to do the reading for you.** Subagents read code from a fresh context without the accumulated understanding built across files — they miss cross-file invariants and subtle inconsistencies. Read every file yourself.

Apply these rules while reading:

- **Distrust comments.** Comments describe intent, not reality. When a comment says "this never happens" or "X is always guaranteed" — verify it by tracing the actual code logic. The comment was likely added to justify a guard that CAN fail.
- **Distrust module documentation.** CLAUDE.md and README descriptions can be stale. The source code is the source of truth.
- **Read the corresponding test file** for each source file — this is mandatory, not optional. Understand what is already asserted, what is assumed-but-untested, and what scenarios have no test at all. If you skip test files, you miss context about which behaviors are considered correct by design, and you may incorrectly classify intentional behavior as bugs (or miss bugs that tests expose via their mocks).
- **Maintain a running issue list** as you read. Do not stop to fix. Complete the full read of all files first — later files often reveal whether an earlier suspicious pattern is actually a bug or an intentional invariant. **After finishing each layer (e.g., all service files), print the current issue list so the user can see progress.** Do not disappear silently for 10 files.

**Phase 2 self-check before proceeding to Phase 3:** For each source file, state:
- Which test file(s) cover it
- What the tests assert about each public method
- What each test does NOT assert (gaps that could hide bugs)

Simply listing file names is not sufficient — you must demonstrate you read the test content. If you cannot answer "what does TC-X assert about method Y?" for the key methods, you have not completed Phase 2.

**Reading order for large modules (>10 files)** — adapt to the stack:
- **Backend:** business logic / service layer → data access / repository → controllers / routes / handlers
- **Frontend:** state management / stores / hooks → components (logic-heavy) → pages / views (rendering)
- **CLI / scripts:** core algorithm / business logic → I/O and error handling → entry point
- **Any stack:** start where the most consequential decisions happen, end at the outermost layer

**What to look for** — consult `references/reading-patterns.md` while reading each file. Key patterns: race conditions, missing transactions, aggregate-vs-per-item checks, null/undefined boundary failures, guard clauses that can be bypassed, dead code, type coercion bugs, off-by-one errors, and business rules enforced in one path but missing in another.

---

## Phase 3 — Analyze Findings

After reading all files, review the running issue list. For each item, determine:

1. **Is it a real logic bug?** Would it cause incorrect behavior, data corruption, a security vulnerability, a race condition, or meaningful user-facing confusion in production? If the answer is "maybe, theoretically" — it is not a bug yet.
2. **Is it reachable?** Can the buggy branch actually be triggered from a production code path? Trace the call chain.
3. **Is it already tested?** Grep test files for the condition. If an existing test exercises the path and it passes, revisit the analysis — maybe the "bug" is intentional behavior.
   - **Caveat — mocked tests:** If tests mock all external dependencies (DB models, ORM, HTTP clients), integration-layer bugs (wrong column names, wrong association aliases, wrong API call signatures) will appear tested but aren't actually exercised. When the mock accepts any input and always resolves, the test proves nothing about the real behavior. Tag these findings `[UNIT-TEST-BLIND]` — the finding is real, but the unit test suite cannot confirm or deny it.

4. **Is it provable from source code alone?** Can the bug be demonstrated by tracing the project's own source, without relying on assumptions about how a third-party framework or library behaves internally?
   - If **yes** → proceed with classification.
   - If **no** → verify the library behavior first: grep its source, check official docs, or run a minimal Bash script (`node -e "..."`) to confirm. Do not classify as HIGH without this verification. If verification is not possible in this environment, tag the finding `[NEEDS-RUNTIME-VERIFY]` and cap severity at MEDIUM.

5. **What is the minimal fix?** Before touching any file, run a pre-flight check:
   - Grep test files for assertions on the affected symbol, function, or variable.
   - Determine whether existing tests assert **wrong behavior** (test needs updating) or **correct intent** (the code documents something meaningful even if it has no runtime effect — do not remove it).
   - If more than 3 test files assert the current behavior and the severity is INFO or MEDIUM: defer. Fix cost exceeds benefit.
   - Only after this check: state the exact change, including which test files need updating.

Classify each confirmed issue:
- 🔴 **HIGH** — data integrity, security, race condition, incorrect business rule that affects money/stock/orders
- 🟡 **MEDIUM** — UX confusion, validation missing in one code path but present in equivalent paths, partial cleanup on failure
- 🔵 **INFO** — dead code, misplaced/stale comment, minor inconsistency with no user-visible impact

**Present the classified findings to the user and wait for confirmation before touching any file.** Use `examples/finding-report-template.md` as the format template — each finding must include: file + line, concrete reproduction steps, minimal fix description, and test name. The user decides which severity levels to fix, and in what order.

---

## Phase 4 — Fix (One Bug Per Commit)

For each confirmed bug, in severity order (HIGH first):

1. Apply the **minimal surgical fix** — change only what is necessary to fix this specific bug. Do not refactor adjacent code, rename variables, or improve style in the same commit.

2. Write or update tests that:
   - Would have **failed** with the old code (reproduces the bug)
   - **Pass** with the fix (verifies the correct behavior)
   - Assert the outcome, not the implementation detail
   - Are named to describe the scenario, not the code path

3. Run the test suite for this module. Expected: previously passing tests still pass, the new/updated test passes. If unrelated tests break:
   - **Investigate first** — the fix may have incorrect scope
   - **If the broken test was asserting the old wrong behavior** → update the test to assert the correct behavior, and document why in the commit
   - **If the broken test is unrelated to the fix** → the fix has too wide a scope; narrow it before continuing

4. Run the **full** project test suite to confirm no regressions.

5. Run the project's linter/formatter if one exists and is configured.

6. **Spawn an independent verification agent.** Give it only the list of changed files — no description of what was fixed or why. Use the exact prompt template in `references/verification-techniques.md` (Independent Verification Agent Prompt section). The agent must not know your intent; that context biases it toward confirming rather than finding remaining issues. Compare its findings against your fix.
   - **If the agent surfaces new findings** (unrelated to the fix): verify each one yourself with grep/Read before reporting to the user. Do NOT relay subagent output directly — agents can hallucinate line numbers or misread context. Apply the same provability standard as Phase 3 step 4. Before queuing any of these findings for fixing, run the Phase 3 step 5 pre-flight check (test assertion grep + fix cost assessment) on each one — do not skip directly to Phase 4 step 1.

7. Commit with a message that answers three questions: what was wrong, why it was wrong, what changed. Use the commit format in `references/verification-techniques.md`.

**Repeat for each bug. One bug = one commit. Do not batch multiple bugs into a single commit.**

### Phase 4 Exit Gate

Before proceeding to Phase 5, confirm every item below. Do not skip or defer silently — if an item cannot be done, state the reason explicitly.

- [ ] Test written or updated for each fix — would have FAILED before the fix, passes after (Phase 4 step 2)
- [ ] Independent verification agent run for every fix (Phase 4 step 6)
- [ ] Full project test suite passes (not just module tests)
- [ ] No fix was batched — each bug has its own commit
- [ ] Phase 5 (stale documentation) is next — do not jump to Phase 6

**After completing all items:** update `.claude/logic-audit-state.json` → `{"phase4_gate": true, "phase5_gate": false}`

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

### Phase 5 Exit Gate

- [ ] Every doc file that referenced changed behavior has been checked (not just the obvious ones — use grep by function name)
- [ ] Test-count metrics in documentation updated if the project tracks them
- [ ] If no doc updates were needed, state explicitly why (not silence)

**After completing all items:** update `.claude/logic-audit-state.json` → `{"phase4_gate": true, "phase5_gate": true}`

---

## Phase 6 — Summary

Print a final summary:
- Bugs found and fixed, with short description and commit hash for each
- Files read (total count)
- Documentation files updated
- Items deferred: issues found but not fixed, with explicit reason for each (out of scope, by design, requires environment to verify, user decision to defer)

**After printing the summary:** delete `.claude/logic-audit-state.json` (cleanup — allows the Stop hook to pass).

---

## Ground Rules (Apply Throughout)

- **Read code, not descriptions.** When behavior is unclear, read the implementation — not the CLAUDE.md, not the README, not the test names.
- **Read yourself — no subagent delegation.** Delegating file reading to subagents produces shallow, context-free analysis. Every file must be read directly in this session.
- **No assumption of correctness.** "It looks right" is not verification. If you think it's correct, run the test that proves it.
- **No shortcuts on reading.** A 600-line file requires reading 600 lines. There is no representative sample.
- **Verify before and after every fix.** Run the test suite before touching the code (baseline), and again after (regression check).
- **One bug = one commit.** Each commit must be independently revertable. If you discover two bugs, fix them in two separate commits.
- **Document what you don't fix.** If something is wrong but out of scope, confirmed by design, or requires an environment you don't have — say so explicitly in the Phase 6 summary. Silence is not acceptable.
- **For very large modules (50+ source files):** Do not attempt to finish in one session if the context window cannot hold all files. Instead: (1) audit the highest-priority layer (service/business logic) in this session, commit findings and fixes, (2) report clearly what was covered and what remains, (3) continue in a fresh session. Partial coverage with honest scope is better than shallow coverage of everything.

---

## Additional Resources

Load these references when needed — they contain detailed patterns and techniques that are too long to include here:

- **`references/reading-patterns.md`** — Concrete patterns to look for while reading: race conditions, transaction boundaries, guard clause bypasses, null/undefined failures, type coercion, off-by-one, business rule coverage, dead code
- **`references/verification-techniques.md`** — False-positive filtering, independent verification agent prompt, test strategy, doc discovery, severity classification, commit message format

Working examples for reference:

- **`examples/finding-report-template.md`** — Template for presenting audit findings to the user: file + line, reproduction steps, minimal fix, test name
- **`examples/independent-verification-exchange.md`** — How to run Phase 4 step 6 independent verification and interpret the results, including how to handle new findings the agent surfaces
