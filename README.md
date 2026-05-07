# Bộ cấu hình Global cho Claude Code (`~/.claude/`)

> Tổng hợp từ tài liệu chính thức Anthropic (`code.claude.com`, `platform.claude.com`), Engineering Blog, blog `claude.com`, MindStudio, ClaudeFast, và best practices cộng đồng GitHub. Áp dụng MỌI project. Tối ưu cho **dev người Việt** — tiếng Việt cho comment/log/commit, tiếng Anh chuẩn convention cho identifier.

## 1. Cấu trúc thư mục sau khi cài

```
~/.claude/
├── CLAUDE.md                       # Hướng dẫn global (load mọi session, ~88 dòng)
├── REFERENCE.md                    # Cheatsheet — chỉ tra cứu, KHÔNG load
├── settings.json                   # Quyền, hooks, env vars
├── rules/
│   ├── communication.md            # ✅ Auto-import (essential mỗi turn)
│   └── security.md                 # ✅ Auto-import (essential mọi task)
├── references/
│   ├── coding-standards.md         # ⏸️ @-reference khi cần
│   └── git-workflow.md             # ⏸️ @-reference khi cần
├── skills/                         # Workflow tái sử dụng (gọi /tên)
│   ├── commit/SKILL.md             # Conventional Commit, subject TV
│   ├── code-review/SKILL.md        # Review 6 góc nhìn
│   ├── debug/SKILL.md              # Reproduce → root cause → failing test → fix
│   ├── refactor/SKILL.md           # Pre-flight → step-by-step verify
│   ├── explain/SKILL.md            # Kim tự tháp ngược, top-down
│   ├── handoff/SKILL.md            # 🆕 Brief để chuyển session
│   └── context-check/SKILL.md      # 🆕 Đánh giá context, đề xuất action
├── agents/                         # Subagent chuyên biệt (context riêng)
│   ├── code-reviewer.md            # Senior reviewer (sonnet)
│   ├── security-auditor.md         # Security audit (opus)
│   ├── test-writer.md              # AAA test (sonnet)
│   └── architect.md                # Architecture decision (opus)
├── output-styles/
│   └── concise-vietnamese.md       # Style tiếng Việt ngắn gọn
└── templates/                      # Template COPY vào TỪNG project mới
    ├── project-CLAUDE.md           # → <project>/CLAUDE.md
    ├── project-CLAUDE.local.md     # → <project>/CLAUDE.local.md
    ├── project-settings.json       # → <project>/.claude/settings.json
    └── HANDOFF.md                  # → <project>/.claude/HANDOFF.md (gitignored)
```

**Triết lý baseline tokens** (token cố định mỗi session, đo bằng `/context`):
- `CLAUDE.md` global ≈ 1,900 tokens
- 2 rules auto-import (`communication`, `security`) ≈ 3,100 tokens
- Skill descriptions ≈ 940 tokens, agent descriptions ≈ 470 tokens
- **Tổng memory+skills+agents ≈ 6,400 tokens** (~0.6% Opus 1M). Cao hơn Boris Cherny ~2,500 do Vietnamese tokenize kém hiệu quả; vẫn hợp lý
- 2 references còn lại chỉ load khi `@`-reference → KHÔNG ăn baseline

## 2. Cài đặt

### Bước 1 — Backup config cũ (nếu có)

```bash
[ -d ~/.claude ] && cp -r ~/.claude ~/.claude.backup-$(date +%Y%m%d)
```

### Bước 2 — Sao chép vào `~/.claude/`

```bash
# macOS / Linux
mkdir -p ~/.claude
cp -r dotclaude/. ~/.claude/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"
Copy-Item -Recurse -Force dotclaude\* "$env:USERPROFILE\.claude\"
```

### Bước 3 — Verify

Mở Claude Code trong project bất kỳ:

```
/memory          # CLAUDE.md + rules đã load
/skills          # Skills đã đăng ký
/agents          # Subagents
/context         # Token usage breakdown — baseline nên < 5%
/doctor          # Chẩn đoán cấu hình
```

