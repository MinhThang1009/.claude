# CI/CD Gates

Run linting, type-checking, and tests after every implementation phase before proceeding to the next. Prevents code quality degradation (6.5) through deterministic enforcement — a failing gate stops the pipeline unconditionally, unlike iteration-cleanup which is probabilistic.

> **This rule is a template.** It does nothing until you define the actual commands for your project. Add the three lines below to your project's `CLAUDE.md` (or inject into the main agent's context before starting a pipeline):

```
LINT_COMMAND:      npm run lint          # replace with your linter
TEST_COMMAND:      npm test              # replace with your test runner
TYPECHECK_COMMAND: tsc --noEmit         # replace with your type checker, or omit if N/A
```

Other examples:
```
# Python:     ruff check . / pytest -q / mypy .
# Go:         golangci-lint run / go test ./... / (no separate typecheck)
# Rust:       cargo clippy / cargo test / (typecheck = cargo build)
# Ruby:       rubocop / bundle exec rspec / (no separate typecheck)
```

**Do:**
- Run all three gate commands after every agent edit phase, before spawning the next phase
- Stop the pipeline immediately if ANY gate command exits with non-zero status
- Inject `TEST_COMMAND` into `handoff-validator` skill invocations (that skill runs it as part of phase handoff verification)
- Treat gate failures as a signal to spawn `iteration-cleanup` (`../agents/iteration-cleanup.md`) before retrying

**Don't:**
- Proceed to the next agent phase if lint, tests, or type-check fail
- Let agents self-assess code quality in place of running a gate
- Skip gates between phases to reduce latency — a missed regression compounds into later phases

**If no CI/CD is set up:** Define at minimum one test command before using multi-agent implementation workflows. Without a gate, `iteration-cleanup` (probabilistic) is the only quality check — significantly weaker.
