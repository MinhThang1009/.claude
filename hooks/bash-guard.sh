#!/usr/bin/env bash
# Bash command guard cho Claude Code PreToolUse hook.
# Dùng python parse JSON thay jq (không có sẵn trên Windows git bash).
# Exit 2 + stderr → Claude nhận feedback và adjust.

set -u

INPUT=$(cat)
CMD=$(echo "$INPUT" | python -c "import sys, json; print(json.loads(sys.stdin.read() or '{}').get('tool_input', {}).get('command', ''))" 2>/dev/null)

# Không có command → cho qua
[ -z "$CMD" ] && exit 0

# 1. Đọc file sensitive qua Bash (bypass Read deny rule)
if echo "$CMD" | grep -qE '(^|[[:space:]]|;|\||&)(cat|head|tail|less|more|grep|egrep|fgrep|awk|sed|nl|od|xxd|strings|hexdump)([[:space:]]).*(\.env(\.|$|[[:space:]])|\.pem|\.key|id_rsa|id_ed25519|\.p12|\.jks|credentials\.json)'; then
  echo "BLOCKED: reading sensitive file via Bash (bypasses Read deny rule). Dùng Read tool nếu cần và file không bị deny." >&2
  exit 2
fi

# 2. Pipe download → shell (curl|bash, wget|sh)
if echo "$CMD" | grep -qE '(curl|wget)[^|]*\|[[:space:]]*(bash|sh|zsh|ksh|dash)([[:space:]]|$)'; then
  echo "BLOCKED: piping downloaded content to shell (curl|bash pattern). Tải file về, kiểm tra, rồi chạy." >&2
  exit 2
fi

# 3. rm -r/-rf trên target nguy hiểm: root, home, current dir, parent dir
# Match: rm + flag chứa r/R + target ∈ {/, /*, ~, ~/, ~/*, $HOME, ${HOME}, ., ./, ./*, ..}
# CHỈ chặn target nguy hiểm cụ thể, KHÔNG chặn rm -rf /tmp/foo hay rm -rf ./node_modules.
if echo "$CMD" | grep -qE '(^|[[:space:]]|;|\||&)rm[[:space:]]+-[a-zA-Z]*[rR][a-zA-Z]*[[:space:]]+(/|/\*|~|~/|~/\*|\$HOME|\$\{HOME\}|\.|\./|\./\*|\.\.)([[:space:]]|$|;|\||&)'; then
  echo "BLOCKED: rm -r/-rf trên root, home, current, hoặc parent directory. Để xóa subdir cụ thể, dùng path đầy đủ (vd: rm -rf ./node_modules)." >&2
  exit 2
fi

# 4. Fork bomb
case "$CMD" in
  *":(){"*)
    echo "BLOCKED: fork bomb pattern" >&2
    exit 2
    ;;
esac

# 5. dd ghi vào disk device (overwrite physical disk - data destruction)
# CHỈ chặn dd of=/dev/sd*, /dev/hd*, /dev/nvme*, etc. KHÔNG chặn dd of=file.img.
if echo "$CMD" | grep -qE '(^|[[:space:]]|;|\||&)dd([[:space:]][^|;&]*)?[[:space:]]of=/dev/(sd|hd|nvme|disk|loop|mmcblk|vd|xvd)'; then
  echo "BLOCKED: dd writing to disk device (data destruction risk)" >&2
  exit 2
fi

exit 0
