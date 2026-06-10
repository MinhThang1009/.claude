#!/usr/bin/env python3
"""Validate .claude-plugin/marketplace.json và cấu trúc plugins/.

Check:
- marketplace.json parse được và có đúng schema
- Mỗi plugin entry có required fields
- Source path của mỗi plugin tồn tại
- Mỗi plugin có .claude-plugin/plugin.json

Exit 0: pass. Exit 1: có error.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

REQUIRED_PLUGIN_FIELDS = {"name", "description", "author", "source", "category"}


def main():
    errors = []

    # 1. Parse marketplace.json
    if not MARKETPLACE.exists():
        print(f"ERROR: {MARKETPLACE.relative_to(ROOT)} không tồn tại", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: marketplace.json parse lỗi: {e}", file=sys.stderr)
        sys.exit(1)

    plugins = data.get("plugins", [])
    if not plugins:
        print("ERROR: marketplace.json không có plugins[]", file=sys.stderr)
        sys.exit(1)

    # 2. Validate từng plugin entry
    for p in plugins:
        name = p.get("name", "<unknown>")

        # Required fields
        missing = REQUIRED_PLUGIN_FIELDS - set(p.keys())
        if missing:
            errors.append(f"  {name}: thiếu field {sorted(missing)}")
            continue

        # Source path tồn tại
        source = p["source"]
        if source.startswith("./"):
            source_path = ROOT / source[2:]
        else:
            source_path = ROOT / source

        if not source_path.is_dir():
            errors.append(f"  {name}: source '{source}' không tồn tại")
            continue

        # plugin.json tồn tại
        plugin_json = source_path / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            errors.append(f"  {name}: thiếu .claude-plugin/plugin.json")
            continue

        # plugin.json parse được
        try:
            plugin_data = json.loads(plugin_json.read_text(encoding="utf-8"))
            if "name" not in plugin_data:
                errors.append(f"  {name}: plugin.json thiếu field 'name'")
        except json.JSONDecodeError as e:
            errors.append(f"  {name}: plugin.json parse lỗi: {e}")

    # 3. Kiểm tra plugins/ trên disk có trong marketplace không
    plugins_dir = ROOT / "plugins"
    listed_names = {p["name"] for p in plugins}
    if plugins_dir.is_dir():
        for plugin_dir in plugins_dir.iterdir():
            if plugin_dir.is_dir() and plugin_dir.name not in listed_names:
                errors.append(
                    f"  {plugin_dir.name}: có trong plugins/ nhưng không có trong marketplace.json"
                )

    if errors:
        print(f"{len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        sys.exit(1)

    print(f"marketplace.json valid — {len(plugins)} plugins OK")
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
