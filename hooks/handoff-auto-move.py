#!/usr/bin/env python3
"""Hook: tự động chuyển handoff.md từ project root vào .claude/ của project."""

import json
import os
import shutil
import sys
from pathlib import Path


def main() -> None:
    # Windows dùng cp1252 mặc định — reconfigure sang UTF-8 (in-place, không close buffer)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        raw = sys.stdin.buffer.read().decode("utf-8")
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
        sys.exit(0)

    file_path_raw = (
        data.get("tool_input", {}).get("file_path") or data.get("file_path") or ""
    )
    if not file_path_raw:
        sys.exit(0)

    file_path = Path(file_path_raw)
    if file_path.name.lower() != "handoff.md":
        sys.exit(0)

    project_dir_raw = os.environ.get("CLAUDE_PROJECT_DIR", "")
    project_dir = Path(project_dir_raw) if project_dir_raw else file_path.parent

    target = project_dir / ".claude" / "handoff.md"

    # Bỏ qua nếu file đã nằm đúng chỗ
    try:
        if file_path.resolve() == target.resolve():
            sys.exit(0)
    except OSError:
        pass

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(target))
        print(f"Đã tự động chuyển handoff.md -> {target}")
    except (OSError, shutil.Error) as e:
        print(f"[handoff-auto-move] Không thể move file: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
