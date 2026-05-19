# Token Budget

Monitor context usage and select models by task type before spawning agents. Prevents token and cost explosion (5.3).

**Do:**
- Check `/context` **before spawning each sub-agent** — if usage is above 40%, compact first before spawning more agents. Note: this 40% threshold applies specifically to spawning new sub-agents (sub-agent output will consume additional context). It does not mean all activity stops at 40% — the main conversation can continue; the restriction is on spawning new sub-agents that will return large outputs.
- Select the model appropriate for the task type by setting the `model:` field in the agent definition:
  - Research, exploration, search → `model: haiku`
  - Review, audit, verification → `model: sonnet`
  - Architecture, planning, complex reasoning → `model: opus`
- Limit sub-agent output in the prompt: "Report at most 5 findings ranked by severity", "Summary under 200 words"
- Use fork (`CLAUDE_CODE_FORK_SUBAGENT=1`) when a sub-agent needs a large amount of parent context — fork reuses the parent's prompt cache and is significantly cheaper than manual injection

**Don't:**
- Continue spawning agents when context exceeds 40%
- Pre-load all tools in the prompt — use ToolSearch on-demand instead (ToolSearch significantly reduces token overhead by discovering tools dynamically rather than listing all upfront; exact savings vary by workflow)
- Allow sub-agents to return full file contents when a summary is sufficient

**When token usage spikes more than 20% after one agent return:** stop spawning, compact immediately before continuing.
