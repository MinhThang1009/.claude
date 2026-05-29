#!/usr/bin/env bash
# Wrapper minimal cho self-review-nudge.py.
# Stop hook — nhắc spawn fresh reviewer khi nhiều Edit chưa review.
# Toàn bộ logic đếm + nhắc nằm trong file .py.
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)' >/dev/null 2>&1; then
    exec "$PY" "$HOME/.claude/hooks/self-review-nudge.py"
  fi
done
# Python thiếu → silent skip (Stop hook không block).
exit 0
