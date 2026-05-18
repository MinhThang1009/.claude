"""Unit tests cho hooks/handoff-auto-move.py."""

from __future__ import annotations

import io
import json
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def run_main(module, stdin_data: dict | str, env: dict | None = None):
    """Chạy main() với stdin giả và env giả, trả về SystemExit code hoặc None."""
    raw = json.dumps(stdin_data) if isinstance(stdin_data, dict) else stdin_data
    raw_bytes = raw.encode("utf-8")
    env = env or {}
    mock_stdin = MagicMock()
    mock_stdin.buffer.read.return_value = raw_bytes
    with patch("sys.stdin", mock_stdin):
        with patch.dict("os.environ", env, clear=False):
            try:
                module.main()
                return None
            except SystemExit as e:
                return e.code


class TestInvalidInput:
    def test_invalid_json_exits_0(self, handoff_auto_move):
        assert run_main(handoff_auto_move, "not json") == 0

    def test_empty_string_exits_0(self, handoff_auto_move):
        assert run_main(handoff_auto_move, "") == 0

    def test_no_file_path_exits_0(self, handoff_auto_move):
        assert run_main(handoff_auto_move, {"other": "field"}) == 0

    def test_empty_file_path_exits_0(self, handoff_auto_move):
        assert run_main(handoff_auto_move, {"file_path": ""}) == 0


class TestFileNameFilter:
    def test_non_handoff_filename_exits_0(self, handoff_auto_move):
        assert run_main(handoff_auto_move, {"file_path": "/some/plan.md"}) == 0

    def test_handoff_lowercase_passes(self, handoff_auto_move, tmp_path):
        src = tmp_path / "handoff.md"
        src.write_text("content")
        result = run_main(handoff_auto_move, {"file_path": str(src)})
        assert result is None

    def test_handoff_uppercase_passes(self, handoff_auto_move, tmp_path):
        src = tmp_path / "HANDOFF.md"
        src.write_text("content")
        result = run_main(handoff_auto_move, {"file_path": str(src)})
        assert result is None


class TestFilePathSources:
    def test_reads_from_tool_input(self, handoff_auto_move, tmp_path):
        src = tmp_path / "handoff.md"
        src.write_text("x")
        data = {"tool_input": {"file_path": str(src)}}
        result = run_main(handoff_auto_move, data)
        assert result is None

    def test_reads_from_root_file_path(self, handoff_auto_move, tmp_path):
        src = tmp_path / "handoff.md"
        src.write_text("x")
        result = run_main(handoff_auto_move, {"file_path": str(src)})
        assert result is None


class TestAlreadyInTarget:
    def test_file_already_in_claude_dir_exits_0(self, handoff_auto_move, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        target = claude_dir / "handoff.md"
        target.write_text("content")
        result = run_main(
            handoff_auto_move,
            {"file_path": str(target)},
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result == 0


class TestProjectDirResolution:
    def test_uses_claude_project_dir_env(self, handoff_auto_move, tmp_path):
        project = tmp_path / "project"
        project.mkdir()
        src = project / "handoff.md"
        src.write_text("brief")
        result = run_main(
            handoff_auto_move,
            {"file_path": str(src)},
            env={"CLAUDE_PROJECT_DIR": str(project)},
        )
        assert result is None
        assert (project / ".claude" / "handoff.md").exists()

    def test_falls_back_to_parent_dir_when_no_env(self, handoff_auto_move, tmp_path):
        src = tmp_path / "handoff.md"
        src.write_text("brief")
        with patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": ""}, clear=False):
            result = run_main(handoff_auto_move, {"file_path": str(src)})
        assert result is None
        assert (tmp_path / ".claude" / "handoff.md").exists()


class TestMoveSuccess:
    def test_moves_file_to_claude_dir(self, handoff_auto_move, tmp_path, capsys):
        src = tmp_path / "handoff.md"
        src.write_text("session brief")
        run_main(
            handoff_auto_move,
            {"file_path": str(src)},
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert not src.exists()
        assert (tmp_path / ".claude" / "handoff.md").read_text() == "session brief"

    def test_creates_claude_dir_if_missing(self, handoff_auto_move, tmp_path):
        src = tmp_path / "handoff.md"
        src.write_text("x")
        assert not (tmp_path / ".claude").exists()
        run_main(
            handoff_auto_move,
            {"file_path": str(src)},
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert (tmp_path / ".claude").is_dir()

    def test_prints_confirmation(self, handoff_auto_move, tmp_path, capsys):
        src = tmp_path / "handoff.md"
        src.write_text("x")
        run_main(
            handoff_auto_move,
            {"file_path": str(src)},
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert "handoff.md" in capsys.readouterr().out


class TestMoveFailure:
    def test_move_error_prints_stderr_and_exits_0(
        self, handoff_auto_move, tmp_path, capsys
    ):
        src = tmp_path / "handoff.md"
        src.write_text("x")
        with patch("shutil.move", side_effect=OSError("disk full")):
            result = run_main(
                handoff_auto_move,
                {"file_path": str(src)},
                env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
            )
        assert result == 0
        assert "handoff-auto-move" in capsys.readouterr().err

    def test_shutil_error_exits_0(self, handoff_auto_move, tmp_path, capsys):
        src = tmp_path / "handoff.md"
        src.write_text("x")
        with patch("shutil.move", side_effect=shutil.Error("cannot move")):
            result = run_main(
                handoff_auto_move,
                {"file_path": str(src)},
                env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
            )
        assert result == 0


class TestStreamReconfigure:
    def test_stream_without_reconfigure_skipped(self, handoff_auto_move, tmp_path):
        src = tmp_path / "handoff.md"
        src.write_text("x")
        mock_stream = MagicMock(spec=["write", "flush"])  # không có reconfigure
        with patch("sys.stdout", mock_stream):
            with patch("sys.stderr", mock_stream):
                result = run_main(
                    handoff_auto_move,
                    {"file_path": str(src)},
                    env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
                )
        assert result is None


class TestSessionStart:
    def test_moves_handoff_when_no_file_path(self, handoff_auto_move, tmp_path):
        """SessionStart: không có file_path → scan project root."""
        src = tmp_path / "HANDOFF.md"
        src.write_text("session brief")
        result = run_main(
            handoff_auto_move,
            {},
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result == 0
        assert not src.exists()
        assert (tmp_path / ".claude" / "handoff.md").read_text() == "session brief"

    def test_no_handoff_at_root_exits_0(self, handoff_auto_move, tmp_path):
        """SessionStart: không có HANDOFF.md ở root → exit 0 yên lặng."""
        result = run_main(
            handoff_auto_move,
            {},
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result == 0


class TestResolveOSError:
    def test_oserror_during_resolve_continues(self, handoff_auto_move, tmp_path):
        src = tmp_path / "handoff.md"
        src.write_text("x")
        with patch.object(Path, "resolve", side_effect=OSError("broken symlink")):
            result = run_main(
                handoff_auto_move,
                {"file_path": str(src)},
                env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
            )
        assert result is None
