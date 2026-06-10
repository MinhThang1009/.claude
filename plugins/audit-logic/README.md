# audit-logic

Systematic logic audit workflow for any codebase module.

## What it does

Reads every line of source code in a target module, identifies real logic bugs (not style issues), fixes them with minimal changes, updates affected tests and documentation, and commits each fix independently.

## When to use

- Before drawing architecture diagrams — ensures diagrams reflect correct code
- After implementing a feature — verify business rules are correctly enforced
- When reviewing an unfamiliar module — systematic coverage without gaps
- When a bug report points to a module — root cause analysis via full read

## Usage

```
/audit-logic <module-path>
```

Example: `/audit-logic backend/src/modules/orders`

## What makes this different from code-review

`/code-review` reviews diffs. `/audit-logic` reads the entire module from scratch — no diff bias, no assumption that unchanged code is correct.

## Skills

- **audit-logic** — full audit workflow (discover → read all → analyze → completeness check → fix & verify, 1 commit/bug → update docs → summary)

## Requirements

- **Stop gate hook** — bundled with this plugin (`hooks/hooks.json` → `audit-logic-gate.sh` → `audit-logic-gate.py`). Blocks the **first** attempt to end the turn while phase gates in `.claude/audit-logic-state.json` are incomplete; a second consecutive stop is allowed (soft block — this is how the executor pauses to wait for user input; if another plugin's Stop hook blocked first, this gate may pass that cycle and re-arms next turn). Canonical wording of this soft-block contract lives in SKILL.md (Phase 3 waiting rule + Ground Rules) — if descriptions diverge, SKILL.md wins. Loads automatically when the plugin is enabled; requires `bash` and Python ≥ 3.6 on PATH (silently skips if Python is missing). If `bash` itself is missing (Windows without Git Bash), the hook command fails on every stop — noisy but non-blocking, and the gate never arms; install Git Bash or disable the plugin. If an audit is aborted midway, delete `.claude/audit-logic-state.json` — an orphaned state file re-triggers the block on the first stop of **every turn** in later sessions of that project. Before deleting, check no other concurrent session of the same project is mid-audit (the file may be theirs, not an orphan).
- **Related, NOT a dependency:** `verify-then-draw` — the trigger phrase "gate tầng 0" refers to running this audit as the tier-0 (logic-correctness) gate before drawing diagrams; the full diagram pipeline is `/verify-then-draw`. audit-logic works standalone without it.
- **`/pipeline-retrospective`** — provided by the `subagent-system` plugin, required by Phase 7. If it is not installed, the skill records the skip in the summary and still closes the gates (see SKILL.md Phase 7, Exception) — the session is never left permanently blocked.

## Maintenance

- The `description` in `.claude-plugin/plugin.json` is **canonical**; the `audit-logic` entry in the repo's `.claude-plugin/marketplace.json` must match it verbatim.
- Version bump checklist (required for ANY content change — the installed cache only refreshes on a bump): update `version` in `.claude-plugin/plugin.json` AND in `skills/audit-logic/SKILL.md` frontmatter, then update/reinstall the plugin.

## Headless / Windows notes

- Invoking from Git Bash: `claude -p "/audit-logic ..."` gets mangled by MSYS path conversion (the prompt arrives as `C:/Program Files/Git/audit-logic ...`, so the slash command never expands). Do **not** work around it with `MSYS_NO_PATHCONV=1` — that variable propagates into the session's child hook processes and breaks their path conversion instead. Safe options: invoke from PowerShell/CMD, or pipe the prompt via stdin.
- In headless (`-p`) mode the executor usually cannot create `.claude/audit-logic-state.json` (permission auto-deny), so the Stop gate hook never arms; the skill then tracks gates in its report instead. The gate enforcement is only fully active in interactive sessions.

## References (inside the skill)

- `references/reading-patterns.md` — async, transactions, guard clauses, dead code patterns
- `references/verification-techniques.md` — false-positive filtering, independent verification, commit format
