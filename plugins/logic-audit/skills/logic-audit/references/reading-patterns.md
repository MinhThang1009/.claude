# Reading Patterns — Systematic Code Analysis

Reference for Phase 2 of the logic-audit skill. Load while reading each source file.

---

## Null / Undefined / None Boundary Failures

The most common class of logic bug across all languages:

- Function assumes input is non-null but no guard exists at the entry point
- Optional chaining (`?.`, `&.`, `?.`) hides a null that should be an error
- Default value masks a missing required field: `x || defaultValue` silently accepts invalid input
- Array/list index access without bounds check: `items[0]` when `items` might be empty
- Map/dict access without existence check: `obj[key]` when key might be absent

**Verify:** trace every parameter back to its origin. Is there a path where it arrives as null/undefined/None? If so, is that path handled or does it silently propagate?

---

## Type Coercion and Comparison Bugs

- Loose equality (`==` in JS, implicit casting in other langs) treating `0`, `""`, `null`, `false` as equivalent when they are not
- String-to-number conversion that silently produces `NaN` or `0` instead of failing
- Integer division producing `0` instead of a fraction (Python 2 vs 3, integer math in Go/Java/C)
- Comparing values of different numeric types: float precision loss, overflow when casting large integers
- String comparison that is case-sensitive when the spec requires case-insensitive (or vice versa)

**Aggregate functions on empty collections:**
- Calling `min`, `max`, `sum`, `average` on an empty list produces a sentinel or throws — always check whether the collection could be empty after filtering
- In most languages (Python, Java, Go) aggregating an empty collection raises an explicit error — easy to catch
- **JS-specific silent trap:** `Math.min(...[])` = `Infinity`, `Math.max(...[])` = `-Infinity` — no error, just a wrong sentinel value. Any downstream `> 0` or `!== null` check silently passes. Same for `reduce()` without initial value → `TypeError` on empty. **Verify:** add `.length > 0` guard before `Math.min/max(...)` spread, or use `reduce` with an explicit initial value.

---

## Off-By-One Errors

- Loop bound: `< length` vs `<= length`, `> 0` vs `>= 0`
- Index: 0-based vs 1-based inconsistency between caller and callee
- Pagination: `offset = page * size` vs `offset = (page - 1) * size`
- Date/time range: `>=` vs `>` at boundary, inclusive vs exclusive end
- String slicing: `str[0:n]` vs `str[0:n+1]`

---

## Async / Concurrency Patterns

**Race conditions to look for:**
- Read-then-write without atomic lock: `findOne()` followed by `create()` or `update()` — two concurrent requests can both see "not found" and both create, producing duplicates
- Check-then-act: `if (stock > 0) { decrement() }` without a database lock — oversell risk
- Double-submit: no idempotency key, so retried requests create duplicate records

**Transaction boundary failures:**
- Transaction wraps only part of an atomic operation — some operations outside the transaction can partially succeed while the transaction rolls back
- Sub-operations inside a transaction not passed the transaction object (ORM pattern: `{ transaction }` missing from nested calls)
- Outer catch logs the error but doesn't re-throw — caller thinks the operation succeeded when it partially failed

**Fire-and-forget side effects:**
- `sendEmail()`, `publishEvent()`, `deleteFile()` called without `await` and without `.catch()` — failure is silent
- Background job scheduled but result never checked — errors disappear

---

## Guard Clauses and Early Returns

**Disabled UI ≠ handler unreachable:**
- A UI element with `disabled={condition}` does NOT guarantee the handler can't be triggered — keyboard events, programmatic `.click()`, direct API calls, or tests can bypass the disabled state
- Check: does the handler itself have a guard clause that mirrors the disable condition?

**"Always true" invariant claims:**
- Comment says "X is always Y here" — trace every call site to verify the invariant holds for ALL callers, including edge cases and direct test calls
- If the comment was written to justify a guard, the guard may exist precisely because the invariant CAN fail

**Guard order:**
- Guard against `null` before accessing `.property` — flipped order causes NPE in the guard itself
- Validation before side effects — if the validation runs after a DB write, partial state exists on validation failure

---

