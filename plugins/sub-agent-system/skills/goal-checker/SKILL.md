---
name: goal-checker
description: >
  Evaluates whether a sub-agent's output directly addresses the original objective. Use
  after each phase of long-running workflows to detect goal drift before it compounds.
  Returns a 0-5 score — score below 3 triggers re-anchoring. For CRITICAL phases, invoke
  as a fresh sub-agent (not inline) to avoid the same self-review bias this skill is
  designed to detect. Inline invocation is acceptable for routine phase checks.

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
