#!/usr/bin/env bash
# Wrapper minimal cho statusline.py.
# Statusline fail silently (output empty) thay vì block — nếu Python không có.
# Cùng pattern với bash-guard.sh.
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)' >/dev/null 2>&1; then
    exec "$PY" "$HOME/.claude/hooks/statusline.py"
  fi
done
# Silent fail — statusline blank thay vì error message.
exit 0
