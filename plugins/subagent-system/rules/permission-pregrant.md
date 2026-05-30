# Permission Pre-grant

Grant all required tool permissions before spawning background agents. Prevents silent tool denial and permission inheritance issues.

**Do:**
- Before spawning background agents, run one foreground agent with the same tools to trigger permission prompts
- Accept required permissions during that foreground run, then spawn background agents
- Use `disallowedTools` in agent definitions to restrict per-agent access to only what is needed
- `permissionMode` is **not** a reliable boundary against a permissive parent: if the parent runs `bypassPermissions`, `acceptEdits`, or `auto` mode, the parent takes precedence and the child's `permissionMode` is ignored *(Claude Code sub-agents docs)*. It is also silently ignored for **plugin-defined** agents. Restrict access with `disallowedTools`, not `permissionMode`.

**Don't:**
- Use `--dangerously-skip-permissions` when the session will spawn subagents — all subagents inherit the bypass, including those inside worktrees (`isolation: "worktree"` provides filesystem isolation but NOT permission restriction)
- Assume background agents will prompt for missing permissions — they silently auto-deny ungranted tools and continue

**Signals of silent tool denial:**
- Output is empty or under 50 words for a complex task
- Zero findings for a large scope (e.g., 10+ files)
- No evidence quotes in output despite an audit task

When these signals appear: retry the task in foreground mode to surface permission prompts.
