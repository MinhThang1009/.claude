---
description: Guided verify-then-draw — audit code (T0) then draw a diagram that matches it (T1) with correct notation (T2), through 3 hard gates with human sign-off.
argument-hint: "[module | diagram-name]  e.g. orders, state-01-order"
allowed-tools: Read Grep Glob Bash Write Edit TodoWrite Agent
---

## Your Task

Run the **verify-then-draw** pipeline for: **$ARGUMENTS** (if empty, ask which module/diagram).

Follow the `verify-then-draw` skill (read its `FRAMEWORK.md`). Do NOT skip a gate.

### Step 0 — Locate/init project instance
- Find `verify-workflow/` at repo root. If absent, scaffold it from the skill templates (`PROJECT.example.yaml` → `PROJECT.yaml`, copy `scripts/`, create empty `invariants.<domain>.md` + `diagram-manifest.yaml`). Stop and ask the user to fill stack params.
- Run `node verify-workflow/lint-config.mjs --gate`. Fix config until it passes.

### Step 1 — T0: code is business-correct (HARD GATE)
- **GATE-A**: ensure invariants for the target module are written + approved by the human. Run `node verify-workflow/check-invariants-approved.mjs --gate --id-prefix <PREFIX>`. If it fails, STOP — ask the human to approve invariants (do NOT self-approve).
- Audit logic: spawn parallel multi-lens finders (correctness/race/state-completeness/cross-module/security), then a fresh adversarial verifier per finding. Fix confirmed bugs.
- Add integration/property tests that assert **OUTCOME** (not "method called"). Run mutation on critical scope (`mutation_critical_cmd`, break-threshold ≠ null).
- **GATE-B** (HARD STOP): human compares test-asserts vs invariants. Wait.

### Step 2 — T1: diagram matches code (loop until dry)
- Completeness-enumerate the ground truth **cross-module** (route enumerator / enum source / AST) — do not trust a single grep pattern; read whole service files when in doubt.
- Draw the diagram (PlantUML/Mermaid/DBML per `PROJECT.yaml` toolchain).
- Spawn the **diagram-verifier** subagent (this plugin) to diff diagram-vs-code and report MISSING/EXTRA/WRONG. Verify its findings with tools. Fix. Loop until ≥2 consecutive 0-finding rounds.

### Step 3 — T2: notation + readability
- Render to PNG. **Read the PNG** and check the vision checklist (correct nodes / logic-flow / UML notation / no overlap / not cluttered / readable on the target page / consistent terms / B&W-safe).
- Fix the source + re-render until it passes.

### Step 4 — close
- **GATE-D** (HARD STOP): present the PNG, ask the human to sign that it represents their understanding and is sufficient. Do not rubber-stamp.
- Update `diagram-manifest.yaml` status to `signed`. Run `node verify-workflow/check-ledger.mjs`.

Be honest about residual risk (FRAMEWORK §10). Never claim "0 errors".
