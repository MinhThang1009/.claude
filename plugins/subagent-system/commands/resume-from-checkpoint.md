---
description: Resume pipeline from last saved checkpoint.
---

Read the saved checkpoint state and prepare to resume the workflow.

**Steps:**

1. **Resolve PROJECT_ROOT** — read `PIPELINE_CONFIG.md` to get the absolute project path:
   ```bash
   Bash("cat .claude/PIPELINE_CONFIG.md 2>/dev/null | grep '^PROJECT_ROOT:' | cut -d' ' -f2-")
   ```
   If found, use that path as `PROJECT_ROOT`. If not found, fall back to current directory and warn: "PIPELINE_CONFIG.md not found — using session cwd. Checkpoint paths may be wrong if session root differs from project root."

2. Glob `[PROJECT_ROOT]/.claude/checkpoints/*.md` to list all checkpoint files
3. Find and read the most recent checkpoint file:
   ```bash
   Bash("ls [PROJECT_ROOT]/.claude/checkpoints/phase-*.md 2>/dev/null | sort -V | tail -1")
   ```
4. Report:
   - Which phase completed (from the checkpoint)
   - Which phase needs to continue next
   - Key context to inject into the next agent (files modified, key decisions, prerequisites)
5. Read `[PROJECT_ROOT]/.claude/alerts/*.md` if any alert files exist — report any unresolved anomalies from the pipeline-monitor
6. Ask for user confirmation before re-spawning any agents

**Note on session resumption:** `/resume` and `/rewind` do not restore in-process agent teams. This command provides the state information needed to manually re-spawn agents from the last known good checkpoint. Use the checkpoint content to reconstruct the context that would be passed to the next phase agent.

**Output format:**

```
RESUME_STATE:
Last completed phase: Phase [N] — [description]
Checkpoint file: [path]
Checkpoint commit: [git hash if available]

Next phase to run: Phase [N+1] — [description]

Context for next agent:
[Key decisions and state from checkpoint]

Unresolved alerts: [list from .claude/alerts/ or NONE]

Ready to re-spawn Phase [N+1]? Awaiting confirmation.
```
