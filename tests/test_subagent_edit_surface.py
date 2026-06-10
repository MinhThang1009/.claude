"""Tests cho hooks/subagent-edit-surface.py (PostToolUse(Agent) surface git diff)."""

from __future__ import annotations

import io
import json
import subprocess
import unittest.mock as mock


def run_main(module, stdin_data: str, run_side_effect=None, stdout_value=None):
    """Chạy main() với stdin giả + subprocess.run giả, trả (exit_code, stdout)."""
    captured_stdout = io.StringIO()

    def fake_run(*args, **kwargs):
        if run_side_effect is not None:
            raise run_side_effect
        proc = mock.Mock()
        proc.stdout = stdout_value
        return proc

    with (
        mock.patch("sys.stdin", io.StringIO(stdin_data)),
        mock.patch("sys.stdout", captured_stdout),
        mock.patch.object(module.subprocess, "run", fake_run),
    ):
        code = module.main()
    return code, captured_stdout.getvalue()


AGENT_EVENT = json.dumps({"tool_name": "Agent", "cwd": "/tmp/repo"})


class TestMain:
    def test_malformed_stdin(self, subagent_edit_surface):
        code, out = run_main(subagent_edit_surface, "{not json")
        assert code == 0 and out == ""

    def test_empty_stdin(self, subagent_edit_surface):
        code, out = run_main(subagent_edit_surface, "", stdout_value="x | 1 +")
        assert code == 0 and out == ""

    def test_non_dict_stdin(self, subagent_edit_surface):
        code, out = run_main(subagent_edit_surface, "[1]")
        assert code == 0 and out == ""

    def test_other_tool_skipped(self, subagent_edit_surface):
        code, out = run_main(
            subagent_edit_surface,
            json.dumps({"tool_name": "Edit"}),
            stdout_value="x | 1 +",
        )
        assert code == 0 and out == ""

    def test_git_oserror_silent(self, subagent_edit_surface):
        code, out = run_main(
            subagent_edit_surface, AGENT_EVENT, run_side_effect=OSError("no git")
        )
        assert code == 0 and out == ""

    def test_git_timeout_silent(self, subagent_edit_surface):
        code, out = run_main(
            subagent_edit_surface,
            AGENT_EVENT,
            run_side_effect=subprocess.TimeoutExpired(cmd="git", timeout=10),
        )
        assert code == 0 and out == ""

    def test_empty_diff_no_output(self, subagent_edit_surface):
        code, out = run_main(subagent_edit_surface, AGENT_EVENT, stdout_value="  \n")
        assert code == 0 and out == ""

    def test_none_stdout_no_output(self, subagent_edit_surface):
        code, out = run_main(subagent_edit_surface, AGENT_EVENT, stdout_value=None)
        assert code == 0 and out == ""

    def test_diff_surfaced_as_additional_context(self, subagent_edit_surface):
        stat = " app.py | 3 +++"
        code, out = run_main(subagent_edit_surface, AGENT_EVENT, stdout_value=stat)
        assert code == 0
        payload = json.loads(out)["hookSpecificOutput"]
        assert payload["hookEventName"] == "PostToolUse"
        assert stat.strip() in payload["additionalContext"]

    def test_missing_cwd_defaults_to_dot(self, subagent_edit_surface):
        code, out = run_main(
            subagent_edit_surface,
            json.dumps({"tool_name": "Agent"}),
            stdout_value=" app.py | 1 +",
        )
        assert code == 0
        assert "additionalContext" in out

    def test_long_diff_truncated(self, subagent_edit_surface):
        stat = "x" * (subagent_edit_surface.MAX_STAT_CHARS + 100)
        code, out = run_main(subagent_edit_surface, AGENT_EVENT, stdout_value=stat)
        assert code == 0
        ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
        assert "truncated" in ctx
