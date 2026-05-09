# Contributing — dotclaude

> Cảm ơn bạn quan tâm đóng góp. Repo này là user-config cá nhân cho Claude Code, share để cộng đồng dev người Việt tiết kiệm 1-2 ngày setup. Mọi đóng góp chất lượng đều welcome.

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

Repo này tổng hợp từ docs Anthropic. Nội dung có thể outdated khi Anthropic update. Nếu bạn phát hiện claim sai (env var đã rename, slash command đã removed, model ID mới…):

1. Mở issue tag `fact-check` với:
   - File:line (vd `REFERENCE.md:1234`)
   - Claim hiện tại
   - Source chính thức bác bỏ (URL `code.claude.com/docs/...` hoặc CHANGELOG entry)
2. Hoặc submit PR fix trực tiếp.

Tham khảo workflow fact-check trong commit history (search `docs: fix .* fact-check`) để theo style.

## Submit Pull Request

### Style guidelines

- **Commit message**: [Conventional Commits](https://www.conventionalcommits.org/), subject **tiếng Việt**, type tiếng Anh (`feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`...). Tham khảo [skills/commit/SKILL.md](skills/commit/SKILL.md).
- **Markdown**: Theo style file đang sửa (terse, bullet-heavy, tiếng Việt cho prose, tiếng Anh cho identifier/code).
- **Không thêm dependency** vào hooks/* mà không thảo luận trước (issue).

### Quy trình

1. Fork repo → tạo branch `fix/...` hoặc `feat/...`.
2. Sửa, **verify**:
   - Markdown: render preview check link không broken.
   - Hooks: chạy `bash hooks/test-bash-guard.sh` (97 test case).
   - settings.json: validate JSON syntax (`python -c "import json; json.load(open('settings.json'))"` hoặc `jq . settings.json`).
3. Commit từng change nhỏ (revert được độc lập).
4. Push fork → mở PR vào `main` với:
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

## Setup dev

```bash
git clone https://github.com/<your-fork>/dotclaude.git
cd dotclaude
# Test hooks
bash hooks/test-bash-guard.sh
# Lint markdown (optional)
npx markdownlint-cli2 "**/*.md"
```

## License

Bằng việc submit PR, bạn đồng ý đóng góp dưới [MIT License](LICENSE) — cùng license với repo.

## Liên hệ

- Issue: [github.com/MinhThang1009/dotclaude/issues](https://github.com/MinhThang1009/dotclaude/issues)
- Discussion: [github.com/MinhThang1009/dotclaude/discussions](https://github.com/MinhThang1009/dotclaude/discussions) (nếu enabled)
