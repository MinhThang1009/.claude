---
name: convention-injector
description: >
  Reads project CLAUDE.md and rules files, then produces a compact convention block for
  injection into sub-agent prompts. Use before spawning any sub-agent that may not load
  CLAUDE.md automatically — specifically Explore agents, Plan agents, and all
  Task-tool-spawned agents.
allowed-tools: Read Bash
---

**Note:** Explore and Plan agents never auto-load CLAUDE.md. Task-tool-spawned sub-agents also do not load CLAUDE.md or rules files automatically. Always use this skill before spawning these agent types.

**Step 1 — Collect convention sources.**
Use `$HOME` (not `~`) — required for Windows Git Bash path resolution:
```bash
Bash("ls \"$HOME/.claude/rules/\"*.md 2>/dev/null; ls .claude/rules/*.md 2>/dev/null")
```
Read each file found with:
```bash
Bash("cat \"$HOME/.claude/rules/\"*.md 2>/dev/null")    # user-level rules
Bash("cat .claude/rules/*.md 2>/dev/null")               # project-level rules
Bash("cat \"$HOME/.claude/CLAUDE.md\" 2>/dev/null")      # user CLAUDE.md
Bash("cat .claude/CLAUDE.md 2>/dev/null")                # project CLAUDE.md
```
If all return empty: note "No convention files found — proceeding without conventions."

**Step 2 — Extract relevant conventions.**
From all sources, extract conventions relevant to the sub-agent's specific task:
- Coding conventions (naming, structure, style)
- Security rules (input validation, secret handling)
- Naming patterns (variables, files, functions, branches)
- Project-specific constraints (dependencies, compatibility, performance limits)

Skip conventions that do not apply to the sub-agent's task type (e.g., do not inject git workflow rules into a read-only audit agent).

**Step 3 — Produce a compact block.**
Target ≤300 tokens. Be specific and imperative.

**If conventions exceed 300 tokens:** Do NOT silently truncate. Instead, fall back in order:
1. Use the `skills` field in the agent definition — full SKILL.md content is auto-injected at startup without consuming the prompt
2. Create a dedicated convention skill file and reference it via `skills`

**Output format:**

```
PROJECT CONVENTIONS (inject into sub-agent prompt):
─────────────────────────────────────────────────
[Convention category]: [concise rule]
[Convention category]: [concise rule]
[Convention category]: [concise rule]
─────────────────────────────────────────────────
Source: [list of files read]
Token estimate: ~N
```

The main agent prepends this block to the sub-agent's prompt before spawning.

**Step 4 — Add self-confirmation suffix (recommended).**
Append to the sub-agent prompt after the convention block:

```
Before starting: confirm you have read and understood the PROJECT CONVENTIONS above.
If any convention is unclear, state it explicitly before proceeding.
```

This prompts the sub-agent to acknowledge conventions, reducing silent violations.
