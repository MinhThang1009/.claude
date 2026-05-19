---
name: consolidate-findings
description: >
  Merges findings from multiple audit agents into a single report sorted by severity.
  Deduplicates overlapping findings across agents. Run after all parallel audit agents
  complete, before finding-validator. Produces a FINDINGS_REPORT.md in .claude/.
allowed-tools: Bash Write
---

**Input:** List of agent outputs (injected directly) OR paths to progress files.

**Step 1 — Parse findings from each agent output.**
For each agent, extract findings with format:
`[severity emoji] [file:line] — [description]`

Severity mapping:
- 🔴 = CRITICAL (weight 4)
- 🟠 = HIGH (weight 3)
- 🟡 = MEDIUM (weight 2)
- 🟢 = LOW (weight 1)

**Step 2 — Deduplicate.**
Two findings are duplicates if they reference the same `file:line` AND describe the same issue category (e.g., both flag "missing rate limit" at same location). When duplicating:
- Keep the HIGHER severity verdict
- Note "Confirmed by N agents" in the merged finding
- Do NOT merge findings at different lines even if same issue type (they may be separate instances)

**Step 3 — Sort by severity, then by file path.**
Order: CRITICAL → HIGH → MEDIUM → LOW.
Within same severity, group by file path alphabetically.

**Step 4 — Count totals.**
```
CRITICAL: N | HIGH: N | MEDIUM: N | LOW: N | TOTAL: N
Duplicates removed: N
Agents consolidated: N
```

**Step 5 — Write FINDINGS_REPORT.md.**
```bash
Bash("mkdir -p .claude")
Write(".claude/FINDINGS_REPORT.md", [report content])
```

**Output format:**

```markdown
# Security Audit Findings Report
Generated: [ISO timestamp]
Agents: [list]

## Summary
| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | N |
| 🟠 HIGH | N |
| 🟡 MEDIUM | N |
| 🟢 LOW | N |
| **TOTAL** | **N** |

Duplicates removed: N

## Critical Findings (fix immediately)
### [file:line]
**Severity:** 🔴 CRITICAL
**Agent(s):** T1, T3
**Issue:** [description]
**Fix:** [specific fix]

[additional findings...]

## High Findings
[...]

## Medium Findings
[...]

## Low Findings
[...]
```

**Step 6 — Report.**
```
CONSOLIDATION_COMPLETE:
Report: .claude/FINDINGS_REPORT.md
Total: [N] findings ([C] CRITICAL, [H] HIGH, [M] MEDIUM, [L] LOW)
Duplicates removed: [N]
Proceed to: /severity-gate or finding-validator for top findings verification
```
