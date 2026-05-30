#!/usr/bin/env python3
"""Stop hook: nhắc spawn fresh reviewer khi tích lũy nhiều Edit chưa review.

Đếm số Edit/Write/MultiEdit kể từ lần delegate (Agent/Task) gần nhất trong
transcript. Vượt ngưỡng → in nhắc (non-blocking) theo rules/verification.md
§Self-Review Bias. KHÔNG block — chỉ gợi ý; fail-safe exit 0 ở mọi lỗi để
hook không bao giờ làm hỏng session.
"""

from __future__ import annotations

import json
import sys

# Đếm edit là proxy deterministic — hook không tự phán được "risk-bearing".
# Rule thật (§Self-Review Bias) là risk-based: >5 edit chỉ là 1 signal để NHẮC;
# agent tự đánh giá batch có risk-bearing không (shared/logic-bearing, behavior).
EDIT_THRESHOLD = 5
EDIT_TOOLS = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})
# Agent/Task = đã delegate sang subagent (fresh context) → reset bộ đếm.
RESET_TOOLS = frozenset({"Agent", "Task"})


def iter_tool_names(transcript_path: str):
    """Yield tên mỗi tool_use theo thứ tự trong transcript JSONL.

    Schema transcript không được Anthropic công bố đầy đủ → duyệt linh hoạt và
    bỏ qua dòng/parse lỗi thay vì crash (hook không được làm hỏng session).
    """
    try:
        with open(transcript_path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        # Tool call nằm trong message.content[] với type == "tool_use".
        message = obj.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                name = item.get("name")
                if isinstance(name, str):
                    yield name


def count_edits_since_review(transcript_path: str) -> int:
    """Đếm Edit tích lũy kể từ lần delegate (Agent/Task) gần nhất."""
    count = 0
    for name in iter_tool_names(transcript_path):
        if name in RESET_TOOLS:
            count = 0
        elif name in EDIT_TOOLS:
            count += 1
    return count


def main() -> int:
    try:
        obj = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    if not isinstance(obj, dict):
        return 0
    # Stop hook tự convert sang SubagentStop khi subagent kết thúc (hooks docs).
    # Nudge này dành cho MAIN agent (spawn fresh reviewer); subagent không spawn
    # được subagent → skip để tránh nudge thừa trong context subagent.
    if obj.get("hook_event_name") == "SubagentStop":
        return 0
    # Nếu chính hook này đã giữ session chạy tiếp → không lặp lại.
    if obj.get("stop_hook_active"):
        return 0
    transcript_path = obj.get("transcript_path")
    if not isinstance(transcript_path, str) or not transcript_path:
        return 0
    edits = count_edits_since_review(transcript_path)
    if edits > EDIT_THRESHOLD:
        msg = (
            f"⚠️ §Self-Review Bias: {edits} edit kể từ lần delegate gần nhất, "
            "chưa fresh-agent review. Nếu đây là batch risk-bearing (shared/"
            "logic-bearing file, behavior change), dispatch một subagent mới để "
            "review thay vì tự kiểm (rules/verification.md §Self-Review Bias)."
        )
        # systemMessage = nhắc non-blocking, hiện cho user. Không block stop.
        print(json.dumps({"systemMessage": msg}))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
