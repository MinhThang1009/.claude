#!/usr/bin/env bash
# Format file sau khi Edit/Write/MultiEdit.
# - Skip nếu file ngoài $CLAUDE_PROJECT_DIR (tránh ghi vào file system khác).
# - Skip prettier nếu có config .js/.cjs/.mjs (RCE risk: require() execute code).
# - Silent skip nếu formatter chưa cài.

set -u

INPUT=$(cat)
FILE=$(echo "$INPUT" | python -c "import sys, json; print(json.loads(sys.stdin.read() or '{}').get('tool_input', {}).get('file_path', ''))" 2>/dev/null)

[ -z "$FILE" ] && exit 0

# Resolve absolute paths để compare. Dùng python (cross-platform, không cần realpath).
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
RESOLVED=$(python -c "
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
      # Skip prettier nếu có executable config HOẶC plugin reference trong package.json
      # (RCE risk qua require() khi prettier khởi động).
      # Override: set CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG=1 nếu trust config (vd: monorepo nội bộ)
      cd "$PROJECT_DIR" 2>/dev/null
      HAS_RISKY_CONFIG=0
      if [ -f .prettierrc.js ] || [ -f .prettierrc.cjs ] || [ -f .prettierrc.mjs ] || \
         [ -f prettier.config.js ] || [ -f prettier.config.cjs ] || [ -f prettier.config.mjs ]; then
        HAS_RISKY_CONFIG=1
      fi
      # Check package.json: prettier plugins load qua require() khi format chạy
      if [ "$HAS_RISKY_CONFIG" != "1" ] && [ -f package.json ]; then
        if grep -qE '(@prettier/plugin-|prettier-plugin-|"plugins"[[:space:]]*:[[:space:]]*\[)' package.json 2>/dev/null; then
          HAS_RISKY_CONFIG=1
        fi
      fi
      if [ "$HAS_RISKY_CONFIG" = "1" ] && [ "${CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG:-}" != "1" ]; then
        echo "WARN: skipping prettier — executable config hoặc plugin reference (package.json) is RCE risk via require(). Set CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG=1 to override." >&2
      else
        prettier --write "$FILE" >/dev/null 2>&1
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
