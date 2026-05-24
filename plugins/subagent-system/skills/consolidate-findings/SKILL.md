---
name: consolidate-findings
description: This skill should be used when the user asks to "merge findings", "consolidate audit results", "combine security findings", or after all parallel audit agents complete and before running finding-validator or severity-gate. Produces FINDINGS_REPORT.md sorted CRITICAL→HIGH→MEDIUM→LOW with duplicates removed.
version: 0.1.0
allowed-tools: Bash Write
---

**Input:** List of agent outputs (injected directly) OR paths to progress files.

**Step 1 — Parse findings from each agent output.**

Two formats are supported — detect per-agent which applies:

**Format A** (security-auditor, quick-audit style):
`[severity emoji] [file:line] — [description]`

**Format B** (pipeline-reviewer style — block format):
```
Finding: [description]
File: [path]
Line: [N]
Evidence: "[quote]"
Severity: CRITICAL | HIGH | MEDIUM | LOW
```
For Format B, map severity text to emoji: CRITICAL→🔴, HIGH→🟠, MEDIUM→🟡, LOW→🟢.
If an agent's output contains `Finding:` / `Severity:` blocks, use Format B. Otherwise use Format A.

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
PROJECT_ROOT must be injected in the input or auto-detected. Resolve it first (the return value is the path):
```bash
Bash("git rev-parse --show-toplevel 2>/dev/null || echo '.'")   # → ROOT
Bash("mkdir -p \"[ROOT]/.claude\"")
Write("[ROOT]/.claude/FINDINGS_REPORT.md", [report content])
```
Use absolute path to avoid writing to session cwd instead of the project directory.

After writing, verify the file is non-empty:
```bash
Bash("wc -c < \"[ROOT]/.claude/FINDINGS_REPORT.md\" | tr -d ' '")
```
If result is `0`: output `CONSOLIDATION_FAILED: FINDINGS_REPORT.md was written but is empty — report content was not rendered. Do NOT proceed to severity-gate.` and stop.

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
