---
name: plan-tasks
description: "This skill should be used when the user asks to generate a parallel execution plan from a task list ('plan tasks', 'chia task chay song song', 'dependency graph for tasks'). Drives the task-partitioner skill and outputs dependency-ordered batches with non-overlapping file ownership."
argument-hint: [task-list-or-file]
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

**Cross-plugin agents:** `test-writer` ships with the **test-toolkit** plugin and `code-explorer` with the **feature-dev** plugin — neither lives in subagent-system, and its `plugin.json` declares no dependency on them. If those plugins are not enabled, fall back to the generic `claude` agent type for test writing (and never rely on `code-explorer`).

**Model selection:** All agents default to `sonnet`. Override with `model: haiku` only for pure read/exploration tasks with no Bash/Write (e.g., "summarize this module", "list all API endpoints") to reduce token cost. Never use haiku for implementation, security review, or verification — it produces lower-quality findings.

**Mandatory pipeline shape — always end with this sequence:**
```
Batch N-2: [fix agents in parallel]
     ↓
     [iteration-cleanup] ← AUTO-SCHEDULE if fix batch has N≥3 agents (see rule below)
     ↓
Batch N-1: pipeline-reviewer
     ↓
     severity-gate  ← MUST run inline before chain-verifier
     If any CRITICAL finding → STOP, spawn targeted fix agents, re-run from pipeline-reviewer
     ↓
Batch N:   chain-verifier
     ↓
     /audit-output [TEST_COMMAND]
     ↓
     pipeline-retrospective  ← ALWAYS run as final step; reads artifacts, writes improvement proposals
```
Never skip severity-gate or pipeline-retrospective. pipeline-retrospective runs even when the pipeline was clean — a clean run still produces useful "what worked well" evidence for future improvement.

**Iteration-cleanup — auto-schedule rule:**
If the fix batch contains **N≥3 agents modifying code** (not audit/review/analysis agents):
- Schedule one `iteration-cleanup` agent BETWEEN the fix batch and `pipeline-reviewer`
- Scope: only files touched by the fix agents in this batch (use `git diff --name-only HEAD` to determine)
- Purpose: catches structural erosion introduced by incremental fixes — functions >50 lines,
  nesting >3 levels, duplicated logic, and dead code added by fixes
- This agent uses `Edit` to simplify — it must NOT change behavior, only structure
- Rationale from benchmark: 5 fix agents ran but iteration-cleanup was never triggered;
  the large-function issue (I1) went unreported because the pipeline skipped this step

**Non-git projects:** `chain-verifier` requires git and will output `CHAIN_VERIFICATION_BLOCKED` on non-git repos. For non-git projects, replace the final `chain-verifier` batch with a manual verification step: have `pipeline-reviewer` do a second pass over all affected files, then escalate to the user for sign-off instead of automated APPROVED verdict.

**Present the plan to the user for approval before spawning any agents.** Do not begin execution until the user confirms.

**Monitoring prerequisite:** Before finalizing the plan, confirm how agent health will be monitored:
- If using `pipeline-monitor`:
  1. Each subagent prompt MUST include the progress file instruction (template suffix below)
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
- [SECURITY FIX ONLY] Grep for the OLD vulnerable pattern in the edited file to confirm
  it no longer exists. Example: fixing SQL injection → grep for string interpolation `${`
  inside SQL strings. If the old pattern is still found → fix is INCOMPLETE, do NOT report COMPLETED.
- [SECURITY FIX ONLY] Grep for the NEW secure pattern to confirm it was applied at the
  correct location. Example: SQL fix → confirm `db.prepare(` appears in the patched route.
  If new pattern is absent → the fix may have been applied to the wrong section.
```

**Why this matters:** Partial fixes (e.g., validating `resolvedPath` but serving `filePath`) pass
naive read-back verification. Only pattern-level grep catches this class of regression.

**Re-fix loop — when chain-verifier returns NEEDS_FIX:**

Do not stop. Follow this loop:
1. Extract the specific findings from chain-verifier output.
2. Spawn targeted fix agents — one per finding or one per file, using the same checklist suffix above.
3. Re-run pipeline-reviewer on the re-fixed files.
4. Run severity-gate.
5. Re-run chain-verifier.
6. Repeat until chain-verifier returns APPROVED or the loop has run 3 times.

After 3 iterations without APPROVED: stop and escalate to the user with a summary of unresolved findings. Do not loop indefinitely.

