---
name: session-report
description: 'This skill should be used when the user asks for a "session report", "usage report", "token usage stats", "báo cáo phiên", "thống kê token", or "xem báo cáo usage Claude Code". Generates an explorable HTML report of Claude Code session usage (tokens, cache, subagents, skills, expensive prompts) from ~/.claude/projects transcripts.'
allowed-tools: Read Grep Edit Bash(node:*)
---

# Session Report

Produce a single-file HTML report of Claude Code usage and save it to the current working directory.

## Steps

> Run every command below via the **Bash tool** (sh syntax), and keep the quotes around `<skill-dir>` (it may contain spaces). `<skill-dir>` = the directory containing this SKILL.md, as an absolute path. `<ts>` = one short timestamp (e.g. HHMMSS) you pick once at the start and reuse verbatim wherever `<ts>` appears — it keeps concurrent sessions in the same cwd from clobbering each other's data file.
>
> **On ANY stop/abort after step 1** (analyzer error, zero data, build error), still delete `./session-report-data-<ts>.json` (step 5's command) before stopping — never leave the data file in the user's cwd. If `node` itself is unavailable (step 1 failed with command-not-found), tell the user to delete the leftover file manually instead.

1. **Get data.** Run the bundled analyzer (default window: last 7 days; honor a different range if the user passed one, e.g. `24h`, `30d`, or `all`). Write the JSON into the **current working directory** — not `/tmp`, which the Read tool cannot resolve on Windows:
   ```sh
   node "<skill-dir>/analyze-sessions.mjs" --json --since 7d > ./session-report-data-<ts>.json
   ```
   For all-time, omit `--since`. **Check the exit code**: non-zero → STOP and show the user the error; never reuse a stale data file from a previous run.

2. **Read** `./session-report-data-<ts>.json`. Skim `overall`, `by_project`, `by_subagent_type`, `by_skill`, `cache_breaks`, `top_prompts`. **Zero-data branch:** if `overall.api_calls` is 0 (empty window, wrong `--dir`, no transcripts), tell the user there is nothing to report for that window and STOP — do not build a report or fabricate findings.

3. **Build the report** — one command copies the template and embeds the JSON (the blob never passes through your context):
   ```sh
   node "<skill-dir>/build-report.mjs" ./session-report-data-<ts>.json
   ```
   It prints the written report path (`./session-report-<timestamp>.html`). Non-zero exit → STOP and show the error.

4. **Fill the two AGENT blocks.** First locate them (`Grep` for `AGENT:` in the report file), Read those regions of the report file, then Edit (use Edit, not Write — preserve the template's JS/CSS):
   - **Replace the placeholder row** inside `<!-- AGENT: anomalies -->` ("No findings generated yet.") with **3–5 one-line findings**. Express figures as a **% of total tokens** wherever possible (total = `overall.input_tokens.total + overall.output_tokens`). One line per finding, exact markup:
     ```html
     <div class="take bad"><div class="fig">41.2%</div><div class="txt"><b>cc-monitor</b> consumed 41.2% of the week across just 3 sessions</div></div>
     ```
     Classes: `.take bad` for waste/anomalies (red), `.take good` for healthy signals (green), `.take info` for neutral facts (blue). The `.fig` is one short number (a %, a count, or a multiplier like `12×`). The `.txt` is one plain-English sentence naming the project/skill/prompt; wrap the subject in `<b>`. Look for: a project or skill eating a disproportionate share, cache-hit <85%, a single prompt >2% of total, subagent types averaging >1M tokens/call, cache breaks clustering.
   - **Replace the placeholder callout** inside `<!-- AGENT: optimizations -->` (at the **bottom** of the page, "No suggestions generated yet.") with 0–4 `<div class="callout">` suggestions tied to specific rows (e.g. "`/weekly-status` spawned 7 subagents for 8.1% of total — scope it to fewer parallel agents"). On a healthy week with nothing actionable, replace it with a single `<div class="callout">No action needed — usage looks healthy.</div>` instead of fabricating a suggestion.
   - Do not restructure existing sections.

5. **Clean up** the temp data file:
   ```sh
   node -e "require('fs').unlinkSync('./session-report-data-<ts>.json')"
   ```

6. **Report** the saved file path to the user. Do not open it or render it. Remind the user that the report embeds prompt previews and project/session identifiers (common secret patterns are masked best-effort, the rest is not) — it should not be committed or shared casually.

## Notes

- The template is the source of interactivity (sorting, expand/collapse, block-char bars). Your job is data + narrative, not markup.
- Keep commentary terse and specific — reference actual project names, numbers, timestamps from the JSON.
- `top_prompts` already includes subagent tokens and rolls task-notification continuations into the originating prompt.
- The analyzer caps `top_prompts` and `cache_breaks` at 100 entries each, and escapes `<` in the JSON so embedded transcript text cannot break out of the report's `<script>` data element.
