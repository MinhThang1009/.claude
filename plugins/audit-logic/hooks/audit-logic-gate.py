#!/usr/bin/env python3
"""Stop hook: block khi audit-logic phase gates chưa hoàn tất.

State file: ${CLAUDE_PROJECT_DIR}/.claude/audit-logic-state.json
  {"findings_confirmed": false, "phase4_gate": false, "phase5_gate": false, "phase6_gate": false, "phase7_gate": false}
  (JSON shape canonical: SKILL.md Phase 1 step 4 — nếu hai bên lệch, SKILL.md wins.)

- File không tồn tại  → không đang chạy audit-logic → allow (exit 0)
- File tồn tại, gates chưa done → block (exit 2, print reminder)
- File tồn tại, tất cả done → allow (exit 0, kèm nhắc xóa file — Phase 7 step 3)

Fail-safe: mọi lỗi parse/IO đều exit 0 (không block session).
"""

import json
import os
import sys


def main() -> int:
    try:
        obj = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
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
    state_file = os.path.join(project_dir, ".claude", "audit-logic-state.json")

    if not os.path.exists(state_file):
        return 0  # Không đang chạy audit-logic

    try:
        # utf-8-sig: chấp nhận cả file có BOM (PowerShell/notepad trên Windows
        # dễ thêm BOM khi user sửa tay) — BOM với utf-8 thuần gây JSONDecodeError
        # → fail-safe exit 0 → gate âm thầm tắt.
        # Lưu ý: file UTF-16 (mặc định của redirect `>` trên Windows PowerShell 5.1)
        # vẫn fail parse → fail-open (exit 0) đúng thiết kế fail-safe; test suite
        # có case UTF-16LE ghi nhận hành vi này.
        with open(state_file, encoding="utf-8-sig") as f:
            state = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return 0  # Lỗi đọc file → không block
    if not isinstance(state, dict):
        return 0  # JSON hợp lệ nhưng không phải object → fail-safe, không block

    # Gate chỉ được coi là đóng khi giá trị là JSON true đúng nghĩa —
    # string "true"/"false" (malformed) đều tính là chưa đóng.
    GATE_LABELS = (
        (
            "phase4_gate",
            "Phase 4 Exit Gate  (completeness check - document all dismissed findings)",
        ),
        (
            "phase5_gate",
            "Phase 5 Exit Gate  (verification agent + full test suite + 1 commit/bug)",
        ),
        ("phase6_gate", "Phase 6 Exit Gate  (stale documentation update)"),
        (
            "phase7_gate",
            "Phase 7 Exit Gate  (summary + /pipeline-retrospective + delete state file)",
        ),
    )
    missing = [
        (gate, label) for gate, label in GATE_LABELS if state.get(gate) is not True
    ]

    # Mọi chuỗi message runtime (os.write bên dưới) cố ý KHÔNG dấu (ASCII-only):
    # stderr của hook hiển thị trên console Windows codepage không phải UTF-8
    # (cp1252/cp437) sẽ garble bytes UTF-8 có dấu. Đừng "sửa" thêm dấu vào chúng.
    if missing:
        lines = ["[audit-logic] Gates chua hoan tat - hoan thanh truoc khi ket thuc:"]
        for _, label in missing:
            lines.append(f"  - [ ] {label}")
        lines.append("")
        # Incremental hint: chỉ nhắc gate KẾ TIẾP, dạng single-field —
        # không đưa full-state JSON (copy-paste full state có thể wipe gate đã true
        # hoặc lén đổi findings_confirmed; field đó chỉ Phase 3 + user được set).
        nxt = missing[0][0]
        lines.append(
            f'Sau khi HOAN TAT phase work tuong ung: set "{nxt}": true trong .claude/audit-logic-state.json '
            "(CHI doi field nay - khong dong gate khac, khong doi findings_confirmed)."
        )
        lines.append(
            "Neu dang dung de CHO USER tra loi: in thong bao dang cho va ket thuc luot lan nua "
            "(lan stop thu hai duoc phep). KHONG set gate true chi de qua hook."
        )
        lines.append(
            "Neu KHONG co audit-logic nao dang chay - ke ca o session/cua so khac cua cung project "
            "(state file mo coi tu audit bi bo do truoc do): "
            "xoa .claude/audit-logic-state.json roi ket thuc binh thuong."
        )
        msg = "\n".join(lines) + "\n"
        os.write(
            2, msg.encode("utf-8")
        )  # fd 2 = stderr — hiện trong Stop hook feedback
        return 2  # Block stop

    # Warn (non-blocking): tất cả gates true nhưng user chưa từng confirm findings.
    # Phase 3 yêu cầu explicit confirmation — không có implicit approval.
    if state.get("findings_confirmed") is not True:
        warn = "[audit-logic] WARNING: tat ca gates da true nhung findings chua tung duoc user xac nhan (findings_confirmed: false). Phase 3 yeu cau xac nhan truc tiep - kiem tra lai voi user truoc khi dong audit.\n"
        os.write(2, warn.encode("utf-8"))

    # Nhắc xóa (non-blocking): file đã đóng hết gate là file Phase 7 step 3 quên xóa —
    # không chặn, nhưng nhắc mỗi lần stop để không thành rác vĩnh viễn.
    note = "[audit-logic] Tat ca gates da true - audit da xong. Xoa .claude/audit-logic-state.json (Phase 7 step 3) neu chua xoa.\n"
    os.write(2, note.encode("utf-8"))

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
