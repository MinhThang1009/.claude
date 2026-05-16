# 🚀 dotclaude — Bộ cấu hình `~/.claude/` cho Claude Code, tối ưu cho dev người Việt

## 📌 Repo làm gì?

Cấu hình global ready-to-use cho Claude Code. Tiếng Việt cho comment/commit/log, tiếng Anh chuẩn cho identifier. Tiết kiệm 1-2 ngày setup.

## ✨ Chức năng nổi bật

- **9 skills** gọi qua `/<tên>`: [`/commit`](../plugins/commit-commands/skills/commit/SKILL.md), [`/code-review`](../plugins/pr-review-toolkit/skills/code-review/SKILL.md), [`/full-review`](../plugins/pr-review-toolkit/skills/full-review/SKILL.md), [`/feature-dev`](../plugins/feature-dev/skills/feature-dev/SKILL.md), [`/debug`](../plugins/debug/skills/debug/SKILL.md), [`/refactor`](../plugins/code-simplifier/skills/refactor/SKILL.md), [`/explain`](../plugins/feature-dev/skills/explain/SKILL.md), [`/handoff`](../plugins/session/skills/handoff/SKILL.md), [`/context-check`](../plugins/session/skills/context-check/SKILL.md)
- **24 subagents** chuyên biệt: [`code-architect`](../plugins/feature-dev/agents/code-architect.md) · [`code-explorer`](../plugins/feature-dev/agents/code-explorer.md) · [`code-reviewer`](../plugins/pr-review-toolkit/agents/code-reviewer.md) · [`code-simplifier`](../plugins/pr-review-toolkit/agents/code-simplifier.md) · [`comment-analyzer`](../plugins/pr-review-toolkit/agents/comment-analyzer.md) · [`debugger`](../plugins/debug/agents/debugger.md) · [`dependency-manager`](../plugins/performance/agents/dependency-manager.md) · [`documentation-engineer`](../plugins/documentation/agents/documentation-engineer.md) · [`nextjs-developer`](../plugins/documentation/agents/nextjs-developer.md) · [`performance-engineer`](../plugins/performance/agents/performance-engineer.md) · [`security-auditor`](../plugins/security-guidance/agents/security-auditor.md) · [`silent-failure-hunter`](../plugins/pr-review-toolkit/agents/silent-failure-hunter.md) · [`test-analyzer`](../plugins/test-toolkit/agents/test-analyzer.md) · [`test-writer`](../plugins/test-toolkit/agents/test-writer.md) · [`type-design-analyzer`](../plugins/pr-review-toolkit/agents/type-design-analyzer.md) · và 10 agents khác (xem [`marketplace.json`](../.claude-plugin/marketplace.json))
- **3 hook deterministic**: chặn `rm -rf` / fork bomb / `dd`, auto-format đa ngôn ngữ, hiển thị git status đầu session
- **Statusline real-time** ([`hooks/statusline.py`](../hooks/statusline.py)): hiển thị model + window mode (1M/200k) + ⚡ effort + 📁 cwd + 🌿 git branch + context % + tokens + 💰 cost + ⏱ duration + rate limits 5h/7d. 5 threshold zones theo context usage (🟢 sweet spot <40% → ⛔ hard limit ≥90%)
- **Permission rules** deny secrets (`.env`, `*.key`, `*.pem`) và lệnh nguy hiểm
- **6 template** project sẵn dùng ([`CLAUDE.md`](../templates/project-CLAUDE.md), [`settings.json`](../templates/project-settings.json), [`.mcp.json`](../templates/project-mcp.json), [`HANDOFF.md`](../templates/HANDOFF.md), [`CLAUDE.local.md`](../templates/project-CLAUDE.local.md), [`skill-evals.json`](../templates/skill-evals.json))
- [**REFERENCE.md**](REFERENCE.md) cheatsheet ~2145 dòng tổng hợp slash command, hook, env var

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
