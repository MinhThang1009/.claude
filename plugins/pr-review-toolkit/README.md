# pr-review-toolkit

Comprehensive PR review agents specializing in comments, tests, error handling, type design, code quality, and code simplification.

## Installation

```bash
claude plugin install pr-review-toolkit@dotclaude
```

## Contents

### Agents

- `code-reviewer` — General code review against project guidelines, style, and bug detection
- `code-simplifier` — Identifies unnecessary complexity, redundant code, and suggests cleaner implementations
- `comment-analyzer` — Checks comment accuracy vs actual code; finds outdated or misleading documentation
- `pr-test-analyzer` — Evaluates behavioral test coverage, critical gaps, and test quality
- `silent-failure-hunter` — Hunts empty catch blocks, inadequate error handling, and inappropriate fallbacks
- `type-design-analyzer` — Rates type encapsulation, invariant expression, and enforcement on a 1-10 scale

### Skills

- `/code-review` — Review code changes in working tree, branch, or PR for bugs, security, performance, and style
- `/full-review` — Multi-agent adaptive review dispatching up to three specialized agents with consolidated report
- `/review-pr` — Comprehensive PR review using specialized agents

### Commands

- `/code-review` — Code review a pull request
- `/review-pr` — Comprehensive PR review using specialized agents
