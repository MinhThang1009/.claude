# Contributing — dotclaude

> Repo cung cấp bộ user-config cho Claude Code dành cho cộng đồng dev người Việt — tiết kiệm 1-2 ngày setup. Mọi đóng góp chất lượng đều được hoan nghênh.

## Báo lỗi

Trước khi mở issue, kiểm tra:

1. **Lỗi reproduce được không?** → Mô tả cụ thể version Claude Code (`claude --version`), OS, command/skill chạy, expected vs actual.
2. **Đã search issue chưa?** → Tránh duplicate.
3. **Liên quan dotclaude config hay Claude Code core?** → Nếu là bug Claude Code chính nó (không phải config), report ở [anthropics/claude-code/issues](https://github.com/anthropics/claude-code/issues) thay.

**Issue template** (paste vào issue body):

```markdown
**Version Claude Code**: vX.Y.Z (`claude --version`)
**OS**: macOS / Linux / Windows
**Plan**: Pro / Max / Team / API key

**Reproduce**:
1. ...
2. ...

**Expected**: ...
**Actual**: ...

**Log/screenshot** (nếu có):
```

## Báo nội dung sai (fact-check)

Repo này tổng hợp từ docs Anthropic. Nội dung có thể outdated khi Anthropic update. Khi phát hiện claim sai (env var đã rename, slash command đã removed, model ID mới…):

1. Mở issue tag `fact-check` với:
   - File:line (vd `REFERENCE.md:1234`)
   - Claim hiện tại
   - Source chính thức bác bỏ (URL `code.claude.com/docs/...` hoặc CHANGELOG entry)
2. Hoặc submit PR fix trực tiếp.

Tham khảo workflow fact-check trong commit history (search `docs: fix .* fact-check`) để theo style.

## Submit Pull Request

### Style guidelines

- **Commit message**: [Conventional Commits](https://www.conventionalcommits.org/), subject **tiếng Việt**, type tiếng Anh (`feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`...). Tham khảo [skills/commit/SKILL.md](../skills/commit/SKILL.md).
- **Markdown**: Theo style file đang sửa (terse, bullet-heavy, tiếng Việt cho prose, tiếng Anh cho identifier/code).
- **Không thêm dependency** vào hooks/* mà không thảo luận trước (issue).

### Quy trình

1. Fork repo → tạo branch `fix/...` hoặc `feat/...`.
2. Sửa, **verify** local trước khi push:
   - Markdown: render preview check link không broken (`markdownlint-cli2 "**/*.md"` nếu cài).
   - Hooks: chạy `bash hooks/test-bash-guard.sh` (119 test case, must 119/119 PASS).
   - JSON: validate syntax (`python -m json.tool settings.json` hoặc `jq . settings.json`).
   - Shell: `shellcheck hooks/*.sh` (nếu cài).
   - Python: `ruff check hooks/` (nếu cài).
3. CI trên GitHub Actions chạy 9 jobs tự động khi push/PR — phải pass hết trước khi merge:
   - Hook regression tests (119 cases) — Ubuntu + macOS + Windows matrix (3 jobs)
   - JSON syntax validate
   - Markdown link check (lychee, offline mode)
   - markdownlint cho `**/*.md`
   - shellcheck cho `hooks/*.sh`
   - ruff cho `hooks/*.py`
   - pytest cho `tests/`
   - actionlint cho `.github/workflows/*.yml`
   - Frontmatter schema validate cho skills/agents/output-styles
4. Commit từng change nhỏ (revert được độc lập).
5. Push fork → mở PR vào `main` với:
   - Title: Conventional Commit style.
   - Body: WHY change, link issue (`Closes #N`).
   - **Self-review checklist** (tick trong PR body):
     - [ ] Tested locally (Claude Code v2.1.x current)
     - [ ] Markdown link không broken
     - [ ] Không log/expose secret
     - [ ] Theo style file đang sửa
     - [ ] Update REFERENCE.md / CLAUDE.md nếu thêm feature mới

### Loại PR welcome

- ✅ Fix fact (model ID, version, env var, slash command outdated)
- ✅ Sửa typo, broken link, lỗi grammar
- ✅ Thêm slash command / env var / hook event mới Anthropic vừa ship
- ✅ Cải thiện skill prompt (description rõ hơn, allowed-tools chuẩn hơn)
- ✅ Thêm hook test case
- ✅ Update version-gating khi Anthropic ship feature mới

### Loại PR cân nhắc kỹ trước khi submit

- ⚠️ Đổi default `model` / `effortLevel` / `outputStyle` — config cá nhân, không nên impose
- ⚠️ Thêm skill / agent mới — chỉ khi pattern proven (đã dùng 5+ lần), generic, không project-specific
- ⚠️ Đổi rule trong `rules/communication.md` / `rules/security.md` — opinion mạnh, discuss trong issue trước
- ⚠️ Refactor lớn — issue trước để align scope

### Loại PR không nhận

- ❌ Cấu hình tiếng Anh thuần (repo target dev VN, có repo English-only khác)
- ❌ Tự promote tool/blog/MCP server cá nhân
- ❌ Đổi license

### Cập nhật CHANGELOG.md

PR có user-visible change (feature, fix, breaking) cần thêm entry vào section `## [Unreleased]` của [CHANGELOG.md](../CHANGELOG.md), theo format [Keep a Changelog](https://keepachangelog.com/en/1.1.0/):

- **Added**: tính năng mới
- **Changed**: thay đổi behavior tính năng có sẵn
- **Deprecated**: tính năng sắp removed
- **Removed**: tính năng đã removed
- **Fixed**: bug fix
- **Security**: vá lỗ hổng

Bỏ qua nếu PR chỉ là internal refactor / typo / test-only.

## Setup dev

```bash
git clone https://github.com/<your-fork>/dotclaude.git
cd dotclaude

# Test hooks (119 case)
bash hooks/test-bash-guard.sh

# Validate frontmatter (cần PyYAML)
pip install pyyaml
python scripts/validate-frontmatter.py

# Lint markdown
npx markdownlint-cli2 "**/*.md"
```

### Pre-commit hooks (recommended)

Setup pre-commit để catch lỗi tự động trước mỗi commit (tránh CI fail sau khi push):

```bash
pip install pre-commit
pre-commit install
```

Sau đó mỗi `git commit` sẽ chạy:
- `bash-guard-tests` (nếu có thay đổi trong `hooks/`)
- `frontmatter-validate` (nếu có thay đổi skill/agent/output-style)
- `shellcheck`, `ruff`, `markdownlint-cli2` cho file tương ứng
- Built-in: trailing whitespace, EOF newline, JSON/YAML syntax, merge conflict, private key detection

Manual run tất cả: `pre-commit run --all-files`. Skip 1 lần (chỉ khi cần thiết, lý do rõ ràng): `git commit --no-verify`.

## License

Đóng góp qua PR mặc nhiên áp dụng [MIT License](../LICENSE) — cùng license với repo.

## Liên hệ

- Issue: [github.com/MinhThang1009/dotclaude/issues](https://github.com/MinhThang1009/dotclaude/issues)
- Discussions: hiện chưa enabled. Sẽ kích hoạt khi cộng đồng phát triển; trước đó dùng Issue cho mọi câu hỏi.
