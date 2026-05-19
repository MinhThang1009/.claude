#!/bin/bash
# install.sh — setup dotclaude plugin sync sau git clone
# Chạy 1 lần: bash scripts/install.sh

set -e
DOTCLAUDE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="sub-agent-system"
PLUGIN_SRC="$DOTCLAUDE_ROOT/plugins/$PLUGIN"
MARKETPLACE="$HOME/.claude/plugins/marketplaces/minhthang-plugins/plugins/$PLUGIN"

echo "=== dotclaude install: $PLUGIN ==="

# 1. Install git hook
cp "$DOTCLAUDE_ROOT/hooks/post-commit" "$DOTCLAUDE_ROOT/.git/hooks/post-commit"
chmod +x "$DOTCLAUDE_ROOT/.git/hooks/post-commit"
echo "✓ post-commit hook installed"

# Helper: sync một thư mục sang nhiều destinations
sync_dir() {
  local src_dir="$1" ; shift
  local label="$1" ; shift
  echo ""; echo "Syncing $label..."
  for f in "$src_dir"/*.md; do
    [ -f "$f" ] || continue
    filename=$(basename "$f")
    for dst in "$@"; do
      [ -d "$dst" ] && cp "$f" "$dst/$filename" && echo "  ✓ $filename → $(basename $dst)/"
    done
  done
}

sync_dir "$PLUGIN_SRC/commands" "commands" \
  "$HOME/.claude/commands" \
  "$MARKETPLACE/commands"

sync_dir "$PLUGIN_SRC/agents" "agents" \
  "$HOME/.claude/agents" \
  "$MARKETPLACE/agents"

# Skills: có subdirectory mỗi skill
echo ""; echo "Syncing skills..."
for skill_dir in "$PLUGIN_SRC/skills"/*/; do
  skill=$(basename "$skill_dir")
  for f in "$skill_dir"*.md; do
    [ -f "$f" ] || continue
    filename=$(basename "$f")
    [ -d "$HOME/.claude/skills/$skill" ] && cp "$f" "$HOME/.claude/skills/$skill/$filename" && echo "  ✓ $skill/$filename → skills/"
    [ -d "$MARKETPLACE/skills/$skill" ] && cp "$f" "$MARKETPLACE/skills/$skill/$filename"
  done
done

echo ""
echo "Done. All locations synced. Future commits will auto-sync via post-commit hook."
echo "Re-run this script if you clone dotclaude on a new machine."
