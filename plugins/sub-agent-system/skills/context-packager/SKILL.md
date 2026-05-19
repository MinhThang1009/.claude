---
name: context-packager
description: >
  Extracts the minimum context a dependent sub-agent needs from the previous phase's output.
  Use before spawning any agent whose task depends on the results of a prior agent. Prevents
  both context loss (too little) and context rot (too much).
allowed-tools: Read
---

**Input:** Previous phase results + description of the next agent's task.

Extract only the information the next agent needs to avoid breaking existing work:

1. **Interface changes** — function signatures, API contracts, or data structures that changed in the previous phase
2. **Breaking changes** — anything the next agent must not violate (renamed functions, removed parameters, changed return types)
3. **Key file changes** — which files were modified and a one-line description of what changed
4. **Constraints discovered** — performance limits, security requirements, compatibility notes uncovered during the previous phase

**Target output size: ≤500 tokens.** This is a guideline, not a hard limit:
- If interface changes are complex, include more detail
- If the context needed exceeds ~1,000 tokens, recommend using a fork sub-agent (`CLAUDE_CODE_FORK_SUBAGENT=1`) instead of manual injection — fork reuses the parent's prompt cache and handles large context more efficiently

**Exclude:**
- Internal implementation details that do not affect the next agent's task
- Style or formatting changes
- Intermediate reasoning or chain-of-thought from the previous phase

**Empty context guard:** After extracting, if all four sections (interface changes, breaking changes, key file changes, constraints) are empty or contain only "none" / "N/A" entries, output:
```
WARNING: context package is empty — the previous phase may not have produced output,
or its output was not in a parseable form. Verify the previous phase actually completed
before injecting this package into the next agent.
```

**Output format:**

```
CONTEXT PACKAGE for [next agent task]:
─────────────────────────────────────
Interface changes:
- [function/API]: [what changed]

Breaking changes:
- [what must not be violated]

Key file changes:
- [file]: [one-line summary]

Constraints:
- [constraint]: [detail]
─────────────────────────────────────
Estimated tokens: ~N
Recommendation: INJECT | USE_FORK (if >1000 tokens)
```
