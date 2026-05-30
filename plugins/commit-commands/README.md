# commit-commands

Commands for git commit workflows including commit, push, and PR creation. Enforces Conventional Commits with Vietnamese subjects and cleans up stale local branches.

## Installation

```bash
claude plugin install commit-commands@minhthang-plugins
```

## Contents

### Skills

- `/commit` — Create a Conventional Commit after reviewing staged diff; no Claude attribution added
- `/commit-push-pr` — Commit, push branch, and open a pull request in one flow
- `/clean-gone` — Remove all local git branches marked `[gone]` (deleted on remote), including associated worktrees

### Commands

- `/commit` — Create a git commit
- `/commit-push-pr` — Commit, push, and open a PR
- `/clean_gone` — Clean up all `[gone]` local branches
