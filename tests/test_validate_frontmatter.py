"""Tests cho scripts/validate-frontmatter.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML required for frontmatter tests")

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load module trực tiếp (tên file có hyphen).
_spec = importlib.util.spec_from_file_location(
    "validate_frontmatter", REPO_ROOT / "scripts" / "validate-frontmatter.py"
)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
sys.modules["validate_frontmatter"] = _mod
_spec.loader.exec_module(_mod)

parse_frontmatter = _mod.parse_frontmatter
validate = _mod.validate
SCHEMAS = _mod.SCHEMAS


# ── parse_frontmatter ──────────────────────────────────────────────


class TestParseFrontmatter:
    def test_valid_skill(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\ndescription: hello\n---\nbody", encoding="utf-8")
        fm, err = parse_frontmatter(f)
        assert err is None
        assert fm == {"description": "hello"}

    def test_missing_opening(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("description: hello\n---\n", encoding="utf-8")
        fm, err = parse_frontmatter(f)
        assert fm is None
        assert "opening" in err

    def test_missing_closing(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\ndescription: hello\n", encoding="utf-8")
        fm, err = parse_frontmatter(f)
        assert fm is None
        assert "closing" in err

    def test_invalid_yaml(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\n: [unclosed\n---\n", encoding="utf-8")
        fm, err = parse_frontmatter(f)
        assert fm is None
        assert "YAML" in err

    def test_not_a_mapping(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\n- item1\n- item2\n---\n", encoding="utf-8")
        fm, err = parse_frontmatter(f)
        assert fm is None
        assert "mapping" in err

    def test_empty_frontmatter(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\n---\nbody", encoding="utf-8")
        fm, err = parse_frontmatter(f)
        assert fm is None
        assert "mapping" in err

    def test_unicode_fields(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text(
            "---\ndescription: Kiểm tra tiếng Việt\nname: café\n---\n",
            encoding="utf-8",
        )
        fm, err = parse_frontmatter(f)
        assert err is None
        assert fm["description"] == "Kiểm tra tiếng Việt"

    def test_crlf_line_endings(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_bytes(b"---\r\ndescription: hello\r\n---\r\nbody")
        fm, err = parse_frontmatter(f)
        assert err is None
        assert fm == {"description": "hello"}

    def test_file_not_readable(self, tmp_path):
        f = tmp_path / "nonexistent.md"
        fm, err = parse_frontmatter(f)
        assert fm is None
        assert "cannot read" in err


# ── validate ───────────────────────────────────────────────────────


class TestValidate:
    @pytest.fixture(autouse=True)
    def _patch_root(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_mod, "ROOT", tmp_path)

    def test_valid_skill(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\ndescription: hello\n---\n", encoding="utf-8")
        errors = validate(f, "skill")
        assert errors == []

    def test_missing_required_field(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\nname: test\n---\n", encoding="utf-8")
        errors = validate(f, "skill")
        assert any("missing required field 'description'" in e for e in errors)

    def test_empty_required_field(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\ndescription: ''\n---\n", encoding="utf-8")
        errors = validate(f, "skill")
        assert any("empty" in e for e in errors)

    def test_whitespace_only_required_field(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\ndescription: '   '\n---\n", encoding="utf-8")
        errors = validate(f, "skill")
        assert any("empty" in e for e in errors)

    def test_unknown_field_typo(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("---\ndescription: ok\ndescrption: typo\n---\n", encoding="utf-8")
        errors = validate(f, "skill")
        assert any("unknown field 'descrption'" in e for e in errors)

    def test_agent_requires_name_and_description(self, tmp_path):
        f = tmp_path / "agent.md"
        f.write_text("---\nname: test\n---\n", encoding="utf-8")
        errors = validate(f, "agent")
        assert any("description" in e for e in errors)

    def test_output_style_valid(self, tmp_path):
        f = tmp_path / "style.md"
        f.write_text("---\nname: concise\ndescription: short\n---\n", encoding="utf-8")
        errors = validate(f, "output-style")
        assert errors == []

    def test_all_allowed_skill_fields(self, tmp_path):
        f = tmp_path / "SKILL.md"
        fields = "\n".join(f"{k}: test" for k in SCHEMAS["skill"]["allowed"])
        f.write_text(f"---\n{fields}\n---\n", encoding="utf-8")
        errors = validate(f, "skill")
        assert errors == []

    def test_all_allowed_agent_fields(self, tmp_path):
        f = tmp_path / "agent.md"
        fields = "\n".join(f"{k}: test" for k in SCHEMAS["agent"]["allowed"])
        f.write_text(f"---\n{fields}\n---\n", encoding="utf-8")
        errors = validate(f, "agent")
        assert errors == []

    def test_agent_memory_field_accepted(self, tmp_path):
        # Regression: 'memory: user' đã gây CI fail PR #81 vì validator
        # chưa sync allowlist sau khi commit 2a0303a thêm field này.
        f = tmp_path / "agent.md"
        f.write_text(
            "---\nname: t\ndescription: d\nmemory: user\n---\n",
            encoding="utf-8",
        )
        assert validate(f, "agent") == []

    def test_agent_unknown_field_rejected(self, tmp_path):
        f = tmp_path / "agent.md"
        f.write_text(
            "---\nname: t\ndescription: d\nfoobar: x\n---\n",
            encoding="utf-8",
        )
        errors = validate(f, "agent")
        assert any("unknown field 'foobar'" in e for e in errors)

    def test_validate_propagates_parse_error(self, tmp_path):
        # validate() khi parse_frontmatter return error → wrap với rel path
        f = tmp_path / "broken.md"
        f.write_text("no frontmatter at all", encoding="utf-8")
        errors = validate(f, "skill")
        assert len(errors) == 1
        assert "broken.md" in errors[0]
        assert "missing opening" in errors[0]


# ── main() integration ─────────────────────────────────────────────


class TestMain:
    @pytest.fixture(autouse=True)
    def _patch_root(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_mod, "ROOT", tmp_path)

    def _run(self):
        try:
            _mod.main()
        except SystemExit as e:
            return e.code
        return None

    def test_no_directories(self, capsys):
        # Không có skills/, agents/, output-styles/ → 0 file, exit 0
        code = self._run()
        out = capsys.readouterr().out
        assert "All 0 frontmatter file valid" in out
        assert code == 0

    def test_valid_skill(self, tmp_path, capsys):
        sk = tmp_path / "skills" / "demo"
        sk.mkdir(parents=True)
        (sk / "SKILL.md").write_text("---\ndescription: ok\n---\n", encoding="utf-8")
        code = self._run()
        assert code == 0
        assert "All 1 frontmatter file valid" in capsys.readouterr().out

    def test_valid_agent_and_style(self, tmp_path, capsys):
        ag = tmp_path / "agents"
        ag.mkdir()
        (ag / "a.md").write_text(
            "---\nname: a\ndescription: d\n---\n", encoding="utf-8"
        )
        st = tmp_path / "output-styles"
        st.mkdir()
        (st / "s.md").write_text(
            "---\nname: s\ndescription: d\n---\n", encoding="utf-8"
        )
        code = self._run()
        assert code == 0
        assert "All 2 frontmatter file valid" in capsys.readouterr().out

    def test_invalid_file_exits_1(self, tmp_path, capsys):
        ag = tmp_path / "agents"
        ag.mkdir()
        # Missing required 'description'
        (ag / "bad.md").write_text("---\nname: t\n---\n", encoding="utf-8")
        code = self._run()
        captured = capsys.readouterr()
        assert code == 1
        assert "missing required field 'description'" in captured.err
        assert "1 error(s) trong 1 file" in captured.err
