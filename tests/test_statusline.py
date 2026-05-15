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
        assert "5h:" in out
        assert "23%" in out
        assert "7d:" in out
        assert "41%" in out

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


class TestStdinErrors:
    def test_invalid_json_exits(self, statusline):
        with patch("sys.stdin", io.StringIO("not valid json")):
            try:
                statusline.main()
            except SystemExit as e:
                assert e.code == 0


class TestGitInfoDisplay:
    def test_branch_with_staged_and_modified(self, statusline, monkeypatch):
        monkeypatch.setattr(
            statusline, "_git_info_cached", lambda sid, cwd: ("feature/x", 2, 5)
        )
        out = _run_main(
            statusline,
            {
                "session_id": "t-git",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
            },
        )
        assert "feature/x" in out
        assert "+2" in out
        assert "~5" in out

    def test_branch_without_staged_or_modified(self, statusline, monkeypatch):
        monkeypatch.setattr(
            statusline, "_git_info_cached", lambda sid, cwd: ("main", 0, 0)
        )
        out = _run_main(
            statusline,
            {
                "session_id": "t-git2",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
            },
        )
        assert "main" in out
        assert "+" not in out.split("main")[1].split("\n")[0]


class TestTotalInputDisplay:
    def test_total_input_tokens_displayed(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t-tok",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {
                    "used_percentage": 5,
                    "total_input_tokens": 12500,
                },
            },
        )
        assert "12k" in out


class TestCostDisplay:
    def test_cost_usd_displayed(self, statusline):
        out = _run_main(
            statusline,
            {
                "session_id": "t-cost",
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/tmp"},
                "context_window": {"used_percentage": 5},
                "cost": {"total_cost_usd": 1.234, "total_duration_ms": 0},
            },
        )
        assert "$1.23" in out


class TestGitInfoCached:
    def test_cache_hit_returns_cached(self, statusline, tmp_path, monkeypatch):
        monkeypatch.setenv("TEMP", str(tmp_path))
        monkeypatch.setenv("TMPDIR", str(tmp_path))
        cache_file = tmp_path / "claude-statusline-git-test-sess"
        cache_file.write_text("main|3|7", encoding="utf-8")
        # mtime mới (vừa ghi), trong CACHE_MAX_AGE
        branch, staged, modified = statusline._git_info_cached(
            "test-sess", str(tmp_path)
        )
        assert branch == "main"
        assert staged == 3
        assert modified == 7

    def test_cache_stale_recomputes(self, statusline, tmp_path, monkeypatch):
        import os
        import time

        monkeypatch.setenv("TEMP", str(tmp_path))
        monkeypatch.setenv("TMPDIR", str(tmp_path))
        cache_file = tmp_path / "claude-statusline-git-stale-sess"
        cache_file.write_text("old|1|1", encoding="utf-8")
        old = time.time() - 3600
        os.utime(cache_file, (old, old))
        monkeypatch.setattr(statusline, "_git_info", lambda cwd: ("fresh", 9, 9))
        branch, staged, modified = statusline._git_info_cached(
            "stale-sess", str(tmp_path)
        )
        assert branch == "fresh" and staged == 9 and modified == 9

    def test_cache_corrupt_int_value_caught(self, statusline, tmp_path, monkeypatch):
        monkeypatch.setenv("TEMP", str(tmp_path))
        monkeypatch.setenv("TMPDIR", str(tmp_path))
        cache_file = tmp_path / "claude-statusline-git-corrupt-sess"
        # Đủ 3 parts → vào nhánh int() → "abc" raise ValueError → except catch
        cache_file.write_text("main|abc|def", encoding="utf-8")
        monkeypatch.setattr(statusline, "_git_info", lambda cwd: ("recovered", 0, 0))
        branch, _, _ = statusline._git_info_cached("corrupt-sess", str(tmp_path))
        assert branch == "recovered"

    def test_cache_wrong_part_count_falls_through(
        self, statusline, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("TEMP", str(tmp_path))
        monkeypatch.setenv("TMPDIR", str(tmp_path))
        cache_file = tmp_path / "claude-statusline-git-short-sess"
        # 2 parts (không phải 3) → if False → fallthrough không qua except
        cache_file.write_text("only|two", encoding="utf-8")
        monkeypatch.setattr(
            statusline, "_git_info", lambda cwd: ("from-fallback", 0, 0)
        )
        branch, _, _ = statusline._git_info_cached("short-sess", str(tmp_path))
        assert branch == "from-fallback"

    def test_cache_write_failure_silent(self, statusline, tmp_path, monkeypatch):
        monkeypatch.setenv("TEMP", str(tmp_path))
        monkeypatch.setenv("TMPDIR", str(tmp_path))
        monkeypatch.setattr(statusline, "_git_info", lambda cwd: ("ok", 0, 0))
        # Mock open to fail when writing cache file
        real_open = open

        def fake_open(path, *args, **kwargs):
            if "claude-statusline-git" in str(path) and (
                args and args[0] == "w" or kwargs.get("mode") == "w"
            ):
                raise OSError("simulated write fail")
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr("builtins.open", fake_open)
        # Phải không raise — silent fallback
        branch, _, _ = statusline._git_info_cached("write-fail-sess", str(tmp_path))
        assert branch == "ok"


class TestGitInfoActual:
    def test_empty_cwd_returns_empty(self, statusline):
        assert statusline._git_info("") == ("", 0, 0)

    def test_nonexistent_cwd_returns_empty(self, statusline):
        assert statusline._git_info("/nonexistent/path/xyz") == ("", 0, 0)

    def test_non_git_dir_returns_empty(self, statusline, tmp_path):
        # tmp_path không phải git repo
        assert statusline._git_info(str(tmp_path)) == ("", 0, 0)

    def test_subprocess_error_caught(self, statusline, tmp_path, monkeypatch):
        import subprocess

        def raise_err(*args, **kwargs):
            raise subprocess.SubprocessError("simulated")

        monkeypatch.setattr(subprocess, "run", raise_err)
        # Phải không crash, return empty
        assert statusline._git_info(str(tmp_path)) == ("", 0, 0)

    def test_real_git_commands_mocked(self, statusline, tmp_path, monkeypatch):
        import subprocess

        def fake_run(args, **kwargs):
            class R:
                returncode = 0
                stdout = ""

            r = R()
            if "rev-parse" in args:
                r.stdout = ".git\n"
            elif "--show-current" in args:
                r.stdout = "main\n"
            elif "--cached" in args:
                r.stdout = "1\t2\tfile1\n"
            else:  # diff --numstat
                r.stdout = "3\t4\tfile2\n5\t6\tfile3\n"
            return r

        monkeypatch.setattr(subprocess, "run", fake_run)
        branch, staged, modified = statusline._git_info(str(tmp_path))
        assert branch == "main"
        assert staged == 1
        assert modified == 2
