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
| Severity gate | inline (severity-gate skill) | Pause pipeline if CRITICAL found — no agent needed |
| Test writing | `test-writer` | Specialized test generation |
| Finding verification (>5) | `finding-validator` | Isolated context prevents confirmation bias |
| Final pipeline integrity | `chain-verifier` | Fresh context, no chain history |

**Critical:** Never use `code-explorer` for tasks that require writing progress files — it has no Bash/Write tools and will silently skip the progress file instruction.

**Mandatory pipeline shape — always end with this sequence:**
```
Batch N-2: [fix agents in parallel]
     ↓
Batch N-1: pipeline-reviewer
     ↓
     severity-gate  ← MUST run inline before chain-verifier
     If any CRITICAL finding → STOP, spawn targeted fix agents, re-run from pipeline-reviewer
     ↓
Batch N:   chain-verifier
```
Never skip severity-gate. If pipeline-reviewer returns 0 findings, severity-gate still runs (it will pass instantly).

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

**Fix agent prompt — mandatory checklist suffix:**

Every implementation/fix agent prompt MUST include this suffix:

```
Verification checklist before finishing:
- If you added or referenced any i18n/translation key (e.g. t('some.key', ...)):
  grep the locale files to confirm the key exists. If missing, add it.
- If you added any import, verify the imported module/function exists.
- Run tests: read PROJECT_ROOT/.claude/PIPELINE_CONFIG.md for TEST_COMMAND, run it,
  confirm pass. If PIPELINE_CONFIG.md not found or TEST_COMMAND is NONE, skip.
- Run a final read of the edited file to confirm no syntax errors.
```

**Re-fix loop — when chain-verifier returns NEEDS_FIX:**

Do not stop. Follow this loop:
1. Extract the specific findings from chain-verifier output.
2. Spawn targeted fix agents — one per finding or one per file, using the same checklist suffix above.
3. Re-run pipeline-reviewer on the re-fixed files.
4. Run severity-gate.
5. Re-run chain-verifier.
6. Repeat until chain-verifier returns APPROVED or the loop has run 3 times.

After 3 iterations without APPROVED: stop and escalate to the user with a summary of unresolved findings. Do not loop indefinitely.

> Tip: For fully automated looping, invoke `/goal` with a goal file that defines success as `chain-verifier VERDICT: APPROVED`.

