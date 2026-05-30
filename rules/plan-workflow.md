# Plan Workflow Rules

> Auto-imported every session. Applies whenever creating or executing any implementation plan.
> Full workflow: `/plan-refactor` skill. Principles: see `references/principles.md` inside that skill (`plugins/plan-workflow/skills/plan-refactor/`).

## The 8 Principles

- **P1 — Plan Is a Contract:** Complete enough for a fresh agent with zero prior context to execute.
- **P2 — Verify Before Trusting:** Every agent claim verified against actual files before entering the plan.
- **P3 — Independent Verification:** The agent that created something cannot reliably verify it.
- **P4 — Test Gates Are Non-Negotiable:** Baseline established before first edit; checked after every phase.
- **P5 — Implementation Creates New Issues:** Post-implementation audit is always mandatory.
- **P6 — Scope Freezes Before Implementation:** Out-of-scope findings go to backlog, not the current plan.
- **P7 — Oscillation = Missing Ground Truth:** Stop iterating; read the code; make a FINAL DECISION.
- **P8 — Agent Executes; Human Approves:** Three mandatory human gates: after Phase 3 (scope), after Phase 5 (plan), after Phase 7 (findings). Agent stops and waits. Agent does not self-approve.

## When to Create a Plan

Create a plan when: >3 files touched, crosses a layer boundary, shared interface affected, session needs /compact, or rollback would be non-trivial. Otherwise: edit directly, run tests, done.

## Always

- Establish BASELINE (test count) before the first edit.
- One phase at a time. Never proceed until tests pass.
- Fresh agent to verify plan (Phase 5). Fresh agent to audit post-implementation (Phase 7).
- After /compact: re-read context files listed in the plan before continuing.

## Never

- Pass unverified agent findings directly into the plan.
- Use grep line counts when you need occurrence counts (they differ when one line has multiple hits).
- Expand scope after Phase 3.
- Self-verify a risk-bearing edit batch (shared/logic-bearing changes, or a batch too large to track — >5 edits is one signal) — dispatch a fresh agent instead.
- Reopen a decision marked FINAL DECISION.
