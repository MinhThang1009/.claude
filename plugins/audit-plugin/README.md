# audit-plugin

Multi-round independent quality audit for Claude Code plugins.

> Summary only — `skills/audit-plugin/SKILL.md` is canonical; if this README and SKILL.md diverge, SKILL.md wins. Versioning: `plugin.json` and the SKILL.md frontmatter move together (plugin.json wins on divergence).

## What it does

Audits a plugin's content (plugin.json, SKILL.md, references, examples, hooks, commands) through multiple independent review rounds: 7-criteria deep review → independent finding validation → user-approved scope → fixes → fresh-reviewer convergence loop (hard cap 4 rounds) → headless benchmark (executable workflow plugins only, user-approved — it costs real money) → learnings recorded into improvement-proposals.md.

The criteria list is self-updating: any defect found outside the 7 criteria (tagged `[OUT-OF-CRITERIA]`) must produce a proposal to extend this plugin's own criteria — a fixed criteria set is a systematic blind spot shared by every future review round.

Core principles: every claim carries a quote + `file:line`; finders maximize coverage and a validator filters false positives afterward; the fixer never self-certifies; the user settles every design decision.

## When to use

- After writing or heavily editing a plugin — before declaring it ready for real use
- When a plugin misbehaves and you need its internal contradictions found
- Periodically for load-bearing plugins (gates, hooks, pipelines) after many small patches

## Usage

```
/audit-plugin plugins/<plugin-name>
```

## What makes this different from a one-shot review

A single read-through (however careful) converges to false confidence — the reviewer has blind spots too. This skill forces: (1) an independent validator filtering the first round's false positives, (2) every fix batch passing a zero-context fresh reviewer, (3) a hard cap against oscillation, and (4) executable plugins proving effectiveness in a real benchmark instead of by reading alone.

## Requirements

- **Task tool** (subagent spawning) — required for the validator and fresh reviewers.
- **finding-validator agent / `/validator` skill** (from the `subagent-system` plugin) — recommended for Stage 2; when absent, the skill falls back to a general-purpose agent using the prompt in references.
- The benchmark (Stage 6) needs the `claude` CLI runnable headless; see the Windows caveats in `skills/audit-plugin/references/benchmark-guide.md`.

## Skills

- **audit-plugin** — full workflow (scope → review → validate → gate → fix → convergence loop → benchmark → record)

## References (inside the skill)

- `references/reviewer-prompts.md` — canonical prompts for the fresh reviewer + validator fallback, plus context-isolation rules
- `references/benchmark-guide.md` — fixture design, 2-stage headless run, Windows caveats, 6-dimension scoring rubric
