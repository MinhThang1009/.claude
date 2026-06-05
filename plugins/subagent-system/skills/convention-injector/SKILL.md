---
name: convention-injector
description: This skill should be used before spawning Explore or Plan agents (which skip CLAUDE.md), or when you need filtered/condensed conventions for a specific task type. Custom named subagents auto-load CLAUDE.md and rules/*.md — use this skill for task-specific filtering (≤300 tokens), anti-contamination for audit agents, and confirmation prompts. Also trigger when user asks to "inject project conventions", "add coding rules to agent", or "prepend CLAUDE.md to subagent".
allowed-tools: Read Bash
---

**Note:** Explore and Plan agents skip CLAUDE.md and rules/*.md. Custom named subagents (Agent-tool-spawned) DO auto-load the full memory hierarchy. Use this skill for Explore/Plan (required), or for any agent when task-specific filtering, anti-contamination, or confirmation prompts are needed.

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
From all sources, extract conventions relevant to the subagent's specific task:
- Coding conventions (naming, structure, style)
- Security rules (input validation, secret handling)
- Naming patterns (variables, files, functions, branches)
- Project-specific constraints (dependencies, compatibility, performance limits)

Skip conventions that do not apply to the subagent's task type (e.g., do not inject git workflow rules into a read-only audit agent).

**Step 2.5 — Anti-contamination filter (audit/security/review agents only).**
If the subagent's task is a security audit, code review, vulnerability scan, or quality assessment:

Inject this prohibition into the subagent prompt:
```
ANTI-CONTAMINATION RULE: Do NOT read any file whose name suggests pre-existing knowledge of issues:
KNOWN_ISSUES.md, BUGS.md, SECURITY_ISSUES.md, FINDINGS.md, VULNERABILITIES.md, or any file
matching *known*issue*, *bug*list*, *security*findings*.
Reading these files contaminates your independent analysis — your findings must come solely
from reading the source code, not from a pre-existing list.
```

Rationale: An agent that reads its own ground truth will appear to have a high detection rate but the result is unreliable and cannot be used for comparative benchmarking. This is the primary contamination vector identified in benchmark testing.

**Step 3 — Produce a compact block.**
Target ≤300 tokens. Be specific and imperative.

**If conventions exceed 300 tokens:** Do NOT silently truncate. Instead, fall back in order:
1. Use the `skills` field in the agent definition — full SKILL.md content auto-injects into the subagent's context at startup (bypasses the ≤300-token block, but still consumes the subagent's context window)
2. Create a dedicated convention skill file and reference it via `skills`

**Output format:**

```
PROJECT CONVENTIONS (inject into subagent prompt):
─────────────────────────────────────────────────
[Convention category]: [concise rule]
[Convention category]: [concise rule]
[Convention category]: [concise rule]
─────────────────────────────────────────────────
Source: [list of files read]
Token estimate: ~N
```

The main agent prepends this block to the subagent's prompt before spawning.

**Step 4 — Add self-confirmation suffix (recommended).**
Append to the subagent prompt after the convention block:

```
Before starting: confirm you have read and understood the PROJECT CONVENTIONS above.
If any convention is unclear, state it explicitly before proceeding.
```

This prompts the subagent to acknowledge conventions, reducing silent violations.
