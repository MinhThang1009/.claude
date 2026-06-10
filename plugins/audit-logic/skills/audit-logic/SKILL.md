---
name: audit-logic
description: This skill should be used when the user asks to "audit logic bugs", "read all source files and find bugs", "gate tầng 0", "logic check a module", "verify module correctness", "find business logic bugs", "audit this module before drawing diagrams", or says "read every line of code". Works on any module, language, or framework — discovers tests, docs, and project structure at runtime. Audit only — when the goal is to also draw the diagrams, use /verify-then-draw instead.
version: 1.0.1
argument-hint: <module-path-or-directory>
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write, Task, Skill, WebFetch, WebSearch]
---

# Audit Logic Skill

Perform a systematic, line-by-line logic audit of the target module. The target is the path passed as the skill argument (`<module-path-or-directory>`); if no argument was given, ask the user for the target before starting. The goal is to find **real bugs** — not style issues, not theoretical edge cases — bugs that cause wrong behavior, data corruption, race conditions, or incorrect business rule enforcement in production.

**Language-agnostic and framework-agnostic.** Adapt discovery, test commands, and doc search to whatever stack exists in the target directory.

---

## Phase 1 — Discover

1. List every source file in the target directory (exclude test files, generated files, build artifacts, lock files). **If the target path does not exist, is a single file rather than a directory (and the user did not explicitly target one file), or zero source files remain after exclusions → stop and ask the user before doing anything else (do NOT create the gate state file).** Print the full list — and note alongside it which test files will also be read in Phase 2 — so the user sees the true audit scope before proceeding.

2. Find the project's primary documentation (CLAUDE.md, README.md, architecture docs, or equivalent). Read the section describing what this module does and what business rules it must enforce. This establishes the expected behavior to audit against — print a 1–3 line summary of those rules (or "no module docs found") so the user sees the baseline the audit will check the code against.

3. Identify and run the existing test suite for this module to establish a **green baseline**:
   - Find the test runner and config (jest.config, pytest.ini, go test, etc.)
   - Run only the tests relevant to this module if possible
   - If **no test files exist** → note this explicitly. Proceed with code-only analysis. All fixes will be unverified by automated tests — flag this prominently in the Phase 7 summary.
   - If tests are **already failing before any changes** → stop, report the failures, and ask the user whether to continue with code-only analysis
   - If tests **cannot be run** (missing environment, requires external services, CI-only) → note this explicitly and proceed with code-only analysis. Flag at the end that fixes should be verified in the appropriate environment.

4. **Create gate state file** — only after the baseline outcome is settled (green baseline, no-tests noted, or the user approved continuing despite failures). **If `.claude/audit-logic-state.json` ALREADY exists, do NOT overwrite it** — it is an orphan from an aborted audit, owned by a concurrent session of the same project that is mid-audit, or left over from YOUR OWN audit interrupted earlier (session crash, `/clear`, compact). Stop and ask the user; only delete-and-recreate after they confirm no other session owns it. For an interrupted own audit there is no in-skill resume: fixes already committed survive in git, but the running issue list lived in the lost context — delete the file and restart at Phase 1. Otherwise, use the Write tool to create `.claude/audit-logic-state.json` at the **project root** (the directory Claude Code was started in — same as `${CLAUDE_PROJECT_DIR}`, which is where the Stop hook reads it; not the cwd if they differ):
   ```json
   {"findings_confirmed": false, "phase4_gate": false, "phase5_gate": false, "phase6_gate": false, "phase7_gate": false}
   ```
   The Stop hook (bundled with this plugin — `hooks/hooks.json` → `audit-logic-gate.sh` → `audit-logic-gate.py`) reads this file and blocks if gates are incomplete. Creating it after step 3 keeps the "stop and ask the user" path for a red baseline unblocked. Delete the file after Phase 7 retrospective completes — or immediately if the user aborts the audit at any point (see Ground Rules).

   **If the Write fails or is denied** (common in headless `-p` runs, where writes to `.claude/` are auto-denied): state explicitly that the Stop gate hook is NOT armed for this run, and track the gates in the audit report instead — at each Exit Gate, print the gate name and its would-be value in the report rather than editing the state file. All other gate rules (order, ownership of `findings_confirmed`, user confirmation) still apply unchanged.

