# session

Session management tools for context window monitoring and conversation handoff.

## Installation

```bash
claude plugin install session@dotclaude
```

## Contents

### Skills

- `/context-check` — Check context window usage and get recommendations (compact, clear, subagent, or handoff)
- `/handoff` — Generate a handoff brief before compacting or switching to a new session; preserves files changed, architecture decisions, and next steps
