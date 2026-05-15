#!/usr/bin/env bash
# Hook: tự động chuyển plan file từ global ~/.claude/plans/ vào project-level .claude/plans/
# Kích hoạt bởi PostToolUse khi Write tool ghi file
# Tương thích đa nền tảng: Linux, macOS, Windows (Git Bash/WSL)

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ -z "$FILE_PATH" ] && exit 0

# Chuẩn hoá dấu \ thành / (tương thích Windows)
FILE_PATH="${FILE_PATH//\\//}"
GLOBAL_PLANS="${HOME}/.claude/plans"
GLOBAL_PLANS="${GLOBAL_PLANS//\\//}"

# So sánh không phân biệt hoa thường (Windows path không phân biệt)
NORM_FILE=$(echo "$FILE_PATH" | tr '[:upper:]' '[:lower:]')
NORM_GLOBAL=$(echo "$GLOBAL_PLANS" | tr '[:upper:]' '[:lower:]')

# Chỉ xử lý file .md trong thư mục global plans, bỏ qua archive
case "$NORM_FILE" in
  "$NORM_GLOBAL/"*.md) ;;
  *) exit 0 ;;
esac
case "$NORM_FILE" in
  */archive/*) exit 0 ;;
esac

# Lấy đường dẫn project từ biến môi trường Claude Code
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
PROJECT_PLANS="$PROJECT_DIR/.claude/plans"
mkdir -p "$PROJECT_PLANS"

FILENAME=$(basename "$FILE_PATH")
mv "$FILE_PATH" "$PROJECT_PLANS/$FILENAME" 2>/dev/null || exit 0

echo "Đã tự động chuyển plan: $FILENAME -> $PROJECT_PLANS/"
