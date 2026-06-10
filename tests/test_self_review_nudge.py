"""Tests cho hooks/self-review-nudge.py (Stop hook nhắc fresh-agent review)."""

from __future__ import annotations

import io
import json
import unittest.mock as mock


def tool_use_line(name, file_path=None, input_override=None):
    """Tạo 1 dòng transcript JSONL chứa tool_use."""
    item = {"type": "tool_use", "name": name}
    if input_override is not None:
        item["input"] = input_override
    elif file_path is not None:
        item["input"] = {"file_path": file_path}
    return json.dumps({"message": {"content": [item]}})


def write_transcript(tmp_path, lines):
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(lines), encoding="utf-8")
    return str(p)


def run_main(module, stdin_data: str):
    """Chạy main() với stdin giả, trả (exit_code, stdout)."""
    captured_stdout = io.StringIO()
    with (
        mock.patch("sys.stdin", io.StringIO(stdin_data)),
        mock.patch("sys.stdout", captured_stdout),
    ):
        code = module.main()
    return code, captured_stdout.getvalue()


# ---------- iter_tool_names ----------


class TestIterToolNames:
    def test_missing_file_yields_nothing(self, self_review_nudge):
        assert list(self_review_nudge.iter_tool_names("/khong/ton/tai.jsonl")) == []

    def test_skips_malformed_lines(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path,
            [
                "",  # dòng rỗng
                "{not json",  # JSON hỏng
                "[1, 2]",  # JSON hợp lệ nhưng không phải dict
                json.dumps({"no_message": True}),  # thiếu message
                json.dumps({"message": "text"}),  # message không phải dict
                json.dumps({"message": {"content": "text"}}),  # content không phải list
                json.dumps({"message": {"content": ["text", {"type": "text"}]}}),
                # tool_use nhưng name không phải str
                json.dumps(
                    {"message": {"content": [{"type": "tool_use", "name": 123}]}}
                ),
                tool_use_line("Edit", "/tmp/a.py"),
            ],
        )
        assert list(self_review_nudge.iter_tool_names(path)) == ["Edit"]

    def test_multiple_tools_in_one_message(self, self_review_nudge, tmp_path):
        line = json.dumps(
            {
                "message": {
                    "content": [
                        {"type": "tool_use", "name": "Read"},
                        {"type": "tool_use", "name": "Edit"},
                    ]
                }
            }
        )
        path = write_transcript(tmp_path, [line])
        assert list(self_review_nudge.iter_tool_names(path)) == ["Read", "Edit"]


# ---------- count_edits_since_review ----------


class TestCountEditsSinceReview:
    def test_counts_edit_tools_only(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path,
            [
                tool_use_line("Read"),
                tool_use_line("Edit", "/tmp/a.py"),
                tool_use_line("Write", "/tmp/b.py"),
                tool_use_line("Grep"),
            ],
        )
        assert self_review_nudge.count_edits_since_review(path) == 2

    def test_agent_resets_counter(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path,
            [
                tool_use_line("Edit", "/tmp/a.py"),
                tool_use_line("Edit", "/tmp/b.py"),
                tool_use_line("Agent"),
                tool_use_line("Edit", "/tmp/c.py"),
            ],
        )
        assert self_review_nudge.count_edits_since_review(path) == 1

    def test_task_resets_counter(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path,
            [tool_use_line("Edit", "/tmp/a.py"), tool_use_line("Task")],
        )
        assert self_review_nudge.count_edits_since_review(path) == 0


# ---------- high_stakes_edit_since_delegate ----------


