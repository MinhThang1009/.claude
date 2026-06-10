# Audit-Plugin Improvement Proposals

> Self-audit log. Per SKILL.md Stage 7, every `[OUT-OF-CRITERIA]` finding must produce a criteria-update proposal here.

Generated: 2026-06-10 (first external audit: plugins/audit-plan — 4 rounds + benchmark)

## External-audit learnings (audit-plan run)

P-3 and P-4 were APPLIED to the canonical block at this audit's Stage 0 step 5 — the self-update loop completed its first full cycle (propose → apply → criteria caught real findings: P-3 caught the drifted plugin.json/marketplace.json description pair in round 0).

**Criteria-update proposals:**
- **P-5 (from the benchmark's safety-filter rejection):** benchmark-guide §1/§2 should advise keeping adversarial/injection cases in a SEPARATE minimal fixture or stage — a plan/codebase containing injection strings can be rejected wholesale by model safety filters in headless runs, blocking the non-adversarial dimensions too. Observed: Stage B rejected until the fixture was sanitized; Stage A (which needed those lines) had already completed. Status: PROPOSED.
- **P-6 (recurring false positive):** two consecutive fresh rounds re-raised "space-separated `allowed-tools` may not parse", refuted both times by the docs ("Accepts a space- or comma-separated string, or a YAML list"). Add one line to the canonical prompt's criterion 3: frontmatter `allowed-tools` accepts space/comma/YAML-list forms — do not report the separator style alone as a defect. Saves a validator cycle every future audit. Status: PROPOSED.

---

Generated: 2026-06-10 (v1.0.2 — dogfood round 4, FINAL per hard cap)

## Dogfood Round 4 Result — audit CLOSED at hard cap

**0 HIGH (3rd consecutive round)**, 7 MEDIUM (2 [UNCERTAIN]), 9 LOW. Per the hard-cap rule: confirmed MEDIUMs fixed, then STOP — no 5th round. Fixes: M1 LOW-only confirmation round now routes as clean; M2 ledger now persists round counter + Stage 0 classification (resume actually works); M3 HIGH-at-cap passes the user gate like everything else; M4 ledger status vocabulary completed with Stage 2 verdict mapping (confirmed-pending / unfixed-at-cap added); **M5 self-update loop CLOSED — Stage 0 step 5 now applies/declines PROPOSED criteria updates at the start of every audit**; M7 invalid-argument path covered. LOWs: cost arithmetic made consistent, drifted pointered duplicate re-synced, stale "pending" note fixed, README documents the ledger artifact. M6 remains a USER action: refresh the installed cache (stale 1.0.0 copy) — bump to 1.0.2 makes the divergence unambiguous.

**Honest closure note:** this final fix batch (round 4 MEDIUMs/LOWs) has NOT passed an independent review round — the hard cap forbids a 5th. Risk assessed low (definitional/wording changes, each traceable to a quoted finding). Convergence series: 2H+9M → 0H+5M → 0H+5M → 0H+7M with severity composition shifting from architecture (round 1) to lifecycle bookkeeping (round 4). Per round 4's own [OUT-OF-CRITERIA] items, P-3/P-4 remain PROPOSED below — they will be offered for application at the next audit's Stage 0 step 5.

---

Generated: 2026-06-10 (v1.0.1 — dogfood round 3)

## Dogfood Round 3 Result

**0 HIGH** (2nd consecutive round), 5 MEDIUM, 13 LOW — MEDIUMs all fixed same-session: M1 round-≥2 findings now ALWAYS pass the Stage 3 user gate (closed the "needs no decision → edit without approval" bypass); M2 zero-findings path now routes through Stage 6 when applicable; M3 HIGH-at-cap branch defined (fix + targeted validator pass, no 5th round); M5 Stage 0 structural findings carry into the ledger; **M4 CONFIRMED by direct diff — the installed cache copy at `~/.claude/plugins/cache/.../audit-plugin/1.0.0` was the stale pre-round-2 content under the same version → bumped to 1.0.1 (user must update/reinstall the plugin so the cache refreshes).** Cheap LOWs fixed (fast-path named, token-cost canonical home, temp-dir clause pointer, scope grants for junctions + user-level configs, Task-unavailable stop rule, Stage 2 verdicts→ledger, no-test-harness branch, §4 retitled). Round-2 canonicalization verified working: "the duplicates that still exist all match verbatim today".

**Criteria-update proposals (from round-3 [OUT-OF-CRITERIA]):**
- **P-3:** extend criterion 5's boundary — duplication checks must include plugin-adjacent registry copies (e.g. plugin.json description verbatim-duplicated in marketplace.json) — same blind-spot class as P-1. **Status: APPLIED 2026-06-10** (Stage 0 step 5 of the audit-plan audit; canonical block updated).
- **P-4:** extend criterion 3 — detect dual-loading: the same skill reachable through two mechanisms at once (e.g. junction-synced user-level copy + marketplace plugin) duplicates the trigger surface. **Status: APPLIED 2026-06-10** (same session).

---

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
