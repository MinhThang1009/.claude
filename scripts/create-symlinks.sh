#!/usr/bin/env bash
# Tạo symlinks từ dotclaude sang ~/.claude

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$HOME/.claude"

echo "Source: $SRC"
echo "Target: $DST"
mkdir -p "$DST"

# --- Parse .claude-load.txt ---
# Format: "plugin" | "plugin:agents" | "plugin:skills" | "plugin:commands"
LOAD_FILE="$SRC/.claude-load.txt"
declare -A LOAD_MAP  # plugin -> comma-separated types

if [ -f "$LOAD_FILE" ]; then
    while IFS= read -r line; do
        [[ "$line" =~ ^\s*# ]] && continue
        [[ -z "${line// }" ]] && continue
        line="${line// /}"
        if [[ "$line" == *:* ]]; then
            plugin="${line%%:*}"; type="${line##*:}"
            if [ -z "${LOAD_MAP[$plugin]+x}" ]; then
                LOAD_MAP[$plugin]="$type"
            else
                LOAD_MAP[$plugin]="${LOAD_MAP[$plugin]},$type"
            fi
        else
            LOAD_MAP[$line]="all"
        fi
    done < "$LOAD_FILE"
fi

LOAD_ALL=false
[ ${#LOAD_MAP[@]} -eq 0 ] && LOAD_ALL=true

if $LOAD_ALL; then
    echo "Loading ALL plugins"
else
    echo "Load config: ${!LOAD_MAP[@]}"
fi

should_load_type() {
    local plugin="$1" type="$2"
    $LOAD_ALL && return 0
    [ -z "${LOAD_MAP[$plugin]+x}" ] && return 1
    local types="${LOAD_MAP[$plugin]}"
    [[ "$types" == "all" || "$types" == *"$type"* ]] && return 0
    return 1
}

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

# --- agents/ ---
rm -rf "$DST/agents"; mkdir -p "$DST/agents"
for plugin_dir in "$SRC"/plugins/*/; do
    plugin_name=$(basename "$plugin_dir")
    should_load_type "$plugin_name" "agents" || continue
    while IFS= read -r agent; do
        [ -f "$agent" ] || continue
        ln -s "$agent" "$DST/agents/$(basename "$agent")"
    done < <(find "$plugin_dir" -path "*/agents/*.md")
done
echo "OK agents: $(ls "$DST/agents" | wc -l | tr -d ' ') files"

# --- skills/ ---
rm -rf "$DST/skills"; mkdir -p "$DST/skills"
for plugin_dir in "$SRC"/plugins/*/; do
    plugin_name=$(basename "$plugin_dir")
    should_load_type "$plugin_name" "skills" || continue
    [ -d "${plugin_dir}skills" ] || continue
    for skill_dir in "${plugin_dir}skills"/*/; do
        [ -d "$skill_dir" ] || continue
        ln -s "$skill_dir" "$DST/skills/$(basename "$skill_dir")"
    done
done
echo "OK skills: $(ls "$DST/skills" | wc -l | tr -d ' ') dirs"

# --- commands/ ---
rm -rf "$DST/commands"; mkdir -p "$DST/commands"
for plugin_dir in "$SRC"/plugins/*/; do
    plugin_name=$(basename "$plugin_dir")
    should_load_type "$plugin_name" "commands" || continue
    for cmd in "${plugin_dir}commands"/*.md; do
        [ -f "$cmd" ] || continue
        ln -s "$cmd" "$DST/commands/$(basename "$cmd")"
    done
done
echo "OK commands: $(ls "$DST/commands" | wc -l | tr -d ' ') files"

echo ""
echo "Done! Restart Claude Code de apply changes."
