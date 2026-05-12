# test-toolkit

Specialized agents for writing tests and analyzing test coverage quality. Covers happy paths, edge cases, error paths, and behavioral coverage gaps.

## Installation

```bash
claude plugin install test-toolkit@dotclaude
```

## Contents

### Agents

- `test-writer` — Writes tests for existing code covering happy path, edge cases, and error paths using the project's test framework
- `test-analyzer` — Evaluates existing test suite quality: behavioral coverage, critical gaps, brittle tests, and missing edge cases