---

## Phase 2 — Read Everything (No Gaps)

**Before reading the first file:** read `references/reading-patterns.md` in full. Then print one line:
> "Reading patterns loaded: [list the 5 categories most relevant to this module's stack and domain]."

Use that list as a checklist while reading each source file — it prevents systematic blind spots (e.g., skipping encoding/type-coercion checks on a payment module).

Read **every single line** of every source file listed in Phase 1. Not excerpts. Not grep summaries. Not subagent delegation. Full files, read directly.

**Critical rule: Do NOT use subagents or Explore agents to do the reading for you.** Subagents read code from a fresh context without the accumulated understanding built across files — they miss cross-file invariants and subtle inconsistencies. Read every file yourself.

Apply these rules while reading:

- **Distrust comments.** Comments describe intent, not reality. When a comment says "this never happens" or "X is always guaranteed" — verify it by tracing the actual code logic. The comment was likely added to justify a guard that CAN fail.
- **Distrust module documentation.** CLAUDE.md and README descriptions can be stale. The source code is the source of truth.
- **Read the corresponding test file** for each source file — this is mandatory, not optional. Understand what is already asserted, what is assumed-but-untested, and what scenarios have no test at all. If you skip test files, you miss context about which behaviors are considered correct by design, and you may incorrectly classify intentional behavior as bugs (or miss bugs that tests expose via their mocks).
- **Also read higher-level test files** for the module — even if they cannot be run (require DB, external services). These encode business rules at levels that unit tests with mocks cannot verify:
  - Integration tests (`src/__integration__/` or equivalent) — real DB behavior, constraint enforcement
  - API HTTP tests (`src/__api__/` or equivalent) — full request-response business rule assertions
  - Property-based / invariant test files (e.g. `invariants.*.md`, `*.property.test.js`) — high-level correctness contracts the module must maintain
  Reading these is faster than running them, and they often directly name the bugs unit tests miss.
- **Maintain a running issue list** as you read. Do not stop to fix. Complete the full read of all files first — later files often reveal whether an earlier suspicious pattern is actually a bug or an intentional invariant. **After finishing each layer (e.g., all service files), print the current issue list so the user can see progress.** For modules of ≤10 files (where the layered reading order below does not apply), print it at least once after all source files are read, before moving to Phase 3. Do not disappear silently for 10 files.

**Reading order for large modules (>10 files)** — adapt to the stack:
- **Backend:** business logic / service layer → data access / repository → controllers / routes / handlers
- **Frontend:** state management / stores / hooks → components (logic-heavy) → pages / views (rendering)
- **CLI / scripts:** core algorithm / business logic → I/O and error handling → entry point
- **Any stack:** start where the most consequential decisions happen, end at the outermost layer

**What to look for** — consult `references/reading-patterns.md` while reading each file. Key patterns: race conditions, missing transactions, aggregate-vs-per-item checks, null/undefined boundary failures, guard clauses that can be bypassed, dead code, type coercion bugs, off-by-one errors, and business rules enforced in one path but missing in another.

**Phase 2 self-check before proceeding to Phase 3:** Print a brief coverage summary (visible to the user — not a silent mental check) confirming all of the following:
- For each source file: which unit test file(s) cover it, what they assert about each public method, and what they do NOT assert (gaps).
- Which higher-level test files (integration, API HTTP, invariant) were read and what business rules they assert that unit tests cannot verify.
- For each public function/method: which **production** code path calls it — **print this as a table, one row per public function**: `| function | production caller(s) | unit test(s) | gaps |`. A row whose caller column is empty — only tests call it, or a comment references a flow that does not exist in the codebase — goes on the running issue list as a dead-code candidate (INFO) automatically; do not dismiss it by analyzing the function's internal semantics. Test coverage of a function is NOT evidence it is alive. (Prose summaries are not acceptable for this item — the table format is mandatory; a missing caller cell must be visibly empty.)

