# verify-then-draw

Draw UML / architecture diagrams from a codebase with **minimal error**, through a 3-tier hard-gated pipeline. Core rule: *never trust "the code is correct" and draw on top of it* — a diagram that faithfully matches buggy code is wrong about the business.

## Pipeline

```
T0 code-is-business-correct ──gate──► T1 diagram-matches-code ──gate──► T2 notation + readable
```

- **T0** audit business correctness (multi-lens finders → adversarial verifier → fix → tests assert OUTCOME → mutation/property), gated by human-written invariants.
- **T1** completeness cross-module → draw → adversarial `diagram-verifier` subagent diffs diagram-vs-code → loop until dry.
- **T2** render → vision-check (notation/overlap/clutter/readable-on-page) → human sign-off.

Each tier must anchor ≥1 **out-of-model oracle** (human/spec, run-real-code, structural denominator), because a single agent self-checking has a ceiling.

## Components

| Type | Name | Use |
|---|---|---|
| Skill | `verify-then-draw` | Auto-triggers on "draw/update a diagram from code". Entry + full `FRAMEWORK.md`. |
| Command | `/verify-then-draw:draw [module]` | Guided run through all gates. |
| Agent | `diagram-verifier` | Independent cross-module diagram-vs-code audit (read-only). |

## Per-project setup

The plugin is **generic**. Each project keeps an instance folder `verify-workflow/`:
`PROJECT.yaml` (stack params), `invariants.<domain>.md` (GATE-A oracle), `diagram-manifest.yaml` (denominator), and enforce scripts (`route-enumerator`, `check-ledger`, `check-invariants-approved`, `lint-config`) — templates under `skills/verify-then-draw/`.

## Honest limits

Reduces error, does not eliminate it. See `FRAMEWORK.md §10` for residual risks (wrong invariant, non-independent oracle, rubber-stamp, denominator misconfig). Never claim "0 errors".

Author: Minh Thang · License: MIT
