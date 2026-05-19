# Completion Protocol

Before reporting done, every assigned task must be accounted for. Prevents premature termination (3.2).

**Do:**
- Output a COMPLETION_CHECKLIST before every final response, marking each task `[x]` done or `[o]` skipped with a reason
- Include TASKS_PROCESSED and TASKS_TOTAL counts
- Set STATUS to `COMPLETED`, `PARTIAL`, `FAILED`, or `SUSPICIOUS` (uppercase — required for automated parsing)
- List REMAINING_TASKS when STATUS is `PARTIAL`

**Don't:**
- Report done when TASKS_PROCESSED < TASKS_TOTAL
- Omit the checklist even when the task list is short

**Required output format:**

```
COMPLETION_CHECKLIST:
- [x] Task 1: [name] — [result]
- [o] Task 2: [name] — [reason skipped]
TASKS_PROCESSED: N
TASKS_TOTAL: M
STATUS: COMPLETED | PARTIAL | FAILED | SUSPICIOUS
REMAINING_TASKS: [list of unprocessed tasks if PARTIAL or SUSPICIOUS]
```

**Canary task technique (for main agent use):** Include one task with a known result in the list given to the sub-agent (e.g., a file known to contain a specific bug or pattern). If the sub-agent does not report the expected result for the canary, treat it as evidence of skipping. Place the canary in the middle of the list, not at the start or end.
