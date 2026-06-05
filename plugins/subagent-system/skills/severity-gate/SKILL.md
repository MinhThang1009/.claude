---
name: severity-gate
description: This skill should be used when the user asks to "run severity gate", "check for critical findings", "block pipeline on critical", or after consolidate-findings and before fix agents or chain-verifier. Outputs GATE_PASSED (0 CRITICALs) or GATE_PAUSED (≥1 CRITICAL) with OPTIONS A/B/C for user decision.
allowed-tools: Bash Write
---

**Input:** Consolidated findings (from consolidate-findings skill output OR injected text). Optionally `PROJECT_ROOT: /path` can be injected.

**Step 0 — Resolve PROJECT_ROOT.**
If `PROJECT_ROOT:` was injected in the input, use it. Otherwise auto-detect:
```bash
Bash("cat .claude/PIPELINE_CONFIG.md 2>/dev/null | sed -n 's/^PROJECT_ROOT:[[:space:]]*//p'")
```
If that returns empty, fall back to:
```bash
Bash("git rev-parse --show-toplevel 2>/dev/null || echo '.'")
```
Set `RESOLVED_ROOT` to the result. If RESOLVED_ROOT is `.`, warn "PROJECT_ROOT not resolved — grepping relative path, may miss findings if session cwd ≠ project root."

**Step 1 — Count CRITICAL findings.**

First check if FINDINGS_REPORT.md exists:
```bash
Bash("test -f \"[RESOLVED_ROOT]/.claude/FINDINGS_REPORT.md\" && echo EXISTS || echo MISSING")
```
If MISSING and no findings were injected as text input: output `GATE_BLOCKED: FINDINGS_REPORT.md not found and no findings injected — cannot evaluate gate. Run consolidate-findings first.` and stop. Do NOT output GATE_PASSED.

If MISSING but findings were injected as text: count from injected text directly.

If EXISTS:
```bash
Bash("grep '🔴 CRITICAL' [RESOLVED_ROOT]/.claude/FINDINGS_REPORT.md 2>/dev/null | grep -v '^|' | wc -l | tr -d ' ' || echo 0")
```

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

Get a filename-safe timestamp: `Bash("date -u +%Y%m%dT%H%M%S")   # → TIMESTAMP`

Write to `[RESOLVED_ROOT]/.claude/alerts/severity-gate-[TIMESTAMP].md`:
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
