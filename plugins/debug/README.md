# debug

Systematic debugging workflow: reproduce first, write a failing test, then fix. Prevents jumping to solutions before understanding root cause.

## Installation

```bash
claude plugin install debug@dotclaude
```

## Contents

### Agents

- `debugger` — Debugging specialist for root cause analysis, implementing fixes, and verifying solutions

### Skills

- `/debug` — Step through bug reproduction, failing test creation, and fix in a structured sequence

### Commands

- `/debug` — Debug a bug systematically — reproduce first, write failing test, then fix
