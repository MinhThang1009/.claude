#!/usr/bin/env bash
# Sync plugin agents/commands/skills → ~/.claude
# Đọc .claude-load.txt để biết plugin nào và loại nào được sync.
# Chạy sau khi thêm/xóa file trong plugins, hoặc qua git hook.

set -euo pipefail

DOTCLAUDE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE="$HOME/.claude"
LOAD_FILE="$DOTCLAUDE/.claude-load.txt"

# ── Đọc config ──────────────────────────────────────────────────────────────

# Trả về danh sách "plugin:type" được enable (type = agents|skills|commands|all)
load_entries() {
  [[ -f "$LOAD_FILE" ]] || return
  grep -v '^\s*#' "$LOAD_FILE" | grep -v '^\s*$' | grep -v '^\s*!' | while IFS= read -r line; do
    plugin="${line%%:*}"
    type="${line#*:}"
    [[ "$plugin" == "$type" ]] && type="all"   # không có dấu ':' → load all
    echo "$plugin:$type"
  done
}

# Trả về danh sách tên bị exclude (dòng bắt đầu bằng !)
load_excludes() {
  [[ -f "$LOAD_FILE" ]] || return
  grep -v '^\s*#' "$LOAD_FILE" | grep '^\s*!' | sed 's/^\s*!//'
}

is_excluded() {
  local name="${1%.md}"
  while IFS= read -r ex; do
    [[ "$name" == "$ex" ]] && return 0
  done < <(load_excludes)
  return 1
}

# Kiểm tra plugin:type có được enable không
is_enabled() {
  local plugin="$1" type="$2"
  # Nếu file trống hoặc không tồn tại → load tất cả
  local count
  count=$(load_entries | wc -l)
  [[ "$count" -eq 0 ]] && return 0

  while IFS=: read -r p t; do
    if [[ "$p" == "$plugin" ]]; then
      [[ "$t" == "all" || "$t" == "$type" ]] && return 0
    fi
  done < <(load_entries)
  return 1
}

# Lấy tên plugin từ đường dẫn file (plugins/<plugin>/agents/foo.md → <plugin>)
plugin_of() {
  echo "$1" | sed "s|$DOTCLAUDE/plugins/||" | cut -d'/' -f1
}

# ── Sync agents / commands ───────────────────────────────────────────────────

sync_files() {
  local type="$1"   # agents | commands
  local dest="$CLAUDE/$type"
  mkdir -p "$dest"

  # Hardlink file mới từ plugin vào .claude
  while IFS= read -r src; do
    name=$(basename "$src")
    plugin=$(plugin_of "$src")
    is_enabled "$plugin" "$type" || continue
    is_excluded "$name" && continue

    dest_file="$dest/$name"
    src_inode=$(ls -i "$src" | awk '{print $1}')
    dest_inode=$(ls -i "$dest_file" 2>/dev/null | awk '{print $1}' || true)

    if [[ "$src_inode" != "$dest_inode" ]]; then
      rm -f "$dest_file"
      ln "$src" "$dest_file"
      echo "  linked: $type/$name"
    fi
  done < <(find "$DOTCLAUDE/plugins" -path "*/$type/*.md" 2>/dev/null)

  # Xóa file không còn được enable hoặc bị exclude
  for dest_file in "$dest"/*.md; do
    [[ -f "$dest_file" ]] || continue
    name=$(basename "$dest_file")
    dest_inode=$(ls -i "$dest_file" | awk '{print $1}')
    src=$(find "$DOTCLAUDE/plugins" -inum "$dest_inode" 2>/dev/null | head -1)

    if [[ -z "$src" ]]; then
      echo "  removing orphan: $type/$name"
      rm "$dest_file"
    else
      plugin=$(plugin_of "$src")
      if ! is_enabled "$plugin" "$type" || is_excluded "$name"; then
        echo "  removing excluded: $type/$name"
        rm "$dest_file"
      fi
    fi
  done
}

# ── Sync skills ──────────────────────────────────────────────────────────────

sync_skills() {
  local dest="$CLAUDE/skills"
  mkdir -p "$dest"

  # Junction skill dir mới
  while IFS= read -r src_dir; do
    name=$(basename "$src_dir")
    plugin=$(plugin_of "$src_dir")
    is_enabled "$plugin" "skills" || continue
    is_excluded "$name" && continue

    dest_dir="$dest/$name"
    if [[ ! -e "$dest_dir" ]]; then
      if powershell.exe -Command "New-Item -ItemType Junction -Path '$(cygpath -w "$dest_dir")' -Target '$(cygpath -w "$src_dir")' | Out-Null" 2>/dev/null; then
        echo "  linked: skills/$name"
      else
        echo "  ERROR: junction failed: skills/$name"
      fi
    fi
  done < <(find "$DOTCLAUDE/plugins" -mindepth 3 -maxdepth 3 -path "*/skills/*" -type d 2>/dev/null)

  # Xóa skill junction không còn được enable hoặc bị exclude
  for dest_dir in "$dest"/*/; do
    [[ -d "$dest_dir" ]] || continue
    name=$(basename "$dest_dir")
    src=$(find "$DOTCLAUDE/plugins" -mindepth 3 -maxdepth 3 -path "*/skills/$name" -type d 2>/dev/null | head -1)

    remove=0
    if [[ -z "$src" ]]; then
      remove=1
      echo "  removing orphan: skills/$name"
    else
      plugin=$(plugin_of "$src")
      if ! is_enabled "$plugin" "skills" || is_excluded "$name"; then
        remove=1
        echo "  removing excluded: skills/$name"
      fi
    fi

    if [[ "$remove" -eq 1 ]]; then
      powershell.exe -Command "Remove-Item -Path '$(cygpath -w "$dest_dir")' -Force" 2>/dev/null || rm -rf "$dest_dir"
    fi
  done
}

# ── Main ─────────────────────────────────────────────────────────────────────

echo "Syncing dotclaude → ~/.claude ..."
sync_files "agents"
sync_files "commands"
sync_skills
echo "Done."
