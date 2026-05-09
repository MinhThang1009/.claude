#!/usr/bin/env python3
"""Validate YAML frontmatter trong skill / agent / output-style files.

Check:
- Frontmatter parses thành YAML hợp lệ.
- Field bắt buộc (description) tồn tại và non-empty.
- Field schema không có typo (chỉ accept allowlist).

Exit 0: pass. Exit 1: có error (in stderr).

Usage: python scripts/validate-frontmatter.py
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent

# Allowlist field cho từng loại file (theo Claude Code docs).
# Ref: https://code.claude.com/docs/en/skills, /sub-agents, /output-styles
SCHEMAS = {
    "skill": {
        "required": ["description"],
        "allowed": {
            "name",
            "description",
            "when_to_use",
            "argument-hint",
            "arguments",
            "disable-model-invocation",
            "user-invocable",
            "allowed-tools",
            "model",
            "effort",
            "context",
            "agent",
            "hooks",
            "paths",
            "shell",
        },
    },
    "agent": {
        "required": ["name", "description"],
        "allowed": {
            "name",
            "description",
            "tools",
            "model",
            "color",
            "isolation",
            "skills",
            "disallowedTools",
            "maxTurns",
            "permissionMode",
            "mcpServers",
            "hooks",
            "memory",
            "background",
            "effort",
            "initialPrompt",
        },
    },
    "output-style": {
        "required": ["name", "description"],
        "allowed": {"name", "description", "keep-coding-instructions"},
    },
}


def parse_frontmatter(path: Path):
    """Return (frontmatter_dict, error_msg). frontmatter_dict=None nếu lỗi."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"cannot read file: {e}"

    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, "missing opening '---'"

    # Find closing ---
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None, "first line must be exactly '---'"

    end = -1
    for i, line in enumerate(lines[1:], start=1):
        if line == "---":
            end = i
            break
    if end == -1:
        return None, "missing closing '---'"

    fm_text = "\n".join(lines[1:end])
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"

    if not isinstance(fm, dict):
        return None, "frontmatter must be a YAML mapping (got %s)" % type(fm).__name__
    return fm, None


def validate(path: Path, kind: str):
    """Return list of error messages (empty if all good)."""
    errors = []
    fm, err = parse_frontmatter(path)
    if err:
        return [f"{path.relative_to(ROOT)}: {err}"]

    schema = SCHEMAS[kind]
    rel = path.relative_to(ROOT)

    # Required field check
    for req in schema["required"]:
        if req not in fm:
            errors.append(f"{rel}: missing required field '{req}'")
        elif not fm[req] or (isinstance(fm[req], str) and not fm[req].strip()):
            errors.append(f"{rel}: required field '{req}' is empty")

    # Unknown field check (catch typo: 'descripton' vs 'description')
    for field in fm:
        if field not in schema["allowed"]:
            errors.append(
                f"{rel}: unknown field '{field}' (allowed: {sorted(schema['allowed'])})"
            )

    return errors


def main():
    all_errors = []
    file_count = 0

    # Skills: skills/<name>/SKILL.md
    skills_dir = ROOT / "skills"
    if skills_dir.is_dir():
        for skill_md in skills_dir.glob("*/SKILL.md"):
            file_count += 1
            all_errors.extend(validate(skill_md, "skill"))

    # Agents: agents/*.md
    agents_dir = ROOT / "agents"
    if agents_dir.is_dir():
        for agent_md in agents_dir.glob("*.md"):
            file_count += 1
            all_errors.extend(validate(agent_md, "agent"))

    # Output styles: output-styles/*.md
    styles_dir = ROOT / "output-styles"
    if styles_dir.is_dir():
        for style_md in styles_dir.glob("*.md"):
            file_count += 1
            all_errors.extend(validate(style_md, "output-style"))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        print(f"\n{len(all_errors)} error(s) trong {file_count} file", file=sys.stderr)
        sys.exit(1)

    print(f"All {file_count} frontmatter file valid")
    sys.exit(0)


if __name__ == "__main__":
    main()
