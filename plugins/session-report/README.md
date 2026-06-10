# session-report

Generates a single-file, explorable HTML report of Claude Code usage — tokens, cache hit-rate, subagents, skills, most expensive prompts, session timeline — from the `~/.claude/projects` transcripts. (Everything is inline except an optional web-font fetch from Google Fonts when opened online; the monospace fallback covers offline viewing.)

## Usage

```
/session-report:session-report          # last 7 days (default)
/session-report:session-report 30d      # custom window (Nd / Nh / ISO date)
/session-report:session-report all      # all-time
```

The report is written to the current working directory as `session-report-<timestamp>.html`. Open it in a browser — sorting, drill-downs, and the day timeline are client-side. Note: the report embeds prompt previews and project/session identifiers (common secret patterns are masked best-effort, the rest is not) — it should not be committed or shared casually.

## Requirements

- **Node.js** on PATH (the bundled `analyze-sessions.mjs` analyzer runs locally; no network access, no external dependencies).
- Commands in the skill are sh-syntax — they run via the Bash tool, not PowerShell.

## Components

- `skills/session-report/analyze-sessions.mjs` — transcript analyzer (`--json`, `--since`, `--dir`, `--cache-break`, and `--top` for text mode only — `--json` caps lists at 100). Invalid or missing flag values exit with an error instead of silently changing the window; common secret patterns in prompt text are masked best-effort; the analyzer escapes `<` in the JSON so embedded transcript text cannot break out of the report's `<script>` data element.
- `skills/session-report/build-report.mjs` — embeds the JSON into the template and writes `session-report-<timestamp>.html` (the data blob never passes through the agent's context).
- `skills/session-report/template.html` — report shell; the skill fills the two `AGENT:` blocks (`anomalies`, rendered under the "findings" heading, and `optimizations`, under "recommendations").

> Canonical workflow definition lives in [SKILL.md](skills/session-report/SKILL.md) — this README is a summary. The plugin `description` in [.claude-plugin/plugin.json](.claude-plugin/plugin.json) is the canonical copy; the entry in the repo's `marketplace.json` mirrors it verbatim.
