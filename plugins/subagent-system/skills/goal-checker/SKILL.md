---
name: goal-checker
description: This skill should be used after receiving output from any subagent in a long-running pipeline to verify the output actually addresses the original objective — not a related but different problem. Invoke when a subagent's output seems off-topic, overly broad, or suspiciously brief. Returns a 0–5 score; below 4 triggers intervention (re-anchor for 2–3, compact + respawn for <2). Also trigger when user asks to "check goal alignment" or "detect goal drift".
version: 0.1.0
---

**Input:** Original objective (verbatim quote) + agent output to evaluate.

Score the output on three criteria:

**1. Direct address (0–2)**
Does the output explicitly address the objective, or does it only touch on tangentially related topics?
- 2: Output directly and specifically addresses the objective
- 1: Output addresses parts of the objective but omits key aspects
- 0: Output is about related topics but does not address the objective itself

**2. Completeness (0–2)**
Does the output cover the key aspects of the objective?
- 2: All key aspects are covered
- 1: Most key aspects are covered; minor gaps
- 0: Significant aspects of the objective are absent

**3. Action alignment (0–1)**
Do the actions taken (edits, findings, decisions) serve the objective?
- 1: Actions directly serve the objective
- 0: Actions are unrelated to or diverge from the objective

**Total score: 0–5**

**Output format:**

```
GOAL_CHECK:
Objective: "[verbatim quote]"

Score breakdown:
  Direct address [0-2]: [score] — [one sentence of reasoning]
  Completeness [0-2]: [score] — [one sentence of reasoning]
  Action alignment [0-1]: [score] — [one sentence of reasoning]

Total score: [N]/5

VERDICT: ALIGNED | PARTIAL_DRIFT | DRIFTED
  ALIGNED (≥4): output addresses the objective well
  PARTIAL_DRIFT (2–3): output addresses the objective partially; drift has begun
  DRIFTED (<2): output has diverged from the objective

Evidence of drift: [specific examples from the output, or NONE]

Recommended action:
  ALIGNED: Continue
  PARTIAL_DRIFT: Re-anchor with goal-anchor skill, then continue
  DRIFTED: Compact + re-inject objective + spawn a fresh phase
```

**In automated (unattended) pipelines:** This skill produces an LLM score with no secondary verification. A miscalibrated score (scoring drifted output as ALIGNED) propagates silently — there is no meta-checker for this skill. Apply a conservative rule at the boundary:
- Score exactly 3 (PARTIAL_DRIFT boundary) → treat as PARTIAL_DRIFT and re-anchor; do not continue without re-anchoring.
- For high-stakes pipelines: invoke this skill twice with different phrasings and escalate if results disagree (scores differ by ≥2).

  **Template for second phrasing (negated form):**
  - Phrasing 1 (positive): `"[verbatim objective as originally stated]"`
  - Phrasing 2 (negated): `"Is there any evidence that [key outcome of objective] was NOT achieved? List specific gaps, omissions, or contradicting evidence in the output."`

  The negated phrasing activates different reasoning paths and is more likely to surface missed requirements that a positive framing overlooks. If the two scores differ by ≥2, treat the lower score as authoritative and escalate.