class TestHighStakesEdit:
    def test_missing_file_returns_false(self, self_review_nudge):
        assert (
            self_review_nudge.high_stakes_edit_since_delegate("/khong/ton/tai.jsonl")
            is False
        )

    def test_skips_malformed_lines(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path,
            [
                "",
                "{not json",
                "[1]",
                json.dumps({"message": "text"}),
                json.dumps({"message": {"content": "text"}}),
                json.dumps({"message": {"content": [{"type": "text"}]}}),
            ],
        )
        assert self_review_nudge.high_stakes_edit_since_delegate(path) is False

    def test_edit_to_plan_flags(self, self_review_nudge, tmp_path):
        path = write_transcript(tmp_path, [tool_use_line("Edit", "/tmp/PLAN.md")])
        assert self_review_nudge.high_stakes_edit_since_delegate(path) is True

    def test_edit_to_normal_file_not_flagged(self, self_review_nudge, tmp_path):
        path = write_transcript(tmp_path, [tool_use_line("Edit", "/tmp/app.py")])
        assert self_review_nudge.high_stakes_edit_since_delegate(path) is False

    def test_delegate_resets_flag(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path,
            [tool_use_line("Edit", "/tmp/handoff.md"), tool_use_line("Agent")],
        )
        assert self_review_nudge.high_stakes_edit_since_delegate(path) is False

    def test_input_not_dict_ignored(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path, [tool_use_line("Edit", input_override="not-a-dict")]
        )
        assert self_review_nudge.high_stakes_edit_since_delegate(path) is False

    def test_file_path_not_str_ignored(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path, [tool_use_line("Edit", input_override={"file_path": 123})]
        )
        assert self_review_nudge.high_stakes_edit_since_delegate(path) is False

    def test_non_edit_non_reset_tool_ignored(self, self_review_nudge, tmp_path):
        path = write_transcript(
            tmp_path,
            [tool_use_line("Read"), tool_use_line("Edit", "/tmp/audit-report.md")],
        )
        assert self_review_nudge.high_stakes_edit_since_delegate(path) is True


# ---------- main ----------


class TestMain:
    def test_malformed_stdin(self, self_review_nudge):
        code, out = run_main(self_review_nudge, "{not json")
        assert code == 0 and out == ""

    def test_empty_stdin(self, self_review_nudge):
        code, out = run_main(self_review_nudge, "")
        assert code == 0 and out == ""

    def test_non_dict_stdin(self, self_review_nudge):
        code, out = run_main(self_review_nudge, "[1, 2]")
        assert code == 0 and out == ""

    def test_subagent_stop_skipped(self, self_review_nudge):
        code, out = run_main(
            self_review_nudge, json.dumps({"hook_event_name": "SubagentStop"})
        )
        assert code == 0 and out == ""

    def test_stop_hook_active_skipped(self, self_review_nudge):
        code, out = run_main(self_review_nudge, json.dumps({"stop_hook_active": True}))
        assert code == 0 and out == ""

    def test_missing_transcript_path(self, self_review_nudge):
        code, out = run_main(self_review_nudge, "{}")
        assert code == 0 and out == ""

    def test_empty_transcript_path(self, self_review_nudge):
        code, out = run_main(self_review_nudge, json.dumps({"transcript_path": ""}))
        assert code == 0 and out == ""

    def test_below_threshold_no_nudge(self, self_review_nudge, tmp_path):
        path = write_transcript(tmp_path, [tool_use_line("Edit", "/tmp/a.py")] * 5)
        code, out = run_main(self_review_nudge, json.dumps({"transcript_path": path}))
        assert code == 0 and out == ""

    def test_above_threshold_nudges(self, self_review_nudge, tmp_path):
        path = write_transcript(tmp_path, [tool_use_line("Edit", "/tmp/a.py")] * 6)
        code, out = run_main(self_review_nudge, json.dumps({"transcript_path": path}))
        assert code == 0
        msg = json.loads(out)["systemMessage"]
        assert "6 edit" in msg

    def test_high_stakes_nudges(self, self_review_nudge, tmp_path):
        path = write_transcript(tmp_path, [tool_use_line("Write", "/tmp/handoff.md")])
        code, out = run_main(self_review_nudge, json.dumps({"transcript_path": path}))
        assert code == 0
        msg = json.loads(out)["systemMessage"]
        assert "HIGH-STAKES" in msg

    def test_both_nudges_joined(self, self_review_nudge, tmp_path):
        path = write_transcript(tmp_path, [tool_use_line("Edit", "/tmp/plan.md")] * 6)
        code, out = run_main(self_review_nudge, json.dumps({"transcript_path": path}))
        assert code == 0
        msg = json.loads(out)["systemMessage"]
        assert "HIGH-STAKES" in msg and "6 edit" in msg
