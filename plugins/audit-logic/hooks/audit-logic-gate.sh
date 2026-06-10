#!/usr/bin/env bash
# Wrapper cho audit-logic-gate.py.
# Stop hook — block nếu audit-logic phase gates chưa hoàn tất.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)' >/dev/null 2>&1; then
    exec "$PY" "$SCRIPT_DIR/audit-logic-gate.py"
  fi
done
# Python thiếu → silent skip (không block session).
exit 0
