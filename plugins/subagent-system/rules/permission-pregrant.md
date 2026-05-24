# Permission Pre-grant

Grant all required tool permissions before spawning background agents. Prevents silent tool denial (5.1) and permission inheritance issues (7.2).

**Do:**
- Before spawning background agents, run one foreground agent with the same tools to trigger permission prompts
- Accept required permissions during that foreground run, then spawn background agents
- Use `disallowedTools` in agent definitions to restrict per-agent access to only what is needed
- Use `permissionMode: default` in agent definitions to prevent bypass inheritance from a parent running in a permissive mode
  - **Plugin agent caveat:** `permissionMode` is silently ignored in plugin-defined agents (security restriction). For plugin agents, use `disallowedTools` to restrict access — `permissionMode` has no effect and provides a false sense of security if relied upon.

**Don't:**
- Use `--dangerously-skip-permissions` when the session will spawn subagents — all subagents inherit the bypass, including those inside worktrees (`isolation: "worktree"` provides filesystem isolation but NOT permission restriction)
- Assume background agents will prompt for missing permissions — they silently auto-deny ungranted tools and continue

**Signals of silent tool denial:**
- Output is empty or under 50 words for a complex task
- Zero findings for a large scope (e.g., 10+ files)
- No evidence quotes in output despite an audit task

When these signals appear: retry the task in foreground mode to surface permission prompts.
