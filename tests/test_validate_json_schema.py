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


class TestFetchSchema:
    def test_cache_hit_skips_network(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_mod, "SCHEMA_CACHE_DIR", tmp_path)
        url = "https://example.test/schema.json"
        cache_key = url.replace("/", "_").replace(":", "_")
        (tmp_path / cache_key).write_text(
            '{"type": "object", "cached": true}', encoding="utf-8"
        )

        # urlopen sẽ raise nếu được gọi → cache hit thì không touch network
        def raise_if_called(*a, **kw):
            raise AssertionError("urlopen should not be called on cache hit")

        monkeypatch.setattr(_mod.urllib.request, "urlopen", raise_if_called)
        schema = _mod.fetch_schema(url)
        assert schema == {"type": "object", "cached": True}

    def test_cache_miss_fetches_and_writes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_mod, "SCHEMA_CACHE_DIR", tmp_path)

        class FakeResp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return b'{"type": "object", "fetched": true}'

        monkeypatch.setattr(
            _mod.urllib.request, "urlopen", lambda url, timeout: FakeResp()
        )
        url = "https://example.test/fresh.json"
        schema = _mod.fetch_schema(url)
        assert schema == {"type": "object", "fetched": True}
        # Cache file đã được ghi
        cache_key = url.replace("/", "_").replace(":", "_")
        assert (tmp_path / cache_key).exists()


class TestValidateFileSchemaPath:
    def test_validates_against_schema_pass(self, tmp_path, monkeypatch):
        f = tmp_path / "ok.json"
        f.write_text(
            '{"$schema": "https://x.test/s.json", "name": "ok"}', encoding="utf-8"
        )
        monkeypatch.setattr(
            _mod,
            "fetch_schema",
            lambda u: {"type": "object", "required": ["name"]},
        )
        ok, msg = validate_file(f)
        assert ok is True
        assert "valid against" in msg

    def test_validates_against_schema_fail(self, tmp_path, monkeypatch):
        f = tmp_path / "bad.json"
        f.write_text('{"$schema": "https://x.test/s.json"}', encoding="utf-8")
        monkeypatch.setattr(
            _mod,
            "fetch_schema",
            lambda u: {"type": "object", "required": ["name"]},
        )
        ok, msg = validate_file(f)
        assert ok is False
        assert "schema validation fail" in msg


class TestMain:
    def test_no_files(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        code = _mod.main()
        out = capsys.readouterr().out
        assert "No JSON files" in out
        assert code == 0

    def test_only_skipped_files(self, tmp_path, monkeypatch, capsys):
        # File không có $schema → skip, checked = 0
        (tmp_path / "x.json").write_text('{"key": "val"}', encoding="utf-8")
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        code = _mod.main()
        out = capsys.readouterr().out
        assert "No JSON files" in out
        assert code == 0

    def test_validates_ok_files(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "x.json").write_text(
            '{"$schema": "https://x.test/s.json", "name": "ok"}',
            encoding="utf-8",
        )
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        monkeypatch.setattr(_mod, "fetch_schema", lambda u: {"type": "object"})
        code = _mod.main()
        out = capsys.readouterr().out
        assert "OK" in out
        assert "Validated 1 files, 0 failures" in out
        assert code == 0

    def test_reports_failures(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "x.json").write_text(
            '{"$schema": "https://x.test/s.json"}', encoding="utf-8"
        )
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        monkeypatch.setattr(
            _mod,
            "fetch_schema",
            lambda u: {"type": "object", "required": ["name"]},
        )
        code = _mod.main()
        captured = capsys.readouterr()
        assert "FAIL" in captured.err
        assert "1 failures" in captured.out
        assert code == 1
