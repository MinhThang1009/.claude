---
name: goal-anchor
description: >
  Template header for sub-agent prompts at risk of goal drift — specifically long-running
  agents (over 15 turns) and any agent resuming after context compaction. Prevents gradual
  deviation from original objectives.
tools: []
---

Inject this block at the start of the sub-agent prompt. Replace bracketed placeholders with actual content from the `/plan-tasks` output.

```
OBJECTIVE (fixed — does not change during this session):
[Original objective — copy verbatim from /plan-tasks output]

SCOPE (fixed):
[File list and constraints — copy from execution plan]

Every 5 turns, check: "Is my current output directly addressing the OBJECTIVE above?"
If not → stop, explain why drift occurred, return to the objective.
```

**maxTurns guidance** (set in the agent definition, not here):
- Debate and review agents: `maxTurns: 7` — echoing risk increases after 7 turns
- General task agents: `maxTurns: 15` to `maxTurns: 20` — goal drift risk rises with turn count
- These are two distinct thresholds for two distinct failure modes

**Compact + re-inject pattern for phase transitions.**

Instead of letting an agent run continuously across multiple phases in one session:

1. At the end of each phase, run `/compact` with the instruction: "Preserve objective and key decisions; drop implementation details."
2. Re-inject the original objective verbatim into the next phase's context.
3. Spawn the next phase with a clean context that includes the objective explicitly.

Reason: longer context causes models to pattern-match against accumulated text rather than reason from the objective, increasing drift with each turn. Re-injecting the objective after compaction resets this tendency.

**When to use this skill:**
- Any agent expected to run more than 15 turns
- Any agent resuming after a `/compact` or session interruption
- Any agent in a chain where prior phases have accumulated significant context

---

## Echo Prevention (for multi-reviewer / debate setups — issue 6.1)

When spawning multiple agents to review the same artifact in parallel, apply these constraints to prevent echoing (agents abandoning assigned roles and mirroring each other's outputs):

**Spawn rules:**
- Spawn review agents in parallel and in complete isolation — do NOT pass Agent B's output to Agent A before both have completed their independent assessment
- Set `maxTurns: 7` in review/debate agent definitions (echoing begins after 7+ turns)
- Require each agent's output to include a `DISAGREEMENT:` field stating explicitly what it disagrees with from any prior context

**Runtime echo detection:**
After receiving outputs from two or more review agents — if their conclusions appear substantially identical in both reasoning and evidence, spawn a fresh LLM check:
> "Compare these two outputs: [A] and [B]. Are they independently reasoned, or does B appear to echo A's reasoning? Answer: INDEPENDENT or ECHO with one sentence of explanation."

If result is ECHO: discard the echoing agent's output and re-spawn with a stronger role isolation prompt (agent must not see A's output at all).
