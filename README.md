# dotclaude — Claude Code plugin (EXPERIMENTAL)

> ⚠️ **EXPERIMENTAL branch `plugin-experiment/v1`** — Plugin format thay vì user-config repo. Yêu cầu **migration thủ công** sau install. **ĐỌC [SECURITY.md](./.github/SECURITY.md) trước.**

> Branch `main` (commit `70a925a`) = user-config repo gốc với full security posture, **recommended cho production use**. Plugin branch chỉ test concept.

## ⚠️ User đã dùng main branch — namespace thay đổi

Skills + agents trong plugin format bị **namespaced**:

| Main branch (user-config) | Plugin branch |
|---|---|
| `/code-review` | `/dotclaude:code-review` |
| `/commit` | `/dotclaude:commit` |
| `/debug` | `/dotclaude:debug` |
| `/refactor` | `/dotclaude:refactor` |
| `/explain` | `/dotclaude:explain` |
| `/handoff` | `/dotclaude:handoff` |
| `/context-check` | `/dotclaude:context-check` |
| Agent `code-reviewer` | `dotclaude:code-reviewer` |
| Agent `architect` | `dotclaude:architect` |
| Agent `security-auditor` | `dotclaude:security-auditor` |
| Agent `test-writer` | `dotclaude:test-writer` |

Muscle memory **sẽ break**. Cân nhắc trước khi switch.

## Install

### Recommended: commit SHA pinned (secure)

