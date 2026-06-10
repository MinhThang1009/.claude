#!/usr/bin/env bash
# Cảnh báo khi hardlink giữa repo dotclaude và ~/.claude bị đứt.
# Nguyên nhân đứt thường gặp: git checkout/pull/stash/reset chạm vào file phía repo,
# hoặc tool ghi kiểu atomic-write (ghi file tạm rồi rename) → tạo inode mới một phía.
# So inode hai bên: khác nhau = link đứt → in cảnh báo kèm lệnh khôi phục.

REPO="$HOME/dotclaude"
LIVE="$HOME/.claude"
FILES="CLAUDE.md settings.json"

[ -d "$REPO" ] && [ -d "$LIVE" ] || exit 0

for f in $FILES; do
  [ -f "$REPO/$f" ] && [ -f "$LIVE/$f" ] || continue
  if [ "$(stat -c %i "$REPO/$f")" != "$(stat -c %i "$LIVE/$f")" ]; then
    win_live=$(cygpath -w "$LIVE/$f" 2>/dev/null || echo "$LIVE/$f")
    win_repo=$(cygpath -w "$REPO/$f" 2>/dev/null || echo "$REPO/$f")
    echo "⚠️ HARDLINK ĐỨT: $f — repo và ~/.claude đang là 2 file riêng (sửa 1 bên sẽ KHÔNG sync)."
    echo "   Khôi phục (xem bản nào mới hơn trước, rồi): rm \"$LIVE/$f\" && cmd //c 'mklink /H $win_live $win_repo'"
  fi
done
exit 0
