#!/usr/bin/env python3
"""Validate JSON files declaring `$schema` field against their schema.

Skip silently nếu file không có `$schema`. Fail nếu schema URL fetch fail
hoặc validation fail. Cache schemas trong tempdir để không fetch lại
trong cùng run.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

# Force UTF-8 stdout/stderr cho Windows cp1252.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import jsonschema
except ImportError:
    print(
        "ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr
    )
    sys.exit(2)

SCHEMA_CACHE_DIR = Path(tempfile.gettempdir()) / "dotclaude-schema-cache"
SCHEMA_CACHE_DIR.mkdir(exist_ok=True)


def fetch_schema(url: str) -> dict:
    """Fetch schema, cache trong tempdir."""
    cache_key = url.replace("/", "_").replace(":", "_")
    cache_file = SCHEMA_CACHE_DIR / cache_key
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    with urllib.request.urlopen(url, timeout=20) as r:
        body = r.read().decode("utf-8")
    cache_file.write_text(body, encoding="utf-8")
    return json.loads(body)


def find_json_files(root: Path) -> list[Path]:
    """Find all JSON files tracked by git (excluding cspell/markdownlint configs)."""
    skip_files = {"cspell.json", ".cspell.json"}
    skip_dirs = {".git", "node_modules", "__pycache__"}
    out: list[Path] = []
    for p in root.rglob("*.json"):
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.name in skip_files:
            continue
        out.append(p)
    return out


def validate_file(path: Path) -> tuple[bool, str]:
    """Return (ok, message). Skip files without `$schema` (return ok=True)."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {e}"
    if not isinstance(data, dict):
        return True, "skip (not object)"
    schema_url = data.get("$schema")
    if not schema_url:
        return True, "skip (no $schema)"
    if not schema_url.startswith(("http://", "https://")):
        return True, f"skip (schema url not http: {schema_url})"
    try:
        schema = fetch_schema(schema_url)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        return False, f"fetch schema fail: {e}"
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        return False, f"schema validation fail: {e.message} (at {list(e.path)})"
    return True, f"valid against {schema_url}"


def main() -> int:
    root = Path(os.environ.get("GITHUB_WORKSPACE") or ".").resolve()
    files = find_json_files(root)
    fails = 0
    checked = 0
    for f in files:
        rel = f.relative_to(root)
        ok, msg = validate_file(f)
        if "skip" in msg:
            continue
        checked += 1
        if ok:
            print(f"OK  {rel} — {msg}")
        else:
            print(f"FAIL {rel} — {msg}", file=sys.stderr)
            fails += 1
    if checked == 0:
        print("No JSON files với $schema field. Skip.")
        return 0
    print(f"\nValidated {checked} files, {fails} failures.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
