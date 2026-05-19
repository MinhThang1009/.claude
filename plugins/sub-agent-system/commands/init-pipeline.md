---
description: One-time setup for sub-agent-system pipeline in a project. Run before the first pipeline. Configures WorktreeCreate hooks, creates .claude/ dirs, and validates prerequisites.
---

Setup the sub-agent-system pipeline for a project.

**Steps:**

1. **Read PROJECT_ROOT from `$ARGUMENTS`**. If not provided, use current git repo root:
```bash
Bash("git rev-parse --show-toplevel 2>/dev/null || echo MISSING")
```
If MISSING: stop and ask user to provide the project path explicitly.

2. **Verify git repo:**
```bash
Bash("git -C [PROJECT_ROOT] rev-parse --show-toplevel 2>/dev/null && echo GIT_OK || echo NO_GIT")
```
If NO_GIT: warn "Project is not a git repo — checkpoint commits will be skipped. Continue? (y/n)"

3. **Create .claude/ directory structure:**
```bash
Bash("mkdir -p [PROJECT_ROOT]/.claude/{checkpoints,progress,alerts,tmp}")
```

4. **Check if .claude/ is gitignored:**
```bash
Bash("git -C [PROJECT_ROOT] check-ignore -q .claude 2>/dev/null && echo IGNORED || echo NOT_IGNORED")
```
If IGNORED: warn:
```
⚠️  .claude/ is in .gitignore — checkpoint files will NOT be committed.
   To enable checkpoint commits, add to .gitignore:
     !.claude/
     !.claude/checkpoints/
     !.claude/progress/
   Or accept that checkpoints are ephemeral (still usable within session).
```

5. **Check WorktreeCreate hooks in settings.json:**
```bash
Bash("grep -q 'WorktreeCreate' \"$HOME/.claude/settings.json\" 2>/dev/null && echo HAS_HOOK || echo NO_HOOK")
```
If NO_HOOK AND session cwd is not a git repo: warn:
```
⚠️  WorktreeCreate hook not found. If your session root is not a git repo,
   agent spawning will fail. Run /update-config to add it, or start Claude Code
   from within a git repository.
```

6. **Detect test command:**

Run these checks in order and stop at the first match:
```bash
# Node/JS
Bash("node -e \"const p=require('[PROJECT_ROOT]/package.json'); console.log(p.scripts&&p.scripts.test?'npm test':'NONE')\" 2>/dev/null || echo NONE")
# Python pytest
Bash("ls [PROJECT_ROOT]/pytest.ini [PROJECT_ROOT]/pyproject.toml [PROJECT_ROOT]/setup.cfg 2>/dev/null | head -1 || echo NONE")
# Go
Bash("ls [PROJECT_ROOT]/go.mod 2>/dev/null || echo NONE")
# Makefile test target
Bash("grep -q '^test:' [PROJECT_ROOT]/Makefile 2>/dev/null && echo 'make test' || echo NONE")
```

Set `TEST_COMMAND` to the first non-NONE result:
- `npm test` / `yarn test` / `pnpm test` — for Node
- `pytest` — for Python
- `go test ./...` — for Go
- `make test` — for Makefile
- `NONE` — if no test suite detected

7. **Write pipeline config:**
Write `[PROJECT_ROOT]/.claude/PIPELINE_CONFIG.md`:
```markdown
# Pipeline Config

PROJECT_ROOT: [absolute path]
GIT_REPO: YES | NO
INITIALIZED: [ISO timestamp]
CLAUDE_SETTINGS_HOOKS: CONFIGURED | MISSING
TEST_COMMAND: [detected command or NONE]
```

8. **Record chain-start-commit** (only if GIT_REPO: YES):
```bash
Bash("git -C [PROJECT_ROOT] rev-parse HEAD > [PROJECT_ROOT]/.claude/checkpoints/chain-start-commit")
```
This allows `chain-verifier` to determine git diff scope automatically. Without it, chain-verifier cannot compute which files changed and will output `CHAIN_VERIFICATION_BLOCKED`.

8. **Report:**
```
PIPELINE_READY:
Project: [PROJECT_ROOT]
Git: YES | NO
.claude/ dirs: ✓ created
Gitignore warning: [YES/NO]
WorktreeCreate hook: CONFIGURED | MISSING
Test command: [TEST_COMMAND]
Next step: Run /plan-tasks to design your pipeline.
```
