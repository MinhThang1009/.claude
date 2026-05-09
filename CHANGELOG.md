# Changelog

Toàn bộ thay đổi đáng chú ý của branch `plugin-experiment/v1` được ghi nhận trong file này.

Format theo [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), tuân thủ [Semantic Versioning](https://semver.org/lang/vi/).

> ⚠️ **EXPERIMENTAL branch** — Đây là proof-of-concept convert dotclaude từ user-config repo sang Claude Code plugin format. Branch này KHÔNG promote vào `main`. Production use → branch `main`.

## [Unreleased]

### Added

Đồng bộ các community standards file từ `main` (round 7 audit cho cả 2 branches):

- `CHANGELOG.md` — file ghi log thay đổi (file này).
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1.
- `CONTRIBUTING.md` — quy trình đóng góp + PR workflow + pre-commit setup.
- `.github/ISSUE_TEMPLATE/{bug-report,feature-request,fact-check-report,config}.yml` — form-based issue templates.
- `.github/pull_request_template.md` — PR checklist.
- `.github/dependabot.yml` — auto-update GitHub Actions weekly.
- `.github/workflows/ci.yml` — 9 CI jobs (đã adapt path cho plugin layout: `plugins/dotclaude/hooks/`, `plugins/dotclaude/skills/`, `plugins/dotclaude/agents/`).
- `.pre-commit-config.yaml` — local enforcement (đã adapt path).
- `.markdownlint-cli2.jsonc` — markdownlint config (disable cosmetic rules cho Vietnamese-prose).
- `scripts/validate-frontmatter.py` — schema validate cho `plugins/dotclaude/{skills,agents,output-styles}` (path đã adapt).

### Changed

Đồng bộ với main branch round 7:

- `INTRODUCTION.md`: "5 template" → "6 template" (thêm `skill-evals.json` link); add markdown links cho slash skills + subagents + templates + REFERENCE; "Max/Team Premium" → "Max/Team plan".
- `templates/project-CLAUDE.local.md`: refactor personal pronouns sang Anthropic Formal Style; thêm header note giải thích first-person convention.
- `templates/project-mcp.json`: bỏ broken `$schema: json.schemastore.org/mcp.json` URL (404).
- `templates/project-settings.json`: bỏ broken `$schema: json.schemastore.org/claude-code-settings.json` (404); xóa misleading deny rules (`Bash(curl * | bash:*)` no-op per docs).
- `README.md` (plugin guide): test count "97 case" → "119 case" tại 2 chỗ; sync với main fix.

### Fixed

- Hook events count audit: số chính xác là **29** (per docs/en/hooks). Mọi mention `30 events` đã revert về 29.
- Boris Cherny title soften: "Head of Claude Code" → "Anthropic Claude Code lead" (exact title không verifiable public).
- 4 hook bypass vector + IFS + glob detection (đồng bộ từ main commit `f92e802`).
- Test suite mở rộng từ 97 → 119 cases.

## [0.1.0-experimental] - 2026-05-09

Tag `dotclaude-v0.1.0-experimental` ở commit `14fe966` — POC convert dotclaude sang Claude Code plugin format. Kết luận:

- ✅ Plugin format technically work (skills + agents + hooks distribute qua marketplace).
- ❌ Permissions, env vars, model defaults KHÔNG distribute qua plugin spec → user phải migration thủ công (CRITICAL gap, dễ skip).
- ❌ Namespace UX disruption: `/code-review` → `/dotclaude:code-review` (muscle memory break).
- ❌ Security posture giảm so với main branch user-config format.

Format không promote vào `main`. Branch + tag giữ làm reference cho community + để re-evaluate khi Anthropic ship plugin permissions distribution support.

[Unreleased]: https://github.com/MinhThang1009/dotclaude/compare/dotclaude-v0.1.0-experimental...plugin-experiment/v1
[0.1.0-experimental]: https://github.com/MinhThang1009/dotclaude/releases/tag/dotclaude-v0.1.0-experimental
