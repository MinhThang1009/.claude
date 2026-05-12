#!/usr/bin/env bash
# Tạo symlinks từ dotclaude sang ~/.claude

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$HOME/.claude"

echo "Source: $SRC"
echo "Target: $DST"
mkdir -p "$DST"

# --- Dirs symlinked as whole ---
for d in .claude-plugin docs hooks output-styles rules templates; do
    rm -rf "$DST/$d"
    ln -s "$SRC/$d" "$DST/$d"
    echo "OK dir: $d"
done

# --- Files symlinked individually ---
for f in CLAUDE.md README.md; do
    rm -f "$DST/$f"
    ln -s "$SRC/$f" "$DST/$f"
    echo "OK file: $f"
done

# --- agents/: collect từ plugins/**/agents/*.md → flat symlinks (recursive) ---
rm -rf "$DST/agents"
mkdir -p "$DST/agents"
while IFS= read -r agent; do
    [ -f "$agent" ] || continue
    ln -s "$agent" "$DST/agents/$(basename "$agent")"
done < <(find "$SRC/plugins" -path "*/agents/*.md")
echo "OK agents: $(ls "$DST/agents" | wc -l | tr -d ' ') files"

# --- skills/: collect từ plugins/*/skills/*/ → flat dir symlinks ---
rm -rf "$DST/skills"
mkdir -p "$DST/skills"
for skill_dir in "$SRC"/plugins/*/skills/*/; do
    [ -d "$skill_dir" ] || continue
    ln -s "$skill_dir" "$DST/skills/$(basename "$skill_dir")"
done
echo "OK skills: $(ls "$DST/skills" | wc -l | tr -d ' ') dirs"

# --- commands/: collect từ plugins/*/commands/*.md → flat symlinks ---
rm -rf "$DST/commands"
mkdir -p "$DST/commands"
for cmd in "$SRC"/plugins/*/commands/*.md; do
    [ -f "$cmd" ] || continue
    ln -s "$cmd" "$DST/commands/$(basename "$cmd")"
done
echo "OK commands: $(ls "$DST/commands" | wc -l | tr -d ' ') files"

echo ""
echo "Done! Restart Claude Code để apply changes."
