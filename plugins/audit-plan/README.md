# audit-plan

Audit plan files (migration, refactor, feature) against the actual codebase.

## Features

- **Full audit**: Loop scan until 0 new gaps found
- **Gap listing**: `gaps` — list all gap entries as numbered table
- **Verify cleanup**: `verify` — execute grep commands from Dead Code Removal Checklist
- **Test coverage**: `tests` — count test cases per phase, flag missing coverage

## Usage

```
/audit-plan                    # Full audit (auto-detect plan file)
/audit-plan gaps               # List gaps only
/audit-plan verify             # Run cleanup checklist
/audit-plan tests              # Check test coverage
/audit-plan path/to/plan.md    # Audit specific file
```
