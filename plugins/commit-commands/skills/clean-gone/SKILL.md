---
name: clean-gone
description: "Cleans up all local git branches marked as [gone] (deleted on remote but still exist locally), including removing associated worktrees."
---

## Your Task

You need to execute the following bash commands to clean up stale local branches that have been deleted from the remote repository.

## Commands to Execute

1. **First, list branches to identify those with [gone] status**
   Execute the following command:
   ```bash
   git branch -v
   ```

   Note: Branches prefixed with '+' have an associated worktree and must have that worktree removed before the branch can be deleted.

2. **Next, identify worktrees to remove for [gone] branches**
   Execute the following command:
   ```bash
   git worktree list
   ```

3. **Finally, remove worktrees and delete [gone] branches (handles both regular branches and branches with worktrees)**
   Execute the following command:
   ```bash
   # Process all [gone] branches, stripping the '+' prefix if present
   git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
     echo "Processing branch: $branch"
     # Find and remove worktree if one exists
     worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
     if [ ! -z "$worktree" ] && [ "$worktree" != "$(git rev-parse --show-toplevel)" ]; then
       echo "  Removing worktree: $worktree"
       git worktree remove --force "$worktree"
     fi
     # Delete the branch
     echo "  Deleting branch: $branch"
     git branch -D "$branch"
   done
   ```

## Expected Behavior

After executing these commands, you will:

- See a list of all local branches with their statuses
- Identify and remove worktrees associated with [gone] branches
- Delete all branches marked as [gone]
- Provide feedback on which worktrees and branches were removed

If no branches are marked as [gone], report that no cleanup is needed.
