#!/usr/bin/env python3
"""Hook: tự động chuyển handoff.md từ project root vào .claude/ của project.

Trigger bởi:
- PostToolUse → Write: khi Write tool ghi file tên handoff.md
- SessionStart: scan project root tìm HANDOFF.md còn sót
"""

import json
import os
import shutil
import sys
from pathlib import Path


def move_to_claude(file_path: Path, project_dir: Path) -> None:
    target = project_dir / ".claude" / "handoff.md"
    try:
        if file_path.resolve() == target.resolve():
            sys.exit(0)
    except OSError:
        pass
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            print(f"[handoff-auto-move] Ghi đè handoff.md cũ tại {target}")
        shutil.move(str(file_path), str(target))
        print(f"Đã tự động chuyển handoff.md -> {target}")
    except (OSError, shutil.Error) as e:
        print(f"[handoff-auto-move] Không thể move file: {e}", file=sys.stderr)
        sys.exit(0)


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

    project_dir_raw = os.environ.get("CLAUDE_PROJECT_DIR", "")
    project_dir = Path(project_dir_raw) if project_dir_raw else None

    # SessionStart: không có file_path → scan project root tìm HANDOFF.md sót lại
    file_path_raw = (
        data.get("tool_input", {}).get("file_path") or data.get("file_path") or ""
    )
    if not file_path_raw:
        if project_dir:
            candidate = project_dir / "HANDOFF.md"
            if candidate.exists():
                move_to_claude(candidate, project_dir)
        sys.exit(0)

    # PostToolUse → Write: xử lý file cụ thể
    file_path = Path(file_path_raw)
    if file_path.name.lower() != "handoff.md":
        sys.exit(0)

    # Fallback về thư mục chứa file nếu không có CLAUDE_PROJECT_DIR
    effective_project_dir = project_dir if project_dir else file_path.parent
    move_to_claude(file_path, effective_project_dir)


if __name__ == "__main__":  # pragma: no cover
    main()
