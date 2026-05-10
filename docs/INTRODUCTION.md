# 🚀 dotclaude — Bộ cấu hình `~/.claude/` cho Claude Code, tối ưu cho dev người Việt

## 📌 Repo làm gì?

Cấu hình global ready-to-use cho Claude Code. Tiếng Việt cho comment/commit/log, tiếng Anh chuẩn cho identifier. Tiết kiệm 1-2 ngày setup.

## ✨ Chức năng nổi bật

- **9 skills** gọi qua `/<tên>`: [`/commit`](../skills/commit/SKILL.md), [`/code-review`](../skills/code-review/SKILL.md), [`/full-review`](../skills/full-review/SKILL.md), [`/feature-dev`](../skills/feature-dev/SKILL.md), [`/debug`](../skills/debug/SKILL.md), [`/refactor`](../skills/refactor/SKILL.md), [`/explain`](../skills/explain/SKILL.md), [`/handoff`](../skills/handoff/SKILL.md), [`/context-check`](../skills/context-check/SKILL.md)
- **15 subagents** chuyên biệt: [`code-architect`](../agents/code-architect.md) · [`code-explorer`](../agents/code-explorer.md) · [`code-reviewer`](../agents/code-reviewer.md) · [`code-simplifier`](../agents/code-simplifier.md) · [`comment-analyzer`](../agents/comment-analyzer.md) · [`debugger`](../agents/debugger.md) · [`dependency-manager`](../agents/dependency-manager.md) · [`documentation-engineer`](../agents/documentation-engineer.md) · [`nextjs-developer`](../agents/nextjs-developer.md) · [`performance-engineer`](../agents/performance-engineer.md) · [`security-auditor`](../agents/security-auditor.md) · [`silent-failure-hunter`](../agents/silent-failure-hunter.md) · [`test-analyzer`](../agents/test-analyzer.md) · [`test-writer`](../agents/test-writer.md) · [`type-design-analyzer`](../agents/type-design-analyzer.md)
- **3 hook deterministic**: chặn `rm -rf` / fork bomb / `dd`, auto-format đa ngôn ngữ, hiển thị git status đầu session
- **Statusline real-time** ([`hooks/statusline.py`](../hooks/statusline.py)): hiển thị model + window mode (1M/200k) + ⚡ effort + 📁 cwd + 🌿 git branch + context % + tokens + 💰 cost + ⏱ duration + rate limits 5h/7d. 5 threshold zones theo context usage (🟢 sweet spot <40% → ⛔ hard limit ≥90%)
- **Permission rules** deny secrets (`.env`, `*.key`, `*.pem`) và lệnh nguy hiểm
- **6 template** project sẵn dùng ([`CLAUDE.md`](../templates/project-CLAUDE.md), [`settings.json`](../templates/project-settings.json), [`.mcp.json`](../templates/project-mcp.json), [`HANDOFF.md`](../templates/HANDOFF.md), [`CLAUDE.local.md`](../templates/project-CLAUDE.local.md), [`skill-evals.json`](../templates/skill-evals.json))
- [**REFERENCE.md**](REFERENCE.md) cheatsheet ~2092 dòng tổng hợp slash command, hook, env var

## 🛠️ Cài đặt (3 bước)

1. Backup `~/.claude/` cũ nếu có
2. Clone repo:
   ```bash
   git clone https://github.com/MinhThang1009/dotclaude.git
   ```
3. Copy sang `~/.claude/` — script đầy đủ cho Linux/macOS, PowerShell, CMD trong [README](../README.md)

**Verify:** `/skills` · `/agents` · `/context` · `/doctor`

## ✅ Có hữu ích không?

- 🟢 **Phù hợp**: dev VN dùng Claude Code v2.1.111+, ưu tiên Max/Team/Enterprise plan (Opus 4.7 + 1M context included); Pro/API cũng dùng được qua extra usage
- 🔴 **Không phù hợp**: dev English-only, user muốn tự config từ đầu
- 🛡️ **Quality**: schema chuẩn Anthropic, MIT License, bảng fallback cho Pro/Bedrock/Vertex

## 🔗 Repo

<https://github.com/MinhThang1009/dotclaude>

Issues và PR luôn welcome.

---

**Topics:** `claude-code` · `anthropic` · `dotfiles` · `dev-vn` · `ai-tooling`
