#!/usr/bin/env bash
# Bash command guard cho Claude Code PreToolUse hook.
# Dùng python parse JSON thay jq (không có sẵn trên Windows git bash).
# Exit 2 + stderr → Claude nhận feedback và adjust.

set -u

INPUT=$(cat)
CMD=$(echo "$INPUT" | python -c "import sys, json; print(json.loads(sys.stdin.read() or '{}').get('tool_input', {}).get('command', ''))" 2>/dev/null)

# Không có command → cho qua
[ -z "$CMD" ] && exit 0

# 1. Pattern destructive nguy hiểm
case "$CMD" in
  *"rm -rf"*"/"*|*":(){"*|*"dd if="*)
    echo "BLOCKED: dangerous command pattern (rm -rf /, fork bomb, dd)" >&2
    exit 2
    ;;
esac

# 2. Đọc file sensitive qua Bash (bypass Read deny rule)
if echo "$CMD" | grep -qE '(^|[[:space:]]|;|\||&)(cat|head|tail|less|more|grep|egrep|fgrep|awk|sed|nl|od|xxd|strings|hexdump)([[:space:]]).*(\.env(\.|$|[[:space:]])|\.pem|\.key|id_rsa|id_ed25519|\.p12|\.jks|credentials\.json)'; then
  echo "BLOCKED: reading sensitive file via Bash (bypasses Read deny rule). Dùng Read tool nếu cần và file không bị deny." >&2
  exit 2
fi

# 3. Pipe download → shell (curl|bash, wget|sh)
if echo "$CMD" | grep -qE '(curl|wget)[^|]*\|[[:space:]]*(bash|sh|zsh|ksh|dash)([[:space:]]|$)'; then
  echo "BLOCKED: piping downloaded content to shell (curl|bash pattern). Tải file về, kiểm tra, rồi chạy." >&2
  exit 2
fi

exit 0
