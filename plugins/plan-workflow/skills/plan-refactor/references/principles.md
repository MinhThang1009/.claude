# Core Principles (P1–P8)

These 8 principles govern every rule in the plan workflow. When in doubt, return to these.

## P1: The Plan Is a Contract Between Sessions

A plan is not a to-do list. It is a contract that must be complete enough for a fresh agent — with zero context from the planning session — to execute correctly. If the plan requires the reader to remember something not written in it, the plan will fail at /compact, session resume, or handoff.

**Consequence:** Every piece of information the implementer needs must be in the plan document.

## P2: Every Claim Must Be Verified Before It Enters the Plan

Agents report wrong line numbers, miss files, truncate content, and generate false positives. A claim that flows from agent output directly into the plan — without personal verification — is a liability.

**Consequence:** Read the actual file at the actual location before writing any location into the plan. Run the actual search before writing any count. Not the subagent — the lead agent.

## P3: The Agent That Created Something Cannot Reliably Verify It

An agent that wrote a plan has confirmation bias about that plan. An agent that made changes has confirmation bias about those changes. Self-verification consistently misses the errors it introduced.

**Consequence:** Every verification step — before implementation (Phase 5) and after (Phase 7) — uses a fresh agent with no prior context.

## P4: Test Gates Are Non-Negotiable

A passing test baseline is established before the first edit. Every phase gate confirms the baseline is still passing. A failing test stops the work until the root cause is understood and fixed — not until the test is deleted or bypassed.

**Consequence:** No phase proceeds without a passing test gate.

## P5: Implementation Creates Issues That Planning Cannot Predict

A plan is built from a static view of the code. Implementation changes the code. The changed code has properties — newly dead dependencies, newly broken contracts, newly inconsistent parallel paths — that no static analysis could have predicted.

**Consequence:** Post-implementation audit (Phase 7) is always mandatory. A thorough plan does not prevent implementation from creating new issues.

## P6: Scope Freezes Before Implementation Begins

Any finding discovered during audit that is outside the original scope goes into a backlog, not into the current plan. Expanding scope during implementation breaks test gates.

**Consequence:** After Phase 3, scope is frozen. New findings during implementation are noted and deferred.

## P7: Oscillation Signals Missing Ground Truth

When the same design question gets answered differently across multiple audit rounds, the cause is not that the question is hard — agents lack direct access to the facts. More iterations will not resolve this. Reading the actual code will.

**Consequence:** When oscillation is detected, stop generating subagent reports. Read the code. Decide. Write `**FINAL DECISION: [reason]**`. Do not reopen it.

## P8: The Agent Executes; The Human Approves

At critical gates — before scope is frozen, before the plan becomes binding, before findings are accepted — the human must review and explicitly approve. Without these gates, the agent moves forward with unverified assumptions the human never saw.

**Consequence:** Three mandatory human approval gates: after Phase 3 (scope), after Phase 5 (plan), after Phase 7 (findings). The agent stops and waits. The agent does not self-approve.

## Failure Modes Mapped to Principles

| Failure | Principle violated | Fix |
|---------|-------------------|-----|
| Tests fail mid-phase | P2 (missed a file) | Search entire codebase for missed location |
| Phase 5 finds blockers | P2 (unverified claims) | Return to Phase 4; read the file; fix claim |
| New issues in Phase 7 | P5 (emergent effects) | Trace cascade; add to audit checklist |
| Stale references after Phase 8 | P2 (documentation not in inventory) | Add file; update; re-run Phase 8 |
| Agent oscillates | P7 (missing ground truth) | Read code. FINAL DECISION. Stop. |
| Scope expands mid-plan | P6 (not enforced) | Move to backlog. Freeze scope. |
| Context lost after /compact | P1 (plan not self-contained) | Re-read files listed in plan |
| Self-review misses regressions | P3 (not enforced) | Fresh agent review after >5 edits |
