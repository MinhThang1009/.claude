---
name: plan-refactor
description: This skill should be used when the user asks to "create a plan", "plan this refactoring", "plan this feature", "make an implementation plan", "how should we approach this", or when a change touches more than 3 files, crosses layer boundaries, or requires /compact to complete. Provides a universal 8-phase workflow with 3 human approval gates for any plan type.
---

# Implementation Plan Workflow

Universal 8-phase process for creating verified, implementation-ready plans. Applicable to any plan type: feature addition, bug fix, refactoring, rename, migration, security hardening.

## Core Principles (P1–P8)

Eight principles govern every decision in this workflow. Full descriptions with failure mode mappings are in `references/principles.md`. Summary:

- **P1 — Contract:** The plan must be self-contained — a fresh agent with zero prior context can execute it after /compact without asking questions.
- **P2 — Verify:** Every agent claim must be verified against actual files before entering the plan. Agents report wrong line numbers, miss files, truncate content, and generate false positives.
- **P3 — Independent:** The agent that created something cannot reliably verify it. Self-verification consistently misses the errors it introduced. Every verification step uses a fresh agent.
- **P4 — Test Gates:** A passing test baseline is established before the first edit. Every phase gate confirms the baseline is still passing. A failing test stops work until root cause is understood.
- **P5 — Emergent Issues:** Implementation changes code. Changed code has properties — newly dead dependencies, newly broken contracts, newly inconsistent paths — that planning cannot predict. Post-implementation audit is mandatory.
- **P6 — Scope Freeze:** After Phase 3, scope is frozen. Any finding outside the original scope goes to a backlog file, not into the current plan. Expanding scope during implementation breaks test gates.
- **P7 — Oscillation:** When the same design question gets answered differently across audit rounds, agents lack ground truth. Stop iterating. Read the actual code. Make a final decision and write `**FINAL DECISION: [reason]**`. Do not reopen it.
- **P8 — Human Gates:** Three mandatory approval gates exist. After Phase 3 (scope), after Phase 5 (plan), after Phase 7 (findings). The agent stops and waits at each gate. The agent does not self-approve.

## When to Create a Formal Plan

Create a plan when any of these is true:
- More than 3 files will be touched
- The change crosses a layer boundary (UI → service → DB, or similar)
- The same logical concept exists in multiple places (partial update = inconsistent state)
- The session will require /compact (plan must survive context loss — P1)
- Rollback would be non-trivial
- The change affects a shared interface that other code depends on

If none of these apply: make the change directly, run tests, done.

## Plan Type Detection

Identify the plan type from the user's request, then read the corresponding appendix for type-specific audit criteria, risk ordering, and verification steps:

- **Rename / Structural refactoring** → `references/appendix-rename.md`
- **Bug fix** → `references/appendix-bugfix.md`
- **Feature addition** → `references/appendix-feature.md`
- **Other** → use the universal phases below; adapt audit prompts to the specific domain

## Phase Gate Sequence

```
Phase 0  PRE-FLIGHT    → test baseline + git clean + behavioral baseline (P4)
        ↓
Phase 1  EXPLORE       → ground truth inventory (P2)
        ↓
Phase 2  AUDIT ×2      → two independent agents, max 2 rounds (P3)
        ↓
Phase 3  CONSOLIDATE   → verify every finding; scope freeze (P2, P6)
        ↓ ★ HUMAN GATE 1: approve findings + scope
Phase 4  DRAFT PLAN    → self-contained contract document (P1)
        ↓
Phase 5  VERIFY PLAN   → fresh agent, adversarial — use /verify-plan (P3)
        ↓ ★ HUMAN GATE 2: approve plan before first edit
Phase 6  IMPLEMENT     → one phase at a time; test gate after each (P4)
        ↓
Phase 7  POST-IMPL     → cascade + schema + docs — use /audit-dead (P5)
        ↓ ★ HUMAN GATE 3: review findings before sign-off
Phase 8  FINAL VERIFY  → test = BASELINE, 0 stale references (P4)
```

## Phase Details

### Phase 0 — Pre-flight

1. Run the project's test suite. Record the exact pass count as **BASELINE**. This number is referenced in every subsequent phase gate — if it changes, something broke.
2. Verify git state is clean. Uncommitted changes make mid-plan rollback painful. Commit or stash first.
3. Identify the scope: which directories and modules are in scope for this change.
4. If the scope touches code that processes external input (user input, API responses, LLM output), document current behavioral edge cases now. The unit test gate counts pass/fail — it does not catch behavioral regressions.

