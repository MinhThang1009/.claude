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

**Present the plan to the user for approval before spawning any agents.** Do not begin execution until the user confirms.

**Monitoring prerequisite:** Before finalizing the plan, confirm how agent health will be monitored:
- If using `pipeline-monitor`: each sub-agent prompt MUST include the progress file instruction below. Add it to the plan as a required template suffix for all sub-agent prompts:
  ```
  After processing each file, append one line to .claude/progress/[AGENT_ID]-progress.md:
  | [timestamp] | [filename] | [lines read] | [findings count] | DONE |
  ```
- If not using `pipeline-monitor`: note that OTel (CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1) or foreground mode is the fallback for anomaly detection.

If the task list contains ambiguous dependencies (tasks that might or might not need to be sequential), surface them explicitly and ask the user to decide before finalizing the plan.

**Chain verification prerequisite:** If the plan includes a chain-verifier invocation at the end of the pipeline, the plan MUST include `checkpoint-writer` at the end of Phase 1 (before Phase 2 begins). The chain-verifier requires `.claude/checkpoints/chain-start-commit` written by `checkpoint-writer` Step 0. Without this, chain-verifier will block with `CHAIN_VERIFICATION_BLOCKED`. Note this dependency explicitly in the execution plan under Phase 1.
