---
name: review-pr
description: "Comprehensive PR review using specialized agents, each focusing on a different aspect of code quality."
argument-hint: [review-aspects]
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
context: fork
---

# Comprehensive PR Review

Runs a comprehensive pull request review using multiple specialized agents, each focusing on a different aspect of code quality.

**Review Aspects (optional):** "$ARGUMENTS"

## Review Workflow

1. **Determine Review Scope**
   - Check git status to identify changed files
   - Parse arguments to see which specific review aspects the user requested
   - Default: Run all applicable reviews

2. **Available Review Aspects:**

   - **comments** - Analyze accuracy and maintainability of code comments
   - **tests** - Review test quality and coverage completeness
   - **errors** - Check error handling for silent failures
   - **types** - Analyze type design and invariants (if new types were added)
   - **code** - General code review against project guidelines
   - **simplify** - Simplify code to improve clarity and maintainability
   - **all** - Run all applicable reviews (default)

3. **Identify Changed Files**
   - Run `git diff --name-only` to see edited files
   - Check if a PR already exists: `gh pr view`
   - Identify file types and which reviews are applicable

4. **Determine Applicable Reviews**

   Based on changes:
   - **Always applicable**: code-reviewer (general quality)
   - **If test files changed**: pr-test-analyzer
   - **If comments/docs were added**: comment-analyzer
   - **If error handling changed**: silent-failure-hunter
   - **If types were added/modified**: type-design-analyzer
   - **After passing review**: code-simplifier (polish and refinement)

5. **Launch Review Agents**

   **Sequential approach** (one at a time):
   - Easier to understand and act on
   - Each report is complete before moving to the next
   - Better for interactive reviews

   **Parallel approach** (user may request):
   - Launch all agents simultaneously
   - Faster for comprehensive reviews
   - Results returned all at once

6. **Consolidate Results**

   After agents finish, summarize:
   - **Critical Issues** (must fix before merging)
   - **Important Issues** (should fix)
   - **Suggestions** (nice to have)
   - **Positive Observations** (strengths)

7. **Provide Action Plan**

   Organize findings:
   ```markdown
   # PR Review Summary

   ## Critical Issues (X found)
   - [agent-name]: Issue description [file:line]

   ## Important Issues (X found)
   - [agent-name]: Issue description [file:line]

   ## Suggestions (X found)
   - [agent-name]: Suggestion [file:line]

   ## Strengths
   - What was done well in this PR

   ## Recommended Action
   1. Fix critical issues first
   2. Address important issues
   3. Consider suggestions
   4. Re-run review after fixes
   ```

## Usage Examples

**Full review (default):**
```
/pr-review-toolkit:review-pr
```

**Specific aspects:**
```
/pr-review-toolkit:review-pr tests errors
# Review only test coverage and error handling

/pr-review-toolkit:review-pr comments
# Review code comments only

/pr-review-toolkit:review-pr simplify
# Simplify code after passing review
```

**Parallel review:**
```
/pr-review-toolkit:review-pr all parallel
# Launch all agents in parallel
```

## Agent Descriptions

**comment-analyzer**:
- Verifies comment accuracy against code
- Identifies comment rot
- Checks documentation completeness

**pr-test-analyzer**:
- Reviews behavioral test coverage
- Identifies critical gaps
- Evaluates test quality

**silent-failure-hunter**:
- Finds silent failures
- Reviews catch blocks
- Checks error logging

**type-design-analyzer**:
- Analyzes type encapsulation
- Reviews invariant representation
- Evaluates type design quality

**code-reviewer**:
- Checks CLAUDE.md compliance
- Detects bugs and issues
- Reviews overall code quality

**code-simplifier**:
- Simplifies complex code
- Improves clarity and readability
- Applies project standards
- Preserves functionality

## Tips

- **Run early**: Before creating a PR, not after
- **Focus on changes**: Agents analyze git diff by default
- **Address critical issues first**: Fix high-priority issues before dealing with lower-priority ones
- **Re-run after fixes**: Verify that issues have been resolved
- **Use targeted reviews**: Focus on specific aspects when you know where the problem is

## Workflow Integration

**Before committing:**
```
1. Write code
2. Run: /pr-review-toolkit:review-pr code errors
3. Fix critical issues
4. Commit
```

**Before creating a PR:**
```
1. Stage all changes
2. Run: /pr-review-toolkit:review-pr all
3. Address all critical and important issues
4. Re-run targeted reviews to verify
5. Create PR
```

**After receiving PR feedback:**
```
1. Make requested changes
2. Run a targeted review based on the feedback
3. Verify issues have been resolved
4. Push updates
```

## Notes

- Agents run automatically and return detailed reports
- Each agent focuses on its specialty for in-depth analysis
- Results are actionable with specific file:line references
- Agents use models appropriate to their complexity
- All agents are listed in `/agents`
