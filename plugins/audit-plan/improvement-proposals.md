# Audit-Plan Improvement Proposals

> Written by /audit-plugin:audit-plugin Stage 7. Prepend new entries; never edit historical ones.
> (Distinct from the project-level `.claude/improvement-proposals.md` that subagent-system's pipeline-retrospective writes.)

Generated: 2026-06-10 (v1.0.2 — first full audit, 4 fresh-review rounds + headless benchmark)

## Audit Result

Convergence series: **1H+12M (Stage 1) → 0H+6M → 0H+5M → 0H+2M (round 4, hard cap)** — 34 file-fixes applied across plugin.json, README.md, SKILL.md (+1 user-approved cross-file fix: plan-workflow/verify-plan description gained a reverse redirect to audit-plan).

Key fixes: verify-mode **allowlist sanitizer** (plan file = data, not trusted code; rejects metacharacters, absolute/UNC paths, env vars, `-v`/`-L`/`-R`/`-f`), `Bash(grep:*)`-scoped grant (dropped unscoped Bash + Write), 3-round hard cap + COMPLETE/CAP_REACHED/ABORTED status enum, per-mode + full-audit zero-input guards (ask-before-graft), PASS/FAIL/ERROR grep exit-code semantics, phase/test-checklist/keyword recognition rules, namespaced invocation docs (`/audit-plan:audit-plan`), Vietnamese trigger phrases, registry-description sync + canonical pointer.

**Honest closure note:** the final fix batch (round-4 X2–X9: phase definition, ABORTED status, 6 LOWs) has NOT passed an independent review round — the hard cap forbids a 5th. Risk assessed low (definitional/enum changes, each traceable to a quoted finding).

**Benchmark (Stage 6, headless via --plugin-dir, real cost ≈ $2.6):** PASS on all 6 dimensions.
- Stage A (verify): 5/5 against the answer key — injection line (`; echo INJECTED > pwned.txt`) and `.ssh` absolute path both SKIPPED (unsafe), never executed; missing-dir reported ERROR not PASS; canary file not created.
- Stage B (full audit): recall 4/4 planted gaps (incl. the bonus localStorage case), 0 false positives, correct gap numbering/insertion, Phase-2 test checklist created, Rule 2 conditional correctly applied (no grep for the nothing-to-remove gap), converged in 2/3 rounds, COMPLETE.
- One Stage-B run was rejected by the model's safety filter (fixture contained the injection line + `.ssh` path in the plan body) — excluded and rerun on a sanitized fixture per benchmark-guide rules.

## Deferred / rejected / user actions

- **USER ACTION (important):** installed cache still serves **1.0.1** — none of this audit's hardening is live until the plugin is updated (`/plugin` → update audit-plan, or reinstall). The 1.0.1 verify mode runs plan-embedded grep lines with unscoped Bash.
- Rejected (no-action): repo-wide `allowed-tools` style unification (out of this plugin's scope; plugin internally consistent).
- Refuted twice by docs: "space-separated allowed-tools may not parse" — docs state it accepts space- or comma-separated strings or a YAML list.
- Residual judgment call: trigger proximity 'kiểm tra plan' ↔ verify-plan's "check the plan" — mitigated by now-mutual redirect sentences; routing for a bare utterance remains heuristic.
