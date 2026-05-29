# Coding Standards

> Auto-imported every session via `rules/`.

## Before Starting

- **State assumptions explicitly** before implementing — even when fairly confident. "I understand X is Y; correct me if wrong."
- **If something is unclear** → stop, name exactly what's unclear, and ask.

## Core Principles

- **Read before you write**: prefer reading the whole containing function before making a change; for functions >100 lines, 30 lines of context around the change plus the signature/return is enough. Small fixes (1–2 lines) can use narrower context. New file → scan a similar file first to match the pattern.
- **Codebase conventions first, "best practices" second**. snake_case if the codebase uses snake_case. Tabs if the codebase uses tabs.
- **Correct > clean > fast**. Working code matters more than fancy patterns.
- **Don't over-engineer**. YAGNI. Generic abstractions should emerge from real needs, not speculation. If 200 lines can be solved in 50 → rewrite.
- **Functions < 50 lines** ideally. >100 lines → consider splitting (unless the logic is cohesive throughout). Nesting >3 levels → consider flattening.
- **Name things clearly**. `getUserById` over `getUser`. `isEmailVerified` over `verified`. Avoid `data`, `info`, `obj` unless context makes them obvious.

## Surgical Changes

- **Only change what was asked**. Every changed line must trace directly back to the user's request.
- Do NOT "improve" surrounding code, comments, or formatting while fixing something else. Do NOT refactor things that aren't broken.
- Orphans you created (imports, variables, functions that are unused *after* your change) → **delete them**. Pre-existing dead code → **mention it, don't delete** unless the user asks.
- Self-check: "Would a senior engineer find this diff more complex than necessary?" If yes → simplify.

## Verification During Refactoring

- Refactoring → **run tests BEFORE changing** (confirm baseline passes), make the change, **run tests AFTER** (confirm no regressions).
- If the task is vague ("make it work", "clean up") → translate it into specific, verifiable criteria before starting. Weak criteria → ask the user instead of guessing.

## Comments

- **Comment WHY, not WHAT** (code already says WHAT).
- **Vietnamese** for comments explaining logic/rationale (fully English project → English).
- **English** for TODO/FIXME tags (so tools can grep them): `// TODO(name): Short description`.
- Docstrings/JSDoc: Vietnamese for the description, but keep standard format (`@param`, `@returns`, `@throws`).

Good example:
```python
# Cache by IP to prevent users from bypassing rate limits across multiple accounts
limiter = RateLimiter(key_func=get_remote_ip)
```

Bad example (comments WHAT instead of WHY):
```python
# Create rate limiter
limiter = RateLimiter(...)
```

## Error Handling

- Do NOT empty-catch / swallow exceptions. Errors must be handled intentionally.
- Do NOT use blanket `catch (Exception e)` — catch the specific expected error types.
- Do NOT add error handling for scenarios that cannot happen. Only validate at system boundaries (user input, external APIs, I/O).
- Prefer **early return / guard clauses / Result types** over try-catch where possible. Use try-catch only when you genuinely need to catch exceptions (I/O, network, parsing).
- Fallback behavior must be **explicit and justified** — never silently fall back without the user knowing. Optional chaining (`?.`) can hide errors — only use it when `undefined` is a valid result.
- Re-throw with context: `throw new ServiceError("Failed to fetch user", { cause: e })`.
- User-facing error messages: **Vietnamese**, generic, no stack trace or internal info exposed.
- Internal logs: Vietnamese OK, include context (user id, request id).

## Testing

- Project has a test framework → every new feature has tests, every bug fix has failing-test-then-fix.
- Name tests descriptively: `test_login_fails_when_password_wrong` over `test_login_2`.
- Arrange-Act-Assert. One logical assertion per test.
- Do NOT over-mock: only mock external dependencies (DB, HTTP, time, random). Don't mock the code under test.
- Test descriptions in Vietnamese: `it('trả về 401 khi token hết hạn', ...)`.

## Performance

- **Measure before optimizing**. Profile (`cProfile`, `py-spy`, Chrome DevTools, `perf`) — don't guess.
- **Big-O matters more than micro-optimization**. O(n²) on 10k items = 100 million operations — very slow; micro-optimization won't save it.
- DB: index on queried columns, not randomly. N+1 queries → batch or join.
- Network: batch requests, cache appropriately, set timeouts.

## Type Safety

- Project has a type system (TypeScript, mypy, Pydantic, Rust…) → use it fully.
- Do NOT use `any`/`Any` unless truly necessary, with an explanatory comment. Prefer `unknown` (TS) over `any` for values whose type isn't known — it's type-safe and forces narrowing before use.
- Strong types at boundaries (input from user/network/file): validate at runtime, don't trust the TypeScript compiler alone.

## Style

- Format using the project formatter (`prettier`, `black`, `gofmt`, `rustfmt`…). Don't change style arbitrarily.
- Lint must pass before reporting done. `eslint`, `ruff`, `clippy`, `golangci-lint`…
- Import order: follow formatter conventions, not manual ordering.

## Red Flags — STOP AND ASK

Confirm with the user before:
- Adding a new dependency (even a "popular" one) — check maintained/license/CVEs first (see security.md §Dependencies).
- Changing a DB schema / running a migration.
- Modifying production config / deployment config.
- Editing a shared file (used by >3 modules) in a way that changes behavior.
- Cross-cutting refactor (>5 files).
- Changing a public API signature.
- Deleting files/code you're not 100% certain is dead.
