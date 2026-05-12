---
name: code-review
description: "Reviews code changes in the working tree, current branch, or PR. Finds bugs, security issues, performance problems, style violations, and test coverage gaps."
allowed-tools: Read Grep Glob Bash(git diff:*) Bash(git log:*) Bash(git status:*) Bash(gh pr view:*) Bash(gh pr diff:*)
context: fork
agent: code-reviewer
argument-hint: "[optional: branch name or PR number]"
---

# Skill: Code Review

You are called to review code thoroughly but with prioritization.

## Auto-injected context

```!
git diff HEAD 2>/dev/null || echo "No git diff available"
```

## Step 1: Determine scope

Depending on `$ARGUMENTS`:

- **No argument**: review the diff injected above (unstaged + staged changes)
- **Number (123)**: review PR #123 (`gh pr diff 123` — requires GitHub CLI; if `gh` is not available → ask user to provide diff)
- **Path (`src/foo.ts`)**: review the contents of that file
- **`branch <name>`**: review changes of the branch against the default branch (auto-detect: `git symbolic-ref refs/remotes/origin/HEAD` → fallback `main` → `master`)

Display the selected scope to the user before continuing.

## Step 2: Read context

- Read related files in the diff to fully understand context (not just the hunk).
- Read corresponding test files (if any).
- Check commit message and PR description (if any) to understand intent.
- **Git history**: `git blame` for changed lines — understand who wrote it, when, which commit. If `gh` is available → check old PR comments/reviews on that file (`gh pr list --search "file:path" --state merged --limit 3`).
- **CLAUDE.md + REVIEW.md**: read if they exist — use as baseline for compliance check in Step 3.

## Step 3: Review from 6 perspectives

In priority order:

### 1. Correctness (Critical)
- Does the logic match the intent? Are there any missed edge cases?
- Off-by-one, null/undefined, race condition, incorrect type coercion?
- Does error handling swallow errors?

### 2. Security (Critical)
- Are there hardcoded secrets/tokens?
- Is there injection (SQL, command, XSS, SSRF, path traversal)?
- Is input validated at the boundary?
- Auth/authz check on new endpoints?

### 3. Tests (High)
- Does new code have tests? Do tests actually verify behavior?
- Are edge cases sufficiently covered (boundary, null, empty, error path)?
- Do any behavior changes make existing tests semantically incorrect?

### 4. Performance (Medium)
- N+1 query?
- Unnecessary nested loops?
- Cache miss for something worth caching?
- Bundle size impact (frontend)?

### 5. Maintainability (Medium)
- Is naming clear?
- Is the function too long? (Reference: [`coding-standards.md` line 11](../../../../rules/coding-standards.md) — <50 ideal, >100 suggest splitting)
- Are there duplicate code segments elsewhere in the codebase (suggestion: use Grep to find patterns)?
- Do comments explain WHY or just repeat WHAT?
- **Code comments compliance**: read comments in modified files — verify changes do not contradict guidance in existing comments (e.g., a comment says "must be called before X" but the diff removes that call).

### 6. CLAUDE.md / REVIEW.md Compliance (Low)
- If CLAUDE.md or REVIEW.md has specific rules → check whether the diff violates them.
- Only flag when the guideline **explicitly mentions** that issue (do not infer broadly).
- Compliance violations → severity 🟡 (non-blocking), unless the guideline explicitly states it is blocking.

### 7. Style (Low)
- Following codebase convention?
- Correct formatting (project formatter)?
- Lint passing?

## Step 4: Present results

Standard format:

```markdown
## Summary
[1-2 sentences: what this code does, whether it should be merged, scale of changes]

## 🔴 Must fix (blocking)
- **<file>:<line>** — <brief issue>
  → <specific fix suggestion, with code if possible>

## 🟡 Should fix (non-blocking but worth doing)
- ...

## 🟢 Suggestions (optional)
- ...

## ✅ Strengths
- [Brief praise — important for balanced feedback]
```

Rules:
- Each finding must have a **specific location** (file:line) and a **fix suggestion**.
- **Confidence scoring**: only report findings with confidence ≥80%. Self-assess using this rubric: 100 = certain bug/vulnerability, 75 = very likely wrong, 50 = possibly wrong but needs more context, 25 = style suggestion only, 0 = uncertain. Findings <80% → drop or move to 🟢 Suggestions.
- Do NOT nitpick style if a formatter is in use — the formatter handles it automatically.
- Do NOT suggest rewrites as "do it differently" if it is merely a preference.
- Do NOT flag pre-existing issues (old code not in the diff) unless the diff makes them a problem.
- Do NOT flag issues that linter/typecheck will catch (CI handles those).
- Do NOT flag intentional behavior changes already explained in the commit message/PR description.
- Do NOT flag code that has a lint-ignore comment (already acknowledged).
- If everything looks fine → clearly state "No blocking issues, ready to merge." Do not fabricate problems.

## Step 5: Follow-up question

After delivering results, ask: "Do you need specific diffs for the 🔴 issues, or is the list sufficient?"

This skill is read-only (frontmatter `allowed-tools` does not include Edit/Write). Diff output is a **text suggestion** in chat — user copies/applies it. To auto-apply, use the `/refactor` skill or a subagent with Edit/Write.

## Gotchas

- **Race conditions, off-by-one, memory leaks**: not obvious from the diff. Read SURROUNDING CONTEXT, not just changed lines.
- **Security holes** (SQLi, XSS, IDOR, SSRF): check input validation + auth checks; do not trust a diff that "looks OK".
- **Test coverage ≠ quality**: tests may test the wrong thing. Read test assertions, not just coverage %.
- **Style nit priority is LOWEST**: flag them but do not block the PR if the logic is correct. Prioritize bug + security fixes first.
