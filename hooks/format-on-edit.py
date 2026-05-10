#!/usr/bin/env python3
"""Format file sau khi Edit/Write/MultiEdit.

- Skip nếu file ngoài CLAUDE_PROJECT_DIR (tránh ghi vào file system khác).
- Skip prettier nếu có config .js/.cjs/.mjs hoặc plugin reference trong package.json
  (RCE risk: prettier load qua require() khi format chạy).
- Silent skip nếu formatter chưa cài.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PRETTIER_EXTS = frozenset(
    {
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".json",
        ".md",
        ".yml",
        ".yaml",
        ".css",
        ".scss",
        ".html",
    }
)

RISKY_PRETTIER_CONFIGS = (
    ".prettierrc.js",
    ".prettierrc.cjs",
    ".prettierrc.mjs",
    "prettier.config.js",
    "prettier.config.cjs",
    "prettier.config.mjs",
)

PLUGIN_PATTERN = re.compile(r'(@prettier/plugin-|prettier-plugin-|"plugins"\s*:\s*\[)')


def parse_input(data: str) -> str | None:
    """Parse JSON stdin, trả về file_path hoặc None nếu thiếu/invalid."""
    try:
        obj = json.loads(data or "{}")
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    tool_input = obj.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return None
    file_path = tool_input.get("file_path", "")
    if not isinstance(file_path, str) or not file_path:
        return None
    return file_path


def resolve_in_project(project_dir: str, file_path: str) -> str | None:
    """Resolve absolute paths. Trả về resolved target hoặc None nếu file ngoài project."""
    try:
        proj = os.path.realpath(project_dir)
        target = os.path.realpath(file_path)
        rel = os.path.relpath(target, proj)
    except (ValueError, OSError):
        # ValueError xảy ra trên Windows khi paths khác drive
        return None
    if rel.startswith(".."):
        return None
    return target


def has_risky_prettier_config(project_dir: str) -> bool:
    """Detect prettier config có RCE risk qua require() execution."""
    proj = Path(project_dir)
    for name in RISKY_PRETTIER_CONFIGS:
        if (proj / name).is_file():
            return True
    pkg_json = proj / "package.json"
    if not pkg_json.is_file():
        return False
    try:
        content = pkg_json.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return bool(PLUGIN_PATTERN.search(content))


def run_formatter(cmd: list[str], cwd: str | None = None) -> None:
    """Chạy formatter, silent skip nếu binary chưa cài."""
    if shutil.which(cmd[0]) is None:
        return
    subprocess.run(cmd, capture_output=True, check=False, cwd=cwd)


def format_file(file_path: str, project_dir: str) -> None:
    """Dispatch formatter theo extension."""
    ext = Path(file_path).suffix.lower()
    if ext in PRETTIER_EXTS:
        trust = os.environ.get("CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG") == "1"
        if has_risky_prettier_config(project_dir) and not trust:
            print(
                "WARN: skipping prettier — executable config hoặc plugin reference "
                "(package.json) is RCE risk via require(). "
                "Set CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG=1 to override.",
                file=sys.stderr,
            )
            return
        run_formatter(["prettier", "--write", file_path], cwd=project_dir)
    elif ext == ".py":
        run_formatter(["ruff", "format", file_path])
    elif ext == ".go":
        run_formatter(["gofmt", "-w", file_path])
    elif ext == ".rs":
        run_formatter(["rustfmt", file_path])


def main() -> int:
    data = sys.stdin.read()
    file_path = parse_input(data)
    if file_path is None:
        return 0
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    resolved = resolve_in_project(project_dir, file_path)
    if resolved is None:
        return 0
    format_file(file_path, project_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
