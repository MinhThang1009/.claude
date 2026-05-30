# Git State Verify

After a subagent reports edits, verify those edits actually exist in the working tree. Prevents state hallucination.

**Do:**
- Run `git diff HEAD -- [file]` for every file a subagent claims to have edited before accepting the result
- Verify the diff content matches the claimed change intent, not just that a diff exists
- Re-dispatch the edit task when a diff is empty

**Don't:**
- Trust a subagent's report that it edited a file without running `git diff HEAD -- [file]`
- Continue the pipeline when a claimed edit produces an empty diff

An empty diff after a claimed edit means the edit did not occur. This is state hallucination — treat it as a task failure and re-dispatch.
