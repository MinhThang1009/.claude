---
name: severity-gate
description: >
  Checks consolidated findings for CRITICAL severity issues and pauses the pipeline
  if any exist. Use after consolidate-findings and before spawning fix agents or
  chain-verifier. Prevents continuing a pipeline when blockers exist.
allowed-tools: Bash Write
---

**Input:** Consolidated findings (from consolidate-findings skill output OR injected text).

**Step 1 — Count CRITICAL findings.**
```bash
Bash("grep '🔴 CRITICAL' [PROJECT_ROOT]/.claude/FINDINGS_REPORT.md 2>/dev/null | grep -v '^|' | grep -v '^| Severity' | wc -l | tr -d ' ' || echo 0")
```
Dùng `grep -v '^|'` để loại bỏ dòng summary table (bắt đầu bằng `|`). Nếu FINDINGS_REPORT.md không tồn tại, count từ injected text thay thế.

**Step 2 — Evaluate gate.**

**If CRITICAL count = 0:**
```
GATE_PASSED:
CRITICAL findings: 0
HIGH findings: [N]
Pipeline may continue to next phase.
ACTION: PROCEED
```

**If CRITICAL count > 0:**
List all CRITICAL findings (file:line + one-line description).
Then output:
```
GATE_PAUSED:
CRITICAL findings: [N]

[List each CRITICAL with file:line and description]

The pipeline is paused because CRITICAL findings exist.
These issues may cause data loss, security breaches, or financial damage if not addressed first.

OPTIONS:
  A) Fix CRITICALs first, then re-run pipeline from checkpoint
  B) Acknowledge and continue anyway (document reason)
  C) Abort pipeline

Awaiting user decision.
```

Write to `.claude/alerts/severity-gate-[timestamp].md`:
```markdown
SEVERITY_GATE_TRIGGERED:
Timestamp: [ISO]
CRITICAL count: [N]
[list of CRITICAL findings]
User decision: PENDING
```

**Do NOT proceed to the next pipeline phase without explicit user confirmation.**

**Step 3 — If user chooses B (continue anyway):**
Update the alert file with:
```
User decision: ACKNOWLEDGED — continuing with known CRITICALs
Reason: [user-provided reason]
```
Output: `GATE_OVERRIDDEN — proceeding with [N] unresolved CRITICALs documented in .claude/alerts/`
