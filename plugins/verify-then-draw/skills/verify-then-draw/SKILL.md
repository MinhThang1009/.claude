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
| **T2** | Render → spawn **fresh `diagram-verifier` agent** (zero context of how diagram was drawn) to vision-check PNG → fix → loop until 0 findings | vision-check (independent agent) + human GATE-D |

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
2. **T0**: confirm invariants for the module are approved (`check-invariants-approved.mjs --gate --id-prefix <X>`). Audit logic with **≥2 independent lenses** (e.g. correctness + race-condition; correctness + boundary-validation) — minimum even for simple modules; 1-endpoint modules still need at least: (a) validate field names match DB schema/ENUM, (b) check error handling is not silently swallowed. Fix bugs found, add integration/property tests asserting OUTCOME. Run mutation on critical scope (break-threshold ≠ null). Skip mutation only when module has 0 state-mutating paths (document why).

   **T0 required output format — no shortcuts:**
   ```
   T0 Lens 1 — <name>: <specific things checked + finding or "PASS">
   T0 Lens 2 — <name>: <specific things checked + finding or "PASS">
   ```
   **PROHIBITED:** "prior session audit found 0 bugs" does NOT satisfy T0. Memory from previous sessions is stale and unverified in the current working tree. T0 MUST be run fresh every invocation — read the source files, run the lenses, produce the output table. No exceptions.
3. **T1**: completeness-grep cross-module → draw the diagram → spawn the `diagram-verifier` agent to diff diagram-vs-code → **before applying any fix, lead agent MUST produce a verification table** (skip = finding treated as unverified, diagram not eligible for T2):

   ```
   | Claim | file:line cited | Read? | Evidence (quoted) |
   |---|---|---|---|
   | <T1 finding> | <file>:<line> | ✓/✗ | "<exact quote from file>" |
   ```

   Only rows with ✓ + evidence get applied as fixes. Rows with ✗ or missing evidence → discard (false positive until proven otherwise). Root cause: agent self-reports are unreliable; this table forces a Read-tool call per finding. → fix confirmed findings → re-render → loop until dry. **T1 agent prompt PHẢI chứa verbatim:** `"CRITICAL: Do NOT write, modify, or append to any file using Bash or any tool. Bash is read-only (cat/grep only). Do NOT update diagram-manifest.yaml, do NOT seed invariants files. Only report findings."` Root cause: diagram-verifier has Bash access → can sed/echo to files silently without mentioning it in output text.
4. **T2**: render → spawn a **fresh `diagram-verifier` agent** with zero context of how the diagram was drawn — give it only the PNG path + full 9-point checklist from project memory (`feedback_diagram_vision_checklist.md`: node/logic/notation/no-overlap/no-clutter/A4-readable/UTF-8-diacritics/terminology/B&W-print) → agent reads PNG and reports issues **with evidence (quoted text or described visual element)** → for each finding: cross-check against PUML source before treating as real (PNG at small resolution produces false positives — a finding with no PUML evidence is suspect) → fix confirmed findings → re-render → loop until agent returns 0 confirmed findings → stop for human GATE-D sign-off. **NEVER self-review T2** (same agent that drew the diagram cannot reliably catch its own blind spots). **T2 agent prompt PHẢI chứa verbatim:** `"CRITICAL: Do NOT write, modify, or append to any file. Only report findings."`
5. **Manifest update** — chỉ lead agent (không phải T1/T2 subagent) được update `diagram-manifest.yaml`. Sau khi T1 MATCH và T2 PASS xác nhận: set `status: drawn`, ghi comment `T0 ✓ · T1 MATCH · T2 PASS · Chờ GATE-D`. Sau GATE-D human sign-off: set `status: signed`. Run `check-ledger.mjs`.

## Honest limits

This reduces error, does not eliminate it. Residual risks are listed in FRAMEWORK.md §10 (wrong invariant nothing catches; oracle not truly independent if spec+code share a wrong assumption; human-gate rubber-stamp; denominator misconfig; property/mutation only catch what's declared). Do not claim "0 errors".
