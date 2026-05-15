---
name: audit-plan
description: "Audit a plan file against the actual codebase. Loops until 0 new gaps found. Cross-checks gap coverage, dead code cleanup, and test completeness. Sub-commands: gaps, verify, tests."
allowed-tools: Read Grep Glob Edit Write Bash
argument-hint: "[gaps|verify|tests] [path to plan.md]"
---

# Skill: Audit Plan

Audit a plan file (migration, refactor, feature, etc.) against the actual codebase.

## Sub-commands

Parse `$ARGUMENTS` to determine which mode to run:

| First token | Mode | What it does |
|-------------|------|-------------|
| _(empty or path)_ | **Full audit** | Loop scan until 0 new gaps. Default mode. |
| `gaps` | **List gaps** | Read plan, list all `### Gap` entries as a numbered table. No scanning. |
| `verify` | **Run cleanup checklist** | Execute every `grep` command in the plan's Dead Code Removal Checklist. Report pass (0 matches) or fail (N matches) per command. |
| `tests` | **Check test coverage** | For each phase, count `- [ ]` test cases. Flag phases with 0 tests. Flag gaps that have no corresponding test case. |

If the remaining token after the sub-command is a file path, use it as the plan file.
Otherwise, auto-detect:
1. **Project-level**: `.claude/plans/*.md` in the current working directory (most recent). Use this.
2. **No project-level plans found**: Do NOT fallback to global `~/.claude/plans/` — those may belong to other projects. Instead, report error:
   `"No plan files found in .claude/plans/. Specify a path: /audit-plan <path>"`
3. If multiple project-level files exist, pick the most recently modified one. Log which file was selected.

---

## Mode: Full Audit (default)

### Step 1: Locate and read the plan file

Find the plan file using the priority in Sub-commands section above.
Log which file was selected and why (e.g., "Using project-level plan: .claude/plans/migration.md").

Read the plan file. Identify:
- What type of change it describes (migration, refactor, new feature, etc.)
- What the "old" and "new" patterns are (e.g., old library → new library)
- What phases/steps the plan defines
- What gaps, grep commands, and test cases already exist

### Step 2: Run the audit loop

Repeat until a round finds 0 new gaps.

#### Step 2a: Scan the codebase

Adapt the scan to the plan type. Common categories to grep for:

| Category | Examples |
|----------|---------|
| Old library imports | `from 'old-lib'`, `require('old-lib')` |
| Old API / function calls | Deprecated hooks, removed methods |
| Old type references | Types or interfaces from the old library |
| Config references | Bundler, compiler, package manifest, env, CI config |
| Side effects in state logic | `localStorage`, `window`, non-deterministic calls |
| Cross-cutting files | Files touching 2+ modules being changed |
| Name collisions | Same export name with different semantics in old vs new |
| Direct imports bypassing barrels | Relative imports to old files instead of barrel re-exports |
| Stale comments | Comments referencing the old library or architecture |
| Build artifacts | Path aliases, middleware configs, plugin references |

#### Step 2b: Cross-check findings against the plan

For every pattern found in Step 2a, verify the plan contains all three:
1. A **Gap entry** (`### Gap N:`) describing the issue and resolution
2. A **grep command** in the cleanup checklist (if the pattern must be removed)
3. A **test case** (`- [ ]`) in the relevant phase's test list

If any of the three is missing, mark it as a new gap.

#### Step 2c: Update the plan if new gaps found

For each new gap:
- Add a `### Gap N:` entry with: file path, line number, description, owning phase, recommended fix
- Add a grep command to the cleanup checklist if applicable
- Add a `- [ ]` test case to the appropriate phase
- Report: `"Round X: found Y new gaps. Continuing..."`

#### Step 2d: Stop if 0 new gaps found

Report final statistics and stop the loop.

### Step 3: Print summary

```
| Metric              | Count |
|---------------------|-------|
| Gaps covered        | N     |
| Test cases          | N     |
| Grep verify commands| N     |
| Rounds to converge  | N     |
| Status              | COMPLETE |
```

---

## Mode: gaps

List all existing gaps in the plan as a table. Do NOT scan the codebase or add new gaps.

### Output format

```
| # | Gap | Phase | Has grep? | Has test? |
|---|-----|-------|-----------|-----------|
| 1 | description... | Phase N | ✅/❌ | ✅/❌ |
```

Report totals: N gaps, N with grep, N with test, N missing either.

---

## Mode: verify

Execute every grep command found in the plan's Dead Code Removal / Cleanup Checklist sections against the actual codebase.

### Steps

1. Extract all lines starting with `grep` from the plan file.
2. Run each command in the project root directory.
3. For each command, report:
   - **PASS** (0 matches) — old pattern fully removed
   - **FAIL** (N matches) — old pattern still present, list file:line

### Output format

```
| # | Pattern | Result | Matches |
|---|---------|--------|---------|
| 1 | grep -rn "old-lib" | PASS | 0 |
| 2 | grep -rn "useOldHook" | FAIL | 3 |
```

Report totals: N commands, N pass, N fail.

---

## Mode: tests

Audit test coverage completeness per phase and per gap.

### Steps

1. Read the plan. For each phase, count `- [ ]` items in its test checklist.
2. For each `### Gap N:`, check if there is at least one `- [ ]` test case that references it (by gap number, keyword, or file path).
3. Flag:
   - Phases with 0 test cases
   - Gaps with no corresponding test case
   - Test cases that reference files no longer in the codebase

### Output format

```
| Phase | Test cases | Status |
|-------|-----------|--------|
| Phase 1 (Auth) | 11 | ✅ |
| Phase 2 (UI) | 5 | ✅ |
| Phase 3 (Cart) | 0 | ❌ MISSING |
```

```
Gaps without test coverage: Gap 12, Gap 15
Orphaned test cases (file not found): 0
```

---

## Rules (apply to all modes)

1. **Never skip a finding.** If grep finds it in the codebase, the plan must account for it.
2. **Every gap must have** a test case verifying the fix AND a grep command verifying cleanup.
3. **Cross-cutting files** (touching 2+ modules) must have an explicit ordering rule in the plan.
4. **Non-component code** (utilities, services, scripts accessing shared state outside the normal call flow) must have dedicated test cases — they fail silently.
5. **Build and config files** must appear in the cleanup checklist.
6. **Stale comments** referencing removed code must be in the cleanup grep list.
7. **Be proactive.** If you spot a potential bug (name collision, race condition, type mismatch) while scanning, add it as a gap immediately.
