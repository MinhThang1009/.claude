#!/usr/bin/env bash
# Tạo symlinks từ dotclaude sang ~/.claude

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$HOME/.claude"

echo "Source: $SRC"
echo "Target: $DST"
mkdir -p "$DST"

# --- Đọc .claude-load.txt để lọc plugins ---
LOAD_FILE="$SRC/.claude-load.txt"
LOADED_PLUGINS=""
if [ -f "$LOAD_FILE" ]; then
    LOADED_PLUGINS=$(grep -v '^\s*#' "$LOAD_FILE" | grep -v '^\s*$' | tr -d ' ')
fi

should_load() {
    local plugin="$1"
    [ -z "$LOADED_PLUGINS" ] && return 0
    echo "$LOADED_PLUGINS" | grep -qx "$plugin"
}

if [ -z "$LOADED_PLUGINS" ]; then
    echo "Loading ALL plugins"
else
    echo "Loading plugins: $(echo "$LOADED_PLUGINS" | tr '\n' ' ')"
fi

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
for plugin_dir in "$SRC"/plugins/*/; do
    plugin_name=$(basename "$plugin_dir")
    should_load "$plugin_name" || continue
    while IFS= read -r agent; do
        [ -f "$agent" ] || continue
        ln -s "$agent" "$DST/agents/$(basename "$agent")"
    done < <(find "$plugin_dir" -path "*/agents/*.md")
done
echo "OK agents: $(ls "$DST/agents" | wc -l | tr -d ' ') files"

# --- skills/: collect từ plugins/*/skills/*/ → flat dir symlinks ---
rm -rf "$DST/skills"
mkdir -p "$DST/skills"
for plugin_dir in "$SRC"/plugins/*/; do
    plugin_name=$(basename "$plugin_dir")
    should_load "$plugin_name" || continue
    skills_dir="${plugin_dir}skills"
    [ -d "$skills_dir" ] || continue
    for skill_dir in "$skills_dir"/*/; do
        [ -d "$skill_dir" ] || continue
        ln -s "$skill_dir" "$DST/skills/$(basename "$skill_dir")"
    done
done
echo "OK skills: $(ls "$DST/skills" | wc -l | tr -d ' ') dirs"

# --- commands/: collect từ plugins/*/commands/*.md → flat symlinks ---
rm -rf "$DST/commands"
mkdir -p "$DST/commands"
for plugin_dir in "$SRC"/plugins/*/; do
    plugin_name=$(basename "$plugin_dir")
    should_load "$plugin_name" || continue
    for cmd in "${plugin_dir}commands"/*.md; do
        [ -f "$cmd" ] || continue
        ln -s "$cmd" "$DST/commands/$(basename "$cmd")"
    done
done
echo "OK commands: $(ls "$DST/commands" | wc -l | tr -d ' ') files"

echo ""
echo "Done! Restart Claude Code de apply changes."
