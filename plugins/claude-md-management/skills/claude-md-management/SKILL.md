---
name: claude-md-management
description: Audit and improve CLAUDE.md files in repositories. Use when user asks to check, audit, update, improve, or fix CLAUDE.md files. Scans for all CLAUDE.md files, evaluates quality against templates, outputs quality report, then makes targeted updates. Also use when the user mentions "CLAUDE.md maintenance" or "project memory optimization".
allowed-tools: Read Grep Glob Bash Edit
argument-hint: "[audit | revise | path to CLAUDE.md]"
context: fork
---

# CLAUDE.md Management — Audit & Improve

Two modes: **audit** (evaluate + improve) and **revise** (capture session learnings).

## Mode 1: Audit (default)

When `$ARGUMENTS` is empty or contains `audit`:

### Phase 1: Discovery

Find all CLAUDE.md files:

```bash
find . -name "CLAUDE.md" -o -name ".claude.md" -o -name ".claude.local.md" 2>/dev/null | head -50
```

| Type | Location | Purpose |
|------|----------|---------|
| Project root | `./CLAUDE.md` | Primary context (git, shared) |
| Local override | `./.claude.local.md` | Personal (gitignored) |
| Global | `~/.claude/CLAUDE.md` | Cross-project defaults |
| Package-specific | `./packages/*/CLAUDE.md` | Module-level in a monorepo |
| Subdirectory | Any nested dir | Feature/domain-specific context |

Claude auto-discovers CLAUDE.md files in parent directories — monorepo setup works automatically.

### Phase 2: Quality Assessment

Evaluate each file against 6 criteria:

| Criterion | Weight | Check |
|-----------|--------|-------|
| Commands/workflows | High | Are build/test/deploy commands present? |
| Architecture clarity | High | Does Claude understand the codebase structure? |
| Non-obvious patterns | Medium | Are gotchas and quirks documented? |
| Conciseness | Medium | Is there verbosity or obvious information? |
| Currency | High | Does it accurately reflect the current codebase? |
| Actionability | High | Are instructions executable and unambiguous? |

Scale: **A** (90-100), **B** (70-89), **C** (50-69), **D** (30-49), **F** (0-29).

Per-level scoring (example: Commands/workflows, max 20):
- **20**: complete build/test/dev/lint/deploy, copy-paste ready
- **15**: has main commands but missing 1-2 (e.g., only build, no test)
- **10**: present but vague or outdated
- **5**: only mentions "run tests" without a specific command
- **0**: none

**Red Flags** — flag immediately upon discovery:
- Commands that would fail if actually run
- References to files/dirs that have been deleted
- Copy-pasted from a template but never customized for the project
- TODO items never completed
- Duplicate information between multiple CLAUDE.md files in the same repo

### Phase 3: Quality Report

**ALWAYS output the report BEFORE modifying any file.**

```markdown
## CLAUDE.md Quality Report

### Summary
- Files found: X
- Average score: X/100
- Files needing updates: X

### Per-file evaluation

#### 1. ./CLAUDE.md (Project Root)
**Score: XX/100 (Grade: X)**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Commands/workflows | X/20 | ... |
| Architecture clarity | X/20 | ... |
| Non-obvious patterns | X/15 | ... |
| Conciseness | X/15 | ... |
| Currency | X/15 | ... |
| Actionability | X/15 | ... |

**Issues:** [list]
**Suggested additions:** [list]
```

### Phase 4: Targeted Updates

After the report, ask user for confirmation before editing.

Principles:
- **Only add useful information**: discovered commands, gotchas, package relationships, testing approaches, config quirks.
- **Avoid**: information obvious from code, generic best practices, one-off fixes, verbose explanations.
- **Show diff** for each change with a brief rationale.

### Phase 5: Apply

After user approves → use the Edit tool. Preserve the existing structure.

## Mode 2: Revise (capture session learnings)

When `$ARGUMENTS` contains `revise`:

### Step 1: Reflect

What context was missing that would have made Claude more effective?
- Bash commands used/discovered
- Code style patterns followed
- Testing approaches that worked
- Environment/config quirks
- Gotchas encountered

### Step 2: Draft

**Be concise** — 1 line per concept. CLAUDE.md is part of the prompt; brevity matters.

Distinguish between:
- `CLAUDE.md` → team-shared (git)
- `.claude.local.md` → personal (gitignored)

### Step 3: Show + Apply

Display diff + rationale for each addition. Only apply after user approves.

## What a good CLAUDE.md contains

**Principle**: concise, actionable, project-specific.

**Recommended sections** (only include what is relevant):
- **Commands**: build, test, dev, lint — copy-paste ready
- **Architecture**: directory structure, key modules
- **Key Files**: entry points, config files
- **Code Style**: project conventions (not generic best practices)
- **Environment**: required env vars, setup steps
- **Testing**: commands, patterns, frameworks
- **Gotchas**: quirks, common mistakes, non-obvious behaviors
- **Workflow**: when to do what (deploy process, PR flow)

## Templates by project type

When creating a CLAUDE.md from scratch, use the appropriate template:

### Minimal (small project, script, tool)
```markdown
# Project Name
[1-sentence description]
## Commands
\`\`\`bash
npm run dev    # Development server
npm test       # Run tests
\`\`\`
## Gotchas
- [Non-obvious behavior]
```

### Comprehensive (web app, API service)
```markdown
# Project Name
[1-2 sentence description]
## Commands
[build, test, dev, lint, deploy]
## Architecture
[Directory structure, key modules]
## Key Files
[Entry points, config, shared types]
## Code Style
[Project-specific conventions]
## Environment
[Required env vars, setup steps]
## Testing
[Commands, patterns, test DB setup]
## Gotchas
[Quirks, common mistakes]
```

### Monorepo Root
```markdown
# Monorepo Name
## Structure
[packages/apps listing with 1-line descriptions]
## Shared Commands
[Root-level scripts]
## Cross-package Patterns
[Shared types, build order, dependency rules]
## Per-package CLAUDE.md
[packages/api/CLAUDE.md, packages/web/CLAUDE.md — each package has its own file]
```

### Package/Module (in a monorepo)
```markdown
# Package Name
[Relationship to other packages]
## Commands
[Package-specific commands]
## Key Patterns
[Module-specific conventions]
```

## Verify currency

When assessing "Currency": run (mentally or actually) the documented commands — if they fail, flag as stale.

## Diff format for updates

Present each change as:

```markdown
### Update: ./CLAUDE.md

**Reason:** [1-line explanation of why this addition is helpful]

\`\`\`diff
+ [content to add — keep it short]
\`\`\`
```

## Common Issues to Flag

1. **Stale commands**: build commands that no longer work
2. **Missing deps**: required tools not mentioned
3. **Outdated architecture**: file structure has changed
4. **Missing env setup**: required env vars or config not mentioned
5. **Broken test commands**: test scripts have changed
6. **Undocumented gotchas**: non-obvious patterns not captured

## Tips for users

- **`#` key**: during a session, press `#` to have Claude auto-incorporate learnings into CLAUDE.md.
- **Keep it short**: dense is better than verbose.
- **Actionable commands**: all commands must be copy-paste ready.
- **`.claude.local.md`**: use for personal preferences (add to `.gitignore`).
- **Global defaults**: put user-wide preferences in `~/.claude/CLAUDE.md`.
