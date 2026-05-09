"""Pytest config — load hooks modules có hyphen trong tên via importlib."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Cache loaded modules để pytest collect không reload mỗi test.
_bash_guard = _load_module("bash_guard", REPO_ROOT / "hooks" / "bash-guard.py")
_statusline = _load_module("statusline", REPO_ROOT / "hooks" / "statusline.py")


import pytest


@pytest.fixture
def bash_guard():
    return _bash_guard


@pytest.fixture
def statusline():
    return _statusline
