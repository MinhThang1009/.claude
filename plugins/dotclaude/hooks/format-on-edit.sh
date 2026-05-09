#!/usr/bin/env bash
# Format file sau khi Edit/Write/MultiEdit.
# - Skip nếu file ngoài $CLAUDE_PROJECT_DIR (tránh ghi vào file system khác).
# - Skip prettier nếu có executable config .js/.cjs/.mjs (RCE risk: require() execute code).
# - prettier dùng --no-plugin-search để chống malicious package.json plugins (Sec H-4).
# - Silent skip nếu formatter chưa cài.

set -u

# Security hardening (Sec H-1): sanitize PATH, unset PYTHON env vars
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '^$\|^\.$\|^\./' | tr '\n' ':' | sed 's/:$//')
unset PYTHONPATH PYTHONHOME PYTHONSTARTUP

# Find python interpreter (Win H3 fix: fallback python → python3 cho cross-platform)
PY=""
for p in python python3; do
  if command -v "$p" >/dev/null 2>&1 && "$p" -c '' >/dev/null 2>&1; then
    PY="$p"
    break
  fi
done

[ -z "$PY" ] && exit 0   # No python → silent skip

INPUT=$(cat)
FILE=$(echo "$INPUT" | "$PY" -c "import sys, json; print(json.loads(sys.stdin.read() or '{}').get('tool_input', {}).get('file_path', ''))" 2>/dev/null)

[ -z "$FILE" ] && exit 0

# Resolve absolute paths để compare. Dùng python (cross-platform, không cần realpath).
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
RESOLVED=$("$PY" -c "
import os, sys
try:
    proj = os.path.realpath(sys.argv[1])
    target = os.path.realpath(sys.argv[2])
    # In ra empty nếu target không nằm trong project
    rel = os.path.relpath(target, proj)
    if rel.startswith('..'):
        sys.exit(1)
    print(target)
except Exception:
    sys.exit(1)
" "$PROJECT_DIR" "$FILE" 2>/dev/null)

# File ngoài project → skip
[ -z "$RESOLVED" ] && exit 0

case "$FILE" in
  *.ts|*.tsx|*.js|*.jsx|*.json|*.md|*.yml|*.yaml|*.css|*.scss|*.html)
    if command -v prettier >/dev/null 2>&1; then
      # Skip prettier nếu có executable config (RCE risk qua require())
      # Override: set CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG=1 nếu trust config (vd: monorepo nội bộ)
      cd "$PROJECT_DIR" 2>/dev/null
      HAS_JS_CONFIG=0
      if [ -f .prettierrc.js ] || [ -f .prettierrc.cjs ] || [ -f .prettierrc.mjs ] || \
         [ -f prettier.config.js ] || [ -f prettier.config.cjs ] || [ -f prettier.config.mjs ]; then
        HAS_JS_CONFIG=1
      fi
      if [ "$HAS_JS_CONFIG" = "1" ] && [ "${CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG:-}" != "1" ]; then
        echo "WARN: skipping prettier — executable config (.prettierrc.js/.cjs/.mjs) is RCE risk. Set CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG=1 to override." >&2
      else
        # --no-plugin-search: chặn auto-load plugins từ package.json (Sec H-4)
        prettier --no-plugin-search --write "$FILE" >/dev/null 2>&1
      fi
    fi
    ;;
  *.py)
    command -v ruff >/dev/null 2>&1 && ruff format "$FILE" >/dev/null 2>&1
    ;;
  *.go)
    command -v gofmt >/dev/null 2>&1 && gofmt -w "$FILE" >/dev/null 2>&1
    ;;
  *.rs)
    command -v rustfmt >/dev/null 2>&1 && rustfmt "$FILE" >/dev/null 2>&1
    ;;
esac

exit 0
