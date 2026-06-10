# Session-Report Improvement Proposals

> Written by /audit-plugin:audit-plugin Stage 7. Prepend new entries; never edit historical ones.
> (User-relevant learnings only — operator actions and cost figures live in the project's `.claude/audit-plugin-proposals.md` per the audit-plugin split rule.)

Generated: 2026-06-11 (first full audit — audited input **v1.0.0**, produced **v1.0.1**; 4 fresh-review rounds at hard cap, Stage 6 benchmark skipped — scripts were probe-tested with real fixtures in every round + 4 CLI regression suites instead)

## Audit Result (v1.0.0 → v1.0.1)

Convergence series: **0H+2M Stage 1 → 1H+7M r1 → 1H+3M r2 → 0H+3M r3 → 0H+2M(new) r4 (hard cap)** — ~40 fixes across all 6 content files, plus a new bundled script.

Key changes: **pipeline redesigned** (data JSON written to cwd instead of `/tmp` — the Read tool cannot resolve Git-Bash `/tmp` on Windows; new `build-report.mjs` embeds the blob outside the agent's context; `<ts>`-suffixed data file prevents concurrent-session clobber; cleanup on every abort path); **analyzer hardened** (strict flag validation incl. bare `--since`/`--dir`/prefix-parsed numbers; secret masking — sk-ant-, sk_live_, generic sk-, ghp_/github_pat_, AKIA/ASIA, AIza, xox, JWT, Bearer, BEGIN-blocks; `<` escaped so transcript text can't break the report's `<script>` element; BOM tolerated; `since` + `cache_break_threshold` emitted; big arrays last for skimmable Reads; zero-data stderr warning; skill-count double-count guards); **build-report** uses a function replacement (string replacement let `$&`/`` $` ``/`$'` in transcript text corrupt the embedded JSON — reproduced end-to-end) + idempotent defensive re-escape + seconds-stamped output; **template** renders the cache-break threshold dynamically, day-pill % now uses the report-wide total (was silently computed over the visible 14-day subset), Windows `C--Users-` project names shorten; **docs** (README created, LICENSE copyright filled, `license` field, privacy caution — the report embeds masked-best-effort prompt previews; manual-trigger phrases EN+VI).

## Deferred / open (round-4 LOWs at cap + earlier judgment calls)

- Replayed-history attribution between resumed sessions is enumeration-order-dependent (uuid dedupe prevents double-counting; which sessionId claims the entries may vary).
- Slash-command previews (`/cmd` form) bypass maskSecrets — only a risk if command-message text ever carries inline token arguments.
- Findings block mandates "3–5" with no sparse-data fallback (optimizations block has one); near-empty windows may not yield 3 honest findings.
- `Grep AGENT:` now matches 3 spots (two markers + one explanatory comment); the `/AGENT` closers disambiguate.
- No automated test suite ships with the two non-trivial scripts — every probe-verified behavior is guarded only by comments; consider a small `node --test` file.
- Wall-clock hours sum per-file spans (concurrent sessions double-count); display semantics only.
- `--top` affects text mode only (documented in README).
