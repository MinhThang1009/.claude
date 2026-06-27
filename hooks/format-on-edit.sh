#!/usr/bin/env bash
# Wrapper minimal cho format-on-edit.py.
# Toàn bộ logic dispatch + RCE detection nằm trong file .py.
# Try python3 rồi python (Linux/macOS modern thường có python3; Windows thường chỉ có python.exe).
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)' >/dev/null 2>&1; then
    exec "$PY" "$HOME/.claude/hooks/format-on-edit.py"
  fi
done
# Format-on-edit là PostToolUse hook — silent skip nếu Python thiếu
# (không block tool call như bash_guard PreToolUse).
exit 0
