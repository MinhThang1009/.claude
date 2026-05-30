# Token Budget

Monitor context usage and select models by task type before spawning agents. Prevents token and cost explosion.

**Spawn threshold — check `/context` before spawning each subagent.** Compact first if usage is above the window-appropriate threshold:

| Window | Soft threshold (compact before spawning more) | Absolute ceiling (compact before ANY new agent) |
| ------ | --------------------------------------------- | ----------------------------------------------- |
| 200k (Haiku) | ~40% → ~120k left, fits 2–3 large returns (~30–50k each) | ~65% → ~130k used |
| 1M (Opus 4.6+ / Sonnet 4.6+, plan-dependent + `[1m]` alias) | ~50% → ~500k left | ~65% → ~650k used |

- The threshold gates **spawning new subagents** (their output adds context), not all activity — the main conversation can continue.
- Check which model/window you're on before applying the rule.

**Do:**

- Set `model:` per task type: research / exploration / search → `haiku`; review / audit / verification → `sonnet`; architecture / planning / complex reasoning → `opus`.
- Limit subagent output in the prompt (e.g. "report at most 5 findings ranked by severity", "summary under 200 words").
- Use a fork (`CLAUDE_CODE_FORK_SUBAGENT=1`) when a subagent needs a lot of parent context — it reuses the parent's prompt cache, cheaper than manual injection.

**Don't:**

- Spawn past the window-appropriate soft threshold (~40% on 200k, ~50% on 1M).
- Pre-load all tools in the prompt → use ToolSearch on-demand (discovers tools dynamically rather than listing all upfront; exact savings vary by workflow).
- Let subagents return full file contents when a summary suffices.

**Spike rule** — if context jumps >20 percentage points after one agent return, stop spawning and compact before continuing.

- Spike = `usage_after_return − usage_before_spawn`. Example: 32% before spawn → 54% after return = 22pp → compact.
- A large spike means the agent returned more context than budgeted; remaining capacity is shrinking faster than expected.
