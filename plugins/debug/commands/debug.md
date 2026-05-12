---
description: Debug a bug systematically — reproduce first, write failing test, then fix
argument-hint: "[bug description or error message]"
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

## Your task

Debug the issue: "$ARGUMENTS"

Follow this systematic approach:
1. **Reproduce** the bug first — understand exactly when it occurs
2. **Locate** the root cause by reading relevant code
3. **Write a failing test** that captures the bug
4. **Fix** the code until the test passes
5. **Verify** no regressions introduced
