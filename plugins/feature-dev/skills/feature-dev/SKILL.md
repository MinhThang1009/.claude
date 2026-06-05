---
name: feature-dev
description: "Guided feature development — explore codebase → clarify requirements → design architecture → implement → review. Use when implementing new features affecting multiple modules."
allowed-tools: Read Grep Glob Bash Edit Write WebFetch WebSearch
argument-hint: [feature description to implement]
---

# Feature Development — Multi-phase Orchestration

A systematic feature development process: understand → explore → ask → design → implement → review → wrap up.

## Core Principles

- **Ask specific questions** — identify all ambiguities, edge cases, unspecified behaviors. Wait for user's answer before implementing. Ask early — after understanding the codebase, before designing the architecture.
- **Understand before writing** — read existing code, conventions, and patterns before creating new code.
- **Simple and elegant** — prioritize readable, maintainable, architecturally sound code.
- **Read files from agents** — when launching agents, ask them to return a list of the most important files. After agents finish → read all listed files to build deep context.
- **Use TodoWrite** — track progress throughout all phases.

## Phase 1: Discovery

**Goal**: Understand the feature to build.

1. Create a todo list with all phases.
2. Feature request: `$ARGUMENTS`
3. If unclear, ask user:
   - What problem does it solve?
   - What specifically should the feature do?
   - Any constraints or requirements?
4. Summarize understanding, confirm with user before continuing.

## Phase 2: Codebase Exploration

**Goal**: Understand existing code relevant to the feature.

**Skip if**: user says they already know the codebase ("I know already", "skip explore") — jump directly to Phase 3.

Each agent must trace through the code comprehensively, focusing on understanding abstractions, architecture, and flow of control; each focused on a different aspect of the codebase.

Launch **2-3 code-explorer agents in parallel**, each with a different focus:
- Agent 1: "Find features similar to [feature] and trace implementation"
- Agent 2: "Map architecture and abstractions for [relevant area]"
- Agent 3: "Analyze current implementation of [existing feature/area], trace through code comprehensively"
- Agent 4 (optional): "Analyze UI patterns / testing approaches / extension points related to [feature]"

Each agent returns a **list of 5-10 key files**. After agents finish → read all listed files to build deep context.

Present a comprehensive summary of findings and patterns discovered to the user.

## Phase 3: Clarifying Questions

**CRITICAL**: This is one of the most important phases. MUST NOT BE SKIPPED.

**Goal**: Eliminate all ambiguity before designing.

1. Review findings from Phase 2 + feature request
2. Identify unclear aspects: edge cases, error handling, integration points, scope boundaries, **design preferences**, backward compatibility, performance needs
3. **Present ALL questions to the user** — organized and clear
4. **WAIT for user's answers** before moving to Phase 4

If user says "up to you" → give a specific recommendation, ask for explicit confirmation.

## Phase 4: Architecture Design

**Goal**: Design approaches with trade-offs.

**Small feature** (1-2 files, clear pattern from codebase): 1 approach is enough, no need to dispatch architect agents — lead proposes directly.
**Medium/large feature**: Launch **2-3 code-architect agents in parallel** with different focuses:
- Agent 1: "Minimal changes — fewest changes possible, maximum reuse"
- Agent 2: "Clean architecture — maintainability, elegant abstractions"
- Agent 3: "Pragmatic balance — speed + quality"

Review all approaches and form a view on which is best suited for this specific task (consider: small fix vs large feature, urgency, complexity, team context). Present to user:
- Summary of each approach
- Trade-offs comparison
- Specific implementation differences
- **Clear recommendation of which approach** + rationale
- **Ask user to choose**

## Phase 5: Implementation

**DO NOT start without user approval.**

1. Wait for explicit user approval of the approach
2. Re-read relevant files from Phase 2
3. Implement per the chosen architecture
4. Follow codebase conventions strictly (read CLAUDE.md)
5. Write clean, well-documented code (comment WHY in Vietnamese if needed)
6. Update todo list as work progresses

## Phase 6: Quality Review

**Goal**: Verify code quality before declaring done.

**Small feature** (≤3 files changed): 1 code-reviewer agent is sufficient.
**Medium/large feature**: Launch **3 code-reviewer agents in parallel**:
- Agent 1: **simplicity, DRY, elegant abstractions** — is the code as simple as it can be?
- Agent 2: **bugs, functional correctness** — is the logic correct? Edge cases?
- Agent 3: **project conventions, naming, consistent patterns** — does it follow codebase conventions?
- Agent 4 (optional, security-auditor): **only if** the feature touches auth, payment, crypto, user input, or new API endpoints.

Each reviewer only reports findings with **confidence ≥80%**.

Consolidate findings (count, dedup, higher severity wins). Present to user:
- Issues found (grouped by severity)
- **Ask user**: fix now, fix later, or proceed as-is?
- Fix per user decision

## Phase 7: Summary

1. Mark all todos as complete
2. Summarize:
   - What was built
   - Key decisions made
   - Files modified
   - Suggested next steps

## Do NOT

- DO NOT skip Phase 3 (Clarifying Questions) — this is the most important phase
- DO NOT implement before user approves the architecture
- DO NOT dispatch >3 agents at once (cost + quality)
- DO NOT assume codebase conventions — read CLAUDE.md + scan existing code
