#!/usr/bin/env python3
"""Stop hook: block khi logic-audit phase gates chưa hoàn tất.

State file: ${CLAUDE_PROJECT_DIR}/.claude/logic-audit-state.json
  {"phase4_gate": false, "phase5_gate": false}

- File không tồn tại  → không đang chạy logic-audit → allow (exit 0)
- File tồn tại, gates chưa done → block (exit 2, print reminder)
- File tồn tại, tất cả done → allow (exit 0)

Fail-safe: mọi lỗi parse/IO đều exit 0 (không block session).
"""
from __future__ import annotations

import io
import json
import os
import sys

# Windows cp1252 không encode được emoji/Vietnamese — force UTF-8
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def main() -> int:
    try:
        obj = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    if not isinstance(obj, dict):
        return 0

    # Không block subagent stop
    if obj.get("hook_event_name") == "SubagentStop":
        return 0

    # Nếu hook này đã block lần trước → không lặp lại (tránh infinite loop)
    if obj.get("stop_hook_active"):
        return 0

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    state_file = os.path.join(project_dir, ".claude", "logic-audit-state.json")

    if not os.path.exists(state_file):
        return 0  # Không đang chạy logic-audit

    try:
        with open(state_file, encoding="utf-8") as f:
            state = json.load(f)
    except (json.JSONDecodeError, OSError):
        return 0  # Lỗi đọc file → không block

    missing = []
    if not state.get("phase4_gate"):
        missing.append("Phase 4 Exit Gate  (verification agent + full test suite + 1 commit/bug)")
    if not state.get("phase5_gate"):
        missing.append("Phase 5 Exit Gate  (stale documentation update)")

    if missing:
        lines = ["[logic-audit] Gates chua hoan tat - hoan thanh truoc khi ket thuc:"]
        for m in missing:
            lines.append(f"  - [ ] {m}")
        lines.append("")
        lines.append('Cap nhat .claude/logic-audit-state.json -> {"phase4_gate": true, "phase5_gate": true}')
        msg = "\n".join(lines) + "\n"
        os.write(2, msg.encode("utf-8"))  # fd 2 = stderr — hiện trong Stop hook feedback
        return 2  # Block stop

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
