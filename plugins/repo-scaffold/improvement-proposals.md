# repo-scaffold — Improvement Proposals

> Audit log (audit-plugin). User-relevant learnings + deferred polish.

Generated: 2026-06-29 (2nd audit-plugin run — content-only, Stage 6 N/A; converged in 1 fresh-review round)

## Result (2nd audit)

0 HIGH, 0 surviving MEDIUM. Round 1 fresh review returned 0 verified-new HIGH/MEDIUM → converged in a single round (the plugin was already clean from the 1st audit). The lone reviewer MEDIUM (CoC dead-link) was downgraded to LOW on verification — the recovery instruction already exists at `SKILL.md:45`. A reviewer LOW (`fetch-metadata@v3` "behind current major") was refuted — v3.1.0 IS the current major.

## Fixed

- F1 (MEDIUM): README structure-tree workflow list now includes `auto-merge` (was drifted vs SKILL.md Resources).
- F3 (LOW): README "What it does" now enumerates the optional workflow set (was only CI + release-on-tag).
- F2 (LOW, security): SKILL.md step 4 now notes SHA-pinning as the hardened action-pin option (templates keep readable major tags; Dependabot updates both forms).
- R1-F2 (LOW): CONTRIBUTING.md asset gained a scaffold-note comment to drop the CoC link when no CODE_OF_CONDUCT.md is generated (belt-and-suspenders with SKILL.md:45).
- Version bumped 0.1.0 → 0.1.1 (plugin.json + SKILL.md) to disambiguate the stale install cache.

## Deferred / accepted (unchanged from 1st audit)

- DEF-1 `{{RELEASE_TYPE}}` in the step-3 fill set (only used by step-4 release-please.yml; harmless).
- DEF-2 plugin.json vs marketplace.json `description` differ (both accurate; registry duplication).
- DEF-3 references/readme.md vs README-header.md align-element lists differ (both correct).
- DEF-4 SECURITY.md "latest release on `main`" phrasing.
- DEF-5 no automated tests for workflow templates (they are templates; shell blocks probed manually).
- R1-F6 `.gitattributes` export-ignore leaves root community docs in the `git archive` release zip — acceptable-by-design (asset comment "Adjust per project").

## Honest closure

The final LOW fix (R1-F2 CONTRIBUTING comment) was applied AFTER round 1 converged and was NOT put through a further fresh round — it is a single invisible HTML comment; risk negligible. All HIGH/MEDIUM-relevant content passed the round-1 zero-context review. USER ACTION (refresh install cache to 0.1.1) is recorded in the project-level `.claude/audit-plugin-proposals.md`.

---

Generated: 2026-06-28 (first audit-plugin run — 4 fresh-review rounds at the hard cap; content-only, Stage 6 benchmark N/A)

## Result

Converging severity across 4 zero-context rounds: R1 = 3 MEDIUM + LOWs → R2 = 1 MEDIUM → R3 = 1 MEDIUM → R4 = 1 MEDIUM. Every MEDIUM was fixed in its round. **0 HIGH across all rounds.** Severity composition shifted from real defects (invent-values, dangling refs) to consistency/contradiction polish (step numbers, author name, lifecycle summary) — the practical-convergence signal.

## Fixed — MEDIUM

- F1: SKILL.md `~/.claude/rules/git.md`/`security.md` references made conditional ("if present") so the plugin works when installed elsewhere.
- M-A: topics now derived from the detected stack + confirmed with the user (was an invent-values gap vs the "never invent" principle).
- M-B: `question` label created in github-setup.md; SUPPORT.md/issue config Discussions references marked "if enabled".
- M-C: `.gitattributes` gained `export-ignore` rules so release.yml's `git archive` comment is true.
- R2-1: github-setup.md "step 4" → "step 5" (Configure GitHub is step 5 after the workflows step was inserted).
- R3-1: author name unified to "Minh Thang" across plugin.json + LICENSE (matched marketplace.json).
- R4-1: README "How to use" lifecycle summary now includes the Commit step.

## Fixed — LOW

F2 (step-3 intro reworded to reflect mixed sources), F3 (`gh` added to README Requirements), F4 (no-GitHub-remote exception note), L-1 (labeler config header "v6"), L-2 (verify-major reminder covers every workflow action), L-3/R3-2 (README structure tree completed + pointer to SKILL.md), R2-2 (labeler `pull_request_target` rationale comment), R2-3 (labeler `documentation` glob tightened to avoid matching issue templates), R3-3 (CONTRIBUTING→CoC dead-link note).

## Deferred polish (recorded, not fixed)

- `{{RELEASE_TYPE}}` is listed in the step-3 fill set though it is only used by the step-4 `release-please.yml` asset (documented there; harmless).
- plugin.json vs marketplace.json `description` are different summaries (both accurate; inherent registry duplication with no canonical pointer).
- references/readme.md vs README-header.md enumerate the `align`-allowed elements slightly differently (`div/p/h1-h6` vs `+td/th`; both correct).
- SECURITY.md "latest release on `main`" phrasing (fine for single-stream projects).
- No automated tests for the bundled workflow templates (they are templates; the two non-trivial shell blocks — release create-or-upload, ci-success gate — were probed manually and behave correctly).

## Honest closure

R4-1 (the final-round MEDIUM) was fixed AFTER the 4-round hard cap, so it has NOT passed a subsequent independent fresh-review round (the cap forbids round 5). Risk is minimal: it adds the word "commit" to a prose lifecycle summary. Every earlier fix passed at least one later fresh round.

## Criteria self-update (audit-plugin)

No new criteria gap. The only `[OUT-OF-CRITERIA]` tag (CITATION.cff entity `name:` form) is schema-valid and acceptable for a generic scaffold — no change proposed to audit-plugin's canonical criteria.
