---
description: Lightweight security audit for 1–5 files, no pipeline.
argument-hint: [path] [focus:<concern>]
---

Run a focused security audit on a specific path or module.

**Input:** `$ARGUMENTS` = path to audit + optional focus area.
Examples:
- `/quick-audit src/auth/`
- `/quick-audit src/payment/webhook.js focus:race-condition`
- `/quick-audit frontend/src/features/auth/ focus:token-storage`

**Steps:**

1. **Parse arguments:**
   - Extract PATH (required)
   - Extract FOCUS (optional — specific concern to prioritize)

2. **List files in scope:**
```bash
Bash("find [PATH] \( -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.py' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.rb' -o -name '*.php' \) 2>/dev/null | grep -v node_modules | head -20")
```
If >10 files: warn "Scope has [N] files — consider /plan-tasks for full pipeline. Proceeding with first 10."

3. **Spawn a single audit agent:**

Agent type: `claude`
Agent prompt template:
```
THIS IS A READ-ONLY AUDIT — do NOT edit any project files.

Scope: [PATH]
Focus: [FOCUS or "general security audit"]

Files to audit:
[list from step 2]

Read each file. Report findings with:
- severity: 🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW
- file:line
- description
- specific fix

COMPLETION_CHECKLIST:
Mark each item [x] when done, [o] if skipped (with reason).
[ ] [file 1]
[ ] [file 2]
...
[ ] Summarize findings by severity
```

4. **After agent completes:**
   - Run completion-checker on agent output
   - If STATUS = SUSPICIOUS: note incomplete coverage
   - Output findings directly to conversation

5. **No checkpoint written** — quick-audit is ephemeral. For persistent results, follow up with `/plan-tasks` for a full pipeline.

**When to use quick-audit vs full pipeline:**

| Scenario | Use |
|----------|-----|
| 1-5 files, quick check | `/quick-audit` |
| Single module, pre-PR | `/quick-audit` |
| Full codebase audit | `/plan-tasks` → full pipeline |
| Post-fix verification | `/quick-audit path/to/fixed/file` |
