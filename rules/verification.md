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
  - `CLAUDE_CODE_FORK_SUBAGENT=1` (env var, experimental — requires Claude Code v2.1.117+) → inherits full history + system prompt + tools.
  - `context: fork` (skill frontmatter) → runs in isolation, **does NOT inherit history**; skill content becomes the prompt; CLAUDE.md still loads (except Explore/Plan) *(confirmed — Claude Code skills docs)*.

**Background subagents auto-deny** any tool call that would otherwise prompt.

- A needed clarifying-question call fails, but the subagent continues.
- Unexpected results (few findings, empty output) → suspect silently denied tools. Retry in the foreground for full permission prompts.

**Separate FINDING from VERIFICATION** (audit/review).

- A finder's job is **coverage**: report every candidate, including uncertain and low-severity ones, each tagged with a confidence level.
- A fresh **verifier** (finding-validator / pipeline-reviewer) filters false positives afterward.
- Do NOT tell finders to "be conservative" or "only report high-severity" — newer models follow that literally, dropping recall *(Anthropic — prompt best-practices, §Code review harnesses)*.

**Consolidating multiple subagents' output.**

- **Count findings per subagent yourself** first (don't trust their self-count); record the expected total.
- Consolidated report has fewer → list which findings were dropped and why. Never drop silently.
- Same finding, different severities → use the **higher** severity.
- Finding partially valid → keep the valid part, note the incorrect part.

**Other subagent rules.**

- Audit spec changes mid-run → **re-dispatch** with the new spec; don't re-evaluate old findings from memory (produced under the old spec).
- Subagents **miss content** when files are long or the task is overloaded (e.g. fetch URLs + read files + evaluate + report all at once) → don't trust coverage ratings; "not covered" → **grep-verify** first. Limit each to ≤10 files or ≤3 complex tasks *(heuristic — not in Anthropic's docs)*; split rather than overload.
- **Resume** a subagent instead of re-spawning: ask Claude naturally or call `SendMessage` — both require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. It retains full history + tool calls.
- **Subagents cannot spawn subagents** — nesting is fully blocked. Use Skills or chain subagents from the main conversation.
- **Persistent memory**: `memory: user|project|local` frontmatter → `~/.claude/agent-memory/<name>/`, `.claude/agent-memory/<name>/`, `.claude/agent-memory-local/<name>/`. Separate from main agent memory.

**Startup content ≠ current disk state.** CLAUDE.md, memory, and environment info load at session start and don't auto-refresh when disk changes.

- After `/compact`: project-root CLAUDE.md and auto memory are re-injected ✅; nested CLAUDE.md and path-scoped rules are **not** — lost until a file in that directory is read.
- Affects both subagents and the lead agent. When consolidating or comparing → always Read/Grep from disk, never trust already-loaded content.

## Self-Review Bias

- After a **risk-bearing edit batch** — a shared/logic-bearing file, a behavior change, or a batch large enough to lose track of every change (>5 edits is one signal, not the sole trigger) → dispatch a **fresh subagent** to review instead of self-verifying. Self-fix → self-review = bias *(self-imposed/empirical — not in Anthropic's docs)*.
- The fresh subagent gets **no edit-intent context** — only file paths + "review for correctness". Independent review requires independent context.
- **An artifact YOU produced that another person/agent/session will rely on (handoff / plan / audit / checklist / a "done"/"ready" claim) is HIGH-STAKES BY DEFAULT** — you may NOT silently self-downgrade it; if unsure, it IS high-stakes; to treat it low-stakes, say so explicitly and let the HUMAN decide. Re-reading your own work NEVER proves it complete/correct — it converges to FALSE confidence *(empirical: declared a handoff "complete" 2× in one session; a fresh agent then caught 3 broken references I'd skimmed past)*.
  - **The trigger is "about to be relied on", NOT "I claimed done".** Before anything (you or the human) acts on a high-stakes artifact — even if you never said "done" — it MUST have passed independent validation. A self-check yields a **BLOCKED** state, not a finished one: while "self-checked, NOT independently verified", do NOT end the task, propose dependent steps, or let it be acted on. That phrase is a blocker, not a disclaimer to move past.
  - **Pre-condition (proactive, default):** dispatch the independent validation BEFORE the first done/ready claim — do not wait to be asked, do not rely on the human to catch gaps.
  - **Re-ask backstop:** the FIRST time the human doubts it — ANY phrasing (complete / sure / missing / "ổn chưa" / "check lại" / "đủ chưa"…, judged by INTENT not literal string; a 1-char edit does NOT reset the count; surviving `/compact` does NOT reset it) — self-review is **BANNED as proof**. Dispatch the fresh agent. Record "artifact X awaiting independent pass" in memory/handoff so it survives compaction.
  - **The fresh agent must be genuinely independent:** zero chat history; given NEITHER your conclusions NOR your reference list (feeding it the list recreates your blind spot — broken refs come from refs you never noticed existed). It EXTRACTS every reference from the artifact itself and checks each vs disk (path exists with right name/extension; hash resolves; cited section/number real; command runs).
  - **"Found nothing" counts ONLY with per-reference evidence:** for each reference → path + one verbatim line quoted from disk (or "DOES NOT EXIST"). No quotes = not verified, does not count. (Use coverage-verifier / fact-checker.)
  - **Text alone is NOT binding** — this same principle (as P3) was forgotten this very session. High-stakes artifacts should carry a hard-to-skip block (missing/unticked = NOT done): `INDEPENDENT-VERIFICATION: [ ] dispatched · refs N/N · gaps:___`. Truly binding requires a harness **hook**, not memory.

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
