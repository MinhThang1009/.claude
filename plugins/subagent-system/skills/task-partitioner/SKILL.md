---
name: task-partitioner
description: This skill should be used when the user asks to "partition tasks for parallel agents", "plan multi-agent execution", "create dependency graph", or before spawning any parallel agents. Produces a dependency graph, disjoint file ownership map, and batched execution groups to prevent scope overlap and race conditions.
allowed-tools: Read Glob Grep
---

Analyze the provided task list and produce a multi-agent execution plan.

**Step 1 — Identify dependencies.**
For each task, determine:
- Which other tasks must complete before this one can start (dependencies)
- Which tasks have no dependencies and can run in parallel

**Step 1b — Scope check (before Step 2).**
Count total tasks and total files affected:
- If total tasks > 15 OR total files > 50: split into batches of ≤15 tasks / ≤50 files. Output **one EXECUTION_PLAN per batch**, labeled `Batch 1 of K`, `Batch 2 of K`, etc.
- Each batch is self-contained and processed independently. The main agent runs Batch 1 completely (all groups done, checkpoint written) before starting Batch 2.
- Alert: `"Large scope: [N] tasks / [M] files → split into [K] batches. Complete each batch fully before starting the next."`

**Step 2 — Assign file ownership.**
For each task, assign a disjoint file set:
- Partition by module or directory, not by concern type
- No two tasks in the same execution group may share a file
- Use Glob and Grep to discover which files are relevant to each task

**Step 3 — Group into execution batches.**
- Group 1: all tasks with no dependencies (run in parallel)
- Group 2: tasks that depend only on Group 1 (run in parallel after Group 1 completes)
- Group N: tasks that depend on Group N-1

**Output format — use a markdown table, not JSON.** LLMs produce malformed JSON when it is embedded in mixed text. Tables parse cleanly.

```
EXECUTION PLAN:

Group 1 (parallel):
| Task ID | Files owned              | Depends on | Description              |
|---------|--------------------------|------------|--------------------------|
| A       | src/auth/, src/middleware/ | —          | Refactor AuthService     |
| B       | src/api/                 | —          | Review API endpoints     |

Group 2 (parallel, after Group 1):
| Task ID | Files owned   | Depends on | Description                        |
|---------|---------------|------------|------------------------------------|
| C       | src/services/ | A          | Update services using new AuthService |

TOTAL TASKS: N

FILE OWNERSHIP MAP:
- src/auth/       → Task A
- src/middleware/ → Task A
- src/api/        → Task B
- src/services/   → Task C
```

Present the plan to the main agent for review. Do not spawn any agents — the main agent decides when to proceed.
