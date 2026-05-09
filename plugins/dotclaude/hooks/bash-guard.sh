#!/usr/bin/env bash
# Wrapper minimal cho bash-guard.py.
# Toàn bộ logic pattern matching nằm trong file .py.
# Try python rồi python3 (Windows ưu tiên python.exe; Linux/macOS modern thường có python3).
# Test bằng `<cmd> -c ''` để bỏ qua Windows Store stub fail.

# Security hardening (Sec H-1): sanitize PATH, unset PYTHON env vars
# Loại entries `.` ở đầu hoặc rỗng để chống malicious `./python` injection
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '^$\|^\.$\|^\./' | tr '\n' ':' | sed 's/:$//')
unset PYTHONPATH PYTHONHOME PYTHONSTARTUP

for PY in python python3; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c '' >/dev/null 2>&1; then
    exec "$PY" "${CLAUDE_PLUGIN_ROOT}/hooks/bash-guard.py"
  fi
done
# Không có python → skip silent (không block bừa)
exit 0
