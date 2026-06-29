# Personal Guidelines (Global)

> Loaded into EVERY session. Keep it short — if removing a line still leaves Claude doing the right thing, that line should go.

> 📝 **First-person template convention**: This file is user-config that Claude Code loads into EVERY session. The pronoun "I" in the content below = the **USER** (whoever copies this file into `~/.claude/CLAUDE.md`), "you" = **Claude**. The first-person voice is intentional, following the Claude Code prompt convention — it helps Claude read the instructions as if speaking to itself. When reading the repo for the first time (before copying), substitute "I" = yourself to grasp the intent correctly.

## Language

- Default **Vietnamese**, keep technical terms in English. Details in [`communication.md` §Vietnamese vs English](rules/communication.md).

## Working Style

- When a plan is needed → the single threshold lives in [`plan.md` §When to Create a Plan](rules/plan.md). Plan needed → **draft the plan, wait for my approval**; each step in the form `[Step] → verify: [check]`.
- Unsure of intent → **ASK**, don't guess. One question beats 10 minutes of fixing the wrong thing.
- After a change → **SELF-CHECK** test/lint/typecheck if available. Don't report "done" before verifying.
- I say "ultrathink" → an official keyword; Claude Code adds an in-context instruction requesting deeper reasoning for that turn (the effort level does NOT change). The phrases "think"/"think hard"/"think more" are NOT keywords — treat them as plain text.
- Subagent results, git state, external deps → see details in [`verification.md`](rules/verification.md).

## Response Style

- **Concise**. Diff/code FIRST, explanation AFTER. Details in [`communication.md`](rules/communication.md).

## Code

- Details in [`coding-standards.md`](rules/coding-standards.md). Summary: read before writing, follow codebase conventions, YAGNI, surgical changes, don't add a dependency without asking.

## Git

- Do NOT `git commit`/`git push` unless I ask explicitly — there must be an explicit verb: `commit`, `push`, `ship`, `merge`, or invoking [`/commit`](plugins/commit-commands/skills/commit/SKILL.md). Vague phrases like "save it", "looks good", "done" → NOT enough, ask again.
- Details (add, force, reset, attribution, branch) in [`git.md`](rules/git.md).

## Security

- Details in [`security.md`](rules/security.md).

## Preferred Workflow

- When a plan is needed (per the ["Working Style"](#working-style) rule above) → prefer proposing Plan Mode (`Shift+Tab×2 from default mode`) or `/plan` over writing the plan inline in the response.
- Investigating a broad codebase → propose a subagent ("use a subagent to investigate ...") to keep the main context clean. If not using a subagent → narrow the scope (read only the files/dirs needed, don't explore everything).
- When spawning a subagent → the prompt MUST contain all 4 components: **what** (the specific task), **scope** (which files/dirs, what not to touch), **output format** (what shape to return), **done criteria** (what counts as finished).
- Large refactor → split into small, independently revertable commits.
- Hard bug → reproduce first, write a failing test, then fix (details in coding-standards.md §Testing, §Verification During Refactoring).

## When Errors Occur

- Read the error message carefully BEFORE guessing.
- Two failed fixes in a row → STOP, propose `/clear` + reprompt with what you've learned. Don't spam corrections into a dirty context.

## Context Window Management

- Watch `/context` regularly. **<40% safe (30-40% sweet spot)**, **40-60% dumb zone begins**, **60-77% wrap up actively**, **>77% after auto-compact you MUST act**. Community-curated thresholds; details + source in [`docs/REFERENCE.md` §16.2](docs/REFERENCE.md).
- Finished a phase (auth done, refactor done) → propose `/compact` right away, don't wait for auto-compact to fire (~77% of the 200k window = ~155k tokens, per [Boris Cherny — Anthropic, Claude Code lead](https://x.com/bcherny/status/1977163445205450783); newer docs say default ~95% — may have changed across versions).
- Before compact/clear → I'll ask you to write a handoff brief; use the [`/handoff`](plugins/session/skills/handoff/SKILL.md) skill.
- Quick question that doesn't need to be saved to history → I use `/btw`.

## Compact Instructions

When `/compact` runs (manual or auto), the summary MUST keep:

1. **Files changed** (full path) and the **reason** for each.
2. **Architectural decisions** settled (with a one-sentence rationale).
3. **Build/test/lint commands** confirmed to work with this project.
4. **Constraints** (performance, compatibility, security) that have been established.
5. **Work in progress** + a clear **next step**.
6. Drop: long tool output, dead-end debugging, back-and-forth rephrasing.

## Extended Rule References

> Every file in `~/.claude/rules/` (coding-standards.md, communication.md, git.md, plan.md, security.md, verification.md) auto-loads every session — no `@import` needed.
