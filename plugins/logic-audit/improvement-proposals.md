# Logic-Audit Plugin Improvement Proposals
Generated: 2026-06-06 (latest: wishlist v0.8.0 — 6th run, GOOD)
wishlist: 1 MEDIUM found+fixed (null.toJSON crash on soft-deleted product). 6 consecutive runs GOOD.

---

Generated: 2026-06-06 (users v0.8.0 — 5th run, CLEAN MODULE, all GOOD)
5 consecutive clean runs. users module had 0 bugs — audit correctly identified clean codebase.

---

Generated: 2026-06-06 (reviews v0.8.0 — 4th run, all GOOD)
4 consecutive clean runs. Skill stable.

---

Generated: 2026-06-06 (discount-code v0.8.0 — 3rd run, all GOOD)

## v0.8.0 3rd Run (discount-code)
All 6 dimensions GOOD. No new proposals. 3 consecutive clean runs confirms v0.8.0 stability.

---

Generated: 2026-06-06 (cart v0.8.0 — 2nd run)
Source: logic-audit v0.8.0 run on backend/src/modules/cart — CLEAN RUN, no new proposals

## v0.8.0 2nd Run Result (cart module — HIGH + MEDIUM bugs found)
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | GOOD | 10 source + 10 test suites read; reading-patterns.md loaded ✓ |
| D2 Finding quality | GOOD | 1 HIGH (addToCart duplicate CartItems) + 1 MEDIUM (getCart merge no cap). Agent surfaced 9/9 pre-existing — executor correctly filtered. |
| D3 Completion | GOOD | 7 phases + 2 commits + docs + retrospective complete |
| D4 Pipeline health | GOOD | Phase 7 gate blocked until retrospective — v0.8.0 enforcement working ✓ |
| D5 Fix quality | GOOD | Surgical commits, no scope spill |
| D6 Skill triggering | GOOD | All mandatory steps triggered correctly |

**No new improvements needed for v0.9.0.**

---

## v0.8.0 Benchmark Result (inventory module)
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | GOOD | All 7 source + 4 test files read; reading-patterns.md loaded pre-Phase 2 ✓ |
| D2 Finding quality | GOOD | 1 MEDIUM real, 4 agent false positives correctly dismissed ✓ |
| D3 Completion | GOOD | All 7 phases complete including Phase 4 completeness check ✓ |
| D4 Pipeline health | GOOD | Phase 4 gate enforced; incremental hint correct; no stalls ✓ |
| D5 Fix quality | GOOD | Surgical: 2 files + separate doc commit ✓ |
| D6 Skill triggering | GOOD | reading-patterns.md ✓; Phase 4 ✓; pipeline-retrospective ✓ |

**No new improvements needed for v0.8.0. All gates working correctly.**

---

# Previous Proposals (payment module — v0.5.0 baseline)
Source: logic-audit run on backend/src/modules/payment (TechStore e-commerce)

## Performance Summary
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | PARTIAL | references/reading-patterns.md not consulted during Phase 2 file reading |
| D2 Finding quality | PARTIAL | vnp_RequestId HHmmss collision identified internally, never surfaced in Phase 3 or Phase 6 |
| D3 Completion | PARTIAL | Phase 4 Exit Gate passed despite INFO-1 test being documentation-only, not a regression test |
| D4 Pipeline health | PARTIAL | Phase 3 → Phase 4 transition skipped user confirmation gate |
| D5 Fix quality | GOOD | Commits surgical, lint+tests pass, correct scope |
| D6 Skill triggering | POOR | verification-techniques.md prompt template not used (custom prompt written instead); no completeness critic phase in skill |

## Applied Changes

### P-1 (HIGH): Phase 2 — enforce reading reading-patterns.md before first file
**Target:** `skills/logic-audit/SKILL.md` Phase 2
**Applied:** Added mandatory step at the top of Phase 2 requiring the executor to read
`references/reading-patterns.md` in full and print a one-line summary of the 5 most
relevant categories before reading the first source file.

### P-2 (HIGH): Add Phase 3.5 — Completeness Check
**Target:** `skills/logic-audit/SKILL.md` — new phase between Phase 3 and Phase 4
**Applied:** New phase requiring the executor to account for every item from the Phase 2
running issue list — either in Phase 3 findings or in the Phase 6 deferred table. No item
may silently disappear. Explicit "No dismissed findings." is required if nothing was dropped.

### P-3 (MEDIUM): State file + implicit approval rule
**Target:** `skills/logic-audit/SKILL.md` Phase 1 + Phase 3, and `hooks/logic-audit-gate.py`
**Applied:**
- State file now includes `findings_confirmed: false`
- Phase 3 now specifies the implicit approval rule (user silence = proceed for MEDIUM/HIGH,
  print "Proceeding with implicit approval.")
- Hook: non-blocking warning when `phase4_gate: true` but `findings_confirmed: false`

### P-4 (MEDIUM): Phase 4 Exit Gate — label regression vs documentation tests
**Target:** `skills/logic-audit/SKILL.md` Phase 4 Exit Gate
**Applied:** The test checkbox now requires explicit labeling — either REGRESSION (fails
before fix, passes after) or DOCUMENTATION (behavior unchanged, commit must say so).
DOCUMENTATION label is not permitted for MEDIUM or HIGH severity fixes.

### P-5 (MEDIUM): Phase 4 step 6 — inline verification prompt, ban custom prompts
**Target:** `skills/logic-audit/SKILL.md` Phase 4 step 6
**Applied:** The exact 3-question verification agent prompt is now inlined in SKILL.md
with an explicit "Do NOT write a custom prompt" instruction. Previously it only referenced
an external file, which was easy to ignore.

### P-6 (LOW): Phase 6 — mandatory retrospective
**Target:** `skills/logic-audit/SKILL.md` Phase 6
**Applied:** After deleting the state file, executor must run `/pipeline-retrospective`.
Marked as mandatory, not optional.
