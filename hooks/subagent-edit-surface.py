#!/usr/bin/env python3
"""PostToolUse(Agent) hook (PROTOTYPE): surface git diff sau khi subagent xong.

Mục tiêu: tự động hoá rules/verification.md §Subagents (git-state-verify) — sau
khi subagent (Agent tool) trả về, đưa working-tree diff vào context MAIN agent để
nó verify edit thật, thay vì tin self-report của subagent.

Cơ chế: PostToolUse matcher "Agent" → `git diff --stat HEAD` → trả
`additionalContext` (hooks docs: PostToolUse hỗ trợ additionalContext; tool spawn
subagent tên là "Agent" — tools-reference).

⚠️ GIỚI HẠN (prototype — cần test thật trước khi tin tưởng):
- Chỉ đúng cho FOREGROUND Agent: background subagent trả ngay → diff chưa có edit.
- Subagent `isolation: worktree`: edit ở worktree riêng → KHÔNG hiện trong diff main.
- `git diff --stat HEAD` gồm CẢ uncommitted có sẵn từ trước (không tách riêng edit
  của subagent) → nhiễu nhẹ. Bản proper cần PreToolUse(Agent) snapshot + delta.
- Fail-safe exit 0 ở mọi lỗi (hook không bao giờ làm hỏng session).
"""

from __future__ import annotations

import json
import subprocess
import sys

MAX_STAT_CHARS = 6000  # cắt cho an toàn (hookoutput cap 10k; chừa chỗ cho message)


def main() -> int:
    try:
        obj = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    if not isinstance(obj, dict):
        return 0
    # Chỉ xử lý Agent tool (phòng khi matcher rộng hơn dự kiến).
    if obj.get("tool_name") != "Agent":
        return 0
    cwd = obj.get("cwd") or "."
    try:
        proc = subprocess.run(
            ["git", "-C", cwd, "diff", "--stat", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return 0  # không phải git repo / git lỗi → im lặng
    stat = (proc.stdout or "").strip()
    if not stat:
        return 0  # không có uncommitted change → không nhắc
    if len(stat) > MAX_STAT_CHARS:
        stat = stat[:MAX_STAT_CHARS] + "\n… (truncated — chạy `git diff --stat HEAD`)"
    msg = (
        "§Subagent git-state-verify: subagent (Agent) vừa trả về. Working-tree "
        "đang có uncommitted changes dưới đây — VERIFY chúng khớp với edit subagent "
        "báo cáo (đừng tin self-report; xem `git diff HEAD -- <file>` để biết chi "
        "tiết). Lưu ý: stat gồm cả thay đổi có sẵn từ trước; subagent "
        "background/worktree-isolation có thể không hiện ở đây.\n" + stat
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": msg,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
