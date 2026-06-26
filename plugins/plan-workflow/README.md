# plan-workflow

Universal 8-phase implementation plan workflow with human approval gates. Applicable to any plan type: feature addition, bug fix, refactoring, migration, security hardening.

Built from real-world lessons across multi-file refactoring sessions — captures 8 core principles (P1–P8) that prevent the most common planning failures: unverified claims, scope creep, confirmation bias, dead code cascades, and stale documentation.

## Installation

```bash
claude plugin install plan-workflow@minhthang-plugins
```

## Contents

### Skills

- `/plan-refactor` — Full 8-phase workflow: explore → audit → consolidate → draft plan → verify → implement → post-impl audit → final verify. Three human approval gates built in.
- `/verify-plan` — Adversarial verification of a plan's factual claims against the actual codebase. Use at Phase 5 before implementation.
- `/audit-dead` — Post-implementation audit for dead code, cascade effects, schema gaps, and stale documentation. Use at Phase 7 after implementation.

### Rules

Pairs with `rules/plan.md` (auto-loaded every session) — provides the 8 principles summary and "always/never" guardrails.

## The 8 Principles

| # | Principle | One-liner |
|---|-----------|-----------|
| P1 | Contract | Plan must be self-contained for a fresh agent to execute after /compact |
| P2 | Verify | Every agent claim verified against actual files before entering the plan |
| P3 | Independent | The creating agent cannot verify its own work |
| P4 | Test Gates | Baseline before first edit; checked after every phase |
| P5 | Emergent Issues | Post-implementation audit is mandatory — implementation creates unpredictable effects |
| P6 | Scope Freeze | Out-of-scope findings go to backlog, not the current plan |
| P7 | Oscillation | Stop iterating; read the code; make a FINAL DECISION |
| P8 | Human Gates | Three mandatory approval gates; agent stops and waits |

## Plan Type Support

The core workflow is universal. Type-specific guidance is in `skills/plan-refactor/references/`:

- **Renaming / Structural refactoring** — occurrence counts, DO NOT RENAME list, mass rename scripts, dead parameter cascade
- **Bug fix** — reproduce first, failing test, root cause, regression test
- **Feature addition** — interface-first design, integration points, edge case verification
