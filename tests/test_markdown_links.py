"""Kiểm tra internal links trong .md files — catch broken references trước CI."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git",
    ".pytest_cache",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    # plugins/ chứa official Anthropic files với internal links trỏ đến files không có trong repo
    "plugins",
}


def _collect_md_files() -> list[Path]:
    """Thu thập tất cả .md files trong repo, bỏ qua excluded dirs."""
    files = []
    for p in REPO_ROOT.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        files.append(p)
    return sorted(files)


# Regex match markdown links: [text](path) — chỉ relative paths, bỏ http/https/mailto
_LINK_RE = re.compile(
    r"\[(?:[^\]]*)\]\((?!https?://|mailto:|#)([^)#\s]+?)(?:#[^)]*)?\)"
)


def _extract_internal_links(md_file: Path) -> list[tuple[int, str]]:
    """Trả về list (line_number, relative_path) cho mỗi internal link."""
    links = []
    text = md_file.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(text.splitlines(), start=1):
        for match in _LINK_RE.finditer(line):
            target = match.group(1)
            if target.startswith("$") or target.startswith("!"):
                continue
            links.append((i, target))
    return links


def _resolve_link(md_file: Path, target: str) -> Path:
    """Resolve relative link target từ vị trí file chứa link."""
    return (md_file.parent / target).resolve()


_MD_FILES = _collect_md_files()


@pytest.mark.parametrize(
    "md_file",
    _MD_FILES,
    ids=[str(f.relative_to(REPO_ROOT)) for f in _MD_FILES],
)
def test_internal_links_exist(md_file: Path):
    """Mỗi internal link trong .md file phải trỏ tới file/dir tồn tại."""
    links = _extract_internal_links(md_file)
    broken = []
    for line_no, target in links:
        resolved = _resolve_link(md_file, target)
        if not resolved.exists():
            broken.append(f"  dòng {line_no}: [{target}] → {resolved}")
    if broken:
        rel = md_file.relative_to(REPO_ROOT)
        pytest.fail(f"{rel} có {len(broken)} broken link(s):\n" + "\n".join(broken))
