# 🚀 dotclaude — Bộ cấu hình `~/.claude/` cho Claude Code, tối ưu cho dev người Việt

## 📌 Repo làm gì?

Cấu hình global ready-to-use cho Claude Code. Tiếng Việt cho comment/commit/log, tiếng Anh chuẩn cho identifier. Tiết kiệm 1-2 ngày setup.

## ✨ Chức năng nổi bật

- **7 skills** gọi qua `/<tên>`: [`/commit`](../plugins/dotclaude/skills/commit/SKILL.md), [`/code-review`](../plugins/dotclaude/skills/code-review/SKILL.md), [`/debug`](../plugins/dotclaude/skills/debug/SKILL.md), [`/refactor`](../plugins/dotclaude/skills/refactor/SKILL.md), [`/explain`](../plugins/dotclaude/skills/explain/SKILL.md), [`/handoff`](../plugins/dotclaude/skills/handoff/SKILL.md), [`/context-check`](../plugins/dotclaude/skills/context-check/SKILL.md)
- **4 subagents** chuyên biệt: [`code-reviewer`](../plugins/dotclaude/agents/code-reviewer.md) · [`security-auditor`](../plugins/dotclaude/agents/security-auditor.md) · [`test-writer`](../plugins/dotclaude/agents/test-writer.md) · [`architect`](../plugins/dotclaude/agents/architect.md)
- **3 hook deterministic**: chặn `rm -rf` / fork bomb / `dd`, auto-format đa ngôn ngữ, hiển thị git status đầu session
- **Permission rules** deny secrets (`.env`, `*.key`, `*.pem`) và lệnh nguy hiểm
- **6 template** project sẵn dùng ([`CLAUDE.md`](../templates/project-CLAUDE.md), [`settings.json`](../templates/project-settings.json), [`.mcp.json`](../templates/project-mcp.json), [`HANDOFF.md`](../templates/HANDOFF.md), [`CLAUDE.local.md`](../templates/project-CLAUDE.local.md), [`skill-evals.json`](../templates/skill-evals.json))
- [**REFERENCE.md**](REFERENCE.md) cheatsheet ~2050 dòng tổng hợp slash command, hook, env var

## 🛠️ Cài đặt (3 bước)

1. Backup `~/.claude/` cũ nếu có
2. Clone repo:
   ```bash
   git clone https://github.com/MinhThang1009/dotclaude.git
   ```
3. Copy sang `~/.claude/` — script đầy đủ cho Linux/macOS, PowerShell, CMD trong [README](../README.md)

**Verify:** `/skills` · `/agents` · `/context` · `/doctor`

## ✅ Có hữu ích không?

- 🟢 **Phù hợp**: dev VN dùng Claude Code v2.1.111+, ưu tiên Max/Team plan (Opus 4.7 + 1M context)
- 🔴 **Không phù hợp**: dev English-only, user muốn tự config từ đầu
- 🛡️ **Quality**: schema chuẩn Anthropic, MIT License, bảng fallback cho Pro/Bedrock/Vertex

## 🔗 Repo

<https://github.com/MinhThang1009/dotclaude>

Issues và PR luôn welcome.

---

**Topics:** `claude-code` · `anthropic` · `dotfiles` · `dev-vn` · `ai-tooling`
