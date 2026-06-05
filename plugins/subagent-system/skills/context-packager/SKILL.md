---
name: context-packager
description: This skill should be used before spawning a dependent agent when the previous phase produced interface changes, breaking changes, new constraints, or key file modifications the next agent must not violate. Extracts only the minimum necessary context — not the full prior output. Uses character count to decide INJECT (≤4,000 chars) vs USE_FORK (>4,000 chars). Also trigger when user asks to "package context for next phase", "prepare agent handoff", or "extract phase context".
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
- If the context needed exceeds ~1,000 tokens, recommend using a fork subagent (`CLAUDE_CODE_FORK_SUBAGENT=1`) instead of manual injection — fork reuses the parent's prompt cache and handles large context more efficiently

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
Estimated tokens: ~N  ← count characters in this package ÷ 4 (code-heavy text ≈ 3.5–4 chars/token)
Recommendation: INJECT | USE_FORK
```

**Recommendation logic (character-count based — more reliable than LLM estimation):**
- Package character count ≤ 2,000 chars (~500 tokens) → `INJECT`
- Package character count 2,000–4,000 chars (~500–1,000 tokens) → `INJECT` with caution note
- Package character count > 4,000 chars (>1,000 tokens) → `USE_FORK`

Use character count, not LLM token estimate — LLMs systematically underestimate token counts for code (identifiers and symbols count more than prose words).
