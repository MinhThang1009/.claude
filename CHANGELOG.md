# Changelog

Toàn bộ thay đổi đáng chú ý của repo `dotclaude` được ghi nhận trong file này.

Format theo [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), tuân thủ [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

### Added (2026-05-18)

- **hooks/handoff-auto-move.sh + .py**: hook mới tự động move `HANDOFF.md` từ project root vào `.claude/` sau khi Write tool ghi file. Python version xử lý Unicode + Windows path đúng hơn bash thuần.
- **scripts/rebuild-links.ps1**: script rebuild `skills/`, `agents/`, `commands/` theo `.claude-load.txt` mà không cần chạy lại toàn bộ `create-symlinks.ps1`.
- **scripts/check-links.ps1**: script xem trạng thái symlink/junction của toàn bộ `~/.claude/`.
- **settings.json hook entry**: đăng ký `handoff-auto-move.sh` vào `PostToolUse → Write`.

### Changed (2026-05-18)

- **scripts/create-symlinks.ps1**: đổi `mklink /D` → `mklink /J` (junction, không cần admin). Thêm safety check: skip nếu source là symlink/junction để tránh circular ELOOP.
- **.claude-plugin/marketplace.json**: đổi `name` từ `claude-plugins` → `minhthang-plugins` (tránh impersonation validation của Claude Code).
- **.claude-load.txt**: giới hạn core 7 plugins (`session`, `commit-commands`, `debug`, `code-review`, `hookify`, `feature-dev`, `session-report`) thay vì load tất cả.
- **README.md**: cập nhật mô tả install section — junction mechanism, `.claude-load.txt` usage, `rebuild-links.ps1`, `check-links.ps1`.

### Fixed (2026-05-18)

- **hooks/bash-guard.py**: fix pattern `.key` yêu cầu path separator, tránh block lệnh có từ kết thúc `.key` không phải file path.
- **rules/ circular junction**: `dotclaude/rules/` và `~/.claude/rules/` trỏ vào nhau gây ELOOP. Fix: restore `dotclaude/rules/` về real dir từ git, tạo lại junction đúng chiều `~/.claude/rules/` → `dotclaude/rules/`.

### Changed (2026-05-16 — v2.1.142 compatibility + cross-platform)

- **REFERENCE.md** cập nhật cho Claude Code v2.1.142: `/goal`, `/bg`, `claude agents` flags, hook `args` exec form, `terminalSequence`, `worktree.baseRef`, `autoMode.hard_deny`, reactive compaction, skill budget settings, env vars mới
- **CLI-COMMANDS.md**: fast mode Opus 4.7 default (từ v2.1.142), thêm `/goal`, `/background`
- **README.md**: verify date → 2026-05-16 vs v2.1.142
- **settings.example.json**: thêm `CLAUDE_CODE_MAX_OUTPUT_TOKENS`, `plan-auto-move.sh` hook
- **create-symlinks.sh/ps1**: deploy `settings.json` từ example khi clone mới (fix clone-readiness)
- **create-symlinks.sh**: thêm bash 4+ version check (fix macOS stock bash 3.2)
- **.gitattributes**: thêm `*.py text eol=lf`
- **accept_changes.py**: `/tmp/` → `tempfile.gettempdir()` (cross-platform)
- **bundle-artifact.sh, init-artifact.sh**: shebang `#!/usr/bin/env bash` (portable)
- **Tests**: cập nhật theo .env patterns disabled + statusline output format mới

### Added (2026-05-16)

- **hooks/plan-auto-move.sh**: hook mới auto-move plan từ default mode sang Plan Mode

### Added (2026-05-10 — agent expansion + content updates)

- **5 agents mới** mở rộng coverage cho fullstack JS web/app workflow:
  - `agents/debugger.md` — Root cause analysis + fix + verify (5-step process). Dựa trên docs example chính thức Anthropic.
  - `agents/documentation-engineer.md` — Viết/maintain README, API docs, CHANGELOG, architecture guides. Zero-hallucination extraction từ code.
  - `agents/dependency-manager.md` — Audit deps (CVE, unused, outdated, license), bundle size optimization (moment→dayjs, lodash→lodash-es).
  - `agents/performance-engineer.md` — Profiling (DB N+1, memory leak, connection pool), caching strategy, before/after benchmarks.
  - `agents/nextjs-developer.md` — Next.js 14+ App Router specialist: Server Components, Server Actions, rendering strategies (SSG/SSR/ISR/PPR), SEO.
- **10 agents hiện có được cập nhật**:
  - Tất cả 10 agents: thêm `TodoWrite` (consistency với pattern Anthropic feature-dev plugin).
  - 5 agents (reviewer, explorer, architect, security-auditor, type-design-analyzer): thêm `LSP` cho code intelligence.
  - 3 agents (reviewer, explorer, architect): thêm `WebFetch` + `WebSearch` cho external research.
  - `code-reviewer`: thêm Accessibility checklist (semantic HTML, ARIA, color contrast, keyboard nav, form labels).
  - `code-architect`: thêm API Design section (REST/GraphQL, pagination, versioning, auth patterns, webhooks).
  - `code-simplifier`: thêm Code smell detection (long method, feature envy, data clumps...) + Advanced refactoring patterns (Replace Conditional with Polymorphism...) + Safety guidelines.
  - `documentation-engineer`: thêm Zero-hallucination extraction techniques + SECURITY.md trong docs scope.
- **Memory configuration** cho agents áp dụng cross-session learning: `code-reviewer` (user), `code-architect`/`code-explorer`/`security-auditor`/`code-simplifier`/`test-writer`/`test-analyzer` (project). Theo docs example Anthropic.
- **README.md + INTRODUCTION.md** cập nhật: 4→15 agents, 7→9 skills, 4→6 hooks, token table từ `/context` thực tế (29.8k→46.2k baseline).

### Added (Statusline)

- **Statusline custom** (`hooks/statusline.py` + `hooks/statusline.sh`) — hiển thị real-time ở status bar Claude Code:
  - Line 1: `[model + window mode (1M/200k) + ⚡ effort]` + `📁 cwd basename` + `🌿 git branch` + `+staged ~modified`
  - Line 2: threshold icon + progress bar `▰▱` + `ctx %` + `Nk tokens` + `💰 cost` + `⏱ duration` + `5h:N% 7d:N%` rate limits
  - 5 threshold zones theo multi-author cite: 🟢 sweet spot (<40%) / 🟡 dumb zone (40-60%) / 🟠 wrap up (60-77%) / 🔴 auto-compact firing (77-90%) / ⛔ hard limit (≥90%)
  - Git status cached 5s qua `session_id` để tránh lag repo lớn (theo Anthropic statusline doc dòng 790)
  - Bash wrapper fallback `python3` → `python`, silent fail nếu Python missing (không break statusline)
  - Force UTF-8 stdout cho Windows cp1252 encoding
- `settings.json`: `statusLine` config wire vào `$HOME/.claude/hooks/statusline.sh`.

### Changed (Phase 4 audit fixes — 2026-05-09)

- **Thresholds context window** (REFERENCE.md §16, README, CLAUDE.md, skills/context-check/SKILL.md): unify multi-author cite — Dex Horthy (`<30/<40/60%` + "dumb zone", MLOps Community video), Thariq Shihipar (`300-400k` 1M model context rot, Anthropic Claude Code team), Boris Cherny (`155k` auto-compact 200k window, X tweet). Round 1 cite sai cho Boris toàn bộ ngưỡng % — round 2 đính chính multi-author đúng.
- REFERENCE.md §16 mở rộng từ 7 → 11 subsection: thêm §16.3 "Compact threshold theo task complexity" (claude-codex.fr nuance) + §16.4 "Ngưỡng cho 1M context window" (Thariq compromise + Justin Smith LinkedIn reaffirm).
- Audit cập nhật line counts: REFERENCE.md ~2050 → ~2084 dòng (actual 2084), byte size ~159KB → ~164KB (actual 163798).
- Notation "155k/200k tokens" (ambiguous) → "155k tokens trên window 200k".
- Sonnet 4.6 effort levels: `low/med/high/max` → `low/med/high/(xhigh→high)/max` (rõ fallback behavior).

### Security (Phase 4 audit fixes — 2026-05-09)

- `.gitignore`: mở rộng coverage cho secret file types (`.env*`, `*.key`, `*.pem`, `id_rsa*`, `credentials.json`, `service-account*.json`, etc.) — defense-in-depth bên cạnh pre-commit `detect-private-key` + `permissions.deny` của settings.json.

### Fixed (Phase 4 audit fixes — 2026-05-09)

- `agents/security-auditor.md` L29: ` ```regex ` không phải language tag chuẩn → đổi sang ` ```text `.
- `skills/commit/SKILL.md` L131: bash code block `/tmp/commit-msg.txt` thiếu OS note → bổ sung note Git Bash Windows + PowerShell native.
- `output-styles/concise-vietnamese.md` L9: depersonalize "Bạn là... Tôi đọc code..." → impersonal "Code assistant... Dev thạo nghề đọc code...".
- `.github/CONTRIBUTING.md` L3: tone formal hơn cho public contributing guide.
- `.github/CONTRIBUTING.md` L155: xóa link Discussions trỏ tới URL 404 (Discussions chưa enabled trên repo).

### Changed (file structure)

- Clean root cho readability: move 5 file ra subdirectory chuẩn:
  - `CONTRIBUTING.md` → `.github/CONTRIBUTING.md` (GitHub vẫn detect)
  - `CODE_OF_CONDUCT.md` → `.github/CODE_OF_CONDUCT.md` (GitHub vẫn detect)
  - `SECURITY.md` → `.github/SECURITY.md` (GitHub vẫn detect)
  - `INTRODUCTION.md` → `docs/INTRODUCTION.md`
  - `REFERENCE.md` → `docs/REFERENCE.md`
- Update toàn bộ cross-references trong README.md, docs/INTRODUCTION.md,
  docs/REFERENCE.md, .github/CONTRIBUTING.md, .github/pull_request_template.md
- Root sau cleanup: chỉ còn 5 file visible (`CHANGELOG.md`, `CLAUDE.md`,
  `LICENSE`, `README.md`, `settings.json`) + 4 dot-config files

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
