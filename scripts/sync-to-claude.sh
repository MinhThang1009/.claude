#!/usr/bin/env bash
# Sync plugin agents/commands/skills → ~/.claude
# Chạy sau khi thêm/xóa file trong plugins, hoặc qua git hook.

set -euo pipefail

DOTCLAUDE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE="$HOME/.claude"

sync_files() {
  local type="$1"   # agents | commands
  local dest="$CLAUDE/$type"
  mkdir -p "$dest"

  # Hardlink file mới từ plugin vào .claude
  while IFS= read -r src; do
    name=$(basename "$src")
    dest_file="$dest/$name"
    src_inode=$(ls -i "$src" | awk '{print $1}')
    dest_inode=$(ls -i "$dest_file" 2>/dev/null | awk '{print $1}' || true)

    if [[ "$src_inode" != "$dest_inode" ]]; then
      rm -f "$dest_file"
      ln "$src" "$dest_file"
      echo "  linked: $type/$name"
    fi
  done < <(find "$DOTCLAUDE/plugins" -path "*/$type/*.md" 2>/dev/null)

  # Xóa orphan: file trong .claude không còn nguồn trong dotclaude
  for dest_file in "$dest"/*.md; do
    [[ -f "$dest_file" ]] || continue
    name=$(basename "$dest_file")
    dest_inode=$(ls -i "$dest_file" | awk '{print $1}')
    match=$(find "$DOTCLAUDE/plugins" -inum "$dest_inode" 2>/dev/null)
    if [[ -z "$match" ]]; then
      echo "  removing orphan: $type/$name"
      rm "$dest_file"
    fi
  done
}

sync_skills() {
  local dest="$CLAUDE/skills"
  mkdir -p "$dest"

  # Junction skill dir mới
  while IFS= read -r src_dir; do
    name=$(basename "$src_dir")
    dest_dir="$dest/$name"

    if [[ ! -e "$dest_dir" ]]; then
      cmd.exe /c "mklink /J \"$(cygpath -w "$dest_dir")\" \"$(cygpath -w "$src_dir")\"" > /dev/null 2>&1
      echo "  linked: skills/$name"
    fi
  done < <(find "$DOTCLAUDE/plugins" -mindepth 3 -maxdepth 3 -path "*/skills/*" -type d 2>/dev/null)

  # Xóa orphan skill junctions
  for dest_dir in "$dest"/*/; do
    [[ -d "$dest_dir" ]] || continue
    name=$(basename "$dest_dir")
    match=$(find "$DOTCLAUDE/plugins" -mindepth 3 -maxdepth 3 -path "*/skills/$name" -type d 2>/dev/null)
    if [[ -z "$match" ]]; then
      echo "  removing orphan: skills/$name"
      cmd.exe /c "rmdir \"$(cygpath -w "$dest_dir")\"" > /dev/null 2>&1 || rm -rf "$dest_dir"
    fi
  done
}

echo "Syncing dotclaude → ~/.claude ..."
sync_files "agents"
sync_files "commands"
sync_skills
echo "Done."
