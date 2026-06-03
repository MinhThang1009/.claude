#!/usr/bin/env python3
"""Stop hook: nhắc spawn fresh reviewer khi tích lũy nhiều Edit chưa review.

Đếm số Edit/Write/MultiEdit kể từ lần delegate (Agent/Task) gần nhất trong
transcript. Vượt ngưỡng → in nhắc (non-blocking) theo rules/verification.md
§Self-Review Bias. KHÔNG block — chỉ gợi ý; fail-safe exit 0 ở mọi lỗi để
hook không bao giờ làm hỏng session.
"""

from __future__ import annotations

import json
import re
import sys

# Đếm edit là proxy deterministic — hook không tự phán được "risk-bearing".
# Rule thật (§Self-Review Bias) là risk-based: >5 edit chỉ là 1 signal để NHẮC;
# agent tự đánh giá batch có risk-bearing không (shared/logic-bearing, behavior).
EDIT_THRESHOLD = 5
EDIT_TOOLS = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})
# Agent/Task = đã delegate sang subagent (fresh context) → reset bộ đếm.
RESET_TOOLS = frozenset({"Agent", "Task"})
# Artifact HIGH-STAKES (verification.md §Self-Review Bias): sửa xong PHẢI independent-validate
# TRƯỚC khi tuyên done. Path-match deterministic (đóng root-cause "quên rule").
HIGH_STAKES_RE = re.compile(r"(handoff|plan|audit|checklist)", re.IGNORECASE)


def iter_tool_names(transcript_path: str):
    """Yield tên mỗi tool_use theo thứ tự trong transcript JSONL.

    Schema transcript không được Anthropic công bố đầy đủ → duyệt linh hoạt và
    bỏ qua dòng/parse lỗi thay vì crash (hook không được làm hỏng session).
    """
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
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


def high_stakes_edit_since_delegate(transcript_path: str) -> bool:
    """True nếu có Edit/Write tới artifact HIGH-STAKES (handoff/plan/audit) kể từ lần
    delegate (Agent/Task) gần nhất → cần independent validation TRƯỚC khi tuyên done.
    Self-contained + fail-safe (False ở mọi lỗi) để hook không làm hỏng session."""
    flagged = False
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return False
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
        message = obj.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for item in content:
            if not (isinstance(item, dict) and item.get("type") == "tool_use"):
                continue
            name = item.get("name")
            if name in RESET_TOOLS:
                flagged = False  # đã delegate sang fresh agent → reset
            elif name in EDIT_TOOLS:
                inp = item.get("input")
                fp = inp.get("file_path", "") if isinstance(inp, dict) else ""
                if isinstance(fp, str) and HIGH_STAKES_RE.search(fp):
                    flagged = True
    return flagged


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
    nudges = []
    # HIGH-STAKES artifact (handoff/plan/audit) sửa mà chưa delegate → nudge mạnh (L4 fix).
    if high_stakes_edit_since_delegate(transcript_path):
        nudges.append(
            "⚠️ §Self-Review Bias (HIGH-STAKES): đã sửa artifact handoff/plan/audit kể từ lần "
            "delegate gần nhất mà CHƯA dispatch fresh agent. TRƯỚC khi tuyên done/ready: PHẢI "
            "spawn fresh agent (zero history, KHÔNG đưa conclusions/ref-list) verify từng "
            "reference vs disk per rules/verification.md §Self-Review Bias. KHÔNG self-certify."
        )
    if edits > EDIT_THRESHOLD:
        nudges.append(
            f"⚠️ §Self-Review Bias: {edits} edit kể từ lần delegate gần nhất, chưa fresh-agent "
            "review. Nếu batch risk-bearing (shared/logic-bearing, behavior change) → dispatch "
            "subagent review thay vì tự kiểm."
        )
    if nudges:
        # systemMessage = nhắc non-blocking, hiện cho user. Không block stop.
        print(json.dumps({"systemMessage": "\n".join(nudges)}))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