### Bước 4 — Mỗi project mới

```bash
cd /path/to/project

# CLAUDE.md mô tả project
cp ~/.claude/templates/project-CLAUDE.md ./CLAUDE.md

# Note cá nhân (gitignore)
cp ~/.claude/templates/project-CLAUDE.local.md ./CLAUDE.local.md

# Settings team (commit) + handoff slot (gitignore)
mkdir -p .claude
cp ~/.claude/templates/project-settings.json .claude/settings.json
cp ~/.claude/templates/HANDOFF.md .claude/HANDOFF.md

# .gitignore
cat >> .gitignore <<'EOF'

# Claude Code
CLAUDE.local.md
.claude/settings.local.json
.claude/HANDOFF.md
EOF
```

Sau đó sửa `CLAUDE.md` mô tả: tech stack, lệnh build/test/lint, convention RIÊNG project (KHÔNG lặp lại global).

## 3. File nào KHÔNG đặt ở `~/.claude/` global

| File | Vị trí đúng | Lý do |
|------|-------------|-------|
| `CLAUDE.md` (project) | `<project>/CLAUDE.md` | Context riêng từng repo, COMMIT |
| `CLAUDE.local.md` | `<project>/CLAUDE.local.md` | Note cá nhân, **GITIGNORE** |
| `.mcp.json` (team) | `<project>/.mcp.json` | MCP team-share, COMMIT |
| `.claudeignore` | `<project>/.claudeignore` | File Claude bỏ qua, COMMIT |
| `settings.local.json` | `<project>/.claude/settings.local.json` | Override cá nhân, GITIGNORE |
| `HANDOFF.md` | `<project>/.claude/HANDOFF.md` | Brief chuyển session, GITIGNORE |
| `managed-settings.json` | OS path | Chỉ admin enterprise |

## 4. Thứ tự ưu tiên (precedence)

Cao → thấp khi xung đột:

1. **Managed (enterprise)** — admin tổ chức, không thể override.
2. **CLI flags** — `claude --permission-mode auto`.
3. **`<project>/.claude/settings.local.json`** — override cá nhân của project (gitignore).
4. **`<project>/.claude/settings.json`** — setting team của project (commit).
5. **`~/.claude/settings.json`** — setting global cá nhân.
6. **Default** — mặc định Claude Code.

`CLAUDE.md` ngược lại: **TẤT CẢ cộng dồn** (merge, không override). Cây `~/.claude/CLAUDE.md` + `<project>/CLAUDE.md` + `<project>/<subfolder>/CLAUDE.md` cùng load (cha lúc startup, con lazy).

## 5. Triết lý sử dụng

