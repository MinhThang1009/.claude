#!/usr/bin/env bash
# Wrapper cho logic-audit-gate.py.
# Stop hook — block nếu logic-audit phase gates chưa hoàn tất.
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)' >/dev/null 2>&1; then
    exec "$PY" "$HOME/.claude/hooks/logic-audit-gate.py"
  fi
done
# Python thiếu → silent skip (không block session).
exit 0
