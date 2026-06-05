# Example: Independent Verification Agent Exchange (Phase 4, Step 6)

This shows the correct way to run independent verification and interpret its output.

---

## What to Send the Agent

After fixing a bug, spawn a verification agent with **only** this — no context about what was changed:

```
Read these files:
- src/modules/cart/services/cart-service.js
- src/modules/cart/services/cart-service.test.js

For each file, determine:
1. Is the logic correct? Are all business rules properly enforced?
2. Are there race conditions, data integrity risks, or missing validation?
3. Any edge cases not handled?

Do NOT look at git history or commit messages. Read the current code only.
Report findings with specific file and line number references.
```

---

## Example Agent Response (Good — confirms fix, finds a remaining issue)

```
cart-service.js analysis:

Line 109-115: Total stock check and per-variant check both present. Logic correct
for the case where variantId is provided. When variantId is null, only total
stock is checked — this appears intentional (no specific variant requested).

Line 156-162: removeItem checks item.userId === userId before deletion. Authorization
looks correct.

Line 178: updateQuantity does not check variant-level stock when increasing quantity.
If variant stock is 0, a user could still call updateQuantity(1 → 2) without error.
This is a different path from addItem. file:line 178.

Line 203: validateCart not called from addItem — appears intentional by context.
```

---

## How to Interpret the Response

**"Confirms fix works"** → Lines 109-115 and 156-162 are confirmed correct.

**"Finds a remaining issue"** → Line 178 is a NEW finding the verification agent surfaced. This is the point of independent verification — it found something you missed.

**Action:** Investigate line 178. Decide: is `updateQuantity` also supposed to enforce variant stock? If yes, fix it. If no, document why. Either way, don't ignore it.

---

## Red Flag: Agent Only Confirms, Finds Nothing New

If the verification agent says "everything looks correct, the fix is good" with no additional observations — be skeptical. Either the code is genuinely clean, or the agent was biased by guessing what was changed. Check whether you gave it too much context accidentally.
