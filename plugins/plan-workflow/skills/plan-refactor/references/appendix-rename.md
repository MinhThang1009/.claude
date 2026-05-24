# Appendix A: Symbol Renaming / Structural Refactoring

Read this appendix alongside the universal workflow when the plan involves renaming symbols, reordering methods, or restructuring code.

## Key Concept: Occurrence Counts ≠ Line Counts

`grep` counts **lines**. `replaceAll` counts **occurrences**. One line with "OldName" three times = 1 in grep, 3 in replaceAll. Plans that use grep line counts systematically underestimate scope.

Use occurrence counts in all plan estimates:
- `grep -o "OldName" file | wc -l` counts occurrences (not lines)
- Or run a replaceAll dry-run and count the reported replacements

## Additional Pre-Planning

```
□ Occurrence counts confirmed for all symbols (not line counts)
□ Same-name symbols in different scopes identified
  (local variable "x" in file A must not be renamed when function "x" in file B is renamed)
```

## Additional Plan Sections

```markdown
## DO NOT RENAME
| Symbol | File | Reason (same name, different scope) |
```

## Phase 2 Additions

**Agent A additional:** Flag `MISPLACED_FUNCTION` — a module-level function that operates exclusively on a class's data and is only called from within that class. Not dead (it is used), but belongs as a class static method.

**Agent B additional:** Check `SCHEMA_GAP` — all functions returning the same logical type must return the same fields across ALL execution paths (main path, fallback path, error path). These paths diverge silently.

## Phase 4 Risk Order

1. Local variable renames — single file, zero cross-file impact
2. Parameter/variable renames — single file, update JSDoc
3. Function renames within one file — update exports + internal calls
4. Cross-file renames — all files: production, tests, CLAUDE.md
5. Method/function reordering — structural only, zero logic change
6. File moves — update all import paths

## Phase 6 Additions

Before each edit: re-read the file at the target location. Line numbers go stale after prior-phase edits. Grep to find the current location.

**Single-file mass rename:** `replace_all: true` in the Edit tool.

**Multi-file mass rename** (>5 occurrences across >1 file):
```
Python:  original.count('OldName'); content.replace('OldName', 'NewName')
Node.js: (content.match(/OldName/g)||[]).length; content.replaceAll('OldName','NewName')
sed:     sed 's/OldName/NewName/g'; verify with grep -o afterward
```

After replace: verify old name = 0; verify new name = expected occurrence count. Spot-check changed locations for unintended matches in comments, strings, and different-scope variables.

## Phase 7 Additions

**Dead parameter cascade:** For every parameter removed, trace callers upward. A parameter alive at plan time may become dead mid-implementation when Phase 1 removes its downstream consumer.

**Structural misplacement:** Module-level functions called only from within one class → class static methods. These pass all dead-code checks.

## Phase 8 Additions

```bash
grep -r "OldName" [src_dir] --include="*.[source_ext]"   # must be 0
grep -r "OldName" [src_dir] --include="*.md"              # must be 0
```

## Common False Positives

- Test `describe()`/`it()` strings containing old symbol name → behavior description, not a variable
- Same-name local variable in different file → different scope, do not rename
- Symbol in JSDoc comment → not dead code (but update to new name)
