#!/bin/bash
# install.sh — setup dotclaude plugin sync sau git clone
# Chạy 1 lần: bash scripts/install.sh

set -e

DOTCLAUDE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_COMMANDS="$HOME/.claude/commands"
INSTALL_AGENTS="$HOME/.claude/agents"
PLUGIN_COMMANDS="$DOTCLAUDE_ROOT/plugins/sub-agent-system/commands"
PLUGIN_AGENTS="$DOTCLAUDE_ROOT/plugins/sub-agent-system/agents"

echo "=== dotclaude install ==="
echo "Plugin source: $DOTCLAUDE_ROOT/plugins/sub-agent-system/"
echo ""

# 1. Install git hook
HOOK_SRC="$DOTCLAUDE_ROOT/hooks/post-commit"
HOOK_DST="$DOTCLAUDE_ROOT/.git/hooks/post-commit"
cp "$HOOK_SRC" "$HOOK_DST"
chmod +x "$HOOK_DST"
echo "✓ post-commit hook installed"

# 2. Sync plugin commands → installed location
echo ""
echo "Syncing commands..."
for f in "$PLUGIN_COMMANDS"/*.md; do
  [ -f "$f" ] || continue
  filename=$(basename "$f")
  cp "$f" "$INSTALL_COMMANDS/$filename"
  echo "  ✓ $filename"
done

# 3. Sync plugin agents → installed location
echo ""
echo "Syncing agents..."
for f in "$PLUGIN_AGENTS"/*.md; do
  [ -f "$f" ] || continue
  filename=$(basename "$f")
  cp "$f" "$INSTALL_AGENTS/$filename"
  echo "  ✓ $filename"
done

echo ""
echo "Done. Commands and agents will auto-sync after each git commit."
echo "Re-run this script if you clone dotclaude on a new machine."
