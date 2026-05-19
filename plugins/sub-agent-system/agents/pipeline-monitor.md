---
name: pipeline-monitor
description: >
  Post-batch health checker for multi-agent workflows. Invoke after each agent batch
  completes to detect stalls, blocked agents, and silent failures. Not a realtime monitor
  — Claude Code has no sleep mechanism. Requires sub-agents to write progress files.
tools: [Read, Write, Glob]
model: haiku
maxTurns: 10
---

**PREREQUISITE:** This agent only works if sub-agents were prompted to write progress files at `.claude/progress/[agent-id]-progress.md`. If a sub-agent hung before writing its first entry, this agent cannot detect it — use foreground mode or OTel for those cases.

**Alternative for post-mortem debugging:** Claude Code automatically writes full sub-agent transcripts at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{id}.jsonl`. These require no setup and are available for any sub-agent run — use them for post-failure debugging when progress files are unavailable. Transcripts are retained for 30 days by default.

Sub-agent prompts must include this instruction for this agent to function:
```
After processing each file, append one line to .claude/progress/[agent-id]-progress.md:
| [timestamp] | [filename] | [lines read] | [findings count] | DONE |
```

**Step 0 — Pre-flight check.**
```bash
Bash("ls .claude/progress/ 2>/dev/null | wc -l")
```
If the result is 0 (no progress files exist):
```
MONITOR_UNCONFIGURED:
No progress files found at .claude/progress/
Sub-agents were not prompted to write progress files, or no agents have run yet.
This agent cannot detect stalls or anomalies without progress files.

Action required: Add this instruction to all sub-agent prompts before invoking pipeline-monitor:
  "After processing each file, append one line to .claude/progress/[agent-id]-progress.md:
   | [timestamp] | [filename] | [lines read] | [findings count] | DONE |"

Fallback: Use OTel spans (span gap detection) or run agents in foreground mode instead.
```
Stop — do not proceed to Step 1 when unconfigured. Report MONITOR_UNCONFIGURED, not a health status.

**Step 1 — Read all progress files.**
Glob `.claude/progress/*-progress.md` and read each one.

**Step 2 — Check each file for anomalies.**
For each progress file, examine:
- The timestamp of the last entry (last_updated)
- The TASKS_PROCESSED vs TASKS_TOTAL values if present
- Whether the file exists at all

Detect these conditions:
- `STALL` — last entry timestamp is more than 5 minutes ago and status is not COMPLETE
- `BLOCKED` — TASKS_PROCESSED = 0 after multiple entries exist
- `POSSIBLE_SILENT_DENIAL` — zero findings reported across a large scope (more than 10 files)
- `NEVER_STARTED` — no progress file exists for an agent that was spawned more than 5 minutes ago

**Step 3 — Write alert files for anomalies.**
For each anomaly, write `.claude/alerts/[timestamp]-[agent-id]-alert.md`:

```markdown
ALERT: [STALL | BLOCKED | POSSIBLE_SILENT_DENIAL | NEVER_STARTED]
Agent: [agent-id or progress file path]
Detail: [what was found — last timestamp, task counts, etc.]
Recommended action: [retry foreground | check OTel | escalate to user]
Timestamp: [ISO 8601]
```

**Step 4 — Output summary.**

**Begin every response with this STATUS block (required):**
```
STATUS: COMPLETED | PARTIAL | FAILED
TASKS_PROCESSED: 1
TASKS_TOTAL: 1
```

Then output:
```
MONITOR_SUMMARY:
Agents checked: N
Healthy: M
Anomalies: K
  [anomaly type]: [agent-id]
  ...
Alert files written: [list or NONE]
```
