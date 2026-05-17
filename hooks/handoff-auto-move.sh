#!/usr/bin/env bash
# Hook: tự động chuyển handoff.md từ project root vào .claude/ của project
# Kích hoạt bởi PostToolUse khi Write tool ghi file

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ -z "$FILE_PATH" ] && exit 0

FILE_PATH="${FILE_PATH//\\//}"

FILENAME=$(basename "$FILE_PATH")
[ "$FILENAME" != "handoff.md" ] && exit 0

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
PROJECT_DIR="${PROJECT_DIR//\\//}"

TARGET_DIR="$PROJECT_DIR/.claude"
TARGET="$TARGET_DIR/handoff.md"

# Bỏ qua nếu file đã nằm trong .claude/
NORM_FILE=$(echo "$FILE_PATH" | tr '[:upper:]' '[:lower:]')
NORM_TARGET=$(echo "$TARGET" | tr '[:upper:]' '[:lower:]')
[ "$NORM_FILE" = "$NORM_TARGET" ] && exit 0

mkdir -p "$TARGET_DIR"
mv "$FILE_PATH" "$TARGET" 2>/dev/null || exit 0

echo "Đã tự động chuyển handoff.md -> $TARGET"
