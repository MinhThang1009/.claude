# Structured Output

Every subagent response must begin with a STATUS block. Prevents silent failures and unparseable output (3.1).

**Do:**
- Start every response with the STATUS block shown below
- Include ERRORS when STATUS is `FAILED`
- Include REMAINING_TASKS when TASKS_PROCESSED < TASKS_TOTAL

**Don't:**
- Output only prose without a STATUS block
- Output an empty response

**Required STATUS block:**

```
STATUS: COMPLETED | PARTIAL | FAILED | SUSPICIOUS
TASKS_PROCESSED: N
TASKS_TOTAL: M
```

When STATUS is `FAILED` or TASKS_PROCESSED < TASKS_TOTAL, also include:

```
REMAINING_TASKS: [list of unprocessed tasks]
ERRORS: [description of what failed]
```

Note: Use `PARTIAL` when not every task completed — any task skipped (`[o]`) or TASKS_PROCESSED < TASKS_TOTAL; use `COMPLETED` only when every task is done (`[x]`). `SUSPICIOUS` is used by `completion-checker` when the checklist has fewer items than tasks assigned (possible truncation). All STATUS values are uppercase to enable exact-string matching in automated pipelines.

The main agent uses the STATUS block to validate format before parsing content. A missing STATUS block is treated as a failure — the main agent will retry the task in foreground mode.