Lấy commit SHA mới nhất từ [GitHub branch](https://github.com/MinhThang1009/dotclaude/tree/plugin-experiment/v1):

```text
/plugin marketplace add https://github.com/MinhThang1009/dotclaude.git#<COMMIT_SHA>
/plugin install dotclaude@dotclaude-marketplace
/reload-plugins
```

### Quick (less secure, dev/test only)

```text
/plugin marketplace add MinhThang1009/dotclaude
/plugin install dotclaude@dotclaude-marketplace
/reload-plugins
```

## CRITICAL: Migration steps

Plugin **KHÔNG** distribute CLAUDE.md, rules/, references/, settings.json. Bỏ qua = giảm security posture nghiêm trọng.

### Bước 1 — Clone repo (REQUIRED để get migration files)

**macOS / Linux**:
```bash
git clone https://github.com/MinhThang1009/dotclaude.git /tmp/dotclaude-migration
cd /tmp/dotclaude-migration
git checkout plugin-experiment/v1
```

**Windows (PowerShell)**:
```powershell
git clone https://github.com/MinhThang1009/dotclaude.git $env:TEMP\dotclaude-migration
cd $env:TEMP\dotclaude-migration
git checkout plugin-experiment/v1
```

**Windows (CMD)**:
```cmd
git clone https://github.com/MinhThang1009/dotclaude.git %TEMP%\dotclaude-migration
cd %TEMP%\dotclaude-migration
git checkout plugin-experiment/v1
```

### Bước 2 — Backup ~/.claude/

**macOS / Linux**:
```bash
cp -r ~/.claude ~/.claude.backup-$(date +%Y%m%d)
```

**Windows (PowerShell)**:
```powershell
Copy-Item -Recurse -Force "$env:USERPROFILE\.claude" "$env:USERPROFILE\.claude.backup-$(Get-Date -Format yyyyMMdd)"
```

**Windows (CMD)**:
```cmd
xcopy /E /I /H /Y "%USERPROFILE%\.claude" "%USERPROFILE%\.claude.backup\"
```

### Bước 3 — Copy MIGRATION files vào ~/.claude/

**macOS / Linux**:
```bash
cp MIGRATION-CLAUDE.md ~/.claude/CLAUDE.md
mkdir -p ~/.claude/rules ~/.claude/references
cp -r MIGRATION-RULES/. ~/.claude/rules/
cp -r MIGRATION-REFERENCES/. ~/.claude/references/
```

**Windows (PowerShell)**:
```powershell
Copy-Item MIGRATION-CLAUDE.md "$env:USERPROFILE\.claude\CLAUDE.md"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\rules", "$env:USERPROFILE\.claude\references" | Out-Null
Copy-Item MIGRATION-RULES\* "$env:USERPROFILE\.claude\rules\"
Copy-Item MIGRATION-REFERENCES\* "$env:USERPROFILE\.claude\references\"
```

**Windows (CMD)**:
```cmd
copy /Y MIGRATION-CLAUDE.md "%USERPROFILE%\.claude\CLAUDE.md"
if not exist "%USERPROFILE%\.claude\rules" mkdir "%USERPROFILE%\.claude\rules"
if not exist "%USERPROFILE%\.claude\references" mkdir "%USERPROFILE%\.claude\references"
xcopy /Y MIGRATION-RULES\*.* "%USERPROFILE%\.claude\rules\"
xcopy /Y MIGRATION-REFERENCES\*.* "%USERPROFILE%\.claude\references\"
```

### Bước 4 — Merge settings.json (CRITICAL — đọc kỹ)

Đọc [MIGRATION-SETTINGS.md](./MIGRATION-SETTINGS.md). Quyết định:

- **Quick install** (chưa có ~/.claude/settings.json hoặc OK overwrite):
  ```bash
  cp recommended-settings.json ~/.claude/settings.json
  ```

- **Manual merge** (đã custom settings.json): xem [MIGRATION-SETTINGS.md §Manual merge](./MIGRATION-SETTINGS.md#manual-merge-recommended-cho-user-đã-custom-settingsjson)

⚠️ **CRITICAL**: Nếu skip bước này, plugin sẽ thiếu `permissions.deny` rules — bash-guard.sh chạy nhưng Read tool không filter sensitive files. Xem [SECURITY.md C-1](./.github/SECURITY.md).

### Bước 5 — Verify migration

```bash
# JSON valid
python -c "import json; json.load(open('$HOME/.claude/settings.json', encoding='utf-8'))" && echo "OK"
```

Trong session Claude Code:
```text
/permissions
```
→ Verify deny rules có `.env`, `*.pem`, `~/.aws/credentials`, `Bash(rm -rf /*)`, `Bash(nc:*)`, etc.

```text
/skills
```
→ List skills `dotclaude:*`

```text
/agents
```
→ List 4 agents `dotclaude:*`

## Trade-off so với main branch

| Feature | Main (user-config) | Plugin (this branch) |
|---|---|---|
| Install | Manual copy 3 OS | `/plugin install` 1 lệnh |
| Update | `git pull` + re-copy | `/plugin marketplace update` |
| Skill names | `/code-review`, `/commit` | `/dotclaude:code-review`, `/dotclaude:commit` |
| CLAUDE.md global | ✅ Auto-load | ❌ Phải migration thủ công |
| Rules auto-import | ✅ | ❌ Phải migration |
| Permissions distribute | ✅ Trực tiếp | ❌ Phải migration |
| Hooks distribute | ✅ Settings.json hooks | ✅ Plugin hooks.json (auto) |
| Hook scripts exec bit | ⚠️ Thiếu trên Windows clone | ✅ git update-index --chmod=+x (mode 100755) |
| Security hardening | Standard | + GIT_CONFIG_GLOBAL=/dev/null + sanitize PATH + --no-plugin-search |

## Plugin contents (sau khi install)

Plugin install location: `~/.claude/plugins/cache/<hash>/plugins/dotclaude/`

```text
plugins/dotclaude/
├── .claude-plugin/plugin.json
├── skills/                       # 7 skills, namespace dotclaude:*
├── agents/                       # 4 agents, namespace dotclaude:*
├── output-styles/                # 1 style
└── hooks/                        # PreToolUse + PostToolUse + SessionStart
    ├── hooks.json
    ├── bash-guard.py             # Engine
    ├── bash-guard.sh             # Wrapper (sanitize PATH, unset PYTHON env)
    ├── format-on-edit.sh         # Formatter (--no-plugin-search, python fallback)
    └── test-bash-guard.sh        # Regression 119 case
```

## Uninstall

```text
/plugin uninstall dotclaude@dotclaude-marketplace
/plugin marketplace remove dotclaude-marketplace
```

⚠️ **Manual cleanup required** — uninstall plugin **KHÔNG** clean migration files đã copy:

**macOS / Linux (bash):**

```bash
rm ~/.claude/CLAUDE.md
rm -rf ~/.claude/rules ~/.claude/references
mv ~/.claude.backup-<DATE> ~/.claude
```

**Windows (PowerShell):**

```powershell
Remove-Item "$env:USERPROFILE\.claude\CLAUDE.md"
Remove-Item -Recurse "$env:USERPROFILE\.claude\rules", "$env:USERPROFILE\.claude\references"
Move-Item "$env:USERPROFILE\.claude.backup-<DATE>" "$env:USERPROFILE\.claude"
```

## Verify hook coverage tại máy local (post-install)

```bash
bash ~/.claude/plugins/cache/<hash>/plugins/dotclaude/hooks/test-bash-guard.sh
# Expected: Total 119, PASS 119, FAIL 0
```

## See also

- [SECURITY.md](./.github/SECURITY.md) — security considerations + threat model
- [MIGRATION-SETTINGS.md](./MIGRATION-SETTINGS.md) — settings.json merge guide
- [MIGRATION-CLAUDE.md](./MIGRATION-CLAUDE.md) — CLAUDE.md gốc
- [MIGRATION-RULES/](./MIGRATION-RULES/) — auto-import rules
- [MIGRATION-REFERENCES/](./MIGRATION-REFERENCES/) — @-reference docs
- Branch `main` — user-config repo gốc (full security, no migration needed)

## Đóng góp

Xem [CONTRIBUTING.md](./.github/CONTRIBUTING.md) để biết quy trình PR, coding style, và cách chạy CI local.

## License

[MIT](./LICENSE) — Copyright 2026 MinhThang1009.

## Tài liệu Anthropic tham khảo

- [Plugins](https://code.claude.com/docs/en/plugins)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins)
- [Skills](https://code.claude.com/docs/en/skills) | [Subagents](https://code.claude.com/docs/en/sub-agents) | [Hooks](https://code.claude.com/docs/en/hooks)
