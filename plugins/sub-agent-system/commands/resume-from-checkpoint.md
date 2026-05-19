---
name: resume-from-checkpoint
description: Reads checkpoint files after a session interruption to determine which phase to resume from and what context to inject.
---

Read the saved checkpoint state and prepare to resume the workflow.

**Steps:**

1. Glob `.claude/checkpoints/*.md` to list all checkpoint files
2. Read the most recent checkpoint file (sorted by timestamp in the filename)
3. Report:
   - Which phase completed (from the checkpoint)
   - Which phase needs to continue next
   - Key context to inject into the next agent (files modified, key decisions, prerequisites)
4. Read `.claude/alerts/*.md` if any alert files exist — report any unresolved anomalies from the pipeline-monitor
5. Ask for user confirmation before re-spawning any agents

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
