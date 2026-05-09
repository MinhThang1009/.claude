"""Unit tests cho hooks/statusline.py — main + git helpers.

Catch các bug đã từng gặp:
- Path display "~l" (home substitution buggy) — dùng basename giờ.
- E741 ambiguous `l` variable.
- Missing space giữa icon và bar.
"""

from __future__ import annotations

import io
import json
import sys
from unittest.mock import patch


def _run_main(statusline_module, input_data: dict) -> str:
    """Run statusline.main() với mock stdin → return stdout text."""
    stdin_str = json.dumps(input_data)
    with patch("sys.stdin", io.StringIO(stdin_str)):
        with patch("sys.stdout", new_callable=io.StringIO) as fake_stdout:
            try:
                statusline_module.main()
            except SystemExit:
                pass
            return fake_stdout.getvalue()


class TestThresholds:
    def test_sweet_spot_green(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t1",
                "model": {"display_name": "Opus 4.7"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 17},
            },
        )
        assert "🟢" in out
        assert "17%" in out

    def test_dumb_zone_yellow(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t2",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 50},
            },
        )
        assert "🟡" in out
        assert "50%" in out

    def test_wrap_up_orange(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t3",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 65},
            },
        )
        assert "🟠" in out

    def test_auto_compact_red(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t4",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 80},
            },
        )
        assert "🔴" in out

    def test_hard_limit_block(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t5",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 92},
            },
        )
        assert "⛔" in out


class TestPathDisplay:
    def test_basename_short(self, statusline):
        # Bug class: trước dùng home substitution "~l" — giờ basename returns "Admin"
        out = _run_main(
            statusline,
            {
                "session_id": "t6",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "C:\\Users\\Admin"},
                "context_window": {"used_percentage": 5},
            },
        )
        assert "Admin" in out
        assert "~l" not in out

    def test_unix_path(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t7",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/home/user/project"},
                "context_window": {"used_percentage": 5},
            },
        )
        assert "project" in out

    def test_empty_cwd(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t8",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": ""},
                "context_window": {"used_percentage": 5},
            },
        )
        assert "📁" not in out


class TestModelLabel:
    def test_window_label_skip_when_in_name(self, statusline):
        # "Opus 4.7 (1M context)" đã chứa "1M" → không append duplicate
        out = _run_main(
            statusline,
            {
                "session_id": "t9",
                "model": {"display_name": "Opus 4.7 (1M context)"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {
                    "used_percentage": 5,
                    "context_window_size": 1_000_000,
                },
            },
        )
        # Chỉ 1 lần "1M" trong output (từ display_name), không có duplicate " 1M"
        # Tách ANSI escape khỏi count
        import re

        clean = re.sub(r"\x1b\[[0-9;]*m", "", out)
        assert clean.count("1M") == 1

    def test_window_label_added_for_1m_without_name(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t10",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {
                    "used_percentage": 5,
                    "context_window_size": 1_000_000,
                },
            },
        )
        assert " 1M" in out

    def test_no_window_label_for_200k(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t11",
                "model": {"display_name": "Opus 4.7"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {
                    "used_percentage": 5,
                    "context_window_size": 200_000,
                },
            },
        )
        assert "200k" not in out
        assert " 1M" not in out


class TestEffortLabel:
    def test_effort_xhigh(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t12",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
                "effort": {"level": "xhigh"},
            },
        )
        assert "⚡" in out
        assert "xhigh" in out

    def test_no_effort_when_absent(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t13",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
            },
        )
        assert "⚡" not in out


class TestDurationFormat:
    def test_seconds_only(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t14",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
                "cost": {"total_duration_ms": 7000},
            },
        )
        # Strip ANSI escapes (vd \x1b[0m) trước khi assert vì chứa "0m"
        import re

        clean = re.sub(r"\x1b\[[0-9;]*m", "", out)
        assert "7s" in clean
        # Không có "0m" prefix duration (ANSI đã strip)
        assert "0m" not in clean

    def test_minutes_seconds(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t15",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
                "cost": {"total_duration_ms": 65000},
            },
        )
        assert "1m" in out and "5s" in out

    def test_hours_minutes(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t16",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
                "cost": {"total_duration_ms": 3700000},
            },
        )
        assert "1h" in out

    def test_no_duration_when_zero(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t17",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
                "cost": {"total_duration_ms": 0},
            },
        )
        assert "⏱" not in out


class TestProgressBar:
    def test_min_one_cell_when_pct_positive(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t18",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 4},
            },
        )
        # Bar có ít nhất 1 ô filled (▰) khi pct > 0
        assert "▰" in out

    def test_zero_cell_when_pct_zero(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t19",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 0},
            },
        )
        # Bar 100% empty (▱) khi pct = 0
        assert "▰" not in out

    def test_full_bar_at_100(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t20",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 100},
            },
        )
        # 10 ô filled, 0 empty
        assert "▰" * 10 in out


class TestNullSafety:
    def test_used_percentage_null(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t21",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": None},
            },
        )
        assert "0%" in out

    def test_missing_fields(self, statusline):
        out = _run_main(statusline, {"session_id": "t22"})
        # Không crash, output có default model "?"
        assert "?" in out


class TestRateLimits:
    def test_5h_7d_displayed(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t23",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
                "rate_limits": {
                    "five_hour": {"used_percentage": 23},
                    "seven_day": {"used_percentage": 41},
                },
            },
        )
        assert "5h:23%" in out
        assert "7d:41%" in out

    def test_no_rate_limits_when_absent(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t24",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
            },
        )
        assert "5h:" not in out
        assert "7d:" not in out
