# Example: Phase 3 Finding Report

This is what a well-structured Phase 3 findings presentation looks like after reading all source files. Use this as a template for how to present findings to the user before Phase 4 begins.

---

## Audit Logic — Findings for `src/modules/cart`

Files read: 6 source files, 4 test files.

---

### 🔴 HIGH — Cart `addItem` checks total stock but not per-variant stock

**File:** `services/cart-service.js`, line 109
**Reproduction:** Product with Blue(stock=0) + Red(stock=5): `totalStock = 5 > 0` → passes check → Blue variant added to cart despite being out of stock.

```js
// Current (wrong):
const totalStock = variants.reduce((s, v) => s + v.stockQuantity, 0);
if (totalStock <= 0) throw new AppError('Out of stock', 400);

// Bug: totalStock=5 but the specific requested variant has stock=0
```

**Minimal fix:** After the total-stock check, add: `if (variantId) { const v = variants.find(v => v.id === variantId); if (!v) throw new AppError('Variant not found', 404); if (v.stockQuantity <= 0) throw ... }` (the `!v` guard matters — without it an unknown variantId silently passes the stock check)

**Test needed:** "addItem with out-of-stock variant throws 400 even when other variants have stock"

---

### 🔴 HIGH — `removeItem` deletes items belonging to other users (missing ownership check)

**File:** `services/cart-service.js`, line 156
**Reproduction:** User A calls `DELETE /cart/items/123` where item 123 belongs to User B. The service calls `CartItem.findByPk(id)` without checking `userId`, then deletes it.

```js
// Current (wrong):
const item = await CartItem.findByPk(itemId);
await item.destroy();

// Should verify: item.userId === currentUserId
```

**Minimal fix:** Add `if (item.userId !== userId) throw new AppError('Not authorized', 403)` after the findByPk.

**Test needed:** "removeItem throws 403 when item belongs to different user"

---

### 🔵 INFO — `CartService.validateCart` never called from `addItem`

**File:** `services/cart-service.js`, line 203
**Observation:** `validateCart()` exists and is tested, but only called explicitly from the checkout flow. `addItem` doesn't validate on add, so expired items can accumulate. No business rule currently documented requiring validation on add.

**Action:** Document this as intentional (validate-on-checkout) or add a call.

---

**3 findings total: 2 HIGH, 1 INFO**

Confirm which to fix? Recommended: fix both HIGH now, defer INFO for documentation.

> Severity note: cross-user data deletion is HIGH per the rubric (security bypass + wrong data in DB), not MEDIUM — even though the per-request symptom looks like "just a missing check".
