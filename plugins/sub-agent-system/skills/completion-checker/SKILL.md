---
name: completion-checker
description: >
  Parses a sub-agent's COMPLETION_CHECKLIST to verify all assigned tasks were processed.
  Use after receiving output from any sub-agent with an explicit task list to detect premature
  termination. Input is injected directly into the prompt — no file read required.
allowed-tools: Bash Write
---

**Input:** Original task list assigned to the sub-agent + the sub-agent's full output.

**Step 1 — Save output to a temp file for deterministic counting.**
```bash
Write("/tmp/cc_input.txt", [sub-agent output])
```
Uses `/tmp/` (guaranteed writable on all platforms with bash). Enables `grep` to count mechanically rather than relying on LLM text parsing.

**Step 2 — Count deterministically with grep.**
```bash
Bash("grep -Fc '[x]' /tmp/cc_input.txt")              # done count
Bash("grep -Fc '[o]' /tmp/cc_input.txt")              # skipped count
Bash("grep -Fc 'COMPLETION_CHECKLIST' /tmp/cc_input.txt")  # verify block exists
```
Use `-Fc` (fixed-string, count) — no regex, no escaping issues, portable across all bash environments.
Use these counts as ground truth. Do NOT rely on LLM estimation for count values.

**Step 3 — Identify missing tasks.**
Compare task names in the original task list against lines found in the COMPLETION_CHECKLIST block. A task is MISSING if its name or identifier does not appear in any `[x]` or `[o]` line. This step uses LLM matching — flag any uncertain matches explicitly.

**Step 4 — Compare totals.**
Compare grep-counted items (Step 2) against the number of tasks in the original task list. If checklist item count < assigned task count, flag SUSPICIOUS.

**Step 5 — Determine action.**
- `COMPLETED` — all tasks accounted for in the checklist
- `PARTIAL` — some tasks missing or skipped; list them in REMAINING_TASKS
- `SUSPICIOUS` — checklist has fewer items than tasks assigned (possible truncation or skipping)

Note: `FAILED` (agent crash/error) is intentionally absent from this skill's output. Agent execution failures are detected upstream by `structured-output.md` parsing — a missing or invalid STATUS block in the sub-agent's raw output causes the main agent to retry in foreground mode before invoking completion-checker. By the time completion-checker is invoked, the input is always a valid output; hence only COMPLETED, PARTIAL, and SUSPICIOUS are valid completion states.

Note: Invoke this skill **once per sub-agent output**, not once for a merged multi-agent batch. If checking multiple agents in a batch, invoke sequentially with each agent's individual output. Merging outputs before invoking produces incorrect grep counts.

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
