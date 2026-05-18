#!/usr/bin/env bash
# Wrapper minimal cho handoff-auto-move.py.
# Toàn bộ logic nằm trong file .py (xử lý Unicode + Windows path đúng hơn bash).
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)' >/dev/null 2>&1; then
    exec "$PY" "$HOME/.claude/hooks/handoff-auto-move.py"
  fi
done
exit 0
