# Audit-Plugin Improvement Proposals

> Self-audit log. Per SKILL.md Stage 7, every `[OUT-OF-CRITERIA]` finding must produce a criteria-update proposal here.

Generated: 2026-06-10 (v1.0.0 — dogfood round 2)

## Dogfood Round 2 Result

**0 HIGH** (round 1: 2), 5 MEDIUM, 12 LOW — all fixed same-session. Key structural lesson: **M1 — the dual criteria copies re-drifted immediately despite round 1's "update both copies and re-verify" rule.** Discipline does not beat entropy; structure does. Fix: the 7 criteria + floor rule + severity rubric now live in exactly ONE place (the canonical prompt block in reviewer-prompts.md); SKILL.md Stage 1 only points there. Other fixes: on-disk findings ledger `.claude/audit-plugin-ledger.md` (compact/interruption-safe, created Stage 1, deleted Stage 7, doubles as concurrent-audit lock); confirmation round counts toward the hard cap; README canonical pointer; ledger status `rejected-by-user` added; placeholder unification; cost disclosure moved to Stage 0. Round-1 bookkeeping note: F24/F25 were LOW `[OUT-OF-CRITERIA]` (2H+9M+12L enumerated +2 OOC = 25); "all 25 fixed" = immediate symptoms — P-1's criterion extension remains PROPOSED below.

---

Generated: 2026-06-10 (v1.0.0 — dogfood round 1, fresh reviewer with the plugin's own canonical prompt)

## Dogfood Round 1 Result

2 HIGH + 9 MEDIUM + 14 LOW found; **all 25 fixed in the same session** (user-approved "fix all"). Highlights:

- **F1 (HIGH, fixed):** reviewer-prompts.md header claimed the fresh-reviewer prompt covers "Stage 1 and Stage 5" while SKILL.md wrote Stage 1 as lead-executed — two files asserted different architectures. DECISION: Stage 1 = lead in-context (builds orchestration context); dispatched reviewers are Stage 5 only.
- **F2 (HIGH, fixed):** the canonical prompt's scope clause ("read only within [plugin-path]") made its own criterion 3 (cross-plugin collision, loading-mechanism reachability) unexecutable. Scope now carries an explicit read-only exception. Empirical evidence: the round-1 dispatch itself had to be hand-patched.
- **F3–F6 (MEDIUM, fixed):** criteria copies had already drifted (SKILL.md vs prompt); severity rubric was undefined while the stop criterion counts severities; "new finding" was undefined (deferred findings would burn all 4 rounds); round ≥2 findings bypassed Stage 2 validation. Added: synced criteria, explicit rubric in both copies, findings ledger + NEW definition, Stage-2 routing for round ≥2 findings.
- **F7–F11 (MEDIUM, fixed):** zero-findings path, full-rejection/abort path, unrestricted `rm` grant in the benchmark example, canonical example violating its own MSYS caveat (now stdin form), Stage 6 user-consent gate.
- **F12–F23 (LOW, fixed):** allowedTools arg form, tag-stripping before validation, WebFetch URL + high-stakes definition, README relative path, cost-figure canonical pointer, WebSearch removed from allowed-tools, test-artifact carve-out, git-status rule promoted to SKILL.md Ground Rules, trigger disambiguation vs /audit-plan, agents/commands-only classification bucket, "should"→"must" for regression tests, non-writable-root fallback (`.claude/audit-plugin-proposals.md`).

**Process note:** the `[OUT-OF-CRITERIA]` floor-not-ceiling mechanism fired on its first run (2 findings) — the self-update loop works.

## Criteria-update proposals (from [OUT-OF-CRITERIA] findings)

- **P-1 (from F25, name collision `improvement-proposals.md` vs pipeline-retrospective's project-level file):** extend criterion 3 with **artifact-name collision** — output files/state files a plugin writes must not collide with other installed plugins' artifacts (compare against the artifact names other plugins document). Status: PROPOSED — immediate symptom fixed via Stage 7 note; criterion extension pending next criteria revision.
- **P-2 (from F24, deprecated `onerror`):** no criteria change needed — deprecated-API usage in bundled scripts/examples already fits criterion 6; recorded here as a reminder that examples count as "scripts" for criterion 6 purposes.
