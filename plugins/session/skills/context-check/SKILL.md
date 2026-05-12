---
name: context-check
description: "Checks context window usage and recommends actions (compact/clear/subagent/handoff). Use when asking about context levels or when response quality seems to be declining."
allowed-tools: Read
model: inherit
---

# Skill: Check context window

Purpose: proactively assess context and recommend the right action **before quality degrades**.

## Process

### Step 1 — Read state

Claude **cannot run `/context` itself** because it is a [built-in command only the user can invoke](https://code.claude.com/docs/en/commands). Ask the user:

> Need to run `/context` in the terminal and send back the output (% and breakdown).

After the user sends `/context` output, analyze it per the steps below.

### Step 2 — Analyze by threshold

> Source for % thresholds (multi-author, verified):
> - `<30/<40/60%` + "dumb zone": [Dex Horthy at MLOps Community](https://youtu.be/YwZR6tc7qYg?t=1541) (2026-03-24)
> - `300-400k tokens` context rot (1M model): Thariq Shihipar (Anthropic Claude Code team) via [howborisusesclaudecode.com](https://howborisusesclaudecode.com/)
> - `155k tokens` auto-compact (200k window): [Boris Cherny X tweet](https://x.com/bcherny/status/1977163445205450783)
> - Full citations + nuance by task complexity: [docs/REFERENCE.md §16](../../../../docs/REFERENCE.md#16-quản-lý-context-window--chi-tiết). Anthropic does not publish official % thresholds.

| % context | State                               | Recommended action                                                        |
| --------- | ----------------------------------- | ------------------------------------------------------------------------- |
| `<30%`    | 🟢 Aggressive zone                  | Target for experienced users                                               |
| `30-40%`  | 🟢 Sweet spot                       | Newcomer target — "shoot to keep it under 40%" (Dex)                    |
| `40-60%`  | 🟡 "Dumb zone" begins               | Performance degrading — plan to wrap up current phase                     |
| `60-77%`  | 🟠 Wrap up actively                 | `/compact` OR `/handoff` → `/clear` + new brief                           |
| `~77%`    | 🔴 Critical zone (Boris claim 155k) | Compact proactively — auto-compact default ~95% per newer docs, but quality degrades here |
| `>90%`    | ⛔ Hard limit                        | STOP large task immediately, brief + new session                           |

### Step 3 — Analyze by group

`/context` breaks output down by group (system, memory/CLAUDE.md, skills, MCP tools, conversation, file content). Find any group consuming unusually high context:

| High-consuming group              | Cause                                  | How to reduce                                                    |
| --------------------------------- | -------------------------------------- | ---------------------------------------------------------------- |
| Memory (CLAUDE.md + rules) >10%   | CLAUDE.md / rules too long             | Prune them, move less-used sections to REFERENCE.md              |
| MCP tools >15%                    | Too many MCP servers enabled, not used | `claude mcp` list then disable those not needed for this session |
| Skill descriptions >5%            | Too many auto-discovered skills        | Set `disable-model-invocation: true` for rarely used skills      |
| Conversation history >40%         | Lots of tool output / dead-end paths   | `/compact` now                                                   |
| File content >25%                 | Too many large files `@`-referenced    | `/clear` + only reference files that are needed                  |

### Step 4 — Recommend action

Give **1 main recommendation** with a reason — do NOT list 5 options for user to choose from:

Example output:
> Context is at 73%. Conversation history occupies 45% — mostly from long tool output in a previous debug session. **Recommendation**: run `/handoff` to capture key decisions in 5 lines, then `/compact keep the brief, drop debug logs`. Then continue the current task in this session. Estimated context after compact: ~25%.

## Choosing `/compact` vs `/clear`

| When to use `/compact`                        | When to use `/clear`                     |
| --------------------------------------------- | ---------------------------------------- |
| In the middle of a task, need to keep thread  | Finished a task, moving to a completely different one |
| Important decisions and file paths must survive | History is not needed                   |
| Context 40-60% ("dumb zone")                   | Context >77% (auto-compact zone) or session is muddled |
| Many dead-end debug paths to clean up          | Committed and done, starting a new feature |

**Golden rule**: `/compact` = compress, `/clear` = wipe entirely. Confusing `/clear` with `/compact` = losing context that must be re-explained. Confusing `/compact` with `/clear` = carrying garbage into the new task.

## When context is corrupt / Claude is confused

Symptoms:
- Claude repeatedly references old files/decisions.
- Claude forgets rules in CLAUDE.md (e.g., still writing English comments even though Vietnamese was configured).
- Fix attempted twice and still wrong.
- `Internal server error` / `ECONNRESET` / "Chat has reached its limit".

→ Do NOT `/compact` (compacting dirty context = continuing dirty). Must:
1. `/handoff --save` (or copy-paste brief externally).
2. `/clear` or exit and open a new session.
3. Inject brief into the first prompt.

## Long-term tips

- Set a custom status line showing context %: [code.claude.com/docs/en/statusline](https://code.claude.com/docs/en/statusline).
- Audit `~/.claude/CLAUDE.md` periodically (monthly): remove lines no longer needed.
- Large projects: use subagents (`use a subagent to investigate ...`) to keep main context clean.
- Large tool output (build log, JSON dump >5KB): redirect to a file instead of dumping into chat: `npm test > /tmp/test.log 2>&1 && tail -50 /tmp/test.log`.
