---
description: Analyzes a task list and generates an execution plan with dependency graph, file ownership, and parallel execution groups. Run before any multi-agent workflow.
---

Use the task-partitioner skill to analyze the task list and codebase.

**Steps:**

1. Read the task list from `$ARGUMENTS` if provided, or prompt the user to specify a file or paste the task list.
2. Use the task-partitioner skill to:
   - Identify which tasks depend on outputs from other tasks
   - Assign a non-overlapping file set to each task (partition by module or directory, not by concern type)
   - Group tasks into parallel execution batches separated by dependency barriers
3. Output the execution plan as a markdown table with columns: Task ID, Files owned, Depends on, Description
4. Include a FILE OWNERSHIP MAP section listing which files belong to which task
5. Include TOTAL TASKS count

**Agent type selection — include in the execution plan for each task:**

| Task type | Agent type to spawn | Why |
|-----------|--------------------|----|
| Audit / read-only analysis | `claude` (NOT `code-explorer`) | `code-explorer` lacks Bash/Write — cannot write progress files |
| Implementation / fix | `claude` | Needs Edit, Write, Bash tools |
| Fresh-context code review | `pipeline-reviewer` | Isolated context prevents self-review bias |
| Test writing | `test-writer` | Specialized test generation |
| Finding verification (>5) | `finding-validator` | Isolated context prevents confirmation bias |
| Final pipeline integrity | `chain-verifier` | Fresh context, no chain history |

**Critical:** Never use `code-explorer` for tasks that require writing progress files — it has no Bash/Write tools and will silently skip the progress file instruction.

**Present the plan to the user for approval before spawning any agents.** Do not begin execution until the user confirms.

**Monitoring prerequisite:** Before finalizing the plan, confirm how agent health will be monitored:
- If using `pipeline-monitor`:
  1. Each sub-agent prompt MUST include the progress file instruction (template suffix below)
  2. When invoking pipeline-monitor, ALWAYS pass `PROJECT_ROOT: /absolute/path` explicitly — the agent cannot auto-detect it from session cwd
  ```
  After processing each file, append one line to .claude/progress/[AGENT_ID]-progress.md:
  | [timestamp] | [filename] | [lines read] | [findings count] | DONE |
  ```
- If not using `pipeline-monitor`: note that OTel (CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1) or foreground mode is the fallback for anomaly detection.

If the task list contains ambiguous dependencies (tasks that might or might not need to be sequential), surface them explicitly and ask the user to decide before finalizing the plan.

