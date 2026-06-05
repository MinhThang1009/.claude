# Reading Patterns — Systematic Code Analysis

Reference for Phase 2 of the logic-audit skill. Load when reading complex code patterns.

## Async / Concurrency Patterns

**Race conditions to look for:**
- Read-then-write without transaction: `findOne()` followed by `create()` or `update()` — two concurrent requests can both read "not found" and both create, resulting in duplicates.
- Check-then-act: `if (stock > 0) { decrement() }` without atomic lock — oversell risk.
- Fire-and-forget side effects that must complete before the response: verify `.catch()` handlers exist and don't swallow errors silently.

**When reading async code, trace the happy path AND the failure path:**
- What happens if the first `await` succeeds but the second fails?
- Is there cleanup (temp files, partial DB writes) if mid-flow throws?
- Are transaction boundaries correct — does the transaction wrap ALL the operations that must be atomic?

## Guard Clauses and Early Returns

**Pattern to watch:** disabled UI element + guard clause in handler.
- A button with `disabled={condition}` does NOT guarantee the handler can't be called — keyboard events, programmatic calls, or testing can bypass disabled state.
- Verify: does the handler have its own guard that mirrors the disabled condition?

**"Always true" invariant claims:**
- Comment says "X is always Y here" — trace the call chain and verify the invariant holds for ALL callers, not just the happy path.
- If the comment was added to justify a guard: the guard might be needed precisely because the invariant CAN fail.

## Database / ORM Patterns

**Common integrity issues:**
- `findOne` + `create` without transaction → duplicate rows on concurrent requests
- Stock decrement without `SELECT FOR UPDATE` → oversell
- Cascade operations that silently succeed even when sub-operations fail (catch-swallow)
- Soft-delete queries that forget `WHERE deleted_at IS NULL` on related includes

**Verify transaction scope:**
- Does the transaction wrap all operations that must be atomic?
- Are all sub-operations within the transaction passed the `{ transaction }` option?
- Does the outer catch re-throw or just log? (logging without re-throwing = silent data corruption)

## Caching Patterns

**Common bugs:**
- Cache key collision: two different inputs produce the same cache key
- Stale cache served after mutation: invalidation missing or wrong key used
- Cache populated with partial/incorrect data on first miss
- TTL too short (cache miss storms) or too long (stale data served)

## Business Rule Enforcement

**Pattern: rule enforced in one place but not another**
- Same operation available through multiple endpoints/paths — is the rule enforced on ALL paths?
- Rule enforced at the service layer but the repository layer also directly accessible — can the rule be bypassed?
- Validation in controller but not in service — service can be called directly from tests or other services without validation.

**Pattern: aggregate check misses per-item check**
- `totalStock > 0` does not guarantee the specific requested variant/item has stock.
- `totalPrice > discount` does not guarantee each line item individually passes rules.

## Dead Code Identification

**Dead code in production (not tests):**
- Functions defined but never called (grep all callers, not just the module)
- DTO/model fields populated but never read by any consumer
- Constants defined but only referenced in comments
- Error messages hardcoded in a language the user won't see (EN error in a VI-only API)

**Before marking as dead:**
- Grep the entire codebase, not just the current module
- Check if it's referenced by dynamic access (`obj[key]`, `require(path)`)
- Check if it's a public API that external callers might use
