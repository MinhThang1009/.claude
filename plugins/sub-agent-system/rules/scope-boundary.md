# Scope Boundary

Scope equals the explicitly assigned file set. Prevents scope creep (1.2). Note: tool-level enforcement via `disallowedTools` is the hard boundary — this rule is the probabilistic layer.

**Do:**
- Operate only on the files explicitly listed in your task assignment
- If a problem is found outside scope, note it in the report as "Out of scope: [issue] at [file]"
- Partition work by file/directory ownership, not by concern type

**Don't:**
- Read files not in your assigned scope
- Edit files not in your assigned scope
- Infer that "related" files should be included and act on them without instruction
- Propose architectural changes that span beyond the assigned file set

Out-of-scope findings go into the report only. Do not act on them.
