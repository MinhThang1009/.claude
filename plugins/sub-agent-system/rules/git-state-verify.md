# Git State Verify

After a sub-agent reports edits, verify those edits actually exist in the working tree. Prevents state hallucination (4.2b).

**Do:**
- Run `git diff [file]` for every file a sub-agent claims to have edited before accepting the result
- Verify the diff content matches the claimed change intent, not just that a diff exists
- Re-dispatch the edit task when a diff is empty

**Don't:**
- Trust a sub-agent's report that it edited a file without running `git diff`
- Continue the pipeline when a claimed edit produces an empty diff

An empty diff after a claimed edit means the edit did not occur. This is state hallucination — treat it as a task failure and re-dispatch.