### Phase 1 — Explore (implements P2)

Spawn an **Explore** subagent to produce a ground truth inventory. The prompt must answer three questions:
- What exists now, and where exactly? (functions, classes, APIs, data shapes, dependencies)
- Who depends on it? (all callers, importers, and reference sites — search the entire codebase, not just `src/`)
- What constraints apply? (documented rules in CLAUDE.md files, test coverage, public contracts)

**Non-negotiable:** The inventory must include test files and documentation files (`**/*.md`). These are missed in every first-pass inventory — enumerate them explicitly in the subagent prompt. Identify the test file naming pattern for this codebase (`*.test.js` / `*_test.py` / `*.spec.ts` / etc.).

Do not proceed to Phase 2 until the inventory has been verified by spot-checking locations directly (P2). Read at least 3 locations yourself to confirm the subagent reported correctly.

### Phase 2 — Audit (implements P3, P7)

Spawn two agents in parallel, each reading the codebase independently with no shared context:

**Agent A — structural audit:** Is the current structure correct? Look for code in the wrong place (wrong file, wrong layer, wrong abstraction level), names that don't reflect actual behavior, ordering that conflicts with execution flow, and contracts inconsistent with how callers use them.

**Agent B — correctness audit:** Is anything broken, unused, or inconsistent? Look for dead imports, dead parameters, dead variables, schema gaps between parallel execution paths (e.g., main path returns `stockQuantity` but fallback path does not), and broken assumptions the proposed change will invalidate.

**Rules:**
- **1 round = both agents complete one full pass = 2 agent runs.**
- **Cap at 2 rounds** (4 agent runs total). After round 2, escalate remaining NEEDS_VERIFY items to the user. Do not run round 3 — it produces oscillation, not signal (P7).
- When agents disagree on the same item: read the file directly. Ground truth wins over both agents (P2, P7).

### Phase 3 — Consolidate (implements P2, P6)

For each finding from Phase 2:
1. **Verify it directly.** Read the actual file at the claimed location. Do not pass unverified agent findings into the plan (P2). A subagent claiming "line 99 has X" may be wrong — read line 99 before trusting it.
2. Mark each finding: CONFIRMED / FALSE_POSITIVE / NEEDS_VERIFY.
3. Drop all FALSE_POSITIVE findings. Escalate NEEDS_VERIFY to the user with a specific question — do not guess.
4. If the same design question has been answered differently across audit rounds: stop generating subagent reports. Read the code. Decide. Write `**FINAL DECISION: [reason]**` (P7).

**Scope freeze (P6):** Any finding outside the original scope → log in a separate backlog file. Do not expand the plan. Scope creep is how plans fail.

**Common false positives to filter out:**
- Finding is in a comment, documentation string, or test description → not a code issue
- Symbol used only in test files → alive (tests are callers, not dead weight)
- Same name in a different scope → different entity entirely
- Agent claims a specific location → read that location before trusting it

**★ HUMAN GATE 1:** Present the confirmed findings list and proposed scope to the user. State what is IN scope and what was explicitly moved to backlog. Wait for explicit approval before drafting the plan. Do not proceed to Phase 4 without it.

### Phase 4 — Draft Plan (implements P1)

**Risk ordering:** Phase the changes lowest-risk first, highest-risk last. Lower risk = fewer callers affected, easier to revert, no behavioral change visible to users. Higher risk = shared interfaces, public APIs, data migrations, user-visible behavior. For type-specific risk ordering, read the appropriate appendix.

**For each phase in the plan:** Include specific changes with verified locations (use grep-confirmed locations, not line numbers — line numbers go stale after prior-phase edits), a verification method describing how to confirm the change is correct, and a test gate: `[test command] → BASELINE pass`.

**Required plan sections:**

```markdown
## What Does NOT Change
[Things explicitly reviewed and decided to leave as-is, with reasons.
Prevents re-litigation of settled decisions across sessions. (P1, P7)]

## Implementation Phases
[ordered by risk; each phase has: changes + locations + verification + test gate]

## Files Touched — Complete List
[production files + test files (with codebase-specific pattern) + *.md documentation — all three]

## Post-Implementation Checks
[what specifically to audit after all phases complete — type-specific, see appendix]

## Context Files to Re-read After /compact
[paths to CLAUDE.md files and other context lost after compaction (P1)]
```

