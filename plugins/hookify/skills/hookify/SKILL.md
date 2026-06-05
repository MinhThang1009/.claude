---
name: hookify
description: "Creates Claude Code hooks to prevent unwanted behaviors by analyzing conversation patterns or from explicit instructions. Use when user says 'create a hook', 'prevent behavior X', or invokes /hookify."
allowed-tools: Read Grep Glob Bash Write AskUserQuestion TodoWrite
argument-hint: "[optional — specific behavior to prevent, e.g.: don't use rm -rf]"
---

# Hookify — Create Hooks from Unwanted Behaviors

Creates rule files to prevent Claude from performing unwanted behaviors — no manual `settings.json` editing required.

## Step 1: Gather behaviors

**If `$ARGUMENTS` has content:**
- Analyze the user's instruction: `$ARGUMENTS`
- Additionally scan the last 10-15 messages for context/examples.

**If `$ARGUMENTS` is empty:**
- Dispatch a `conversation-analyzer` agent to analyze the transcript (focus on the **last 20-30 messages**).
- Agent returns structured findings: issue, tool, pattern, severity (high/medium/low), suggested rule.

## Step 2: Ask user for confirmation

Use AskUserQuestion:

1. **Choose behaviors** (multiSelect): list discovered behaviors (up to 4), user selects which ones to hookify.
2. **Action for each behavior**: `warn` (display warning, allow continuing) or `block` (prevent execution)?
3. **Patterns**: display discovered patterns, allow user to edit/add.

## Step 3: Create rule files

Each rule = 1 file `.claude/hookify.<rule-name>.local.md` in the **current project directory** (NOT the plugin directory).

**Naming convention**: kebab-case, starting with an action verb: `block-dangerous-rm`, `warn-console-log`, `require-tests-before-stop`.
Avoid: `hookify.rule1.local.md` (not descriptive), `hookify.md` (missing .local), `danger.local.md` (missing hookify prefix).

### Simple format (1 pattern)

```markdown
---
name: <rule-name>
enabled: true
event: <bash|file|stop|prompt|all>
pattern: <regex pattern>  # matches against `command` (bash) or `new_text` (file) — Python regex
action: <warn|block>   # optional — defaults to warn if not declared
---

<Message displayed to Claude when the rule triggers>
```

### Complex format (multiple conditions)

```markdown
---
name: <rule-name>
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
  - field: new_text
    operator: contains
    pattern: API_KEY
action: warn
---

<Warning message>
```

### Event types

| Event | Matches |
|-------|---------|
| `bash` | Bash tool commands |
| `file` | Edit, Write, MultiEdit tools |
| `stop` | When the agent wants to stop. Use for: mandatory step reminders, completion checklists, process enforcement |
| `prompt` | When user submits a prompt |
| `all` | All events |

### Operators for conditions

| Operator | Description |
|----------|-------------|
| `regex_match` | Match a regex pattern |
| `contains` | Contains a substring |
| `equals` | Exact match |
| `not_contains` | Does not contain a substring |
| `starts_with` | Starts with |
| `ends_with` | Ends with |

### Fields by event type

| Event | Available fields |
|-------|-----------------|
| `bash` | `command` |
| `file` | `file_path`, `new_text`, `old_text`, `content` (full file content after edit) |
| `prompt` | `user_prompt` |
| `stop` | _(check transcript or completion criteria)_ |

**YAML escaping**:
- YAML unquoted: `pattern: \s+-rf` — works as-is, no backslash escaping needed.
- YAML quoted: `pattern: "\\s+-rf"` — requires double backslash.
- Patterns containing `:`, `#`, `{`, `}` → must be quoted.
- **Recommendation: use unquoted** unless pattern contains YAML special characters.

## Step 4: Create files and confirm

1. Check that the `.claude/` directory exists → create it if not (`mkdir -p .claude`).
   - Check `.gitignore` — add `.claude/*.local.md` if not already present, to avoid committing personal rule files to the repo.
2. Use the Write tool to create each file.
3. Display the list of created files:
   ```
   Created 2 hookify rules:
   - .claude/hookify.dangerous-rm.local.md → bash: rm -rf (warn)
   - .claude/hookify.sensitive-files.local.md → file: .env edits (block)

   Rules are active immediately — no restart needed! Hooks will read new rules on the next tool use.
   ```
4. Verify files with Glob/Read.

## Pattern Tips

**Bash patterns:**
- Dangerous commands: `rm\s+-rf|chmod\s+777|dd\s+if=`
- Package installs: `npm\s+install\s+|pip\s+install`

**File patterns:**
- Code smells: `console\.log\(|eval\(|innerHTML\s*=`
- Sensitive files: `\.env$|\.git/|credentials`

## Sub-commands

### `/hookify list`
List all existing rules as a table:

| Rule | Event | Pattern | Action | Enabled |
|------|-------|---------|--------|---------|
| warn-dangerous-rm | bash | `rm\s+-rf` | warn | ✅ |

With a preview of each rule's message.

### `/hookify configure`
Interactive enable/disable rules via AskUserQuestion (multiSelect). Display rule list → user selects to toggle → update the `enabled` field.

### `/hookify help`
Display a usage summary, event types, operators, and examples.

## Manual rule management

- **List**: `ls .claude/hookify.*.local.md` or Glob.
- **Enable/disable**: change `enabled: true/false` in frontmatter.
- **Delete**: delete the file.
- Changes take effect on the next tool use.

## Example workflow

**User**: `/hookify Don't use rm -rf without asking me first`

1. Analyze: user wants to prevent `rm -rf`.
2. Ask: "Block entirely or just warn?" → User selects "Warn".
3. Create `.claude/hookify.warn-dangerous-rm.local.md`:
   ```markdown
   ---
   name: warn-dangerous-rm
   enabled: true
   event: bash
   pattern: rm\s+-rf
   action: warn
   ---

   ⚠️ **rm -rf command detected**
   User has requested a warning before using rm -rf.
   Please confirm the exact path before executing.
   ```
4. Confirm: "Rule is active immediately — try triggering it to test!"

Use TodoWrite to track progress through the steps.

## Sample examples

See the `examples/` directory for 4 complete rules:
- `warn-console-log.local.md` — warns when adding `console.log`
- `block-dangerous-rm.local.md` — blocks `rm -rf` commands
- `require-tests-stop.local.md` — requires running tests before stopping
- `warn-sensitive-files.local.md` — warns when editing sensitive files (multi-condition)

## Testing Patterns

Test regex patterns before using: `python3 -c "import re; print(re.search(r'<pattern>', '<test-string>'))"`
Or use [regex101.com](https://regex101.com) (select Python flavor) to visualize.

## Common pitfalls

- **Pattern too broad**: `rm` matches any command containing "rm" (e.g., `npm run format`). Use `\brm\s+-rf` for more specificity.
- **Pattern too narrow**: `rm -rf /` only matches the exact string, missing `rm -rf ./src`.
- **Escaping issues**: YAML quoted strings (`"pattern"`) need double backslash (`\\s`); YAML unquoted (`pattern: \s`) works as-is. Recommendation: use unquoted.
- **Multiple conditions = AND logic**: all conditions must match for the rule to trigger.

## Troubleshooting

- Rule not triggering → check file is in the correct `.claude/` of the project (not the plugin). Re-read the file with the Read tool to verify the pattern is correct.
- Pattern not matching → test: `python3 -c "import re; print(re.search(r'pattern', 'test'))"`
- Block too strict → change `action: block` to `action: warn`.
