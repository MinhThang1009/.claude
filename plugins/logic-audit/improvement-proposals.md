# Logic-Audit Plugin Improvement Proposals
Generated: 2026-06-06
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
