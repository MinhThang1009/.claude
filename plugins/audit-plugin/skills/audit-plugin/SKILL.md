---
name: audit-plugin
description: This skill should be used when the user asks to "audit a plugin", "review plugin quality", "audit plugin content", "đánh giá chất lượng plugin", "audit plugin này", "kiểm tra chất lượng plugin", or wants a multi-round independent content audit of a Claude Code plugin (plugin.json, SKILL.md, references, examples, hooks, commands). Runs deep review → independent validation → user-gated fixes → fresh-review convergence loop → optional headless benchmark. Not for plan files (use /audit-plan) or application source code (use /audit-logic).
version: 1.0.2
argument-hint: <plugin-path>
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write, Task, Skill, AskUserQuestion, WebFetch]
---

# Audit Plugin Skill

Audit the content quality of a Claude Code plugin through multiple independent review rounds, fix only what the user approves, and loop until convergence. The target is the plugin path passed as the skill argument (`<plugin-path>`); if no argument was given — or the path does not exist, or it contains no `.claude-plugin/plugin.json` (not a plugin) — stop and ask the user before proceeding.

**Core principles:** every claim must carry a verbatim quote + `file:line`; finders maximize coverage, a validator filters false positives afterward; whoever fixes never signs off on their own fixes; the user approves the scope and every design decision.

---

## Stage 0 — Scope

1. List 100% of the plugin's files (plugin.json, README, SKILL.md, references/, examples/, hooks/, commands/, agents/). Print the list so the user sees the audit scope.
2. Classify the plugin to decide whether Stage 6 applies:
   - **Executable workflow** (a skill that drives a pipeline, has hooks/scripts) → benchmark applies.
   - **Content-only** (output style, rules, pure reference) → skip Stage 6 and say why.
   - **Agents/commands-only** (ships agents or commands but no pipeline-driving skill) → treat as content-only for Stage 6, unless a command is itself an executable pipeline — then benchmark that command.
3. Check the plugin is reachable through EVERY loading mechanism the repo actually uses — `.claude-plugin/marketplace.json`, `enabledPlugins` in settings, sync configs (e.g. a load list consumed by a sync script), junctions/symlinks. Marketplace registration alone proves nothing if the repo loads skills another way; a gap in any one mechanism is a structural finding — record it now and carry it into the Stage 1 findings list (it enters the ledger with everything else).
4. Tell the user the expected cost BEFORE Stage 1 begins: ~80–95k tokens per fresh-review round (up to 4 rounds), plus the benchmark figures in `references/benchmark-guide.md` §4 if Stage 6 may apply.
5. **Apply pending self-updates** — read THIS plugin's own `improvement-proposals.md`; if criteria-update proposals are marked PROPOSED, ask the user once whether to apply them to the canonical block before this audit begins, then mark each APPLIED or DECLINED (dated). This step is the trigger that closes the self-update loop — without it the loop only ever writes.

## Stage 1 — Deep Review (7 criteria)

**Stage 1 is performed by you (the lead), in-context** — it builds the understanding needed to orchestrate every later stage. Dispatched zero-context reviewers run the same criteria only at Stage 5. Read 100% of the files. Bundled scripts (hooks, helpers) may be exercised with adversarial input **in a temp dir only** — test artifacts like caches are acceptable; never modify tracked plugin files (same rule as criterion 6 in the canonical block; that wording wins).

**The 7 criteria, the floor-not-ceiling rule, and the severity rubric are defined ONCE — inside the fresh-reviewer prompt block in `references/reviewer-prompts.md`.** Read that block in full now and apply it as written: Stage 1 (lead) and Stage 5 (dispatched) review against the identical text; there is no second copy to drift. Criteria changes happen in that one place only (see Stage 7).

For high-stakes audits (the plugin gates other work, ships hooks, or will be distributed), WebFetch the current Claude Code docs — `https://code.claude.com/docs/en/plugins` and `https://code.claude.com/docs/en/skills` — and cross-check the canonical criteria before starting. The local criteria are a cache; the docs are the source.

Each finding: `file:line` + verbatim quote + severity per the canonical rubric. Suspected but unconfirmed → still report, tagged `[UNCERTAIN]`. Coverage matters more than precision — Stage 2 filters.

