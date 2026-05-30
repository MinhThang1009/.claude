#!/usr/bin/env bash
# Wrapper minimal cho subagent-edit-surface.py (PostToolUse Agent hook, PROTOTYPE).
# Surface git diff sau khi subagent (Agent tool) trả về → main agent verify edit.
# Toàn bộ logic nằm trong file .py.
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)' >/dev/null 2>&1; then
    exec "$PY" "$HOME/.claude/hooks/subagent-edit-surface.py"
  fi
done
# Python thiếu → silent skip (PostToolUse hook không block).
exit 0
