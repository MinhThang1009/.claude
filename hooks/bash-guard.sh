#!/usr/bin/env bash
# Wrapper minimal cho bash-guard.py.
# Toàn bộ logic pattern matching nằm trong file .py.
# Try python rồi python3 (Windows ưu tiên python.exe; Linux/macOS modern thường có python3).
# Test cả Python 3.6+ (yêu cầu f-string) bằng `-c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)'`.
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)' >/dev/null 2>&1; then
    exec "$PY" "$HOME/.claude/hooks/bash-guard.py"
  fi
done
# Không có Python 3.6+ → FAIL-CLOSED (block) thay vì silent allow.
# Defense layer phải hoạt động hoặc user biết để cài.
echo "[bash-guard] BLOCKED: Python 3.6+ không tìm thấy trong PATH. Defense layer không thể hoạt động." >&2
echo "[bash-guard] Cài Python 3 (https://www.python.org/) rồi restart Claude Code, hoặc xóa hook này khỏi settings.json." >&2
exit 2
