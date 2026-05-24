---
name: coverage-verifier
description: This skill should be used after every audit or analysis agent that was assigned specific files to read — invoke before accepting any audit findings as valid. An agent can describe plausible findings without having read the files; this skill detects that by requiring verbatim quotes from 3 positions (beginning, middle, end) of each sampled file. Also trigger when user asks to "verify agent coverage", "check if agent actually read the files", or "spot-check file reading".
version: 0.1.0
allowed-tools: Read
---

**Input:** Agent's coverage report + list of files the agent was assigned.

**Step 1 — Select samples (proportional to scope size).**
Sample size scales with scope — no absolute cap:
- 1–10 files: sample all (100%)
- 11–20 files: sample 3 files (≥15%)
- 21–50 files: sample 5 files (≥10%)
- 51–100 files: sample 10 files (≥10%)
- 101–200 files: sample 20 files (≥10%)
- 200+ files: do NOT spot-check — escalate. Re-dispatch the agent with an explicit file list
  split into batches of ≤50 files. A 10% sample of 500 files = 50 reads, which is feasible;
  a cap of 8 files = 1.6% coverage, which defeats the purpose of this skill entirely.

Prefer files where: (a) the agent reported no findings ("clean"), (b) the agent made specific line-level claims, (c) the file is large (>200 lines, higher risk of skimming). Do not cluster samples in one directory.

**Step 2 — Read the claimed sections.**
If the agent reported line numbers: use those ranges.
If the agent did NOT report line numbers (file-level claims only): read lines 1–50, the middle 20 lines, and the last 30 lines of each sampled file — this covers beginning/middle/end and prevents an agent gaming coverage by only reading the file header.

**Step 3 — Compare with verbatim quote matching.**
For each sampled file, require verbatim quotes from **at least 3 positions** in the file (beginning, middle, end):
- Beginning: lines 1–20
- Middle: lines near `total_lines ÷ 2`
- End: last 20 lines

If the agent's report contains a quote only from one section of a file (e.g., only the first function), score as SUPERFICIAL even if that one quote matches — an agent that read only the first 10 lines will pass a single-quote check but fail a 3-position check.

For files ≤30 lines: a single quote covering most of the file is sufficient (no 3-position requirement).

This prevents a fabricated conformant report (correct line numbers, plausible descriptions, no quotes) from passing as THOROUGH. A fabricated report cannot produce verbatim quotes that match the file — this is the detection mechanism.

**Output per sample:**

```
COVERAGE_CHECK:
Sample 1: [file] lines [X–Y]
  Agent described: "[quote from agent's report]"
  Actual content: "[verbatim quote from the file]"
  Match: YES | NO | PARTIAL

Sample 2: [file] lines [X–Y]
  Agent described: "[quote]"
  Actual content: "[verbatim quote]"
  Match: YES | NO | PARTIAL

[additional samples...]

VERDICT: THOROUGH | SUPERFICIAL | FABRICATED
Confidence: HIGH | MEDIUM | LOW
Action: ACCEPT | RE_DISPATCH_THOROUGH | ESCALATE
```

**Verdict definitions:**
- `THOROUGH` — agent descriptions match actual content across samples
- `SUPERFICIAL` — agent descriptions are vague, generic, or partially wrong — the agent may have skimmed
- `FABRICATED` — agent descriptions contradict actual file content — the agent likely did not read the file

Set `Action: ESCALATE` when verdict is FABRICATED or when confidence is LOW on a THOROUGH verdict.
