# audit-plan

Audit plan files (migration, refactor, feature) against the actual codebase.

## Features

- **Full audit**: Loop scan until 0 new gaps found (hard cap 3 rounds). **Writes into the plan file**: every confirmed gap gets a gap entry and a test case; a cleanup grep command is added only when the gap involves a pattern that must be removed (Rule 2 in SKILL.md).
- **Gap listing**: `gaps` — list all gap entries as numbered table (read-only)
- **Verify cleanup**: `verify` — execute grep commands from Dead Code Removal Checklist (read-only; unsafe lines are skipped, never executed)
- **Test coverage**: `tests` — count test cases per phase, flag missing coverage (read-only)

> Canonical mode definitions live in [SKILL.md](skills/audit-plan/SKILL.md) — this list is a summary. The plugin `description` in [.claude-plugin/plugin.json](.claude-plugin/plugin.json) is the canonical copy; the `audit-plan` entry in the repo's `marketplace.json` mirrors it verbatim, while the repo README's plugin-table row is a free-form summary (not required to match verbatim).

> Wrong-format handling (summary — SKILL.md Step 0 and the full-audit guard are canonical): a plan with **none** of the gap-tracking markers aborts with a pointer to `/plan-workflow:verify-plan` (the right tool for `/plan-workflow:plan-refactor` 8-phase plans); a plan that has other gap-tracking markers (checkboxes or cleanup greps) but no `### Gap` entries instead triggers a confirmation prompt (full-audit mode only — each read-only mode runs when its own marker is present and otherwise reports "nothing to audit") before any gap structure is initialized. The redirect target needs the **plan-workflow** plugin (optional; only relevant for that format).

## Usage

```
/audit-plan:audit-plan                    # Full audit (auto-detect plan file)
/audit-plan:audit-plan gaps               # List gaps only
/audit-plan:audit-plan verify             # Run cleanup checklist
/audit-plan:audit-plan tests              # Check test coverage
/audit-plan:audit-plan path/to/plan.md    # Audit specific file
/audit-plan:audit-plan gaps path/to/plan.md  # Sub-command + explicit file
```

> Manual-invocation only (`disable-model-invocation: true`): invoke explicitly with `/audit-plan:audit-plan ...` — Claude does not trigger this skill automatically, because the default mode edits the plan file.
