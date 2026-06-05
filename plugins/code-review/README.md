# Code Review Plugin

Automated code review for pull requests using multiple specialized agents with independent per-issue validation to filter false positives.

## Overview

The Code Review Plugin automates pull request review by launching multiple agents in parallel to independently audit changes from different perspectives. It validates each flagged issue with an independent subagent to filter out false positives, ensuring only high-quality, actionable feedback is posted.

## Commands

### `/code-review`

Performs automated code review on a pull request using multiple specialized agents.

**What it does:**
1. Checks if review is needed (skips closed, draft, trivial, or already-reviewed PRs)
2. Gathers relevant CLAUDE.md guideline files from the repository
3. Summarizes the pull request changes
4. Launches 4 parallel agents to independently review:
   - **Agents #1 & #2**: Audit for CLAUDE.md compliance
   - **Agent #3**: Scan for obvious bugs in changes
   - **Agent #4**: Scan introduced/changed code for problems (security, incorrect logic)
5. Validates each flagged bug/logic issue with an independent subagent
6. Filters out any issue that fails validation
7. Outputs review (to terminal by default, or as PR comment with `--comment` flag)

**Usage:**
```bash
/code-review [--comment]
```

**Options:**
- `--comment`: Post the review as a comment on the pull request (default: outputs to terminal only)

**Example workflow:**
```bash
# On a PR branch, run locally (outputs to terminal):
/code-review

# Post review as PR comment:
/code-review --comment

# Claude will:
# - Launch 4 review agents in parallel
# - Validate each flagged issue with an independent subagent
# - Output only validated issues (to terminal or PR depending on flag)
# - Skip if no validated issues found
```

**Features:**
- Multiple independent agents for comprehensive review
- Independent per-issue validation reduces false positives
- CLAUDE.md compliance checking with explicit guideline verification
- Bug detection focused on changes (not pre-existing issues)
- Historical context analysis via git blame
- Automatic skipping of closed, draft, or already-reviewed PRs
- Links directly to code with full SHA and line ranges

**Review comment format:**
```markdown
## Code review

Found 3 issues:

1. Missing error handling for OAuth callback (CLAUDE.md says "Always handle OAuth errors")

https://github.com/owner/repo/blob/abc123.../src/auth.ts#L67-L72

2. Memory leak: OAuth state not cleaned up (bug due to missing cleanup in finally block)

https://github.com/owner/repo/blob/abc123.../src/auth.ts#L88-L95

3. Inconsistent naming pattern (src/conventions/CLAUDE.md says "Use camelCase for functions")

https://github.com/owner/repo/blob/abc123.../src/utils.ts#L23-L28
```

**Validation step:**
- Each flagged bug/logic issue is re-checked by an independent subagent before it is reported.
- The validator confirms the issue is real — e.g. that a variable flagged as undefined actually is undefined, or that a cited CLAUDE.md rule is in scope for the file and actually violated.
- Issues that fail validation are dropped. This is a binary keep/drop decision, not a numeric score.

**False positives filtered:**
- Pre-existing issues not introduced in PR
- Code that looks like a bug but isn't
- Pedantic nitpicks
- Issues linters will catch
- General quality issues (unless in CLAUDE.md)
- Issues with lint ignore comments

## Installation

This plugin is included in the Claude Code repository. The command is automatically available when using Claude Code.

## Best Practices

### Using `/code-review`
- Maintain clear CLAUDE.md files for better compliance checking
- Trust the validation step - false positives are filtered
- Run on all non-trivial pull requests
- Review agent findings as a starting point for human review
- Update CLAUDE.md based on recurring review patterns

### When to use
- All pull requests with meaningful changes
- PRs touching critical code paths
- PRs from multiple contributors
- PRs where guideline compliance matters

### When not to use
- Closed or draft PRs (automatically skipped anyway)
- Trivial automated PRs (automatically skipped)
- Urgent hotfixes requiring immediate merge
- PRs already reviewed (automatically skipped)

## Workflow Integration

### Standard PR review workflow:
```bash
# Create PR with changes
# Run local review (outputs to terminal)
/code-review

# Review the automated feedback
# Make any necessary fixes

# Optionally post as PR comment
/code-review --comment

# Merge when ready
```

### As part of CI/CD:
```bash
# Trigger on PR creation or update
# Use --comment flag to post review comments
/code-review --comment
# Skip if review already exists
```

## Requirements

- Git repository with GitHub integration
- GitHub CLI (`gh`) installed and authenticated
- CLAUDE.md files (optional but recommended for guideline checking)

## Troubleshooting

### Review takes too long

**Issue**: Agents are slow on large PRs

**Solution**:
- Normal for large changes - agents run in parallel
- 4 independent agents ensure thoroughness
- Consider splitting large PRs into smaller ones

### Too many false positives

**Issue**: Review flags issues that aren't real

**Solution**:
- Each flagged issue is independently validated (this already filters most false positives)
- Make CLAUDE.md more specific about what matters
- Consider if the flagged issue is actually valid

### No review comment posted

**Issue**: `/code-review` runs but no comment appears

**Solution**:
Check if:
- PR is closed (reviews skipped)
- PR is draft (reviews skipped)
- PR is trivial/automated (reviews skipped)
- PR already has review (reviews skipped)
- No issues passed validation (no comment needed)

### Link formatting broken

**Issue**: Code links don't render correctly in GitHub

**Solution**:
Links must follow this exact format:
```
https://github.com/owner/repo/blob/[full-sha]/path/file.ext#L[start]-L[end]
```
- Must use full SHA (not abbreviated)
- Must use `#L` notation
- Must include line range with at least 1 line of context

### GitHub CLI not working

**Issue**: `gh` commands fail

**Solution**:
- Install GitHub CLI: `brew install gh` (macOS) or see [GitHub CLI installation](https://cli.github.com/)
- Authenticate: `gh auth login`
- Verify repository has GitHub remote

## Tips

- **Write specific CLAUDE.md files**: Clear guidelines = better reviews
- **Include context in PRs**: Helps agents understand intent
- **Trust validation**: Validated issues are usually correct
- **Iterate on guidelines**: Update CLAUDE.md based on patterns
- **Review automatically**: Set up as part of PR workflow
- **Trust the filtering**: Validation prevents noise

## Configuration

### Adjusting review strictness

The command (`commands/code-review.md`) filters issues by **binary validation**: step 4 flags issues against concrete criteria, step 5 validates each flagged bug/logic issue with an independent subagent, and step 6 drops any that fail validation. To make review stricter or looser, edit the flagging criteria in step 4 and the validation criteria in step 5 of the command file.

### Customizing review focus

Edit `commands/code-review.md` to add or modify agent tasks:
- Add security-focused agents
- Add performance analysis agents
- Add accessibility checking agents
- Add documentation quality checks

## Technical Details

### Agent architecture
- **2x CLAUDE.md compliance agents**: Redundancy for guideline checks
- **1x bug detector**: Focused on obvious bugs in changes only
- **1x security/logic detector**: Problems in introduced code (security, incorrect logic)
- **Nx validators**: One per flagged bug/logic issue for independent validation

### Validation system
- Each flagged bug/logic issue is independently validated by a subagent
- Validation checks evidence strength — does the issue actually hold in the code?
- Issues that fail validation are filtered out (binary keep/drop, no numeric score)
- For CLAUDE.md issues: verifies the guideline is in scope for the file and actually violated

### GitHub integration
Uses `gh` CLI for:
- Viewing PR details and diffs
- Fetching repository data
- Posting review comments

## Author

Boris Cherny (boris@anthropic.com)

## Version

1.0.0
