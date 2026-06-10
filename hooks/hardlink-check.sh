#!/usr/bin/env bash
# Tự sửa hardlink giữa repo dotclaude và ~/.claude khi bị đứt.
# Nguyên nhân đứt thường gặp: git checkout/pull/stash chạm file phía repo, hoặc
# tool ghi kiểu atomic-write (Claude Code CLI ghi settings.json, Edit tool...) →
# tạo inode mới một phía. Quy tắc sửa: bản có mtime MỚI HƠN thắng, relink bản kia.

REPO="$HOME/dotclaude"
LIVE="$HOME/.claude"
FILES="CLAUDE.md settings.json"

if [ ! -d "$REPO" ] || [ ! -d "$LIVE" ]; then exit 0; fi

for f in $FILES; do
  rf="$REPO/$f"; lf="$LIVE/$f"
  if [ ! -f "$rf" ] || [ ! -f "$lf" ]; then continue; fi
  [ "$(stat -c %i "$rf")" = "$(stat -c %i "$lf")" ] && continue

  # Link đứt → chọn bản mới hơn làm nguồn, xóa bản kia rồi mklink lại
  if [ "$(stat -c %Y "$rf")" -ge "$(stat -c %Y "$lf")" ]; then
    src="$rf"; dst="$lf"
  else
    src="$lf"; dst="$rf"
  fi
  win_src=$(cygpath -w "$src" 2>/dev/null || echo "$src")
  win_dst=$(cygpath -w "$dst" 2>/dev/null || echo "$dst")
  if rm -f "$dst" && cmd //c "mklink /H $win_dst $win_src" >/dev/null 2>&1; then
    echo "🔗 HARDLINK $f đứt → đã tự relink (nguồn: bản mới hơn $win_src)."
  else
    echo "⚠️ HARDLINK $f đứt, tự relink THẤT BẠI. Sửa tay: rm \"$dst\" && cmd //c 'mklink /H $win_dst $win_src'"
  fi
done
exit 0
