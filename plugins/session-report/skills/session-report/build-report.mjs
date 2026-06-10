#!/usr/bin/env node
/**
 * build-report.mjs
 *
 * Embeds the analyzer's JSON output into template.html and writes a
 * timestamped report file. Keeps the data blob out of the agent's context:
 * the agent only fills the two AGENT blocks afterwards.
 *
 * Usage:
 *   node build-report.mjs <data.json> [out-dir]
 *
 * Prints the written report path on stdout. Exits 1 with a message on any
 * problem (missing/invalid data file, template marker not found).
 */

import fs from 'fs'
import path from 'path'

const dataPath = process.argv[2]
if (!dataPath) {
  console.error('usage: node build-report.mjs <data.json> [out-dir]')
  process.exit(1)
}

let data
try {
  data = fs.readFileSync(dataPath, 'utf8')
} catch {
  console.error(`cannot read data file: ${dataPath} — run analyze-sessions.mjs first`)
  process.exit(1)
}
try {
  JSON.parse(data)
} catch {
  console.error(`${dataPath} is not valid JSON — rerun analyze-sessions.mjs`)
  process.exit(1)
}

const template = fs.readFileSync(new URL('./template.html', import.meta.url), 'utf8')
const MARK = '<script id="report-data" type="application/json">{}</script>'
if (!template.includes(MARK)) {
  console.error('template marker not found — template.html changed?')
  process.exit(1)
}

const d = new Date()
const pad = n => String(n).padStart(2, '0')
// seconds included — minute-only stamps silently clobber same-minute runs
const ts = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`
const out = path.join(process.argv[3] || '.', `session-report-${ts}.html`)

// analyze-sessions.mjs escapes every "<" as the backslash-u003c JSON escape
// sequence; re-apply it here as defense-in-depth (idempotent on an already-
// escaped blob) so a drift in the paired script can never break the element.
const safe = data.replace(/</g, '\\u003c')
// The replacement MUST be a function: with a string replacement, JS would
// interpret $-patterns ($&, $`, $') occurring in transcript text and corrupt
// the embedded JSON.
fs.writeFileSync(
  out,
  template.replace(
    MARK,
    () => `<script id="report-data" type="application/json">${safe}</script>`,
  ),
)
console.log(out)