Simply listing file names is not sufficient — you must demonstrate you read the content. If you cannot answer "what does TC-X assert about method Y?" for key methods, or "what business rule does the integration test for this module verify?", you have not completed Phase 2.

---

## Phase 3 — Analyze Findings

After reading all files, review the running issue list. For each item, determine:

1. **Is it a real logic bug?** Would it cause incorrect behavior, data corruption, a security vulnerability, a race condition, or meaningful user-facing confusion in production? If the answer is "maybe, theoretically" — it is not a bug yet.
2. **Is it reachable?** Can the buggy branch actually be triggered from a production code path? Trace the call chain.
3. **Is it already tested?** Grep test files for the condition. If an existing test exercises the path and it passes, revisit the analysis — maybe the "bug" is intentional behavior.
   - **Caveat — mocked tests:** If tests mock all external dependencies (DB models, ORM, HTTP clients), integration-layer bugs (wrong column names, wrong association aliases, wrong API call signatures) will appear tested but aren't actually exercised. When the mock accepts any input and always resolves, the test proves nothing about the real behavior. Before tagging as `[UNIT-TEST-BLIND]`, check if the integration or API tests read in Phase 2 already cover this behavior — if they do, the finding is tested at integration level and should not be tagged. If they do not, tag `[UNIT-TEST-BLIND]` — the finding is real, but the unit test suite cannot confirm or deny it.

4. **Is it provable from source code alone?** Can the bug be demonstrated by tracing the project's own source, without relying on assumptions about how a third-party framework or library behaves internally?
   - If **yes** → proceed with classification.
   - If **no** → verify the library behavior first: grep its source, check official docs (WebFetch/WebSearch), or run a minimal script in the project's language (`node -e "..."`, `python -c "..."`, `go run`, etc.) to confirm. Do not classify as HIGH without this verification. If verification is not possible in this environment, tag the finding `[NEEDS-RUNTIME-VERIFY]` and cap severity at MEDIUM. Unless the user explicitly approves fixing it anyway, a `[NEEDS-RUNTIME-VERIFY]` finding defaults to deferred — it must appear in the Phase 7 deferred list with reason "requires runtime verification".

5. **What is the minimal fix?** Before touching any file, run a pre-flight check:
   - Grep test files for assertions on the affected symbol, function, or variable.
   - Determine whether existing tests assert **wrong behavior** (test needs updating) or **correct intent** (the code documents something meaningful even if it has no runtime effect — do not remove it).
   - If more than 3 test files assert the current behavior and the severity is INFO or MEDIUM: defer. Fix cost exceeds benefit.
   - If severity is HIGH: do NOT defer based on test count — fix it, update the tests, and document why each test change was needed. High test count means the fix was impactful, not that it should be skipped.
   - Only after this check: state the exact change, including which test files need updating.

Classify each confirmed issue:
- 🔴 **HIGH** — wrong data written to DB, security bypass, race condition that causes incorrect state to persist, business rule not enforced in a path that affects money/stock/orders
- 🟡 **MEDIUM** — UX confusion, validation missing in one code path but present in equivalent paths, partial cleanup on failure, race condition that causes a request to **fail/500** (no wrong data persisted)
- 🔵 **INFO** — dead code, misplaced/stale comment, minor inconsistency with no user-visible impact

**Severity calibration for read-path bugs:** wrong data **returned** (display/response — pagination, formatting, stale read) but nothing wrong **written** to storage → MEDIUM at most, no matter how important the domain feels ("financial UX" does not upgrade a display bug to HIGH). HIGH requires wrong data persisted, a security bypass, or an unenforced rule that corrupts money/stock/order state.