**When Stage 1 completes, write the findings list to the audit ledger** — `.claude/audit-plugin-ledger.md` at the project root (created here, maintained through Stage 5, deleted at Stage 7). Never keep it chat-only: it must survive `/compact` and session death; re-read it when resuming. The ledger holds ALL resume-critical state: the findings with statuses, the Stage 0 classification (benchmark applies or not), and the fresh-review round counter (rounds used / 4). If the file already exists, another audit may be in flight — stop and ask the user.

## Stage 2 — Independent Validation

Every finding must pass independent verification before any fix is proposed (sole exception: the round ≥2 fast-path defined in Stage 5):

- **>5 findings** → dispatch the `finding-validator` agent.
- **≤5 findings** → use the `/validator` skill.
- **Neither available** → dispatch a general-purpose agent with the prompt in `references/reviewer-prompts.md` §Validator fallback.

The validator receives the finding list (file + line + claim) but NOT the Stage 1 reasoning or conclusions — strip `[UNCERTAIN]` and severity tags first; they are confidence signals that bias verdicts. Verdict per finding: CONFIRMED / FALSE POSITIVE / PARTIALLY TRUE, each with a quote from disk. **Report retracted or overstated claims to the user honestly** — before proposing any fix. Record every verdict in the ledger (refuted findings included — Stage 5's NEW-matching depends on them).

**Zero findings** (Stage 1 found nothing, or Stage 2 refuted everything): skip Stages 3–4 and run ONE fresh-review round (Stage 5) as confirmation — a clean first pass is more often a coverage failure than a clean plugin. The confirmation round counts toward the Stage 5 hard cap. If it returns 0 HIGH/MEDIUM → LOW-only output counts as clean (record the LOWs in the ledger as deferred polish) — proceed to Stage 6 if it applies per the Stage 0 classification (with user consent), otherwise Stage 7. If it returns any HIGH/MEDIUM → re-enter the normal path (Stage 2 validation → Stage 3 gate → Stage 4).

## Stage 3 — Gate: User Approval

Present to the user: the validated findings table (severity, location, proposed fix) plus every **design decision** they must settle (use AskUserQuestion, each question with a recommended option and the reason). Design decisions include: changes to workflow behavior, trade-offs between two valid fixes, and anything touching files outside the plugin.

**Wait for the user to approve the scope before editing anything.** No reply → no edits.

If the user rejects ALL findings or aborts the audit: skip Stages 4–6 and go directly to Stage 7 — record every finding as rejected/deferred with the user's reasons. Never run a fresh review of unchanged disk.

## Stage 4 — Fix

- Every change traces back to a specific approved finding. No drive-by improvements outside the scope.
- A modified script/hook requires a written or updated test that passes before the fix counts as done — and each script defect fixed in this audit must gain a regression test as part of that done-criteria. If the audited plugin has no test harness: document the expected behavior in the commit/proposal instead and mark the fix explicitly unverified.
- Validate JSON files after editing (`python -m json.tool`).
- Do NOT `git commit` unless the user explicitly orders it.

## Stage 5 — Convergence Loop (fresh review, hard cap 4 rounds)

After each fix batch, spawn a **fresh reviewer**: a general-purpose agent with zero context — it does NOT know what was fixed and does NOT receive prior findings (feeding it the old list recreates the previous round's blind spots). It only reads the current state on disk and reruns the Stage 1 criteria, using the prompt template in `references/reviewer-prompts.md` §Fresh reviewer.

- **Findings ledger:** maintain the on-disk ledger `.claude/audit-plugin-ledger.md` (created at Stage 1) — every finding ever reported, with status: confirmed-pending (validated, awaiting gate/fix) / fixed / deferred-by-user / rejected-by-user / refuted / unfixed-at-cap. Stage 2 verdict mapping: CONFIRMED → confirmed-pending; FALSE POSITIVE → refuted; PARTIALLY TRUE → confirmed-pending with the valid part restated and the incorrect part noted. Update the round counter here after every fresh round. A fresh round's finding is NEW only if it matches no ledger entry by location + substance (wording may differ between rounds). Re-reports of deferred or rejected findings are not new and do not block convergence — list them in the final report as "still open (deferred)" or "rejected by user" respectively.
- New findings → verify them against disk yourself first (never trust agent self-reports), then run them through Stage 2 validation before fixing. Exception (**the round ≥2 fast-path**): 1–2 findings whose defect is directly visible in the quoted line may be verified by direct Read/Grep alone — state which path you took. Then ALWAYS Stage 3: present the round's confirmed findings to the user for approval — round ≥2 findings are NOT pre-approved by the original scope. Stage 4 only for what the user approves.
- **Stop criterion:** a round reports 0 new HIGH and 0 new MEDIUM.
- **Hard cap: 4 fresh-review rounds.** If the cap is hit with MEDIUMs remaining → fix the confirmed ones, then STOP and report honestly which parts have passed independent review and which have not. If the final round reports a new HIGH → present it at Stage 3 like any finding (the user gate still applies; if the user rejects it, record `rejected-by-user` and state plainly that a known HIGH ships unfixed). On approval: fix it, verify that single fix with a targeted validator pass instead of a full round, then STOP. Do not run a 5th full round on your own initiative.
- Practical convergence signal: finding quality shifts from "reproducible operational defects" to "wording-level judgment calls".

## Stage 6 — Benchmark (executable-workflow plugins only, with user consent)

The benchmark costs real money — give the user the cost estimate from `references/benchmark-guide.md` §4 and run it only on explicit approval. Build a controlled fixture and run the plugin's full pipeline headless, scoring by hand-verified evidence. Fixture design, the 2-stage run (human gate → resume), Windows/headless caveats, and the scoring rubric: see `references/benchmark-guide.md`. For content-only plugins, state "Stage 6 not applicable: <reason>" and skip.

## Stage 7 — Record

- Learnings + unapplied proposals → `improvement-proposals.md` at the audited plugin's root (create it if absent; if it exists, prepend a new entry — never edit historical entries). If the plugin root is not writable (e.g. a marketplace cache install), write to the project's `.claude/audit-plugin-proposals.md` instead and say so. Note: this per-plugin file is distinct from the project-level `.claude/improvement-proposals.md` that subagent-system's pipeline-retrospective writes — when both exist, name which one you mean.
- **Criteria self-update rule:** every finding tagged `[OUT-OF-CRITERIA]` — and every defect discovered by real-world events that no criterion would have caught — MUST produce a proposal to update **this plugin's own** criteria/prompts, written to `improvement-proposals.md` at the audit-plugin root (in addition to the audited plugin's record). The criteria list stays alive only through this loop; a criteria set that never grows is a systematic blind spot shared by every future review round. Criteria changes are applied in exactly ONE place — the canonical block in `references/reviewer-prompts.md`; SKILL.md only points there, so there is nothing to sync.
- Delete `.claude/audit-plugin-ledger.md` — the audit is closed; an orphaned ledger blocks the next audit's Stage 1.
- Final report to the user: per-round summary table (HIGH/MEDIUM/LOW per round), what was fixed, what was deferred/rejected with reasons, test status, and the steps that belong to the user (commit, session restart if the plugin ships hooks).

---

## Ground Rules (apply throughout)

- **No unsourced claims.** Every statement about the plugin's content carries a quote + location. No quote = not reportable.
- **The fixer never self-certifies.** A fix batch only counts as accepted after a fresh reviewer passes it (Stage 5), or the user explicitly accepts the risk (hard cap).
- **Verify before relaying.** Findings from any agent → check them yourself with Read/Grep before reporting to the user or acting on them.
- **Correct the record openly.** When a validator/reviewer refutes one of your own claims, tell the user plainly — never let it slide.
- **Plugins that ship hooks** → remind the user: hooks only take effect from the next session (they load at startup).
- **After any dispatched agent returns** (when the repo has git): check `git status`/`git diff` — unexpected working-tree changes from a read-only agent mean stop and investigate before continuing. No git → compare key files by content.
- **Reference costs**: token figures live in Stage 0 step 4 (canonical); benchmark dollar figures in `references/benchmark-guide.md` §4 (that file wins on divergence).
- **If the Task tool is unavailable** (e.g. running as a subagent — nesting is blocked): STOP and tell the user. The convergence architecture cannot run; do not silently degrade to self-review.

---

## Additional Resources

- **`references/reviewer-prompts.md`** — canonical verbatim prompt templates for the fresh reviewer and the validator fallback, plus context-isolation rules. These prompts are the single source — use them verbatim, replacing only the placeholders.
- **`references/benchmark-guide.md`** — fixture design, 2-stage headless run, Windows caveats, the 6-dimension scoring rubric, and the hand-verification checklist.
