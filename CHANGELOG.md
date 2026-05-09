# Changelog

Toàn bộ thay đổi đáng chú ý của repo `dotclaude` được ghi nhận trong file này.

Format theo [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), tuân thủ [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

### Added

- `CHANGELOG.md` — file ghi log thay đổi theo Keep a Changelog format.
- `SECURITY.md` — security policy + private vulnerability reporting flow.
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1 (tiếng Việt).
- `.github/ISSUE_TEMPLATE/` — 4 form-based templates (bug, feature, fact-check, config).
- `.github/pull_request_template.md` — PR checklist khớp `CONTRIBUTING.md`.
- `.github/dependabot.yml` — auto-update GitHub Actions weekly.
- `.github/workflows/ci.yml` — 9 CI jobs (hook tests cross-OS, JSON validate, markdown link check, markdownlint, ruff, shellcheck, actionlint, frontmatter validate).
- `.pre-commit-config.yaml` — local enforcement trước commit.
- `scripts/validate-frontmatter.py` — schema validate cho skills/agents/output-styles.
- `.markdownlint-cli2.jsonc` — markdownlint config (disable cosmetic rules cho Vietnamese-prose).

### Changed

- Refactor 63 personal-language case sang Anthropic Formal Style:
  - Category A (public docs: README, REFERENCE, CONTRIBUTING) — depersonalize.
  - Category C (LLM prompts: skills/, agents/, output-styles/) — convert "tôi/bạn" → impersonal voice or "user/Claude".
  - Category D (rules + references) — formal voice strict.
- Category B (CLAUDE.md, templates/project-CLAUDE.local.md) — giữ first-person voice intentional, thêm header note giải thích convention.
- Rename ISSUE_TEMPLATE files snake_case → kebab-case (consistency với toàn bộ repo).
- `hooks/bash-guard.py` — thêm split tại redirect operators (`>`, `>>`, `<`, `<<`), `*` boundary cho glob detection, `$IFS` normalization, rm pattern cover `--no-preserve-root` và target trailing `/`.
- `hooks/bash-guard.sh` — fail-CLOSED khi Python missing.
- `hooks/format-on-edit.sh` — skip prettier khi `package.json` có `prettier-plugin-` reference (RCE risk).
- `templates/project-settings.json` — xóa 5 misleading deny rule (`Bash(curl * | bash:*)` no-op per docs).
- `templates/project-mcp.json` — xóa broken `$schema` URL (json.schemastore.org/mcp.json 404).
- `README.md` + `REFERENCE.md` — thêm verify date `2026-05-09` + disclaimer.
- `REFERENCE.md` — fix version-gating list (5 fix sau cross-check raw CHANGELOG anthropics/claude-code), bỏ mention `coding-standards.md`/`git-workflow.md` plain-text → markdown links.
- `INTRODUCTION.md` — thêm markdown links cho 6 template + 7 skill + 4 agent.

### Fixed

- WRONG factual claim phát hiện qua fact-check vs Anthropic docs:
  - REFERENCE.md: Boris Cherny title soften → "Anthropic Claude Code lead" (exact title không verifiable public).
  - README.md: Opus 4.7 đã có trên Bedrock + Vertex (cập nhật bảng fallback).
  - REFERENCE.md: hook events count giữ 29 (docs canonical confirm). Lưu ý: round 1 fact-check tạm đổi 29 → 30 nhưng round 5 verify lại docs/en/hooks confirm 29 — đã revert.
- 6 fact-check issue Tier B+C: bỏ `default` model alias, soften `/schedule` quotas, remove `CLAUDE_CODE_SYNC_PLUGIN_INSTALL` env (unverified), Code Review cost caveat, etc.
- 4 version-gating sai sau verify CHANGELOG: skills system v2.1.0 → v2.0.20, output styles v2.1.101 → v1.0.81, etc.
- Soften env vars unverified specific values (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 95% → "~95%, verify với env docs").
- 3 broken external URL fix: `keepachangelog.com/vi/1.1.0/` → `/en/1.1.0/`; remove `$schema: json.schemastore.org/claude-code-settings.json` (404, similar to mcp.json earlier).
- Stale numbers / counts trong docs:
  - `README.md`: CLAUDE.md "~88 dòng" → "~90 dòng" (actual); test-bash-guard "97 case" → "119 case" (3 chỗ); REFERENCE byte size "~158k chars" → "~159k chars".
  - `INTRODUCTION.md`: "5 template" → "6 template" (thêm `skill-evals.json` vào list).
  - `CONTRIBUTING.md`: CI "6 jobs" → "9 jobs" (matrix Ubuntu+macOS + actionlint + frontmatter validate); fix duplicate `4.` numbering.
  - `REFERENCE.md`: byte size "158KB" → "~159KB"; auto-compact env var "default 95%" → "~95%, verify với env docs".

### Security

- 4 hook bypass vector phát hiện qua audit và patch:
  - Redirect bypass: `echo $SECRET > .env` không bị chặn (split tại `>` segment).
  - Flag bypass: `rm --no-preserve-root -rf /` không bị chặn.
  - Fail-open: `bash-guard.sh` silent allow khi Python missing → fail-CLOSED.
  - Glob detection: `cat *.env` shell expansion.
- Test suite mở rộng từ 97 → 119 cases.

## [0.1.0-experimental] - 2026-05-09

Tag `dotclaude-v0.1.0-experimental` ở commit `14fe966` (branch `plugin-experiment/v1`) — POC convert dotclaude sang Claude Code plugin format. Kết luận: technically work nhưng giảm security posture (permissions không distribute qua plugin spec, namespace UX disruption). Format không promote vào `main`. Branch + tag giữ làm reference.

[Unreleased]: https://github.com/MinhThang1009/dotclaude/compare/dotclaude-v0.1.0-experimental...HEAD
[0.1.0-experimental]: https://github.com/MinhThang1009/dotclaude/releases/tag/dotclaude-v0.1.0-experimental
