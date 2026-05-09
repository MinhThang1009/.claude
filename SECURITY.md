# Security Considerations — dotclaude plugin (EXPERIMENTAL)

> **TL;DR**: Plugin format giảm posture bảo mật so với user-config repo gốc (branch `main`). Đọc kỹ trước khi install.

## ⚠️ Critical: Migration required cho full security

Plugin format **không** distribute permissions/env/model defaults. Thiếu migration = giảm defense-in-depth nghiêm trọng.

### C-1: Plugin install gap → mất `permissions.deny` window

**Threat**: Cửa sổ thời gian giữa `/plugin install` và "user paste MIGRATION-SETTINGS.md" → bash-guard.sh chạy nhưng `~/.claude/settings.json` không có `permissions.deny` → plugin compromise có thể đọc:
- `~/.aws/credentials`, `~/.aws/config`
- `~/.ssh/id_rsa`, `~/.ssh/id_ed25519`
- `**/credentials.json`, `**/serviceAccount*.json`
- `.env`, `.env.*`, `*.pem`, `*.key`

User dễ skip migration vì plugin "đã work" (skills/agents trigger fine).

**MITIGATION**:
1. Đọc [MIGRATION-SETTINGS.md](./MIGRATION-SETTINGS.md) NGAY sau install
2. Copy `recommended-settings.json` → `~/.claude/settings.json` (hoặc merge thủ công)
3. Verify trong session Claude Code: `/permissions` show deny rules

### C-2: Marketplace install không integrity verification

**Threat**: `/plugin marketplace add MinhThang1009/dotclaude` shorthand:
- Không pin commit SHA
- Không signature verification
- Không integrity hash

Risks:
- GitHub account takeover (account deletion → reuse)
- Namespace squatting trên fork
- Compromise commit giữa `/plugin marketplace update` calls

**MITIGATION**:

Recommended install bằng commit SHA pinned:
```
/plugin marketplace add https://github.com/MinhThang1009/dotclaude.git#<COMMIT_SHA>
```

Verify SHA từ [GitHub releases page](https://github.com/MinhThang1009/dotclaude/releases) trước install.

Plain shorthand `MinhThang1009/dotclaude` chỉ dùng cho dev/test, KHÔNG production.

## Hooks runtime security

Hooks plugin chạy với privileges user — plugin compromise = arbitrary code execution.

### Hardening đã apply trong v0.1.0-experimental

- **bash-guard.sh + format-on-edit.sh**: sanitize PATH (remove `.`/`./`), unset `PYTHONPATH`/`PYTHONHOME`/`PYTHONSTARTUP` → chống `./python` malicious + Python sitecustomize injection (Sec H-1)
- **SessionStart hook**: `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null command git -c safe.directory=*` → chống CVE-2022-24765 (malicious `.git/config` poisoning)
- **format-on-edit.sh prettier**: `--no-plugin-search` → chống malicious `package.json` plugins RCE (Sec H-4)
- **format-on-edit.sh path check**: skip nếu file ngoài `$CLAUDE_PROJECT_DIR` (tránh write file system khác)

### Limitations còn lại

- **Concurrent sessions**: 2 sessions edit cùng file → format hooks không atomic (race condition possible)
- **Plugin update mid-session**: cache kept 7 days, sessions cũ tiếp tục dùng path stale cho đến khi `/reload-plugins`
- **Variable-resolved sensitive paths**: `FILE=.env cat $FILE` không bị bash-guard catch (cần dynamic shell parsing)

## Verification trước khi trust plugin (recommended)

Trước khi `/plugin install`, suggest:

```bash
# 1. Clone repo manually
git clone https://github.com/MinhThang1009/dotclaude.git /tmp/dotclaude-verify
cd /tmp/dotclaude-verify
git checkout plugin-experiment/v1

# 2. Diff với last known good commit (nếu có)
git log --oneline -5

# 3. Inspect hook scripts
cat plugins/dotclaude/hooks/*.sh
cat plugins/dotclaude/hooks/hooks.json

# 4. Verify regression tests pass
bash plugins/dotclaude/hooks/test-bash-guard.sh
# Expected: Total 97, PASS 97, FAIL 0

# 5. Local test
claude --plugin-dir ./plugins/dotclaude

# 6. Sau khi trust, install với commit SHA pinned
# /plugin marketplace add https://github.com/MinhThang1009/dotclaude.git#<verified-sha>
```

## Threat model

dotclaude plugin **không phù hợp** cho:
- Máy production với data sensitive (production keys, payment systems)
- Máy shared (multi-user)
- Máy mà attacker có access vật lý

dotclaude plugin **phù hợp** cho:
- Máy dev cá nhân
- Containerized environments (devcontainer, VM)
- Sandboxed Claude Code session với `--plugin-dir` local-only

## Reporting security issues

Nếu phát hiện vulnerability trong dotclaude plugin:
1. **KHÔNG** tạo public issue trên GitHub
2. Email maintainer (xem `plugin.json` author field)
3. Cung cấp: PoC, impact analysis, suggested fix

## See also

- [README.md](./README.md) — install + migration guide
- [MIGRATION-SETTINGS.md](./MIGRATION-SETTINGS.md) — copy permissions/env/model thủ công
- Branch `main` = user-config repo gốc (commit `70a925a`) — full security posture, recommended cho production use
