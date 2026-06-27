<!-- PR title nên tuân Conventional Commits: feat|fix|docs|refactor|chore|ci(scope): mô tả ngắn -->

## Mục đích

<!-- Mô tả ngắn (1-3 câu): PR này giải quyết vấn đề gì hoặc thêm tính năng gì? -->

## Liên kết Issue

<!-- Nếu PR đóng issue: `Closes #123`. Nếu refer mà không đóng: `Refs #123` -->

Closes #

## Loại thay đổi

<!-- Tick các checkbox phù hợp -->

- [ ] Bug fix (non-breaking)
- [ ] Feature mới (non-breaking)
- [ ] Breaking change (sửa hành vi cũ)
- [ ] Documentation only
- [ ] Fact-check fix (sửa claim sai factual vs Anthropic docs)
- [ ] CI / automation
- [ ] Refactor (không thay đổi behavior)

## Scope file

<!-- Liệt kê file đã sửa, kèm 1 dòng giải thích lý do -->

- `file/path.md`: lý do
- `hooks/script.sh`: lý do

## Self-review checklist

<!-- Tick toàn bộ trước khi mark "Ready for review" -->

- [ ] Đã chạy `bash hooks/test_bash_guard.sh` local, 119/119 PASS
- [ ] Nếu sửa skill / agent / output-style: đã chạy `python scripts/validate-frontmatter.py`
- [ ] Đã verify markdown link không broken (preview render)
- [ ] Commit message tuân Conventional Commits, subject tiếng Việt
- [ ] Không log / commit secret, token, API key, credential
- [ ] Theo style của file đang sửa (terse, formal, impersonal Vietnamese)
- [ ] Update [REFERENCE.md](../docs/REFERENCE.md) / [CLAUDE.md](../CLAUDE.md) nếu thêm slash command / env var / hook event mới
- [ ] Nếu fact-check fix: kèm source URL chính thức trong commit message

## Test plan

<!-- Mô tả cách verify thay đổi work đúng -->

- [ ] Manual test: ...
- [ ] CI sẽ run: hook tests, JSON validate, link check, lint, frontmatter

## Notes (optional)

<!-- Bất kỳ context bổ sung nào reviewer nên biết: limitation, follow-up work, breaking change migration -->
