# logic-audit

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
/logic-audit <module-path>
```

Example: `/logic-audit backend/src/modules/orders`

## What makes this different from code-review

`/code-review` reviews diffs. `/logic-audit` reads the entire module from scratch — no diff bias, no assumption that unchanged code is correct.

## Skills

- **logic-audit** — full audit workflow (discover → read all → analyze → fix → verify → update docs → commit)

## References (inside the skill)

- `references/reading-patterns.md` — async, transactions, guard clauses, dead code patterns
- `references/verification-techniques.md` — false-positive filtering, independent verification, commit format
