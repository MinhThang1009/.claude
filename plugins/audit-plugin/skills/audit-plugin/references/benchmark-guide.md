# Benchmark Guide (Stage 6)

Applies only to plugins that are **executable workflows**. Goal: measure real effectiveness (recall, compliance, exception paths) instead of read-and-judge. The process and caveats below were distilled from the real benchmark of the audit-logic plugin (2026-06).

---

## 1. Fixture design

- Create a **dedicated temp dir** (`mktemp -d`), init its own git repo, commit a baseline — never benchmark against a real repo.
- Plant **controlled cases** matching the exact patterns the plugin claims to handle (at least one per severity level). Record the answer key before running.
- If the plugin expects a test framework: write **green** happy-path tests that mask the planted cases — this measures the ability to see through "tests pass".
- Path gotcha: under Git Bash, `/tmp` = `%TEMP%` (`C:\Users\<user>\AppData\Local\Temp`), NOT `C:\tmp`. Write files using real Windows paths.

## 2. Two-stage headless run (respect the human gate)

Before running anything: present the cost figures from §4 to the user — Stage 6 requires explicit approval (SKILL.md).

A plugin with a wait-for-approval gate cannot finish in one command. Run two stages:

```bash
# Stage A — expect the plugin to STOP at the approval gate (the stop itself is a scored item)
# Prompt via stdin — avoids the MSYS mangling of "/<skill> ..." described in the caveats below.
# Multiple --allowedTools rules go comma-separated in ONE argument.
cd <fixture> && printf '%s' "/<skill> <args>" | claude -p --output-format json \
  --allowedTools "Bash(python -m pytest *)" > runA.json

# Extract session_id from runA.json, then:
# Stage B — resume with a real approval (no leading slash → safe as a plain argument)
claude -p --resume <session_id> "Approved: <specific decisions>. Continue the remaining phases." \
  --output-format json > runB.json
```

**Never grant unrestricted deletion (`Bash(rm *)`) to a headless run** — a misbehaving run can delete outside the fixture with no prompt. Prefer omitting the grant and scoring how gracefully the plugin handles the denied deletion (that handling is itself a benchmark item). If deletion must work, scope the pattern to the fixture path and verify your CLI version's pattern support first.

### Windows / headless caveats (paid for in tokens)

- **Do not invoke from Git Bash with a prompt starting with `/`** — MSYS path conversion mangles `"/skill ..."` into `C:/Program Files/Git/skill ...`; the slash command never expands and the skill never loads. **Do not patch it with `MSYS_NO_PATHCONV=1`** — that variable propagates into the session's child hook processes and breaks *their* path conversion instead. Safe options: invoke from PowerShell/CMD, or pipe the prompt via stdin.
- Headless cannot create files under the fixture's `.claude/` (permission auto-deny) → any hook-armed gate mechanism in the plugin will not arm; score that part with a separate smoke test: pre-place the state/resource, open a fresh headless session, and observe whether the hook fires.
- Tools outside the allowlist are auto-denied — anticipate what the plugin needs (`rm`, non-allowlisted test runners, …) and pass them via `--allowedTools`.
- A skill-invoke result that is a stub `"Execute skill: X"` with `is_error: true` means the skill did not load — that run measured the "bare model", MUST be excluded from the benchmark data and rerun.

## 3. Scoring — verify by hand, never trust self-reports

Cross-check the transcript (`~/.claude/projects/<fixture-slug>/<session>.jsonl`) against disk state:

| Dimension | How to verify |
|---|---|
| D1 Coverage | Did the transcript read every file? Do mandatory steps (loading references, printing checklists) leave traces? |
| D2 Finding quality | Against the answer key: recall per severity, false positives, whether dismissal reasons hold |
| D3 Completion | All phases per SKILL.md? Which exception paths fired, and did they follow spec? |
| D4 Gate/pipeline health | Did Stage A truly STOP for approval (clean working tree)? Were any gates faked? |
| D5 Fix quality | Run the tests yourself after the fixes; `git log` follows the audited project's commit conventions (its repo rules/CLAUDE.md — not this repo's); do regression tests prove failure-on-old-code? |
| D6 Skill triggering | Did the full skill content load (grep the transcript for distinctive SKILL.md markers)? |

## 4. Costs & cleanup (read the costs BEFORE running)

- Learnings + proposals → the audited plugin's `improvement-proposals.md` (Stage 7).
- Clean up the fixture: `shutil.rmtree` with an `onexc` handler (Python ≥ 3.12; `onerror` on older versions) that clears read-only flags on `.git` objects on Windows (`os.chmod(path, stat.S_IWRITE)`).
- Leave the benchmark transcripts in `~/.claude/projects/` — `cleanupPeriodDays` cleans them up.
- Reference cost: ~$2–5 per stage depending on fixture size — ~$4–10 total for a clean 2-stage run (observed real-world total ≈ $8.6 including one failed attempt). (Canonical cost figures — SKILL.md points here; this file wins on divergence.)
