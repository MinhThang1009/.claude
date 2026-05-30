---
name: completion-checker
description: This skill should be used after receiving output from a subagent that was assigned an explicit numbered task list and is expected to have produced a COMPLETION_CHECKLIST block. Do not invoke if the subagent was not given a task list — there will be no checklist to parse. Uses grep counts, not LLM estimation, to detect premature termination. Also trigger when user asks to "verify completion checklist", "check if agent finished all tasks", or "detect premature termination".
allowed-tools: Bash Write
---

**Input:** Original task list assigned to the subagent + the subagent's full output.

**Step 1 — Save output to a temp file for deterministic counting.**

If `PROJECT_ROOT` was injected in the input, use it as an absolute base path. Otherwise fall back to the relative path (works only when session cwd = project root — warn if uncertain):
```bash
Bash("mkdir -p [PROJECT_ROOT_OR_DOT]/.claude/tmp")
Write("[PROJECT_ROOT_OR_DOT]/.claude/tmp/cc_input.txt", [subagent output])
```
**Warning:** If the Claude session was started from a directory other than the project root, `.claude/tmp/` resolves to the wrong location and grep counts will be 0. Always inject `PROJECT_ROOT` from `PIPELINE_CONFIG.md` when calling this skill in a multi-project setup.

**Step 2 — Count deterministically with grep.**

First, extract only the COMPLETION_CHECKLIST section to avoid counting `[x]` in code snippets or findings text:
```bash
Bash("grep -Ec 'COMPLETION[_ ]?CHECKLIST' [PROJECT_ROOT_OR_DOT]/.claude/tmp/cc_input.txt")    # block exists (-E optional separator: matches COMPLETION_CHECKLIST, COMPLETION CHECKLIST, COMPLETIONCHECKLIST; case-sensitive to stay in sync with the sed below)
Bash("sed -nE '/COMPLETION[_ ]?CHECKLIST/,/^STATUS:/p' [PROJECT_ROOT_OR_DOT]/.claude/tmp/cc_input.txt > [PROJECT_ROOT_OR_DOT]/.claude/tmp/cc_checklist.txt")   # sed regex MUST match the grep above (same optional separator) — else block is "found" but extracts nothing
Bash("[ -s [PROJECT_ROOT_OR_DOT]/.claude/tmp/cc_checklist.txt ] && echo CHECKLIST_FOUND || echo CHECKLIST_EMPTY")   # guard: sed -n exits 0 even on no match → rely on this non-empty test, NOT the exit code
Bash("grep -Fc '[x]' [PROJECT_ROOT_OR_DOT]/.claude/tmp/cc_checklist.txt")                       # done count (checklist only)
Bash("grep -Fc '[o]' [PROJECT_ROOT_OR_DOT]/.claude/tmp/cc_checklist.txt")                       # skipped count (checklist only)
```
If the guard prints `CHECKLIST_EMPTY` (no COMPLETION_CHECKLIST extracted — note `sed -n` exits 0 even when nothing matches, so trust the `[ -s ]` non-empty test, NOT the exit code): **do NOT count from the full file** — set STATUS=SUSPICIOUS and ACTION=ESCALATE immediately, with reason "CHECKLIST_NOT_FOUND — subagent did not produce a completion checklist." Skip Steps 3-4.
Both the grep and the sed use the same `[_ ]?` optional separator (extended regex, case-sensitive — neither uses `-i`/`I`, so they agree on case) to match `COMPLETION_CHECKLIST`, `COMPLETION CHECKLIST`, and `COMPLETIONCHECKLIST` — agents sometimes use a space or no separator instead of an underscore. The exact uppercase header is mandated below, so case-sensitivity is intentional. Keep the two regexes in sync.
Use `-Fc` for `[x]`/`[o]` counts (fixed-string, no escaping issues). Use these counts as ground truth. Do NOT rely on LLM estimation.

**Format enforcement note:** Sub-agents MUST write their checklist header as exactly `COMPLETION_CHECKLIST:` (underscore, colon). If the detected block uses a different format, note it in the report as a FORMAT_WARNING alongside the counts.

**Step 3 — Identify missing tasks.**
Compare task names in the original task list against lines found in the COMPLETION_CHECKLIST block. A task is MISSING if its name or identifier does not appear in any `[x]` or `[o]` line. This step uses LLM matching — flag any uncertain matches explicitly.

Uncertain match threshold: if more than 30% of matches are flagged uncertain, set STATUS to SUSPICIOUS regardless of grep counts. Uncertain matches that include critical-path tasks (implementation, security, database) → set ACTION to ESCALATE.

**Step 4 — Compare totals.**
Compare grep-counted items (Step 2) against the number of tasks in the original task list. If checklist item count < assigned task count, flag SUSPICIOUS.

**Step 5 — Determine action.**
- `COMPLETED` — all tasks accounted for in the checklist AND skipped count `[o]` = 0
- `PARTIAL` — some tasks missing, or any task skipped (`[o]` count > 0); list them in REMAINING_TASKS. A checklist where every task is present but ≥1 is `[o]` is PARTIAL, never COMPLETED (matches `completion-protocol.md`)
- `SUSPICIOUS` — checklist has fewer items than tasks assigned (possible truncation or skipping)

Note: `FAILED` (agent crash/error) is intentionally absent from this skill's output. Agent execution failures are detected upstream by `structured-output.md` parsing — a missing or invalid STATUS block in the subagent's raw output causes the main agent to retry in foreground mode before invoking completion-checker. By the time completion-checker is invoked, the input is always a valid output; hence only COMPLETED, PARTIAL, and SUSPICIOUS are valid completion states.

Note: Invoke this skill **once per subagent output**, not once for a merged multi-agent batch. If checking multiple agents in a batch, invoke sequentially with each agent's individual output. Merging outputs before invoking produces incorrect grep counts.

**Output format:**

```
COMPLETION_CHECK:
Tasks assigned: N
Tasks in checklist: M
Tasks completed [x]: P
Tasks skipped [o]: Q
Tasks MISSING from checklist: [list or NONE]

STATUS: COMPLETED | PARTIAL | SUSPICIOUS
REMAINING_TASKS: [list if PARTIAL or SUSPICIOUS]
ACTION: PROCEED | RE_DISPATCH [list of missing tasks] | ESCALATE
```

Set `ACTION: ESCALATE` when STATUS is SUSPICIOUS and missing tasks are critical-path items.
