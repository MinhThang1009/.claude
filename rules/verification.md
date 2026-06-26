# Verification Rules

> Supplements "Working Style" in CLAUDE.md. Prevents repeating mistakes from prior sessions.

## Subagents

**Verify impactful results before reporting.** Output with impact (security findings, actions the user will run, claims about numbers/versions) → **verify with a direct tool** (Grep, Read, WebFetch).

- **Named** subagents start fresh, don't see parent context → higher risk of wrong output. **Forked** subagents inherit history → lower risk.
- Skip verification only for purely informational tasks with no action consequence.
- "Found nothing" from an audit/security task is NOT trivial — verify anyway.
- Never report findings without confirming them yourself at least once *(self-imposed — not in Anthropic's docs)*.

**Feed context efficiently.**

- Data already in parent context (WebFetch results, prior tool output, conversation) → **paste the relevant subset** into the prompt.
- Data on disk where the subagent has `Read`/`Grep` → let it find the data directly.
- **Make each prompt self-sufficient**: give it an objective, an output format, guidance on tools/sources, and clear scope boundaries; scale agent count to task complexity *(Anthropic — multi-agent research system: "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries"; "Simple fact-finding requires just 1 agent with 3-10 tool calls... complex research might use more than 10 subagents with clearly divided responsibilities")*.

**What a subagent loads.**

- Only its own system prompt (the agent's markdown body), not the full Claude Code system prompt.
- Custom named subagents **DO load** the full memory hierarchy: `~/.claude/CLAUDE.md`, project rules (`.claude/rules/*.md`), `CLAUDE.local.md`, managed policy files.
- Exception: built-in **Explore and Plan** skip CLAUDE.md and git status.
- Two fork mechanisms:
  - `CLAUDE_CODE_FORK_SUBAGENT=1` (env var, experimental, reportedly v2.1.117+) → inherits full history + system prompt + tools. *(Forked subagents are real: official changelog v2.1.178 references them re depth tracking. But this exact env-var name/version/behavior is NOT in the official changelog, only community blogs; treat as unverified. Recorded 2026-06.)*
  - `context: fork` (skill frontmatter) → runs in isolation, **does NOT inherit history**; skill content becomes the prompt; CLAUDE.md still loads (except Explore/Plan) *(confirmed — Claude Code skills docs)*.

**Background subagents (v2.1.186+) surface permission prompts to the main session** instead of auto-denying; the dialog shows which agent is asking, Esc denies just that tool *(confirmed vs official changelog v2.1.186; before that they auto-denied)*.

- A denied or un-approved tool call fails, but the subagent continues.
- Unexpected results (few findings, empty output) → check whether a tool was denied; retry in the foreground if needed.

**Separate FINDING from VERIFICATION** (audit/review).

- A finder's job is **coverage**: report every candidate, including uncertain and low-severity ones, each tagged with a confidence level.
- A fresh **verifier** (finding-validator / pipeline-reviewer) filters false positives afterward.
- Do NOT tell finders to "be conservative" or "only report high-severity"; newer models follow that literally, dropping recall *(citation unverified: a "Code review harnesses" section was not found in official Anthropic prompt docs as of 2026-06; the principle still holds)*.

**Consolidating multiple subagents' output.**

- **Count findings per subagent yourself** first (don't trust their self-count); record the expected total.
- Consolidated report has fewer → list which findings were dropped and why. Never drop silently.
- Same finding, different severities → use the **higher** severity.
- Finding partially valid → keep the valid part, note the incorrect part.

**Other subagent rules.**

- Audit spec changes mid-run → **re-dispatch** with the new spec; don't re-evaluate old findings from memory (produced under the old spec).
- Subagents **miss content** when files are long or the task is overloaded (e.g. fetch URLs + read files + evaluate + report all at once) → don't trust coverage ratings; "not covered" → **grep-verify** first. Limit each to ≤10 files or ≤3 complex tasks *(heuristic — not in Anthropic's docs)*; split rather than overload.
- **Resume** a subagent instead of re-spawning: call `SendMessage` with its agent ID (retains full history + tool calls; a stopped subagent auto-resumes in the background). Resuming does NOT require agent teams. *(Separately, the agent-teams feature, structured team-protocol messaging + spawning teammates via the Agent `name` param, is still experimental behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` per changelog v2.1.178. Corrected 2026-06 vs official docs.)*
- **Subagent nesting is allowed, up to 5 levels deep** (official changelog v2.1.172; forked/resumed subagents count toward the cap, v2.1.178). Older versions blocked it entirely. Still prefer shallow chains from the main conversation for clarity. *(Corrected 2026-06 vs official changelog.)*
- **Persistent memory**: `memory: user|project|local` frontmatter → `~/.claude/agent-memory/<name>/`, `.claude/agent-memory/<name>/`, `.claude/agent-memory-local/<name>/`. Separate from main agent memory.

**Startup content ≠ current disk state.** CLAUDE.md, memory, and environment info load at session start and don't auto-refresh when disk changes.

- After `/compact`: project-root CLAUDE.md and auto memory are re-injected ✅; nested CLAUDE.md and path-scoped rules are **not** — lost until a file in that directory is read *(empirical, unverified vs docs; recorded 2026-06)*.
- Affects both subagents and the lead agent. When consolidating or comparing → always Read/Grep from disk, never trust already-loaded content.

## Self-Review Bias

> Enforced by the `self-review-nudge.sh` Stop hook — this text is the spec, the hook is the backstop. Origin *(self-imposed/empirical — not in Anthropic's docs)*: a handoff was declared "complete" twice in one session; a fresh agent then found 3 broken references. Re-reading your own work converges to FALSE confidence.

- **Risk-bearing edit batch** (shared/logic-bearing file, behavior change, or too large to track — >5 edits is one signal) → dispatch a **fresh subagent** to review. Never self-verify.
- The reviewer gets **no edit-intent context** — only file paths + "review for correctness".
- **Any artifact another person/agent/session will rely on** (handoff / plan / audit / checklist / "done"/"ready" claim) is **high-stakes by default**. Downgrading it to low-stakes is the HUMAN's call — say so explicitly; never silently self-downgrade.
- High-stakes artifact → independent validation **BEFORE the first done/ready claim** and before anyone acts on it (the trigger is "about to be relied on", not "I said done"). Self-check = **BLOCKED**, not done: do not end the task or propose dependent steps.
- The first time the human doubts it (ANY phrasing — "ổn chưa", "check lại", "đủ chưa"… — judged by INTENT; a 1-char edit or surviving `/compact` does NOT reset this) → self-review is **banned as proof**. Dispatch the fresh agent; record "artifact X awaiting independent pass" in memory/handoff so it survives `/compact`.
- The fresh agent must be genuinely independent: zero chat history, given NEITHER your conclusions NOR your reference list. It EXTRACTS every reference from the artifact itself and checks each against disk (path exists with right name/extension; hash resolves; cited section/number real; command runs).
- "Found nothing" counts ONLY with per-reference evidence: path + one verbatim quoted line (or "DOES NOT EXIST"). No quotes = not verified. (Use coverage-verifier / fact-checker.)
- High-stakes artifacts carry a hard-to-skip block (unticked = NOT done): `INDEPENDENT-VERIFICATION: [ ] dispatched · refs N/N · gaps:___`.

## Batch Edits

- Verify the **replacement content** is correct, not just that the old content is gone. For factual claims (versions, thresholds, URLs) → WebFetch the source first.
- A claim in **multiple files** → grep the whole repo after editing; fixing A while B keeps the old value creates a new inconsistency.
- A file may be **edited by another process** (user, hooks, formatters) mid-edit → re-read before concluding the edit landed.
- Before batch-editing (>3 files) → ensure a **clean git state**. Edit fails mid-way → `/rewind` or `git checkout` to revert. Never leave a half-edited codebase.
- Editing **1 file** → use the Edit tool, not a Python `open(file, 'w')` script (truncation risk). Mass operations may script, but MUST preview affected files, back up / `git stash` first, and use a dry-run if available.

## Tool Output Reliability

- **Truncated** output (Read `limit`, Bash timeout, WebFetch summary) → insufficient; expand/retry before concluding. Not seeing a pattern in a partial read ≠ it's absent.
- **WebFetch is unreliable** for: cross-host redirects (not followed — returns a redirect message; needs a second WebFetch), the **15-minute cache** (re-fetch ≠ fresh), large-page truncation. 404/timeout/auth are standard HTTP failures *(practical, not in Anthropic docs)*. Try another URL or note "could not verify".
- WebFetch summaries come from a **small model in a separate context** → may contain errors. Important data (versions, thresholds, advisories) → cross-check a second URL or `Bash(curl)` for raw content.
- **MCP tool** output → treat like subagent output: cross-check impactful results. MCP servers are third-party (not Anthropic-audited), may be stale.

## Git State

> Only when the project has a git repo. No git → use the filesystem directly.

- Before git operations → **verify the current branch** with `git branch --show-current`. Startup git state reflects the most recent SessionStart hook (only if that hook runs git commands) — it fires on new session, `/resume`, `/clear`, `/compact` (source `"startup"`/`"resume"`/`"clear"`/`"compact"`). Stale if git changed since without re-triggering.
- Checking another branch → use `git ls-tree` / `git show branch:path`, **NOT** `ls`/`find` (the working tree only reflects the current branch).

## External Dependencies

- Using a GitHub Action or external package → **verify it exists** (WebFetch the repo/tag) before committing. WebFetch fails → try another URL or note user confirmation is needed.
- Dependency exists but **version mismatch** → warn the user; don't change versions unilaterally.
