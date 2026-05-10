"""Test cho hooks/format-on-edit.py — target 100% branch coverage.

Cover:
- parse_input: JSON valid/invalid, missing keys, type errors
- resolve_in_project: trong/ngoài project, cross-drive Windows
- has_risky_prettier_config: 6 file config + 3 pattern package.json
- run_formatter: binary có/không
- format_file: dispatch đúng formatter, prettier RCE skip + override
- main: end-to-end flow
"""

from __future__ import annotations

import io
import json
import sys
from unittest.mock import patch


# ============================================================
# parse_input
# ============================================================


class TestParseInput:
    def test_empty_string(self, format_on_edit):
        assert format_on_edit.parse_input("") is None

    def test_invalid_json(self, format_on_edit):
        assert format_on_edit.parse_input("not json {") is None

    def test_json_not_object(self, format_on_edit):
        assert format_on_edit.parse_input("[]") is None
        assert format_on_edit.parse_input('"string"') is None

    def test_missing_tool_input(self, format_on_edit):
        assert format_on_edit.parse_input('{"foo": "bar"}') is None

    def test_tool_input_not_dict(self, format_on_edit):
        assert format_on_edit.parse_input('{"tool_input": "x"}') is None

    def test_missing_file_path(self, format_on_edit):
        assert format_on_edit.parse_input('{"tool_input": {}}') is None

    def test_empty_file_path(self, format_on_edit):
        assert format_on_edit.parse_input('{"tool_input": {"file_path": ""}}') is None

    def test_file_path_not_string(self, format_on_edit):
        assert format_on_edit.parse_input('{"tool_input": {"file_path": 42}}') is None

    def test_valid(self, format_on_edit):
        result = format_on_edit.parse_input(
            '{"tool_input": {"file_path": "/tmp/foo.py"}}'
        )
        assert result == "/tmp/foo.py"


# ============================================================
# resolve_in_project
# ============================================================


