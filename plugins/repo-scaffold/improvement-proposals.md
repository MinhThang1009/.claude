# repo-scaffold — Improvement Proposals

> Audit log (audit-plugin). User-relevant learnings + deferred polish.

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
