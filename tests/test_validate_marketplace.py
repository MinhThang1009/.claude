"""Tests cho scripts/validate-marketplace.py."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate-marketplace.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_marketplace", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = load_module()


class TestMarketplaceValid:
    @pytest.fixture(autouse=True)
    def _patch_root(self, tmp_path, monkeypatch):
        # Patch cả ROOT lẫn MARKETPLACE
        monkeypatch.setattr(_mod, "ROOT", tmp_path)
        mp = tmp_path / ".claude-plugin" / "marketplace.json"
        (tmp_path / ".claude-plugin").mkdir()
        monkeypatch.setattr(_mod, "MARKETPLACE", mp)
        self._tmp = tmp_path
        self._mp = mp

    def _make_plugin(self, name, has_plugin_json=True):
        p = self._tmp / "plugins" / name
        p.mkdir(parents=True)
        if has_plugin_json:
            (p / ".claude-plugin").mkdir()
            (p / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": name}), encoding="utf-8"
            )
        return p

    def _write_mp(self, plugins):
        self._mp.write_text(
            json.dumps({"name": "t", "plugins": plugins}), encoding="utf-8"
        )

    def _run(self):
        try:
            _mod.main()
        except SystemExit as e:
            return e.code
        return 0

    def test_valid_single_plugin(self, capsys):
        self._make_plugin("my-plugin")
        self._write_mp(
            [
                {
                    "name": "my-plugin",
                    "description": "d",
                    "author": {"name": "T"},
                    "source": "./plugins/my-plugin",
                    "category": "development",
                }
            ]
        )
        assert self._run() == 0
        assert "1 plugins OK" in capsys.readouterr().out

    def test_missing_source_fails(self, capsys):
        self._write_mp(
            [
                {
                    "name": "ghost",
                    "description": "d",
                    "author": {"name": "T"},
                    "source": "./plugins/ghost",
                    "category": "development",
                }
            ]
        )
        assert self._run() == 1
        assert "ghost" in capsys.readouterr().err

    def test_missing_plugin_json_fails(self, capsys):
        self._make_plugin("no-json", has_plugin_json=False)
        self._write_mp(
            [
                {
                    "name": "no-json",
                    "description": "d",
                    "author": {"name": "T"},
                    "source": "./plugins/no-json",
                    "category": "development",
                }
            ]
        )
        assert self._run() == 1
        assert "plugin.json" in capsys.readouterr().err

    def test_plugin_on_disk_not_in_marketplace_fails(self, capsys):
        self._make_plugin("unlisted")
        listed = self._make_plugin("listed")
        # marketplace lists "listed" but not "unlisted"
        self._write_mp(
            [
                {
                    "name": "listed",
                    "description": "d",
                    "author": {"name": "T"},
                    "source": "./plugins/listed",
                    "category": "development",
                }
            ]
        )
        assert self._run() == 1
        assert "unlisted" in capsys.readouterr().err

    def test_missing_required_field_fails(self, capsys):
        self._make_plugin("p")
        self._write_mp([{"name": "p"}])  # missing description, author, source, category
        assert self._run() == 1
        assert "thiếu field" in capsys.readouterr().err

    def test_source_without_dot_slash(self, capsys):
        # Source không bắt đầu bằng "./" — branch else trong validate()
        self._make_plugin("bare-plugin")
        self._write_mp(
            [
                {
                    "name": "bare-plugin",
                    "description": "d",
                    "author": {"name": "T"},
                    "source": "plugins/bare-plugin",
                    "category": "development",
                }
            ]
        )
        assert self._run() == 0

    def test_plugin_json_missing_name_field(self, capsys):
        p = self._make_plugin("p", has_plugin_json=False)
        (p / ".claude-plugin").mkdir()
        (p / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"description": "no name"}), encoding="utf-8"
        )
        self._write_mp(
            [
                {
                    "name": "p",
                    "description": "d",
                    "author": {"name": "T"},
                    "source": "./plugins/p",
                    "category": "development",
                }
            ]
        )
        assert self._run() == 1
        assert "name" in capsys.readouterr().err

    def test_plugin_json_invalid_json(self, capsys):
        p = self._make_plugin("p", has_plugin_json=False)
        (p / ".claude-plugin").mkdir()
        (p / ".claude-plugin" / "plugin.json").write_text(
            "{invalid json}", encoding="utf-8"
        )
        self._write_mp(
            [
                {
                    "name": "p",
                    "description": "d",
                    "author": {"name": "T"},
                    "source": "./plugins/p",
                    "category": "development",
                }
            ]
        )
        assert self._run() == 1
        assert "parse lỗi" in capsys.readouterr().err

    def test_empty_plugins_fails(self, capsys):
        self._write_mp([])
        assert self._run() == 1

    def test_invalid_json_fails(self, capsys):
        self._mp.write_text("{invalid}", encoding="utf-8")
        assert self._run() == 1

    def test_missing_marketplace_file_fails(self):
        # File chưa được tạo → phải exit 1
        with pytest.raises(SystemExit) as exc:
            _mod.main()
        assert exc.value.code == 1


class TestRealMarketplace:
    def test_real_marketplace_passes(self, monkeypatch):
        monkeypatch.setattr(_mod, "ROOT", REPO_ROOT)
        monkeypatch.setattr(
            _mod, "MARKETPLACE", REPO_ROOT / ".claude-plugin" / "marketplace.json"
        )
        try:
            _mod.main()
        except SystemExit as e:
            assert e.code == 0

    def test_all_plugins_listed(self):
        data = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        listed = {p["name"] for p in data["plugins"]}
        on_disk = {d.name for d in (REPO_ROOT / "plugins").iterdir() if d.is_dir()}
        assert not (on_disk - listed), (
            f"Plugins thiếu trong marketplace.json: {on_disk - listed}"
        )

    def test_all_sources_exist(self):
        data = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        for p in data["plugins"]:
            path = REPO_ROOT / p["source"].lstrip("./")
            assert path.is_dir(), f"{p['name']}: source không tồn tại"

    def test_all_plugin_json_exist(self):
        data = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        for p in data["plugins"]:
            pj = REPO_ROOT / p["source"].lstrip("./") / ".claude-plugin" / "plugin.json"
            assert pj.exists(), f"{p['name']}: thiếu plugin.json"
