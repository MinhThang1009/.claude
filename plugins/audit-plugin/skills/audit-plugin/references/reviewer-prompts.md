# Reviewer & Validator Prompts

Canonical prompts for audit-plugin — use them verbatim, replacing only the `[...]` placeholders. If SKILL.md and this file ever diverge about the *process*, SKILL.md wins; for the *prompt wording*, this file is the single source.

**The criteria block inside the fresh-reviewer prompt below (7 criteria + floor rule + severity rubric) is the SINGLE canonical definition of the audit criteria.** The lead applies it at Stage 1 and dispatched reviewers receive it verbatim at Stage 5 — there is no second copy anywhere. Criteria changes happen here and only here (SKILL.md Stage 7 rule).

---

## Fresh reviewer (Stage 5)

Dispatch a general-purpose agent with the prompt below at Stage 5. (Stage 1 is performed by the lead in-context — see SKILL.md; this prompt is only for dispatched zero-context rounds.) NEVER add prior findings and NEVER mention what was fixed (feeding the old list recreates the previous round's blind spots).

```
You are a demanding reviewer of Claude Code plugin content quality. Review the plugin at
[plugin-path] (all [N] files: [list files]). Do NOT read git history or git
diff — evaluate only the current state on disk.

What: find every remaining defect against 7 criteria:
(1) clarity/ambiguity of instructions — would Claude, reading them, execute the intended
    behavior; flag steps that never say where their output goes;
(2) internal contradictions across files or within a file (phase/step numbers,
    terminology, prompt templates, severity rubrics, state/lifecycle,
    actual script behavior vs SKILL.md/README descriptions);
(3) plugin structure vs best practice (frontmatter follows conventions; third-person
    trigger description with concrete trigger phrases — including non-English ones the
    user actually uses — and no trigger-phrase collision with OTHER installed skills'
    descriptions; hooks bundled in hooks/hooks.json using ${CLAUDE_PLUGIN_ROOT}; tool
    list matching the workflow's steps; cross-plugin dependencies declared in the
    README; reachability through every loading mechanism the repo actually uses —
    marketplace registration, load lists, settings enabledPlugins, junctions/symlinks —
    AND no dual-loading: the same skill reachable through two mechanisms at once, e.g.
    a junction-synced user-level copy plus a marketplace plugin, duplicates the trigger
    surface);
(4) exception paths that are uncovered or covered contradictorily (abort, orphaned
    state/resources, multi-session, missing dependency, zero-input/zero-findings,
    missing environment such as no test framework or no git);
(5) duplication between any two files of the plugin lacking a canonical pointer (drift
    risk) — including plugin-adjacent registry copies (e.g. plugin.json description
    verbatim-duplicated in marketplace.json) — and whether existing duplicates still
    match verbatim;
(6) technical defects AND security in bundled scripts — logic, paths (Windows vs
    POSIX), encoding (BOM, UTF-8), exit codes, whether fail-safe behavior matches what
    docstrings claim, dangerous command patterns, fail-open vs fail-closed vs
    documented intent, secret/PII leakage into logs or stderr; you may run the test
    suite and probe the scripts with adversarial input via Bash (in a temp dir only —
    test artifacts like caches are acceptable; never modify tracked plugin files);
(7) conciseness & consistency — context bloat (content inlined in SKILL.md that belongs
    in references, overlong description, redundant repetition), and stylistic
    consistency (one language policy, uniform tone/formatting/terminology across files).

These criteria are a FLOOR, not a ceiling: also report any defect that fits no
criterion if it would degrade the plugin in practice — tag it [OUT-OF-CRITERIA].

Severity rubric: HIGH = makes the plugin execute wrongly or not at all (contradictory
architecture, unexecutable instruction, dangerous operation); MEDIUM = degrades
reliability of outcomes (drift between duplicated content, undefined terms that drive
decisions, uncovered exception paths, examples teaching the wrong behavior);
LOW = polish (wording, style, minor inconsistency with no behavioral effect).

Scope: read within [plugin-path]; for criterion 3 you may ALSO read, read-only: other
plugins' SKILL.md frontmatter/description lines, the repo's plugin-loading configs
(marketplace.json, load lists, settings enabledPlugins), junction/symlink targets under
the user-level plugins and skills directories, and the user-level skills directory
listing (each: if present). Edit nothing anywhere.

Output format: a findings list — each finding: file + line (verbatim quote as evidence),
description, severity (HIGH/MEDIUM/LOW). Suspected but unconfirmed → still report,
tagged [UNCERTAIN] — coverage matters more than precision; a false-positive filter runs
afterward. Finally: a one-paragraph conclusion — are there HIGH or MEDIUM issues truly
worth fixing, or is the remainder polish/judgment calls?

Done criteria: all [N]/[N] files read (list them), every finding has a quote + location.
```

## Validator fallback (Stage 2, when finding-validator / /validator is unavailable)

Dispatch a general-purpose agent. Give it the findings list (file + line + short claim) — do NOT include your reasoning or confidence levels; strip `[UNCERTAIN]` and severity tags before sending (they are confidence signals that bias verdicts).

```
Verify each finding below against the actual files on disk. Working directory: [repo-root]

For EACH finding: verdict = CONFIRMED / FALSE POSITIVE / PARTIALLY TRUE (with what part
is wrong), plus a verbatim quote from disk with file path and line number as evidence.
No quote = not verified. Do not trust the finding text — read the files yourself.

Findings to verify:
[F1. <file> line ~<n>: <claim>]
[F2. ...]

Scope: only read files under [repo-root] — plus, for findings that cite them, the
user-level plugin/skill configs and directories (settings, plugin cache, skills).
Do not edit anything.
Done criteria: all [N] findings have a verdict + verbatim evidence quote with file:line.
```

## Context-isolation rules

- Fresh reviewer: zero chat history, zero prior findings, zero description of changes. Path + criteria only.
- Validator: receives the findings but not the overall conclusions (no verdict biasing).
- Every agent output → verify yourself with Read/Grep before relaying to the user or acting on it.
- After any dispatched agent returns (when the repo has git) → check `git status`/`git diff` — unexpected working-tree changes from a read-only agent mean stop and investigate before continuing. No git → compare key files by content. (Process rule — canonical copy in SKILL.md Ground Rules; that wording wins.)