| Thứ | Khi nào dùng |
|-----|--------------|
| **CLAUDE.md** | Hướng dẫn cần load **MỌI session** — giữ ngắn (<100 dòng) |
| **rules/** auto-import | Rule áp dụng MỌI session — chỉ 1-2 file thật cần |
| **references/** | Rule theo chủ đề — `@`-reference khi cần (tiết kiệm context) |
| **skills/** | Workflow tái sử dụng — load **ON-DEMAND** khi gọi |
| **agents/** | Task chuyên biệt cần **context window riêng** |
| **hooks** | Hành động **BẮT BUỘC** chạy mỗi lần (CLAUDE.md là gợi ý, hooks deterministic) |
| **MCP** | Tool ngoài (Notion, Figma, DB, GitHub…) |
| **`.claudeignore`** | Loại file Claude không nên đọc (build output, lockfile lớn, asset) |

**Quy tắc vàng**: Mỗi dòng trong CLAUDE.md trả lời được câu hỏi *"Nếu xóa dòng này, Claude có làm sai không?"*. Nếu KHÔNG → xóa.

## 6. Quản lý context window — 4 cấp độ tối ưu

### Cấp 1 — Giảm baseline (token cố định mỗi session)

- CLAUDE.md global gọn (<100 dòng).
- CLAUDE.md project chỉ chứa thông tin RIÊNG project, KHÔNG lặp global.
- Chỉ auto-import rule thực sự cần MỌI session.
- Skill ít dùng → set `disable-model-invocation: true`.
- Disable MCP server không dùng cho phiên hiện tại.
- `.claudeignore` loại lockfile, asset lớn, `dist/`, `node_modules/`.

### Cấp 2 — Giảm runtime (token tích trong phiên)

- `/clear` aggressive giữa task không liên quan.
- Subagent cho investigation rộng.
- `!command` thay paste output dài.
- `@file` thay copy-paste code.
- `/btw` cho câu hỏi không cần lưu history.
- Output dài → redirect file rồi `tail`/`grep`.
- Tắt thinking khi không cần (`Alt+T`).

### Cấp 3 — Compact thông minh

- Theo dõi `/context` — sweet spot <40%, action ở >60%.
- Kết thúc 1 phase công việc → `/compact ngay` (đừng đợi auto ở 95%).
- `/compact <chỉ thị>` để hướng (vd: `giữ phần API, drop test debug`).
- "Compact Instructions" trong CLAUDE.md để hướng auto-compact (đã có sẵn trong template).

### Cấp 4 — Session handoff (khi compact không đủ)

- Skill `/handoff` tự động tạo brief 5-10 dòng.
- Brief save vào `<project>/.claude/HANDOFF.md`.
- Session mới → `Đọc .claude/HANDOFF.md và tiếp tục` thay vì `--resume`.
- **Brief-injection > resume** vì resume kéo theo stale tool output.

## 7. Phiên bản tương thích

Bộ cấu hình này test với **Claude Code v2.1.59 trở lên** (cần auto memory, plan mode v2, skills merge với commands, MCP deferred default).

```bash
claude --version
claude update
```

Cụ thể các tính năng cần:
- ✅ v2.1.0+: skills system
- ✅ v2.1.59+: auto memory, plan mode v2
- ✅ v2.1.101+: skills+commands merge, output styles built-in
- ✅ v2.2.x+: MCP tool deferred load (giảm baseline lớn)

## 8. Tài liệu tham khảo

- Tài liệu chính thức: <https://code.claude.com/docs>
- Best practices: <https://code.claude.com/docs/en/best-practices>
- Cheatsheet đầy đủ: xem [`REFERENCE.md`](REFERENCE.md)
- Session management: <https://claude.com/blog/using-claude-code-session-management-and-1m-context>

## 9. Cấu trúc nội bộ — vì sao thiết kế thế này

Câu hỏi thường gặp:

**Q: Sao không import cả 4 rules?**  
A: Vì baseline context = mỗi message phải trả tiền. 4 rules = thêm ~6000 tokens × mỗi turn × cả phiên = lãng phí. Chỉ import 2 rule thực sự áp dụng MỌI turn (communication, security). Còn lại để Claude tự đọc khi cần (qua REFERENCE hoặc khi user `@`-reference).

**Q: Sao không gộp REFERENCE vào CLAUDE.md?**  
A: REFERENCE.md = ~1265 dòng, ~19k tokens. Nếu auto-load thì hết ~9.5% context window Sonnet 200k (hoặc ~1.9% Opus 1M) mỗi session. REFERENCE để **NGƯỜI** tra cứu (mở trên màn hình thứ 2 / web), KHÔNG để Claude đọc.

**Q: Sao có cả `/init-context` lẫn `/init`?**  
A: Cũ rồi — đã bỏ `/init-context` (overlap với `/init` built-in của Claude Code v2.1+).

**Q: Sao tiếng Việt cho commit nhưng tiếng Anh cho branch name?**  
A: Branch name vào `git log --oneline`, nhiều tool (Linear, Jira, GitHub Action) parse được khi tiếng Anh chuẩn ASCII. Commit message hiển thị cho dev đọc → tiếng Việt giúp đọc nhanh. Type/scope giữ tiếng Anh để tool Conventional Commit parse được.