class TestResolveInProject:
    def test_file_inside_project(self, format_on_edit, tmp_path):
        target = tmp_path / "sub" / "file.py"
        target.parent.mkdir()
        target.write_text("x")
        result = format_on_edit.resolve_in_project(str(tmp_path), str(target))
        assert result is not None
        assert result.endswith("file.py")

    def test_file_outside_project(self, format_on_edit, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        outside = tmp_path / "outside.py"
        outside.write_text("x")
        assert format_on_edit.resolve_in_project(str(proj), str(outside)) is None

    def test_realpath_oserror(self, format_on_edit, tmp_path):
        with patch("os.path.realpath", side_effect=OSError("bad path")):
            assert format_on_edit.resolve_in_project(str(tmp_path), "/x") is None

    def test_relpath_valueerror(self, format_on_edit, tmp_path):
        # Mô phỏng Windows cross-drive: os.path.relpath raise ValueError
        with patch("os.path.relpath", side_effect=ValueError("cross-drive")):
            assert format_on_edit.resolve_in_project(str(tmp_path), "/x") is None


# ============================================================
# has_risky_prettier_config
# ============================================================


class TestHasRiskyPrettierConfig:
    def test_no_config(self, format_on_edit, tmp_path):
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_prettierrc_js(self, format_on_edit, tmp_path):
        (tmp_path / ".prettierrc.js").write_text("module.exports = {}")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_prettierrc_cjs(self, format_on_edit, tmp_path):
        (tmp_path / ".prettierrc.cjs").write_text("module.exports = {}")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_prettierrc_mjs(self, format_on_edit, tmp_path):
        (tmp_path / ".prettierrc.mjs").write_text("export default {}")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_prettier_config_js(self, format_on_edit, tmp_path):
        (tmp_path / "prettier.config.js").write_text("module.exports = {}")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_prettier_config_cjs(self, format_on_edit, tmp_path):
        (tmp_path / "prettier.config.cjs").write_text("module.exports = {}")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_prettier_config_mjs(self, format_on_edit, tmp_path):
        (tmp_path / "prettier.config.mjs").write_text("export default {}")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_package_json_official_plugin(self, format_on_edit, tmp_path):
        (tmp_path / "package.json").write_text(
            '{"devDependencies": {"@prettier/plugin-php": "0.20.0"}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_package_json_community_plugin(self, format_on_edit, tmp_path):
        (tmp_path / "package.json").write_text(
            '{"devDependencies": {"prettier-plugin-tailwindcss": "0.5.0"}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_package_json_plugins_array(self, format_on_edit, tmp_path):
        (tmp_path / "package.json").write_text(
            '{"prettier": {"plugins": ["./local-plugin.js"]}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_package_json_safe(self, format_on_edit, tmp_path):
        (tmp_path / "package.json").write_text(
            '{"name": "test", "dependencies": {"react": "^18"}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_package_json_false_positive_in_description(self, format_on_edit, tmp_path):
        # Plugin name xuất hiện trong description text, KHÔNG dùng thật → không trigger
        (tmp_path / "package.json").write_text(
            '{"description": "we do NOT use prettier-plugin-tailwindcss here", '
            '"dependencies": {"react": "^18"}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_package_json_peer_dep_plugin(self, format_on_edit, tmp_path):
        (tmp_path / "package.json").write_text(
            '{"peerDependencies": {"@prettier/plugin-xml": "^3"}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_package_json_prettier_plugins_empty(self, format_on_edit, tmp_path):
        # prettier.plugins = [] → falsy, không trigger
        (tmp_path / "package.json").write_text(
            '{"prettier": {"plugins": []}, "dependencies": {"react": "^18"}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_package_json_prettier_not_dict(self, format_on_edit, tmp_path):
        # prettier có thể là string (path tới config) — không phải dict
        (tmp_path / "package.json").write_text(
            '{"prettier": "./prettier.json", "dependencies": {"react": "^18"}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_package_json_deps_not_dict(self, format_on_edit, tmp_path):
        # dependencies là array (malformed nhưng valid JSON) — không crash
        (tmp_path / "package.json").write_text(
            '{"dependencies": ["react"], "devDependencies": null}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_package_json_dep_key_not_string(self, format_on_edit, tmp_path):
        # JSON key luôn là string sau parse, nhưng test defensive cho assert
        (tmp_path / "package.json").write_text(
            '{"dependencies": {"normal-pkg": "1.0", "@prettier/plugin-php": "1.0"}}'
        )
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is True

    def test_package_json_root_not_dict(self, format_on_edit, tmp_path):
        # JSON valid nhưng root là array
        (tmp_path / "package.json").write_text("[]")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_package_json_invalid_json(self, format_on_edit, tmp_path):
        (tmp_path / "package.json").write_text("{not valid json")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_package_json_unreadable(self, format_on_edit, tmp_path):
        (tmp_path / "package.json").write_text("{}")
        with patch("pathlib.Path.read_text", side_effect=OSError("permission")):
            assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False

    def test_package_json_unicode_decode_error(self, format_on_edit, tmp_path):
        # File binary đọc với utf-8 sẽ fail
        (tmp_path / "package.json").write_bytes(b"\xff\xfe\x00\x00")
        assert format_on_edit.has_risky_prettier_config(str(tmp_path)) is False


# ============================================================
# run_formatter
# ============================================================


class TestRunFormatter:
    def test_binary_missing(self, format_on_edit):
        with patch("shutil.which", return_value=None) as which:
            with patch("subprocess.run") as run:
                format_on_edit.run_formatter(["prettier", "--write", "x.ts"])
        which.assert_called_once_with("prettier")
        run.assert_not_called()

    def test_binary_present(self, format_on_edit):
        with patch("shutil.which", return_value="/usr/bin/prettier"):
            with patch("subprocess.run") as run:
                format_on_edit.run_formatter(["prettier", "--write", "x.ts"], cwd="/p")
        run.assert_called_once()
        call_args = run.call_args
        assert call_args.args[0] == ["prettier", "--write", "x.ts"]
        assert call_args.kwargs["cwd"] == "/p"
        assert call_args.kwargs["check"] is False


# ============================================================
# format_file
# ============================================================


class TestFormatFile:
    def test_prettier_safe(self, format_on_edit, tmp_path, monkeypatch):
        monkeypatch.delenv("CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG", raising=False)
        with patch.object(format_on_edit, "run_formatter") as run:
            format_on_edit.format_file("foo.ts", str(tmp_path))
        run.assert_called_once_with(
            ["prettier", "--write", "foo.ts"], cwd=str(tmp_path)
        )

    def test_prettier_risky_no_override(
        self, format_on_edit, tmp_path, monkeypatch, capsys
    ):
        (tmp_path / ".prettierrc.js").write_text("module.exports = {}")
        monkeypatch.delenv("CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG", raising=False)
        with patch.object(format_on_edit, "run_formatter") as run:
            format_on_edit.format_file("foo.ts", str(tmp_path))
        run.assert_not_called()
        err = capsys.readouterr().err
        assert "RCE risk" in err

    def test_prettier_risky_with_override(self, format_on_edit, tmp_path, monkeypatch):
        (tmp_path / ".prettierrc.js").write_text("module.exports = {}")
        monkeypatch.setenv("CLAUDE_FORMAT_TRUST_PRETTIER_CONFIG", "1")
        with patch.object(format_on_edit, "run_formatter") as run:
            format_on_edit.format_file("foo.ts", str(tmp_path))
        run.assert_called_once()

    def test_python(self, format_on_edit, tmp_path):
        with patch.object(format_on_edit, "run_formatter") as run:
            format_on_edit.format_file("foo.py", str(tmp_path))
        run.assert_called_once_with(["ruff", "format", "foo.py"])

    def test_go(self, format_on_edit, tmp_path):
        with patch.object(format_on_edit, "run_formatter") as run:
            format_on_edit.format_file("foo.go", str(tmp_path))
        run.assert_called_once_with(["gofmt", "-w", "foo.go"])

    def test_rust(self, format_on_edit, tmp_path):
        with patch.object(format_on_edit, "run_formatter") as run:
            format_on_edit.format_file("foo.rs", str(tmp_path))
        run.assert_called_once_with(["rustfmt", "foo.rs"])

    def test_unknown_extension(self, format_on_edit, tmp_path):
        with patch.object(format_on_edit, "run_formatter") as run:
            format_on_edit.format_file("foo.xyz", str(tmp_path))
        run.assert_not_called()

    def test_uppercase_extension_normalized(self, format_on_edit, tmp_path):
        with patch.object(format_on_edit, "run_formatter") as run:
            format_on_edit.format_file("Foo.TS", str(tmp_path))
        run.assert_called_once()


# ============================================================
# main (end-to-end)
# ============================================================


class TestMain:
    def _run_main(self, format_on_edit, stdin_data: str, env: dict | None = None):
        with patch.object(sys, "stdin", io.StringIO(stdin_data)):
            with patch.dict("os.environ", env or {}, clear=False):
                return format_on_edit.main()

    def test_empty_stdin(self, format_on_edit):
        with patch.object(format_on_edit, "format_file") as ff:
            assert self._run_main(format_on_edit, "") == 0
        ff.assert_not_called()

    def test_file_outside_project(self, format_on_edit, tmp_path):
        outside = tmp_path / "outside.py"
        outside.write_text("x")
        proj = tmp_path / "proj"
        proj.mkdir()
        payload = json.dumps({"tool_input": {"file_path": str(outside)}})
        with patch.object(format_on_edit, "format_file") as ff:
            ret = self._run_main(
                format_on_edit, payload, {"CLAUDE_PROJECT_DIR": str(proj)}
            )
        assert ret == 0
        ff.assert_not_called()

    def test_file_inside_project(self, format_on_edit, tmp_path):
        target = tmp_path / "foo.py"
        target.write_text("x")
        payload = json.dumps({"tool_input": {"file_path": str(target)}})
        with patch.object(format_on_edit, "format_file") as ff:
            ret = self._run_main(
                format_on_edit, payload, {"CLAUDE_PROJECT_DIR": str(tmp_path)}
            )
        assert ret == 0
        ff.assert_called_once()

    def test_no_project_dir_env_uses_cwd(self, format_on_edit, tmp_path, monkeypatch):
        target = tmp_path / "foo.py"
        target.write_text("x")
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        monkeypatch.chdir(tmp_path)
        payload = json.dumps({"tool_input": {"file_path": str(target)}})
        with patch.object(format_on_edit, "format_file") as ff:
            with patch.object(sys, "stdin", io.StringIO(payload)):
                ret = format_on_edit.main()
        assert ret == 0
        ff.assert_called_once()
