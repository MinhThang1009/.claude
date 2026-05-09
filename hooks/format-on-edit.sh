#!/usr/bin/env bash
# Format file sau khi Edit/Write/MultiEdit.
# Dùng python parse JSON thay jq (không có sẵn trên Windows git bash).
# Skip nếu formatter chưa cài; không bao giờ block tool call.

set -u

INPUT=$(cat)
FILE=$(echo "$INPUT" | python -c "import sys, json; print(json.loads(sys.stdin.read() or '{}').get('tool_input', {}).get('file_path', ''))" 2>/dev/null)

[ -z "$FILE" ] && exit 0

case "$FILE" in
  *.ts|*.tsx|*.js|*.jsx|*.json|*.md|*.yml|*.yaml)
    command -v prettier >/dev/null 2>&1 && prettier --write "$FILE" >/dev/null 2>&1
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
