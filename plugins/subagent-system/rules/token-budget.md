# Token Budget

Monitor context usage and select models by task type before spawning agents. Prevents token and cost explosion (5.3).

**Do:**
- Check `/context` **before spawning each subagent** — if usage is above 40%, compact first before spawning more agents. Note: this 40% threshold applies specifically to spawning new subagents (subagent output will consume additional context). It does not mean all activity stops at 40% — the main conversation can continue; the restriction is on spawning new subagents that will return large outputs.
  - **Rationale for 40%:** Claude Code has two window sizes — 200k (Opus/Haiku) and 1M (Sonnet 4.6+). At 200k: 40% used = ~120k remaining, enough for 2–3 large agent returns (~30–50k each). At 1M: 40% = ~600k remaining — very conservative; 65% is the practical threshold. Check which model you're on before applying this rule blindly.
  - **Absolute ceiling regardless of window:** If context exceeds 65%, compact before spawning any new agent. At 200k window this is ~130k used; at 1M window it's ~650k used — both are close to dangerous territory for multi-agent returns.
- Select the model appropriate for the task type by setting the `model:` field in the agent definition:
  - Research, exploration, search → `model: haiku`
  - Review, audit, verification → `model: sonnet`
  - Architecture, planning, complex reasoning → `model: opus`
- Limit subagent output in the prompt: "Report at most 5 findings ranked by severity", "Summary under 200 words"
- Use fork (`CLAUDE_CODE_FORK_SUBAGENT=1`) when a subagent needs a large amount of parent context — fork reuses the parent's prompt cache and is significantly cheaper than manual injection

**Don't:**
- Continue spawning agents when context exceeds 40%
- Pre-load all tools in the prompt — use ToolSearch on-demand instead (ToolSearch significantly reduces token overhead by discovering tools dynamically rather than listing all upfront; exact savings vary by workflow)
- Allow subagents to return full file contents when a summary is sufficient

**When token usage spikes more than 20 percentage points after one agent return:** stop spawning, compact immediately before continuing.
Definition: spike = `(usage_after_return) − (usage_before_spawn)`. Example: 32% before spawn → 54% after return = 22pp spike → trigger compact. A spike this large means the agent returned more context than budgeted and the remaining capacity is shrinking faster than expected.
