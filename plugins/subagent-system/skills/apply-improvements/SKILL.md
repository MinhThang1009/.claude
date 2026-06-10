---
name: apply-improvements
description: "This skill should be used when the user asks to apply improvement proposals ('apply improvements', 'ap dung improvement proposals') from .claude/improvement-proposals.md (written by pipeline-retrospective) to the plugin files."
argument-hint: [project-root]
---

Read `.claude/improvement-proposals.md` from the project at $ARGUMENTS (or current directory if not specified).

For each proposal in the file:

1. **Parse the proposal** — extract Target (plugin file path), Problem, and Proposed change.

2. **Locate the target file** in the plugin directory. The plugin is at the path shown by:
```bash
`echo ${CLAUDE_PLUGIN_ROOT}`
```

3. **Apply only HIGH and MEDIUM priority proposals automatically.** For LOW priority proposals: show them to the user and ask for confirmation before applying.

4. **For each change applied:**
   - Read the target file
   - Make the surgical edit (description update, process step addition, quality standard addition, etc.)
   - Verify the edit with a final read
   - Note what was changed

5. **Do NOT apply proposals that:**
   - Require deleting existing functionality
   - Change the agent body behavior (not just descriptions)
   - Affect more than 3 files at once
   → For these, show the proposal and ask the user to decide.

6. **After all changes**, output:

```
IMPROVEMENTS_APPLIED:
Applied: N proposals
Skipped (LOW priority, awaiting confirmation): M proposals
Skipped (requires manual review): K proposals

Files modified:
- [plugin file]: [what changed]

Re-run the pipeline on the same project to verify improvements took effect.
```

**Safety rule:** Never apply a proposal that modifies the pipeline-retrospective skill itself, the apply-improvements command itself, or the mandatory pipeline shape — these require manual review.
