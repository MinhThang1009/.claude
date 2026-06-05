---
name: verify-then-draw
description: "This skill should be used when the user asks to draw, create, update, or fix a diagram from a codebase — use case / sequence / state / component / ERD / deployment / pipeline (UML or other notation), especially for a thesis/report or documentation that must match real code. Enforces a 3-tier gated pipeline so a diagram never depicts buggy or incompletely-understood code. Also trigger on: 'vẽ sơ đồ', 'verify then draw', 'audit code before diagramming'."
disable-model-invocation: false
allowed-tools: Read Grep Glob Bash Write Edit TodoWrite Agent
argument-hint: <module-or-diagram-name>
---

# Verify-then-Draw

Draw diagrams from a codebase with **minimal error**. Core rule: **never trust "the code is correct" and draw on top of it** — a diagram that matches buggy code is wrong about the business. Three hard gates, no upper tier until the lower passes.

> Full framework (generic, portable): [`FRAMEWORK.md`](FRAMEWORK.md) in this skill folder.

## The 3 tiers

```
T0 code-is-business-correct ──gate──► T1 diagram-matches-code ──gate──► T2 notation + readable
```

| Tier | Do | Out-of-model oracle (mandatory ≥1) |
|---|---|---|
| **T0** | Audit business correctness: parallel multi-lens finders → adversarial verifier → fix → tests assert OUTCOME | (a) human/spec invariants `WHEN…THEN…` + (b) run-real-code RAW + mutation + property |
| **T1** | Diagram covers code: completeness enumerate **cross-module** → draw → adversarial subagent diff diagram-vs-code → fix → loop | (c) structural denominator (route table / enum set / AST) |
| **T2** | Render → vision-check (node/logic/notation/no-overlap/no-clutter/A4-readable/...) → fix | vision-check + human GATE-D |

**Stop loop only when all 3 hold:** ≥2 consecutive 0-finding rounds (rotate lens) **and** coverage-ledger meets threshold **and** 0 unexplained mutation survivors in critical scope.

**4 human gates (HARD STOP — cannot be automated):** GATE-A you write invariants → GATE-C review the finder prompt → GATE-B compare test-asserts vs invariants → GATE-D sign the diagram.

## How to run in a project

This skill is **generic**. Each project keeps an instance folder `verify-workflow/` with:
- `PROJECT.yaml` — stack params (layer globs, mutation/route/deadcode cmds, toolchain, thresholds). Template: [`PROJECT.example.yaml`](PROJECT.example.yaml).
- `invariants.<domain>.md` — GATE-A oracle (human writes/approves).
- `diagram-manifest.yaml` — the diagrams to draw (denominator).
- enforce scripts (copy from [`scripts/`](scripts/) here, adapt to stack): `route-enumerator.mjs` (real route denominator), `check-ledger.mjs` (gate: logic-heavy diagrams must be signed), `check-invariants-approved.mjs` (gate T0: block while invariants unapproved), `lint-config.mjs` (config self-check).

Steps when invoked with a module/diagram arg:
1. **Init/locate** `verify-workflow/` (create from templates if absent). Run `lint-config.mjs --gate`.
2. **T0**: confirm invariants for the module are approved (`check-invariants-approved.mjs --gate --id-prefix <X>`). Audit logic (multi-lens finder + adversarial verifier), fix, add integration/property tests asserting OUTCOME. Run mutation on critical scope (break-threshold ≠ null).
3. **T1**: completeness-grep cross-module → draw the diagram → spawn the `diagram-verifier` agent to diff diagram-vs-code → fix → loop until dry.
4. **T2**: render → vision-check the PNG (read it) against the checklist → fix until it passes → stop for human GATE-D sign-off.
5. Update `diagram-manifest.yaml` status; run `check-ledger.mjs`.

## Honest limits

This reduces error, does not eliminate it. Residual risks are listed in FRAMEWORK.md §10 (wrong invariant nothing catches; oracle not truly independent if spec+code share a wrong assumption; human-gate rubber-stamp; denominator misconfig; property/mutation only catch what's declared). Do not claim "0 errors".
