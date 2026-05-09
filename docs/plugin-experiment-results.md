# Plugin Experiment Results — dotclaude → Claude Code plugin

> Date: 2026-05-09 · Status: COMPLETED (experimental, not promoted to main)

## Executive Summary

Convert `dotclaude` user-config repo sang Claude Code plugin format **technically work** nhưng có security/UX trade-offs đáng kể. **Recommend giữ `main` branch (user-config) làm canonical cho production use.** Plugin branches giữ ở GitHub cho reference future research.

## Branches

| Branch | Commit | Status | Purpose |
|---|---|---|---|
| `main` | `70a925a` | ✅ Canonical | User-config repo gốc với full security posture |
| `plugin-experiment/v1` | `14fe966` | ✅ Reference | Full migration với 4 commits split + security hardening |
| ~~`plugin-experiment/poc-v0.1`~~ | ~~`e0f87de`~~ | 🗑️ Deleted | PoC test 1 skill — validated plugin format work, branch deleted sau khi xác nhận concept |

Tag: `dotclaude-v0.1.0-experimental` pinned ở `14fe966` (commit-SHA reference cho secure install).

## Methodology

12 audit rounds + 4 specialized agents (security-auditor + 3 general-purpose):
- 18+ docs pages fetched từ Anthropic (plugins, plugins-reference, plugin-marketplaces, discover-plugins, debug-your-config, skills, hooks, sub-agents, commands, memory, plugin-dependencies, env-vars, claude-directory, plugin-hints, troubleshooting, best-practices, sandboxing, server-managed-settings, context-window)
- 16+ deep-grep rounds trên persisted docs
- 4 parallel specialized audits (security/Windows/UX/implementation)

Total findings: 91 (5 BLOCKER + 14 HIGH + 15 MEDIUM + 11 LOW + 46 confirmations)

## What Worked ✅

**1. Plugin format compliance:**
- `marketplace.json` + `plugin.json` schema verified với docs spec
- Skills/agents/output-styles/hooks default locations work
- `${CLAUDE_PLUGIN_ROOT}` path resolution work cross-platform
- Frontmatter compliance: skills (agentskills.io spec), agents (Claude Code subagent spec)

**2. Marketplace E2E flow:**
- `/plugin marketplace add <git URL>#<branch>` work
- `/plugin install <plugin>@<marketplace>` work
- `/reload-plugins` reload cleanly (note: cosmetic counter bug "0 skills" but skills loaded correctly)
- Skills namespace `dotclaude:*` không conflict với user-scope

**3. Security hardening implemented:**
- `bash-guard.sh` + `format-on-edit.sh`: sanitize PATH, unset PYTHONPATH/PYTHONHOME
- SessionStart hook: `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null command git -c safe.directory=*` (CVE-2022-24765 mitigation)
- prettier `--no-plugin-search` (chống malicious package.json plugins)
- `git update-index --chmod=+x` cho 3 hook scripts (mode 100755 cho Linux/macOS exec)

**4. Hook regression:** 97/97 test pass sau migration.

## What Didn't Work / Trade-offs ⚠️

**1. CRITICAL — Permissions distribution gap (Sec C-1):**
- Plugin format **KHÔNG** distribute `permissions.deny` rules
- User phải copy thủ công từ `recommended-settings.json` → `~/.claude/settings.json`
- Cửa sổ giữa "install plugin" và "user merge settings" → bash-guard.sh chạy nhưng Read tool không filter sensitive files
- User dễ skip migration vì plugin "đã work" (skills/agents trigger fine)
- **Mitigation**: README + SECURITY.md + MIGRATION-SETTINGS.md prominent warnings

**2. CRITICAL — Marketplace integrity (Sec C-2):**
- `MinhThang1009/dotclaude` shorthand: không pin commit, không signature
- GitHub account takeover/squatting risk
- **Mitigation**: documented commit SHA pinned install + git tag `dotclaude-v0.1.0-experimental`

**3. HIGH — User experience disruption:**
- Skill names bị namespaced: `/code-review` → `/dotclaude:code-review` (muscle memory break)
- Agent names bị namespaced: `code-reviewer` → `dotclaude:code-reviewer`
- User clone qua `/plugin install` KHÔNG thấy MIGRATION-* files (chỉ trong git repo, phải clone manually)
- 5 bước migration: clone repo + backup + copy 3 file types + merge settings

**4. HIGH — Windows compatibility friction:**
- `git update-index --chmod=+x` cần thiết (Windows `core.fileMode=false` default)
- `python3` Windows Store stub fail → fallback `python` first
- `bash` wrapper trong hooks.json yêu cầu Git for Windows hoặc WSL

**5. MEDIUM — Implementation granularity:**
- 4 commits split logical (manifest → move → hooks → docs) thay vì 1 monolithic
- Verification gates sau mỗi phase (JSON validate, hook regression test)
- Partial failure recovery procedure documented

## Final State

**Plugin format technically works** — proven via:
- PoC branch (`plugin-experiment/poc-v0.1`): 1 skill test ✅
- Full branch (`plugin-experiment/v1`): 7 skills + 4 agents + 3 hooks all loaded

**But canonical use case is `main` branch (user-config):**
- Full security posture (no migration gap)
- No skill namespace disruption
- 1-step install (manual copy)
- Familiar mental model

## Recommendations

1. **Production use**: stick với `main` branch user-config repo (commit `70a925a`)
2. **Plugin format**: keep branches at GitHub cho reference, use only when:
   - Distributing to teammates qua marketplace
   - User base muốn plugin auto-update
   - Anthropic spec evolves to support permissions distribution
3. **Re-test plugin format** nếu Anthropic ship features:
   - Permission rules trong plugin settings.json (currently only `agent`/`subagentStatusLine`)
   - CLAUDE.md from plugin auto-load
   - Rules/references @-import support

## Reference

- Plan file: `~/.claude/plans/l-n-k-ho-ch-y-happy-hickey.md`
- Branch: [plugin-experiment/v1](https://github.com/MinhThang1009/dotclaude/tree/plugin-experiment/v1)
- Tag: [`dotclaude-v0.1.0-experimental`](https://github.com/MinhThang1009/dotclaude/releases/tag/dotclaude-v0.1.0-experimental)
- Note: branch `plugin-experiment/poc-v0.1` (PoC) đã deleted sau khi confirm concept work — chỉ giữ v1 cho full migration reference
- Audit findings: 91 total (chi tiết trong plan file)
- Docs verified: 18+ Anthropic pages
