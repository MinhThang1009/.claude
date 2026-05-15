---
name: full-review
description: "Multi-agent review — adaptively dispatches 1-3 agents (code-review + security-audit + test-analyzer) based on complexity, validates findings, consolidates report. Use for comprehensive review before deploy or merging large PRs."
allowed-tools: Read Grep Glob Bash(git diff:*) Bash(git log:*) Bash(git status:*) WebFetch
argument-hint: "[scope: PR #N | branch | files | all]"
context: fork
---

# Orchestration: Full Review

This skill dispatches 3 subagents in parallel, validates findings, then consolidates — following the Anthropic code-review command pattern.

## Process

### Step 1 — Collect data + Pre-check (hybrid: lead collect → Haiku judge)

**Lead agent** runs first (deterministic, no subagent needed):
1. Determine scope from `$ARGUMENTS` (PR, branch, files, or all)
2. Collect diff stats:
   - Diff scope: `git diff --stat` → count changed lines, number of files
   - All scope: `git ls-files | wc -l` (count tracked files, respects `.gitignore`) + `git ls-files | xargs wc -l` → count codebase LOC. If no git → `find . -type f | wc -l` (adjust excludes per project)
   - PR scope: `gh pr diff <N> --stat` (GitHub). If `gh` CLI is unavailable or using another platform (GitLab, Bitbucket) → ask user to provide diff
3. Collect file list: `git diff --name-only` or `find` → list file names
4. If clean (0 changes for diff scope) → notify user, stop
5. If scope is ambiguous → ask user, do NOT guess

**Dispatch pre-check subagent** (`model: haiku` in the Agent tool call) with collected data (inject diff stats + file list into prompt):
- Subagent receives **actual numbers** (no need to self-count) + file names (sees sensitive areas)
- Check: PR closed/draft? Trivial change (≤5 lines, formatting/typo only)? → "skip"
- **Choose scale tier** based on actual data (see Step 2)

If Haiku returns "skip" → **stop immediately**, do not dispatch Step 2.

### Step 2 — Dispatch agents (adaptive scaling)

**Scale number of agents by complexity** (following [Anthropic multi-agent research pattern](https://www.anthropic.com/engineering/multi-agent-research-system): "Simple fact-finding requires just 1 agent... complex research might use more than 10 subagents"):

Haiku chooses scale based on **actual injected data** from Step 1. Guidelines (qualitative labels + quantitative bounds, criteria designed for code review):

| Tier | Label | Bounds (guidelines, not hard cutoffs) | Agents |
|------|-------|---------------------------------------|--------|
| 1 | **Simple** | ~1-20 lines, 1-2 files, no auth/payment/crypto touched | **1** (code-reviewer only) |
| 2 | **Moderate** | ~20-200 lines, 3-10 files, or security concern present | **2** (code-reviewer + security-auditor) |
| 3 | **Complex** | >200 lines, >10 files, sensitive areas, or architectural change | **3** (full) |

Haiku uses the table above as a **guideline** and may adjust if context suggests different complexity than the bounds indicate (e.g., 15 lines but touches auth → Moderate, not Simple).

"all" scope only defines the review boundary — it does NOT override scaling. Haiku judges based on **actual data** (LOC, file count, file names), not scope label.

Launch subagents per the chosen scale:

**Agent 1: code-reviewer** (model + tools per agent definition)
- Prompt: "Review code changes in [scope]. Find bugs, logic errors, performance issues, maintainability problems. Rate each issue confidence 0-100. Only report confidence ≥ 80."

**Agent 2: security-auditor** (model + tools per agent definition)
- Prompt: "Security audit code changes in [scope]. Find injection, auth flaws, secrets, insecure crypto, SSRF, XSS. Report by CVSS severity."

**Agent 3: test-analyzer** (model + tools per agent definition)
- Prompt: "Analyze test coverage for code changes in [scope]. Check: are new logic paths tested? Are edge cases covered? Are any tests broken? Run the test suite if available."

### Step 3 — Consolidate (adaptive to number of agents)

**If only 1 agent** (Simple tier): skip dedup + validate — output that agent's findings directly. No need to consolidate a single source.

**If 2+ agents**:
1. **Count findings per agent** (count manually, do not trust self-counts).
2. **Deduplicate**: if 2+ agents report the same issue → keep 1, take the higher severity, note "confirmed by N agents".
3. **Do NOT silently drop findings** — every finding must appear in the report or have an explicit reason for exclusion.

### Step 4 — Validate findings (adaptive)

**If 0 Critical/High findings**: skip validation — nothing to validate.

**If Critical/High findings exist**:
- Launch **1 fresh subagent** (receives no context about intent) to verify each finding.
- Subagent only receives: file path + line number + issue description + instruction "verify whether this issue is real".
- Unvalidated findings → mark "unverified", keep in report but note clearly.

### Step 5 — Output (scaled by complexity)

**Simple** (1 agent, few findings): brief output — list findings + 1-2 sentence summary. No complex headers needed.

**Moderate/Complex** (2-3 agents): full output:

```markdown
# Full Review Report

**Scope**: [scope description]
**Agents**: [agents dispatched] (N findings per agent)
**Raw total**: X findings → Y after dedup → Z validated

## 🔴 Critical / High (validated)
[findings]

## 🟡 Medium
[findings]

## 🟢 Low / Info
[findings]

## ⚠️ Unverified (needs user confirmation)
[unvalidated findings — omit section if none]

## ✅ Strengths
[things done correctly]

## Test Coverage
[analysis from test-analyzer — omit section if test-analyzer was not dispatched]
```

### Step 6 — Ask user

After the report, ask:
- "Fix Critical/High now?" → if yes, form a plan and fix
- "Commit as-is?" → if yes, call `/commit`
- "Need further review?" → dispatch more agents if needed

## Do NOT

- Do NOT self-fix without asking the user
- Do NOT drop findings as "false positive" without validating
- Do NOT merge Critical/High with Low — keep them separate
- Do NOT run if scope is unclear
