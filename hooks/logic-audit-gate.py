#!/usr/bin/env python3
"""Stop hook: block khi logic-audit phase gates chưa hoàn tất.

State file: ${CLAUDE_PROJECT_DIR}/.claude/logic-audit-state.json
  {"findings_confirmed": false, "phase4_gate": false, "phase5_gate": false, "phase6_gate": false, "phase7_gate": false}

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
        missing.append("Phase 4 Exit Gate  (completeness check — document all dismissed findings)")
    if not state.get("phase5_gate"):
        missing.append("Phase 5 Exit Gate  (verification agent + full test suite + 1 commit/bug)")
    if not state.get("phase6_gate"):
        missing.append("Phase 6 Exit Gate  (stale documentation update)")
    if not state.get("phase7_gate"):
        missing.append("Phase 7 Exit Gate  (summary + /pipeline-retrospective)")

    if missing:
        lines = ["[logic-audit] Gates chua hoan tat - hoan thanh truoc khi ket thuc:"]
        for m in missing:
            lines.append(f"  - [ ] {m}")
        lines.append("")
        # Incremental hint: chỉ show next gate cần làm — tránh executor
        # copy-paste final state và bỏ qua các phase ở giữa.
        fc = "true" if state.get("findings_confirmed") else "false"
        if not state.get("phase4_gate"):
            hint = f'{{"findings_confirmed": {fc}, "phase4_gate": true, "phase5_gate": false, "phase6_gate": false, "phase7_gate": false}}'
        elif not state.get("phase5_gate"):
            hint = f'{{"findings_confirmed": true, "phase4_gate": true, "phase5_gate": true, "phase6_gate": false, "phase7_gate": false}}'
        elif not state.get("phase6_gate"):
            hint = f'{{"findings_confirmed": true, "phase4_gate": true, "phase5_gate": true, "phase6_gate": true, "phase7_gate": false}}'
        else:
            hint = f'{{"findings_confirmed": true, "phase4_gate": true, "phase5_gate": true, "phase6_gate": true, "phase7_gate": true}}'
        lines.append(f"Cap nhat .claude/logic-audit-state.json -> {hint}")
        msg = "\n".join(lines) + "\n"
        os.write(2, msg.encode("utf-8"))  # fd 2 = stderr — hiện trong Stop hook feedback
        return 2  # Block stop

    # Warn (non-blocking) nếu Phase 5 đã chạy mà user chưa confirm findings
    if state.get("phase5_gate") and not state.get("findings_confirmed"):
        warn = "[logic-audit] WARNING: Phase 5 ran without explicit findings_confirmed. Was this implicit approval? Set findings_confirmed: true in state file if yes.\n"
        os.write(2, warn.encode("utf-8"))

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