**Severity calibration for race conditions:** Ask "what is the worst-case outcome?"
- Two concurrent requests → one writes wrong value to DB (oversell, wrong total, duplicate record) → **HIGH**
- Two concurrent requests → one gets a DB constraint error / 500, no data is corrupted → **MEDIUM at most, consider INFO** if the scenario requires simultaneous manual operations (e.g., two admins cloning the same product at the same millisecond)

**Present the classified findings to the user and wait for confirmation before touching any file.** Use `examples/finding-report-template.md` as the format template — each HIGH/MEDIUM finding must include: file + line, concrete reproduction steps, minimal fix description, and test name; INFO findings may use a lighter format (file + line, observation, recommended action). The user decides which severity levels to fix, and in what order.

**While waiting, the Stop gate hook will block the first attempt to end the turn** (the state file still has `phase4_gate: false` — this is expected, NOT a signal to proceed). When that happens: print "Waiting for user confirmation of findings — ending the turn." and end the turn again; the hook allows the second stop attempt. Do NOT treat the hook firing as implicit approval. Do NOT proceed to Phase 4 or Phase 5 without an explicit user reply.

**After the user confirms** (explicit reply): update the state file, then continue to Phase 4 (Completeness Check) — do not skip Phase 4:
```json
{"findings_confirmed": true, "phase4_gate": false, "phase5_gate": false, "phase6_gate": false, "phase7_gate": false}
```

This is the ONLY place `findings_confirmed` is set to `true` (besides the zero-findings rule below). Exit gates in later phases change their own gate field only — never this one.

**If there are zero findings** (clean module): report "No findings — module clean." to the user, set `"findings_confirmed": true` in the state file (nothing to approve — record "zero findings" as the reason in the Phase 7 summary), and continue. Phases 4–6 will be vacuous — state so explicitly at each gate instead of staying silent.

---

## Phase 4 — Completeness Check

Before starting Phase 5, review the full running issue list from Phase 2.

For every item you considered but did NOT include in Phase 3 findings, track it now for inclusion in the Phase 7 deferred list — print the table now, visible to the user (not a silent mental note):

```
| [finding description] | [reason not included: out of scope / by design / unreachable / fix cost too high / ...] |
```

If nothing was dismissed: note "No dismissed findings." explicitly.

If a dismissed item on second look deserves to be a finding (you dismissed it too quickly), surface it to the user NOW — before Phase 5 runs — and wait for their decision (same waiting rule as Phase 3: the user decides whether it joins the fix list). Do not silently park it in the deferred list, and do not fix it without approval.

**Rule: every item that appeared in the Phase 2 running issue list must appear in either Phase 3 findings or Phase 7 deferred. Silent disappearance is not allowed.**

This step exists because "Document what you don't fix" is a ground rule, but without a checkpoint it is easy to skip. This is the checkpoint.

### Phase 4 Exit Gate

- [ ] Every dismissed finding from Phase 2 running list is tracked with an explicit reason, OR "No dismissed findings." is stated
- [ ] Nothing silently dropped — if unsure whether an item counts, include it in Phase 7 deferred

**After completing all items:** set `"phase4_gate": true` in `.claude/audit-logic-state.json` — change only this field; `findings_confirmed` is owned by Phase 3.

---

## Phase 5 — Fix (One Bug Per Commit)

**If the user approved zero fixes** (every finding deferred): print "No fixes approved — Phase 5 skipped.", set the Phase 5 gate, and proceed to Phase 6. The exit-gate checklist below is then vacuously satisfied — state so explicitly instead of leaving it unaddressed.

**Commits:** invoking this skill counts as explicit authorization for the Phase 5 per-bug fix commits and Phase 6 doc commits — no additional confirmation is needed beyond the Phase 3 findings approval. If the target project is **not a git repository**: skip all commit steps, record each fix in the Phase 7 summary instead, and recommend the user initialize version control.

