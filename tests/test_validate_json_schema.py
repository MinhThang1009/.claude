"""Tests cho scripts/validate-json-schema.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("jsonschema", reason="jsonschema required for JSON schema tests")

REPO_ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "validate_json_schema", REPO_ROOT / "scripts" / "validate-json-schema.py"
)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
sys.modules["validate_json_schema"] = _mod
_spec.loader.exec_module(_mod)

validate_file = _mod.validate_file
find_json_files = _mod.find_json_files


class TestValidateFile:
    def test_valid_json_no_schema(self, tmp_path):
        f = tmp_path / "test.json"
        f.write_text('{"key": "value"}', encoding="utf-8")
        ok, msg = validate_file(f)
        assert ok is True
        assert "skip" in msg

    def test_invalid_json(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("{invalid", encoding="utf-8")
        ok, msg = validate_file(f)
        assert ok is False
        assert "JSON parse error" in msg

    def test_json_array_skipped(self, tmp_path):
        f = tmp_path / "arr.json"
        f.write_text("[1, 2, 3]", encoding="utf-8")
        ok, msg = validate_file(f)
        assert ok is True
        assert "not object" in msg

    def test_non_http_schema_skipped(self, tmp_path):
        f = tmp_path / "local.json"
        f.write_text('{"$schema": "file:///local.json"}', encoding="utf-8")
        ok, msg = validate_file(f)
        assert ok is True
        assert "not http" in msg

    def test_schema_fetch_failure(self, tmp_path):
        f = tmp_path / "fail.json"
        f.write_text(
            '{"$schema": "https://nonexistent.invalid/schema.json"}',
            encoding="utf-8",
        )
        ok, msg = validate_file(f)
        assert ok is False
        assert "fetch schema fail" in msg

    def test_empty_json_object(self, tmp_path):
        f = tmp_path / "empty.json"
        f.write_text("{}", encoding="utf-8")
        ok, msg = validate_file(f)
        assert ok is True
        assert "skip" in msg

    def test_unicode_content(self, tmp_path):
        f = tmp_path / "vn.json"
        f.write_text('{"key": "tiếng Việt"}', encoding="utf-8")
        ok, msg = validate_file(f)
        assert ok is True


class TestFindJsonFiles:
    def test_finds_json(self, tmp_path):
        (tmp_path / "a.json").write_text("{}", encoding="utf-8")
        (tmp_path / "b.txt").write_text("not json", encoding="utf-8")
        files = find_json_files(tmp_path)
        assert len(files) == 1
        assert files[0].name == "a.json"

    def test_skips_cspell(self, tmp_path):
        (tmp_path / "cspell.json").write_text("{}", encoding="utf-8")
        (tmp_path / ".cspell.json").write_text("{}", encoding="utf-8")
        files = find_json_files(tmp_path)
        assert len(files) == 0

    def test_skips_node_modules(self, tmp_path):
        nm = tmp_path / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "package.json").write_text("{}", encoding="utf-8")
        files = find_json_files(tmp_path)
        assert len(files) == 0

    def test_skips_git_dir(self, tmp_path):
        git = tmp_path / ".git" / "config"
        git.parent.mkdir()
        (tmp_path / ".git" / "test.json").write_text("{}", encoding="utf-8")
        files = find_json_files(tmp_path)
        assert len(files) == 0

    def test_nested_json(self, tmp_path):
        sub = tmp_path / "sub" / "dir"
        sub.mkdir(parents=True)
        (sub / "deep.json").write_text("{}", encoding="utf-8")
        files = find_json_files(tmp_path)
        assert len(files) == 1
