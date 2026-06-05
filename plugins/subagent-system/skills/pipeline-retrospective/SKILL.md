---
name: pipeline-retrospective
description: This skill should be used after every completed pipeline run to evaluate agent and skill performance, then propose targeted improvements to the plugin itself. Trigger after /audit-output as the final mandatory step, or when user asks to "retrospect", "evaluate pipeline results", "improve plugin", or "what should we improve". Reads all pipeline artifacts and writes actionable proposals to .claude/improvement-proposals.md.
allowed-tools: Read Glob Write Bash
---

Evaluate the completed pipeline run and propose specific improvements to the plugin's agents, skills, and commands based on what actually happened.

**Input:** PROJECT_ROOT (injected) + paths to pipeline artifacts.

---

**Step 0 — Resolve PROJECT_ROOT.**
If `PROJECT_ROOT:` was injected in the input, use it. Otherwise auto-detect:
```bash
Bash("cat .claude/PIPELINE_CONFIG.md 2>/dev/null | sed -n 's/^PROJECT_ROOT:[[:space:]]*//p'")
```
If that returns empty, fall back to:
```bash
Bash("git rev-parse --show-toplevel 2>/dev/null || echo '.'")
```
Set `PROJECT_ROOT` to the result. Use it for all path references below.

---

**Step 1 — Collect pipeline artifacts.**

Glob for all artifacts produced during the run:
```bash
Bash("ls [PROJECT_ROOT]/.claude/checkpoints/ 2>/dev/null")
Bash("ls [PROJECT_ROOT]/.claude/progress/ 2>/dev/null")
Bash("ls [PROJECT_ROOT]/.claude/alerts/ 2>/dev/null")
```

Read these files if they exist:
- `[PROJECT_ROOT]/.claude/FINDINGS_REPORT.md` — consolidated findings
- `[PROJECT_ROOT]/.claude/AUDIT_REPORT.md` — final audit output
- All progress files: `[PROJECT_ROOT]/.claude/progress/*.md`
- All alert files: `[PROJECT_ROOT]/.claude/alerts/*.md`
- Most recent checkpoint: `[PROJECT_ROOT]/.claude/checkpoints/phase-*.md` (latest by timestamp)

If no artifacts found: output `RETROSPECTIVE_SKIPPED: No pipeline artifacts found. Run /init-pipeline first.` and stop.

---

**Step 2 — Evaluate 6 performance dimensions.**

For each dimension, assign a score (GOOD / PARTIAL / POOR) with evidence:

**D1 — Coverage quality**
Evidence: progress files (were all assigned files processed?) and any coverage-verifier output in conversation history.
Flag POOR if: any agent processed <50% of assigned files, or no progress files were written at all.

**D2 — Finding quality**
Evidence: FINDINGS_REPORT.md — count CRITICAL/HIGH/MEDIUM/LOW, check if finding-validator was run, check false positive rate.
Flag POOR if: >30% findings were FALSE_POSITIVE, or FINDINGS_REPORT.md is empty despite a security audit scope.

**D3 — Completion rate**
Evidence: checkpoint files and progress files — were COMPLETION_CHECKLISTs complete?
Flag POOR if: any checkpoint shows STATUS: PARTIAL or SUSPICIOUS, or TASKS_PROCESSED < TASKS_TOTAL.

**D4 — Pipeline health**
Evidence: alert files and AUDIT_REPORT.md — were there STALL/BLOCKED/POSSIBLE_SILENT_DENIAL anomalies? Did chain-verifier return APPROVED?
Flag POOR if: any alert files exist, or AUDIT_REPORT.md shows PIPELINE_STATUS: ISSUES_FOUND.

**D5 — Fix quality**
Evidence: most recent checkpoint's "Files modified" list — were fixes surgical (only assigned files) or did they spill into unassigned files?
Flag POOR if: any out-of-scope files were modified per chain-verifier UNEXPECTED_CHANGES.

**D6 — Skill triggering**
Infer from what happened: Which skills were actually invoked vs which should have been? Were there phases where convention-injector, completion-checker, or coverage-verifier were skipped?
Flag POOR if: any mandatory step (convention-injector before spawning, completion-checker after each agent) appears to have been skipped.

---

**Step 3 — Identify root causes and map to plugin components.**

For each POOR or PARTIAL dimension, identify which agent/skill/command is responsible:

| Symptom | Likely root cause in plugin |
|---------|----------------------------|
| Low coverage (D1) | Agent prompt missing progress file instruction; convention-injector not invoked |
| High false positive rate (D2) | finding-validator description too weak — triggers too late |
| Incomplete checklists (D3) | completion-checker description doesn't specify COMPLETION_CHECKLIST format requirement clearly |
| Anomalies / stalls (D4) | pipeline-monitor invoked too late or not invoked at all |
| Out-of-scope fixes (D5) | Fix agent prompts lacked scope-boundary instruction |
| Skipped mandatory skills (D6) | plan-tasks.md pipeline shape doesn't enforce these steps |

---

**Step 4 — Write improvement proposals.**

Write `[PROJECT_ROOT]/.claude/improvement-proposals.md`:

```markdown
# Pipeline Improvement Proposals
Generated: [ISO timestamp]
Based on: [pipeline run description]

## Performance Summary
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | GOOD/PARTIAL/POOR | [1-line evidence] |
| D2 Finding quality | ... | ... |
| D3 Completion | ... | ... |
| D4 Pipeline health | ... | ... |
| D5 Fix quality | ... | ... |
| D6 Skill triggering | ... | ... |

## Improvement Proposals

### P-1: [Short name]
**Target:** [agent/skill/command filename]
**Problem:** [What went wrong, with specific evidence]
**Proposed change:** [Exact text to add/modify/remove]
**Priority:** HIGH | MEDIUM | LOW
**Rationale:** [Why this change would prevent the observed problem]

### P-2: ...
```

If all 6 dimensions are GOOD: write "No improvements needed — pipeline ran cleanly."

---

**Step 5 — Output structured report.**

```
RETROSPECTIVE_REPORT:
Run timestamp: [ISO]
Artifacts read: [N checkpoints, M progress files, K alerts]

Performance:
  D1 Coverage:        [score]
  D2 Finding quality: [score]
  D3 Completion:      [score]
  D4 Pipeline health: [score]
  D5 Fix quality:     [score]
  D6 Skill triggering:[score]

Proposals written: [N]
File: .claude/improvement-proposals.md

Next step: Review proposals and run /apply-improvements to implement,
or manually edit the plugin files at the specified targets.
```
