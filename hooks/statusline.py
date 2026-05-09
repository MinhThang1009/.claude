#!/usr/bin/env python3
"""Statusline cho Claude Code — full info display.

Hiển thị 2 dòng:
- Line 1: [model + window + effort] | 📁 cwd | 🌿 git branch + staged/modified
- Line 2: icon + progress bar + ctx% (tokens) | 💰 cost | ⏱️ duration | 5h/7d rate limits

Ngưỡng icon (multi-author, xem docs/REFERENCE.md §16):
- <40%   🟢 sweet spot (Dex Horthy)
- 40-60% 🟡 dumb zone bắt đầu
- 60-80% 🟠 wrap up actively
- >80%   🔴 PHẢI act (gần auto-compact ~77%)

JSON input từ stdin theo doc: https://code.claude.com/docs/en/statusline
Git status cached 5s qua session_id (theo doc dòng 790).
"""
import json
import os
import subprocess
import sys
import time

CACHE_MAX_AGE = 5  # seconds

# ANSI color codes (terminal must support — git bash + Windows Terminal OK)
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ORANGE = "\033[91m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    model = data.get("model", {}).get("display_name", "?")
    cwd = data.get("workspace", {}).get("current_dir", "")
    ctx = data.get("context_window") or {}
    pct = int(ctx.get("used_percentage") or 0)
    window_size = ctx.get("context_window_size") or 200000
    total_input = ctx.get("total_input_tokens") or 0
    cost = data.get("cost") or {}
    cost_usd = cost.get("total_cost_usd") or 0
    duration_ms = cost.get("total_duration_ms") or 0
    session_id = data.get("session_id") or "default"
    effort = (data.get("effort") or {}).get("level")
    rate = data.get("rate_limits") or {}
    five_h = (rate.get("five_hour") or {}).get("used_percentage")
    seven_d = (rate.get("seven_day") or {}).get("used_percentage")

    # Threshold icon + progress bar color (align REFERENCE.md §16.2)
    if pct >= 90:
        icon, bar_color = "⛔", RED      # Hard limit — DỪNG task lớn
    elif pct >= 77:
        icon, bar_color = "🔴", RED      # Auto-compact firing (155k/200k per Boris X)
    elif pct >= 60:
        icon, bar_color = "🟠", ORANGE   # Wrap up actively
    elif pct >= 40:
        icon, bar_color = "🟡", YELLOW   # "Dumb zone" bắt đầu
    else:
        icon, bar_color = "🟢", GREEN    # Sweet spot / Aggressive zone

    # Skip window label nếu model display_name đã chứa (vd "Opus 4.7 (1M context)")
    if window_size >= 1_000_000 and "1m" not in model.lower():
        window_part = " 1M"
    else:
        window_part = ""
    effort_label = f" ⚡{effort}" if effort else ""
    cwd_short = os.path.basename(cwd) if cwd else ""

    # Line 1: model + cwd + git
    branch, staged, modified = _git_info_cached(session_id, cwd)
    line1 = [f"{CYAN}[{model}{window_part}{effort_label}]{RESET}"]
    if cwd_short:
        line1.append(f"📁 {cwd_short}")
    if branch:
        git_status = f"🌿 {branch}"
        if staged:
            git_status += f" {GREEN}+{staged}{RESET}"
        if modified:
            git_status += f" {YELLOW}~{modified}{RESET}"
        line1.append(git_status)
    print(" | ".join(line1))

    # Line 2: progress bar + ctx + cost + duration + rate limits
    # Bar min 1 cell khi pct>0 để không trống hoàn toàn ở zone <10%
    filled = max(1, pct // 10) if pct > 0 else 0
    bar = "▰" * filled + "▱" * (10 - filled)
    line2 = [f"{icon} {bar_color}{bar}{RESET} {pct}%"]
    if total_input:
        line2.append(f"{DIM}{total_input // 1000}k tokens{RESET}")
    if cost_usd > 0:
        line2.append(f"💰 ${cost_usd:.2f}")
    if duration_ms > 0:
        total_secs = duration_ms // 1000
        if total_secs >= 3600:
            line2.append(f"⏱️ {total_secs // 3600}h{(total_secs % 3600) // 60}m")
        elif total_secs >= 60:
            line2.append(f"⏱️ {total_secs // 60}m {total_secs % 60}s")
        else:
            line2.append(f"⏱️ {total_secs}s")
    if five_h is not None:
        line2.append(f"5h:{five_h:.0f}%")
    if seven_d is not None:
        line2.append(f"7d:{seven_d:.0f}%")
    print(" | ".join(line2))


def _git_info_cached(session_id: str, cwd: str) -> tuple[str, int, int]:
    """Cache git info 5s qua session_id (doc dòng 790: stable per session, unique cross sessions)."""
    cache_dir = os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp"
    cache_file = os.path.join(cache_dir, f"claude-statusline-git-{session_id}")

    if os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) <= CACHE_MAX_AGE:
            try:
                with open(cache_file, encoding="utf-8") as f:
                    parts = f.read().strip().split("|")
                if len(parts) == 3:
                    return parts[0], int(parts[1] or 0), int(parts[2] or 0)
            except (OSError, ValueError):
                pass

    branch, staged, modified = _git_info(cwd)
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(f"{branch}|{staged}|{modified}")
    except OSError:
        pass
    return branch, staged, modified


def _git_info(cwd: str) -> tuple[str, int, int]:
    """Run git, return (branch, staged_count, modified_count). Silent fail nếu không phải repo."""
    if not cwd or not os.path.isdir(cwd):
        return "", 0, 0

    def _run(args: list[str]) -> str:
        try:
            r = subprocess.run(
                args, cwd=cwd, capture_output=True, text=True, timeout=2,
            )
            return r.stdout.strip() if r.returncode == 0 else ""
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            return ""

    if not _run(["git", "rev-parse", "--git-dir"]):
        return "", 0, 0

    branch = _run(["git", "branch", "--show-current"])
    staged_out = _run(["git", "diff", "--cached", "--numstat"])
    modified_out = _run(["git", "diff", "--numstat"])
    staged = len([l for l in staged_out.split("\n") if l])
    modified = len([l for l in modified_out.split("\n") if l])
    return branch, staged, modified


if __name__ == "__main__":
    main()