**The plan is ready for Phase 5 when:** all locations are verified against actual files (not estimated), "What Does NOT Change" table is complete (no open questions remain), and the file list explicitly includes test files and documentation files.

### Phase 5 — Verify Plan (implements P3)

Invoke `/verify-plan` or spawn a fresh agent with the plan document only — no context from the planning session (P3).

The agent checks: all stated file paths exist, all stated locations are current (re-reads the file at each location), no file with relevant content is missing from the touched list (test files and documentation files checked explicitly), and "What Does NOT Change" entries correctly identify what should be excluded.

**When blockers found:** Return to Phase 4. Fix the specific claim (re-grep, re-read the file). Re-run Phase 5.
**When warnings found:** Fix inline if obvious; otherwise escalate to the user.

**★ HUMAN GATE 2:** Present the verified plan to the user. State: "Plan verified — 0 blockers. Ready to implement Phase 1. Proceed?" Wait for explicit approval before making any code change. This is the last moment to revise the plan without touching code.

### Phase 6 — Implement (implements P4, P5, P6)

**Rollback protocol:** Commit to git before starting each phase. If a phase needs to be undone: `git revert <phase-commit>`. Never start a new phase with uncommitted changes from the prior one.

For each phase in the plan:
1. **Before editing:** Re-verify the target location in the current file (prior phase edits shift locations — use grep, not plan line numbers). If resumed after /compact: re-read all files listed in "Context Files to Re-read" (P1).
2. **Make the change.** One logical change at a time. For mass changes across files: use a script that reports a count, so the expected number of changes can be verified (P2).
3. **Verify:** Run test suite → must equal BASELINE (P4). Confirm the change is present where expected. Confirm no unintended changes in adjacent code. Sample-check mass replacements for unintended matches.
4. **Cascade check:** Did this change create a new issue not in the plan? (unused dependency, violated contract, inconsistent parallel path) If yes → add to Phase 7 audit list; do not expand the current plan (P6).
5. Proceed to the next phase only after steps 1–4 pass.

**If tests fail:** Test references old behavior → update the test. Functional regression → `git revert` the phase commit; find root cause before re-applying. Unrelated flaky → re-run once; if still failing, investigate and fix before proceeding.

**Anti-bias (P3):** After a risk-bearing edit batch (shared/logic-bearing changes, or too many to track — >5 edits is one signal), dispatch a fresh agent to review the changes before reporting done.

**New issues found during implementation:** Note them, continue the current phase, add to Phase 7 list (P6). Do not stop to replan.

### Phase 7 — Post-Implementation Audit (implements P5)

Invoke `/audit-dead` or execute checks manually. Universal checks that apply to all plan types: cascade effects (did this change make something else unused, unreachable, or incorrect?), consistency across parallel paths (all paths returning the same type still have the same fields?), documentation staleness (search explicitly for stale references), and YAGNI params ("reserved for future use" = remove and trace cascade).

For type-specific checks, read the appendix.

**★ HUMAN GATE 3:** Present findings to the user before signing off. Report: (1) what the plan said would change and is now done, (2) what Phase 7 found that was NOT in the plan, (3) current test count vs BASELINE. The user decides whether Phase 7 findings require additional action before sign-off.

### Phase 8 — Final Verification (implements P4)

Search for stale references in source files (use this codebase's extension), documentation files (`*.md`), and test files (use this codebase's test pattern) → all searches must return 0 results. Run test suite → must equal BASELINE exactly. Log any items deferred to backlog.

Sign off: `BASELINE: N. Final: N. Delta: 0.`

## Additional Resources

### Reference Files

For detailed guidance beyond the core workflow, consult:
- **`references/principles.md`** — Full P1–P8 descriptions with consequences and failure mode mappings
- **`references/appendix-rename.md`** — Symbol renaming and structural refactoring: occurrence counts, DO NOT RENAME list, mass rename scripts, dead parameter cascade, MISPLACED_FUNCTION
- **`references/appendix-bugfix.md`** — Bug fix plans: reproduction, root cause, failing test first, regression test
- **`references/appendix-feature.md`** — Feature addition plans: interface-first design, integration points, edge case verification
