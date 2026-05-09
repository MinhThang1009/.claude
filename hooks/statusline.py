#!/usr/bin/env python3
"""Statusline cho Claude Code.

Hiển thị: icon (theo ngưỡng % context) + model name + context % + cwd ngắn.

Ngưỡng theo multi-author (xem docs/REFERENCE.md §16):
- <40%   sweet spot (Dex Horthy)
- 40-60% "dumb zone" bắt đầu (Dex Horthy)
- 60-80% wrap up actively (Dex Horthy)
- >80%   PHẢI act, gần auto-compact (Boris Cherny: 155k/200k = ~77.5%)

JSON input từ stdin: {model, workspace, context_window, session_id, ...}.
Doc: https://code.claude.com/docs/en/statusline
"""
import json
import os
import sys


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # statusline blank thay vì error

    model = data.get("model", {}).get("display_name", "?")
    pct = data.get("context_window", {}).get("used_percentage", 0)
    cwd = data.get("workspace", {}).get("current_dir", "")

    if pct >= 80:
        icon = "🔴"
    elif pct >= 60:
        icon = "🟠"
    elif pct >= 40:
        icon = "🟡"
    else:
        icon = "🟢"

    home = os.path.expanduser("~")
    short_cwd = cwd
    if cwd and cwd.startswith(home):
        short_cwd = "~" + cwd[len(home):]

    parts = [f"{icon} {model}", f"ctx:{pct}%"]
    if short_cwd:
        parts.append(short_cwd)
    print(" | ".join(parts))


if __name__ == "__main__":
    main()
