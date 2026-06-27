"""Pytest config — load hooks modules có hyphen trong tên via importlib.

Auto-detect hooks path để work trên cả main (hooks/) và
plugin-experiment/v1 (plugins/dotclaude/hooks/).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _find_hooks_dir() -> Path:
    """Detect hooks directory location: main vs plugin branch layout."""
    candidates = [
        REPO_ROOT / "hooks",
        REPO_ROOT / "plugins" / "dotclaude" / "hooks",
    ]
    for c in candidates:
        if (c / "bash_guard.py").is_file():
            return c
    raise FileNotFoundError(
        f"bash_guard.py không tìm thấy ở: {[str(c) for c in candidates]}"
    )


HOOKS_DIR = _find_hooks_dir()


def _load_module(name: str, path: Path):
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_bash_guard = _load_module("bash_guard", HOOKS_DIR / "bash_guard.py")
_statusline = _load_module("statusline", HOOKS_DIR / "statusline.py")
_format_on_edit = _load_module("format_on_edit", HOOKS_DIR / "format-on-edit.py")
_handoff_auto_move = _load_module(
    "handoff_auto_move", HOOKS_DIR / "handoff-auto-move.py"
)
_self_review_nudge = _load_module(
    "self_review_nudge", HOOKS_DIR / "self-review-nudge.py"
)
_subagent_edit_surface = _load_module(
    "subagent_edit_surface", HOOKS_DIR / "subagent-edit-surface.py"
)


@pytest.fixture
def bash_guard():
    return _bash_guard


@pytest.fixture
def handoff_auto_move():
    if _handoff_auto_move is None:
        pytest.skip("handoff-auto-move.py không tồn tại")
    return _handoff_auto_move


@pytest.fixture
def statusline():
    if _statusline is None:
        pytest.skip("statusline.py không tồn tại trên branch này (chỉ có ở main)")
    return _statusline


@pytest.fixture
def format_on_edit():
    if _format_on_edit is None:
        pytest.skip("format-on-edit.py không tồn tại trên branch này")
    return _format_on_edit


@pytest.fixture
def self_review_nudge():
    if _self_review_nudge is None:
        pytest.skip("self-review-nudge.py không tồn tại trên branch này")
    return _self_review_nudge


@pytest.fixture
def subagent_edit_surface():
    if _subagent_edit_surface is None:
        pytest.skip("subagent-edit-surface.py không tồn tại trên branch này")
    return _subagent_edit_surface
