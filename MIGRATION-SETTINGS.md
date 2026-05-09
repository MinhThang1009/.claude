# Migration: settings.json permissions + env + model defaults

> **CRITICAL**: Plugin format **KHÔNG** distribute `permissions`/`env`/`model`/`effortLevel`/`autoUpdatesChannel`/`autoMemoryEnabled`/`claudeMdExcludes`/`attribution`. Plugin chỉ hỗ trợ `agent` + `subagentStatusLine` trong `settings.json` của plugin. Các blocks khác **PHẢI copy thủ công** vào `~/.claude/settings.json` để có full security posture.

> **WARNING**: Bỏ qua bước này = bash-guard.sh chạy NHƯNG `permissions.deny` không có → plugin compromise có thể đọc `~/.aws/credentials`, `~/.ssh/id_rsa` (xem [SECURITY.md](./SECURITY.md) C-1).

## Version

`0.1.0-experimental` — diff với version mới khi update plugin để biết delta cần re-merge.

## Quick install (recommended cho user CHƯA có settings.json)

```bash
# Backup nếu đã có
[ -f ~/.claude/settings.json ] && cp ~/.claude/settings.json ~/.claude/settings.json.backup-$(date +%Y%m%d)

# Replace với recommended
cp recommended-settings.json ~/.claude/settings.json
```

## Manual merge (recommended cho user ĐÃ custom settings.json)

Mở `recommended-settings.json` (cùng folder), copy từng block vào `~/.claude/settings.json` của bạn:

### 1. `permissions.allow` (40+ entries) — append, dedup

```bash
# Diff để xem block mới cần thêm:
diff <(jq '.permissions.allow' recommended-settings.json) <(jq '.permissions.allow' ~/.claude/settings.json)
```

### 2. `permissions.deny` (38+ entries) — **CRITICAL, bắt buộc append**

Block `deny` chứa rules quan trọng nhất:
- Read sensitive files: `.env`, `*.pem`, `*.key`, `id_rsa`, `~/.aws/credentials`, `~/.ssh/id_*`, etc.
- Bash dangerous: `rm -rf /*`, `nc:*`, `socat:*`, `git push --force`, `git reset --hard`

**Skip block này = plugin bash-guard.sh không có "lưới an toàn cuối" từ Read tool.**

### 3. `permissions.ask` (15+ entries) — append

Bash commands cần user confirm: `git commit`, `git push`, `npm install`, etc.

### 4. `permissions.defaultMode` — set `acceptEdits`

### 5. `env` — copy block

```json
"env": {
  "MAX_MCP_OUTPUT_TOKENS": "50000",
  "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "0"
}
```

### 6. `model`, `effortLevel`, `autoUpdatesChannel`

```json
"model": "opus[1m]",
"effortLevel": "xhigh",
"autoUpdatesChannel": "latest"
```

### 7. `autoMemoryEnabled`, `claudeMdExcludes`, `attribution`

```json
"autoMemoryEnabled": true,
"claudeMdExcludes": [
  "**/node_modules/**/CLAUDE.md",
  "**/.next/**/CLAUDE.md",
  "**/dist/**/CLAUDE.md",
  "**/build/**/CLAUDE.md",
  "**/.venv/**/CLAUDE.md"
],
"attribution": {
  "commit": "",
  "pr": ""
}
```

### 8. `hooks` — **KHÔNG copy** (đã migrate sang plugin)

Hooks giờ ở `plugins/dotclaude/hooks/hooks.json`, plugin tự load. Đừng duplicate trong user settings.json.

## Verify sau migrate

```bash
# JSON valid?
python -c "import json; json.load(open('$HOME/.claude/settings.json', encoding='utf-8'))" && echo "OK"

# Permissions effective?
# Trong session Claude Code:
# /permissions
# → Verify deny rules có .env, *.pem, ~/.aws/credentials, etc.
```

## Update workflow

Khi plugin update lên version mới (vd: `0.2.0`), `recommended-settings.json` có thể có rules mới. Diff:

```bash
# Pull update
git -C /tmp/dotclaude-clone pull
diff /tmp/dotclaude-clone/recommended-settings.json ~/.claude/settings.json

# Manually merge delta
```

Plugin update qua `/plugin marketplace update` **KHÔNG** auto-update settings.json — phải làm tay.
