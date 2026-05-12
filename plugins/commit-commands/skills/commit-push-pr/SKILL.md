---
name: commit-push-pr
allowed-tools: Bash(git checkout --branch:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
description: Commit, push, and open a pull request
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`

## Your task

Based on the changes above:

1. Create a new branch if currently on main
2. Create a single commit with an appropriate message
3. Push the branch to origin
4. Create a pull request using `gh pr create`
5. You are capable of calling multiple tools in a single response. You MUST complete all of the above steps in a single message. Do not use any other tools or do anything else. Do not send any other text or messages besides these tool calls.
