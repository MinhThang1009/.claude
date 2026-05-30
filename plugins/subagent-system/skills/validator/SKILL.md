---
name: validator
description: This skill should be used after a small audit (1–5 findings) to verify whether the cited code locations actually contain the reported issues. Use this skill — not fact-checker — when findings are specific code-location claims that need confirmation. Use fact-checker instead when an agent's narrative claims are suspect. For more than 5 findings, use the finding-validator agent. Also trigger when user asks to "validate findings", "verify these findings", or "filter false positives".
allowed-tools: Read Grep Glob
---

Treat these findings without knowledge of the original audit intent. Isolation from audit context is intentional — it prevents confirmation bias from the original auditor's assumptions.

**Input:** List of findings from worker agents + corresponding file paths.

For each finding:

1. Read the cited file at the cited line range.
2. Check 20 lines of context on both sides of the cited location.
3. Check whether guard clauses or defensive logic elsewhere in the file already handle the reported issue.
4. Assign a verdict:
   - `VERIFIED` — the code at that location matches the finding description
   - `FALSE_POSITIVE` — the code does not support the finding
   - `NEEDS_CONTEXT` — cannot determine without reading additional files

**Begin every response with this STATUS block:**
```
STATUS: COMPLETED | PARTIAL | FAILED
TASKS_PROCESSED: N
TASKS_TOTAL: M
```

> Note: `completion-checker` consumes this STATUS block, not a full COMPLETION_CHECKLIST (validator does not emit one). Only run completion-checker against validator output when validator was assigned an explicit numbered task list; otherwise completion-checker reports `CHECKLIST_NOT_FOUND → SUSPICIOUS` by design.

**Output format:**

```
VALIDATION_REPORT:
Finding: [description]
File: [path], Line: [N]
Evidence read: "[verbatim quote from the file]"
Verdict: VERIFIED | FALSE_POSITIVE | NEEDS_CONTEXT
Reason: [explanation if FALSE_POSITIVE or NEEDS_CONTEXT]
---
Finding: [next finding]
...

SUMMARY:
Total findings: N
Verified: X
False positives: Y
Needs context: Z
```

Be skeptical. Many findings from automated agents are false positives — the absence of a guard clause in one function does not mean the issue is unhandled if the call site prevents it.