**Before the first fix:** check `git status` — the working tree must be clean (aside from the audit's own state file). Uncommitted user changes must be stashed/committed by the user, or explicitly acknowledged, before fix commits begin. When committing, stage only the files belonging to the current bug — never `git add .` — otherwise the one-bug-one-commit revertability guarantee breaks.

For each confirmed bug, in severity order (HIGH first):

1. Apply the **minimal surgical fix** — change only what is necessary to fix this specific bug. Do not refactor adjacent code, rename variables, or improve style in the same commit.

   **Before touching any file:** if the fix adds, removes, or renames a parameter in a function that is called from other files (repository methods, service functions, utilities), grep test files for assertions on the current call signature using whatever assertion syntax the project uses (e.g. `toHaveBeenCalledWith`, `assert.calledWith`, `expect(...).toBeCalledWith`, `verify(mock).method(args)`):
   (recipe: `references/verification-techniques.md` §Code snippets for Phase 5). Count how many test assertions use the current call signature (this counts assertions, not files — distinct from the Phase 3 step 5 deferral rule, which counts test files). If more than 3, note upfront that test assertion updates will be needed and which files contain them — this prevents discovering test failures mid-fix and having to context-switch back to understand why they fail.

2. Write or update tests. Default: **REGRESSION** — would have failed before the fix, passes after. Exception: **DOCUMENTATION** — only for INFO fixes where behavior is genuinely unchanged (cosmetic/intent-clarification); must label explicitly in commit message. See Exit Gate for labeling requirements.

   **If the project has no test framework** (established in Phase 1): skip test-writing and follow "When no test runner is available" in `references/verification-techniques.md` — document the expected behavior in the commit message and mark the fix explicitly as unverified. Steps 3–4 below also do not apply; state this instead of staying silent.

   The test must:
   - Have **failed** with the old code, OR be explicitly labeled DOCUMENTATION. **Prove the failure empirically when git is available**: stash the fix (`git stash`), run the new test against the old code, confirm it FAILS, then unstash and confirm it passes. Reasoning "it would have failed" is not proof. (No git, or stash impractical: state explicitly that the REGRESSION label is by-analysis only.)
   - **Pass** with the fix (verifies the correct behavior)
   - Assert the outcome, not the implementation detail
   - Be named to describe the scenario, not the code path
   - **For `[UNIT-TEST-BLIND]` fixes:** unit test updates only document intent — mocks accept any argument so they cannot verify real DB/integration behavior. You must also:
     1. Note in the commit message: "Unit tests document fix; integration/API test required for full verification."
     2. **Always write an integration or API test placeholder** in the appropriate test directory for this project (discovered in Phase 1 — check where integration/API/e2e tests live). Choose based on bug type: DB-level behavior → integration test directory; middleware/validator/request-response behavior → API/HTTP test directory. Even if it cannot run without a real DB/server. Use `test.skip` (or the framework's equivalent) with a comment explaining what it verifies and why it requires a real environment. This is not optional: without this placeholder, the correctness guarantee has no safety net for future test runs in the appropriate environment. (Format example: `references/verification-techniques.md` §Code snippets for Phase 5.)

3. Run the test suite for this module. Expected: previously passing tests still pass, the new/updated test passes. If unrelated tests break:
   - **Investigate first** — the fix may have incorrect scope
   - **If the broken test was asserting the old wrong behavior** → update the test to assert the correct behavior, and document why in the commit
   - **If the broken test is unrelated to the fix** → the fix has too wide a scope; narrow it before continuing

4. Run the **full** project test suite to confirm no regressions.

5. Run the project's linter/formatter if one exists and is configured.

6. **Spawn an independent verification agent** — unless the fix is trivially small. Skip the agent and do a manual read instead when ALL of the following are true: (1) fix changes ≤ 3 lines in 1 file, (2) fix does NOT add/remove a function parameter visible to callers, (3) the changed function has no downstream callers in other modules. For anything larger, spawn the agent. **Do NOT write a custom prompt.** Use the exact template below, replacing only `[list changed files]`:

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

   The agent must not know your intent; that context biases it toward confirming rather than finding remaining issues. Compare its findings against your fix.
   - **If the agent surfaces new findings** (unrelated to the fix): verify each one yourself with grep/Read before reporting to the user. New findings follow the same approval rule as Phase 3 — present them and wait for the user's decision; do NOT fix an unapproved finding. Do NOT relay subagent output directly — agents can hallucinate line numbers or misread context. Apply the same provability standard as Phase 3 step 4. Before queuing any of these findings for fixing, run the Phase 3 step 5 pre-flight check (test assertion grep + fix cost assessment) on each one — do not skip directly to Phase 5 step 1.

7. Commit with a message that answers three questions: what was wrong, why it was wrong, what changed. Use the commit format in `references/verification-techniques.md`.

**Repeat for each bug. One bug = one commit. Do not batch multiple bugs into a single commit.**

### Phase 5 Exit Gate

Before proceeding to Phase 6, confirm every item below. Do not skip or defer silently — if an item cannot be done, state the reason explicitly.

- [ ] Test written or updated for each fix (exception — project has no test framework per Phase 1: record "no test framework — fix unverified by tests" for each fix instead). When tests exist, each must be one of two labeled types:
  - **REGRESSION**: would have FAILED before the fix, passes after. This is the default.
  - **DOCUMENTATION**: fix does not change behavior (cosmetic/intent-clarification only) — test confirms existing behavior. Must write "DOCUMENTATION TEST: fix does not change behavior" explicitly in the commit message. Cannot use this label for MEDIUM or HIGH severity bugs.
  - For `[UNIT-TEST-BLIND]` fixes: the unit test passes; **integration or API test placeholder written** (`test.skip` with `// Verifies [BUG-X]` comment) — this is mandatory, not optional.
- [ ] Independent verification agent run for every fix, OR manual re-read for fixes that meet all skip conditions in step 6
- [ ] Full project test suite passes (not just module tests). Exception — if the Phase 1 baseline was already red or tests cannot run (user-approved code-only continuation): no NEW failures versus the baseline, and the unchanged pre-existing failures are listed explicitly
- [ ] No fix was batched — each bug has its own commit
- [ ] Phase 6 (stale documentation) is next — do not jump to Phase 7

**After completing all items:** set `"phase5_gate": true` in `.claude/audit-logic-state.json` — change only this field.

---

## Phase 6 — Update Stale Documentation

After all bug fixes are committed:

1. Search for documentation files that reference the changed behavior. Use the doc-discovery patterns in `references/verification-techniques.md` (Discovering Stale Documentation section): search by function name, by old behavior keywords, and by checking module-level docs in the same and parent directories.

2. For each doc file found: check whether descriptions of the changed behavior are now factually wrong.
   - Update descriptions that state the old incorrect behavior
   - Update business rule descriptions that no longer match the code
   - Do **not** rewrite accurate sections just to refresh them

3. If the project maintains test-count metrics or coverage summaries in documentation, update those numbers. **Scan the entire repository**, not just the module directory — test counts are often tracked in multiple documentation files outside the module. Use the format you discovered while reading the project's docs to identify what to grep for, then find all files containing that stale count and update them all.

4. Commit doc updates **separately** from code fixes with a message like `docs(<module>): update after <bug-name> fix`. (Non-git project: the Phase 5 no-git rule applies here too — record the doc updates in the Phase 7 summary instead of committing.)

### Phase 6 Exit Gate

- [ ] Every doc file that referenced changed behavior has been checked (not just the obvious ones — use grep by function name)
- [ ] Test-count metrics in documentation updated if the project tracks them
- [ ] If no doc updates were needed, state explicitly why (not silence)

**After completing all items:** set `"phase6_gate": true` in `.claude/audit-logic-state.json` — change only this field.

---

## Phase 7 — Summary

Print a final summary:
- Bugs found and fixed, with short description and commit hash for each (non-git project: note "uncommitted — no git" per the Phase 5 no-git rule)
- Files read (total count)
- Documentation files updated
- Items deferred: issues found but not fixed, with explicit reason for each (out of scope, by design, requires environment to verify, user decision to defer). Include every `[NEEDS-RUNTIME-VERIFY]` finding here unless the user approved fixing it.

**After printing the summary:**

1. Run `/pipeline-retrospective` (provided by the `subagent-system` plugin) to evaluate this audit run — it writes improvement proposals to `.claude/improvement-proposals.md` at the project root. This is mandatory — not optional. An ad-hoc retrospective in chat is not a substitute. **Exception:** if the skill is not installed, **or it is installed but fails to run** (e.g. errors out in headless mode), state this in the summary, record that the retrospective was skipped with the reason (not-installed vs failed, including the error), and continue closing the gates — a missing or broken dependency must not leave the session permanently blocked.
2. Set `"phase7_gate": true` in `.claude/audit-logic-state.json` — change only this field (safety net: keeps the Stop hook passing even if step 3 fails).
3. Delete `.claude/audit-logic-state.json` (cleanup — allows the Stop hook to pass).

### Phase 7 Exit Gate

- [ ] Summary printed (bugs, files read, docs updated, deferred items with reasons)
- [ ] `/pipeline-retrospective` run — or its absence/failure recorded with reason (see step 1 Exception)
- [ ] `.claude/audit-logic-state.json` deleted

---

## Ground Rules (Apply Throughout)

- **Read code, not descriptions.** When behavior is unclear, read the implementation — not the CLAUDE.md, not the README, not the test names.
- **Read yourself — no subagent delegation.** Delegating file reading to subagents produces shallow, context-free analysis. Every file must be read directly in this session.
- **No assumption of correctness.** "It looks right" is not verification. If you think it's correct, run the test that proves it.
- **No shortcuts on reading.** A 600-line file requires reading 600 lines. There is no representative sample.
- **Verify before and after every fix.** Run the test suite before touching the code (baseline), and again after (regression check).
- **One bug = one commit.** Each commit must be independently revertable. If you discover two bugs, fix them in two separate commits.
- **Document what you don't fix.** If something is wrong but out of scope, confirmed by design, or requires an environment you don't have — say so explicitly in the Phase 7 summary. Silence is not acceptable.
- **Abort = cleanup.** If the user cancels the audit at any phase, delete `.claude/audit-logic-state.json` before ending the turn. An orphaned state file blocks the first stop attempt of every turn in every future session of this project.
- **Waiting for user input mid-audit (any phase):** the Stop gate hook blocks the first attempt to end the turn while gates are incomplete. When intentionally stopping to wait for the user, print that you are waiting and end the turn again — the hook allows the second consecutive stop. Never set a gate to true just to satisfy the hook.
- **For very large modules (50+ source files):** Do not attempt to finish in one session if the context window cannot hold all files. Instead: (1) audit the highest-priority layer (service/business logic) in this session, commit findings and fixes, (2) report clearly what was covered and what remains, (3) continue in a fresh session. Partial coverage with honest scope is better than shallow coverage of everything. **State file across sessions:** run the full Phase 3–7 cycle (gates + state-file deletion) for the layer covered in THIS session — closing the gates for an honestly-scoped partial audit is legitimate, not "setting a gate just to satisfy the hook". Never carry an open state file into the next session; that session starts again at Phase 1 scoped to the remaining layers.

---

## Additional Resources

Load these references when needed — they contain detailed patterns and techniques that are too long to include here:

- **`references/reading-patterns.md`** — Concrete patterns to look for while reading: race conditions, transaction boundaries, guard clause bypasses, null/undefined failures, type coercion, off-by-one, business rule coverage, dead code
- **`references/verification-techniques.md`** — False-positive filtering, independent verification agent prompt, test strategy, doc discovery, severity classification, commit message format

Working examples for reference:

- **`examples/finding-report-template.md`** — Template for presenting audit findings to the user: file + line, reproduction steps, minimal fix, test name
- **`examples/independent-verification-exchange.md`** — How to run Phase 5 step 6 independent verification and interpret the results, including how to handle new findings the agent surfaces