## Database / ORM Patterns

**Integrity risks:**
- `findOne` + `create` without transaction → duplicate rows under concurrent load
- Stock or balance decrement without row-level lock (`SELECT FOR UPDATE`) → oversell or balance going negative
- Soft-delete queries that include deleted records in related `include`/`join` by omitting `WHERE deleted_at IS NULL`
- Cascade operations that swallow sub-operation failures in a catch block

**Transaction scope:**
- Does the transaction wrap ALL operations that must be atomic?
- Are all ORM calls inside the transaction passed the transaction reference?
- If the outer catch logs and swallows without re-throwing: a failed transaction looks like success

---

## Business Rule Enforcement

**Rule enforced in one path but missing in another:**
- Same operation reachable via multiple endpoints — is the rule checked on ALL of them?
- Service-layer validation that can be bypassed by calling the repository directly (test code, other services, internal tools)
- Validation only in the controller/handler — internal service-to-service calls skip it

**Aggregate check misses per-item check:**
- `totalStock > 0` does not mean the specific requested variant has stock
- `totalPrice > minOrder` does not mean each individual item meets its own rules
- `allVariantsActive` (via `.some()`) vs "the specific requested variant is active" (via `.find()`)

**Asymmetric enforcement:**
- Create validates a field; update does not — invalid state can be introduced via update
- Rule applied going in (write) but not going out (read) — corrupt data can be read back silently

---

## Caching Patterns

- Cache key constructed from insufficient discriminators — two different inputs hash to the same key
- Mutation that doesn't invalidate or update the cache — stale data served after a write
- Cache populated with the result of a partially-failed operation — error state cached as success
- TTL inconsistency — one caller refreshes every 5 minutes, another caches for 1 hour, producing inconsistent views

---

## Dead Code

**Before marking something as dead, verify:**
- Grep the entire codebase (not just this module) for all callers
- Check for dynamic access: `obj[methodName]()`, dynamic import/require (`require(dynamicPath)`, `import(path)`), reflection/eval
- Check if it's part of a public API used by external consumers
- Check if it's exported but the export itself is unused

**Dead code patterns:**
- Function defined but never called from any production path
- Exported symbol that nothing imports
- Constant defined but only referenced in a stale comment
- Error message in a language no user will see (hardcoded string in the wrong locale for this deployment)
- DTO/model field populated on every write but never read by any consumer

---

## Encoding and Data Integrity

- String encoding mismatch: UTF-8 vs Latin-1, URL-encoded vs raw, Base64-padded vs unpadded
- Numeric serialization: floating-point stored as string and then compared as number without parsing
- Date/time stored without timezone, then interpreted with different timezone on read
- Hash or signature computed over different byte representations on write vs verify

---

## Initialization and Configuration

- Module-level global mutated at runtime — concurrent requests corrupt shared state
- Constructor side effect that throws in test environments but not in production (or vice versa)
- Default configuration value that is unsafe for production (debug mode, open CORS, no auth)
- Required configuration value that has a silently wrong default instead of failing loudly when missing

---

## Response Format vs Consumer Alignment

When an endpoint returns data consumed by a known caller (FE, mobile, another service), verify the response fields are semantically correct for that caller:

- **Ambiguous field names**: `stockQuantity`, `total`, `price`, `count` — does the field represent the entity the caller thinks it does? (e.g., product-level total stock vs variant-level stock)
- **Unit mismatch**: returning variant stock when product total stock was written to DB; returning cents when caller expects dollars (or the project's base currency unit)
- **Stale vs fresh value**: returning the pre-update value from the in-memory instance instead of the post-update value from DB
- **Multiple representations of the same concept** in one response (e.g., `qty` and `total` both valid but representing different things with the same field name across code paths)

**How to check:** Grep the consumer codebase (frontend, mobile app, or downstream service) for the endpoint path and look at how `data.<field>` is used after the response. If the consumer refetches unconditionally after every mutation, the response value may be unused — still worth fixing for API correctness and third-party consumers.

**Common pattern that hides this:** Caller calls `refetch()` after every mutation → response body never read → mismatch goes undetected for months.
