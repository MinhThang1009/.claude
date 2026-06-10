# Bộ cấu hình Global cho Claude Code (`~/.claude/`)

<div align="center">

[![CI](https://github.com/MinhThang1009/dotclaude/actions/workflows/ci.yml/badge.svg)](https://github.com/MinhThang1009/dotclaude/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/MinhThang1009/dotclaude/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.6%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Bash](https://img.shields.io/badge/bash-4%2B-4EAA25?logo=gnubash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Markdown](https://img.shields.io/badge/markdown-CommonMark-000000?logo=markdown&logoColor=white)](https://commonmark.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/MinhThang1009/dotclaude?logo=git&logoColor=white)](https://github.com/MinhThang1009/dotclaude/commits/main)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-v2.1.111%2B-D97757?logo=anthropic&logoColor=white)](https://code.claude.com/docs)

</div>

> Tổng hợp từ tài liệu chính thức Anthropic ([code.claude.com](https://code.claude.com/docs), [platform.claude.com](https://platform.claude.com/docs)), [Engineering Blog](https://www.anthropic.com/engineering), [blog claude.com](https://www.claude.com/blog), [MindStudio](https://www.mindstudio.ai/blog), [ClaudeFast](https://claudefa.st/blog), và best practices cộng đồng GitHub. Áp dụng MỌI project. Tối ưu cho **dev người Việt** — tiếng Việt cho comment/log/commit, tiếng Anh chuẩn convention cho identifier.

> 👉 Lần đầu xem repo? Đọc [**INTRODUCTION.md**](docs/INTRODUCTION.md) cho overview ngắn 1 phút.

> 📅 **Đã verify**: 2026-05-16 vs Claude Code v2.1.142 + Opus 4.7. Model ID, version-gating, env var, slash command, hook event đã cross-check với [docs Anthropic](https://code.claude.com/docs) + [raw CHANGELOG](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md).
>
> ⚠️ **Một số nội dung có thể outdated** khi Anthropic ship version mới hoặc deprecate model. Phát hiện sai sót → submit issue/PR tại [github.com/MinhThang1009/dotclaude/issues](https://github.com/MinhThang1009/dotclaude/issues). Xem [CONTRIBUTING.md](.github/CONTRIBUTING.md) cho quy trình. Lịch sử thay đổi: [CHANGELOG.md](CHANGELOG.md).

## 1. Cấu trúc `~/.claude/` sau khi cài

> Repo source có thêm `docs/`, `.github/`, `scripts/`, `tests/`, `requirements-test.txt`, `.gitattributes`, `LICENSE`, `CHANGELOG.md` cho GitHub browsing + CI — **KHÔNG copy** vào `~/.claude/` (xem [Bước 3](#bước-3--sao-chép-vào-claude)).

```text
~/.claude/
├── CLAUDE.md                       # Hướng dẫn global (load mọi session, ~79 dòng)
├── settings.json                   # Quyền, hooks, env vars
├── rules/
│   ├── communication.md            # ✅ Auto-import (essential mỗi turn)
│   ├── security.md                 # ✅ Auto-import (essential mọi task)
│   ├── verification.md             # ✅ Auto-import (verify & avoid past mistakes)
│   ├── coding-standards.md         # ✅ Auto-import (coding conventions)
│   ├── git-workflow.md             # ✅ Auto-import (git workflow)
│   └── plan-workflow.md            # ✅ Auto-import (8 principles for any implementation plan)
├── plugins/                        # 36 plugins (mỗi plugin có agents/ và/hoặc skills/ bên trong)
│   ├── pr-review-toolkit/          # PR review: code-reviewer, silent-failure-hunter, type-design-analyzer...
│   │   ├── .claude-plugin/
│   │   ├── agents/                 # code-reviewer.md, code-simplifier.md, comment-analyzer.md...
│   │   └── skills/                 # code-review/, full-review/, review-pr/
│   ├── feature-dev/                # Phát triển tính năng: code-architect, code-explorer
│   │   ├── .claude-plugin/
│   │   ├── agents/
│   │   └── skills/                 # explain/, feature-dev/
│   ├── commit-commands/            # Git workflow: commit, commit-push-pr, clean-gone
│   │   ├── .claude-plugin/
│   │   └── skills/
│   ├── debug/                      # Debug: debugger agent + /debug skill
│   ├── documentation/              # Docs: documentation-engineer, nextjs-developer
│   ├── test-toolkit/               # Test: test-writer, test-analyzer
│   ├── security-guidance/          # Security: security-auditor (OWASP)
│   ├── performance/                # Perf: performance-engineer, dependency-manager
│   ├── code-modernization/         # Architecture review: architecture-critic
│   ├── code-simplifier/            # Refactor: /refactor skill
│   ├── hookify/                    # Tạo hooks: conversation-analyzer + /hookify skill
│   ├── frontend-design/            # UI: /frontend-design skill
│   ├── session/                    # Session: /context-check, /handoff
│   ├── claude-md-management/       # Audit CLAUDE.md: /claude-md-management skill
│   └── plugin-dev/                 # Phát triển plugin: 7 skills (agent/skill/hook/mcp/command/structure/settings)
├── .claude-plugin/
│   └── marketplace.json            # Marketplace manifest (36 plugins)
├── output-styles/
│   └── concise-vietnamese.md       # Style tiếng Việt ngắn gọn
├── hooks/                          # Hook scripts (gọi từ settings.json)
│   ├── bash-guard.py               # Engine pattern matching (Python) — defense layer chính
│   ├── bash-guard.sh               # Wrapper minimal gọi python
│   ├── format-on-edit.py           # Engine: prettier/ruff/gofmt/rustfmt + RCE detection
│   ├── format-on-edit.sh           # Wrapper minimal gọi python
│   ├── statusline.py               # StatusLine update script
│   ├── statusline.sh               # Wrapper cho statusline
│   └── test-bash-guard.sh          # Regression test 119 case (dev-only, có thể xóa)
└── templates/                      # Template COPY vào TỪNG project / skill mới
    ├── project-CLAUDE.md           # → <project>/CLAUDE.md
    ├── project-CLAUDE.local.md     # → <project>/CLAUDE.local.md
    ├── project-settings.json       # → <project>/.claude/settings.json
    ├── project-mcp.json            # → <project>/.mcp.json
    ├── HANDOFF.md                  # → <project>/.claude/HANDOFF.md (gitignored)
    └── skill-evals.json            # → <skill>/evals/evals.json (eval-driven optimize)
```

**Baseline tokens** — đo thực tế bằng `/context` (Opus 4.7 1M context, snapshot session start, 2026-05-10, agents/skills từ plugins đã junction):

| Category                      | Tokens     | % of 1M   |
| ----------------------------- | ---------- | --------- |
| System prompt                 | 9,500      | 0.9%      |
| System tools                  | 18,100     | 1.8%      |
| Memory files                  | 10,900     | 1.1%      |
| ├── `CLAUDE.md`               | 3,200      | —         |
| ├── `rules/security`          | 3,100      | —         |
| ├── `rules/verification`      | 2,700      | —         |
| └── `rules/communication`     | 1,900      | —         |
| Custom agents (từ plugins)    | 6,800      | 0.7%      |
| ├── `code-architect`          | 647        | —         |
| ├── `documentation-engineer`  | 538        | —         |
| ├── `security-auditor`        | 438        | —         |
| ├── `test-analyzer`           | 430        | —         |
| ├── `code-explorer`           | 422        | —         |
| └── … (agents còn lại)        | 4,325      | —         |
| Skills (từ plugins)           | 1,400      | 0.1%      |
| Messages (start)              | 13         | <0.1%     |
| **Total used (start)**        | **46,000** | **~5%**   |
| Autocompact buffer (reserved) | 33,000     | 3.3%      |
| Free space                    | 921,000    | 92.1%     |

**Ghi chú**:
- Vietnamese tokenize ~2.3 chars/token cho prose (ước lượng empirical, đo bằng `/context` trên tokenizer Claude — Anthropic không publish ratio chính thức cho từng ngôn ngữ); kém hiệu quả hơn English ~4 chars/token; baseline ~46k cao hơn config English (~10-15k) là expected.
- Agents và skills giờ nằm trong `plugins/` — chỉ load descriptions tại session start, body load khi spawn agent/invoke skill.
- 5 rules auto-load mọi session (communication, security, verification, coding-standards, git-workflow).
- Autocompact buffer 33k reserved (không tính vào used) — Claude Code dành chỗ cho compact summary khi context đầy.

## 2. Cài đặt

### Bước 1 — Backup config cũ (nếu có)

**macOS / Linux**

```bash
[ -d ~/.claude ] && cp -r ~/.claude ~/.claude.backup-$(date +%Y%m%d)
```

**Windows (PowerShell)**

```powershell
if (Test-Path "$env:USERPROFILE\.claude") {
  Copy-Item -Recurse -Force "$env:USERPROFILE\.claude" "$env:USERPROFILE\.claude.backup-$(Get-Date -Format yyyyMMdd)"
}
```

**Windows (CMD)**

```cmd
if exist "%USERPROFILE%\.claude" xcopy /E /I /H /Y "%USERPROFILE%\.claude" "%USERPROFILE%\.claude.backup\"
```

> CMD không có cách lấy timestamp gọn (phụ thuộc locale `%date%`) — backup folder tên cố định `.claude.backup`. Chạy lại sẽ ghi đè. Cần timestamp → dùng PowerShell.

### Bước 2 — Clone repo

Lệnh giống nhau trên cả 3 platform. Chạy ở thư mục bất kỳ — sẽ tạo folder `dotclaude/` ngay tại đó.

```bash
git clone https://github.com/MinhThang1009/dotclaude.git
```

> Sau khi sao chép xong ở Bước 3, có thể xóa `dotclaude/` — nó chỉ là staging.

### Bước 3 — Sao chép vào `~/.claude/`

Chạy script tương ứng với platform — script tạo junctions từ `~/.claude/` trỏ vào repo, sau đó tạo junctions/hardlinks cho từng plugin được chọn:

**Windows (PowerShell)**

```powershell
powershell -File dotclaude\scripts\create-symlinks.ps1
```

**macOS/Linux**

```bash
bash dotclaude/scripts/create-symlinks.sh
```

> **Cơ chế**: `~/.claude/hooks`, `rules`, `templates`, `output-styles`, `.claude-plugin` là **junctions** trỏ vào repo (không cần admin). Sửa file trong `dotclaude/` là Claude Code thấy ngay. `settings.json` và `memory/` là real file — intentionally local, không sync.
>
> **Chọn plugins**: sửa `.claude-load.txt` trong `dotclaude/` trước khi chạy script. Mỗi dòng là tên plugin (load tất cả) hoặc `plugin:skills` / `plugin:agents` / `plugin:commands`. File trống = load tất cả.
>
> **Rebuild sau khi đổi `.claude-load.txt`** (không cần chạy lại toàn bộ script):
> ```powershell
> powershell -File dotclaude\scripts\rebuild-links.ps1
> ```
>
> **Xem trạng thái junctions hiện tại**:
> ```powershell
> powershell -File dotclaude\scripts\check-links.ps1
> ```

### Bước 4 — Verify

Mở Claude Code trong project bất kỳ:

```text
/memory          # CLAUDE.md + rules đã load
/skills          # Skills đã đăng ký
/agents          # Subagents
/context         # Token usage breakdown — baseline nên < 5%
/doctor          # Chẩn đoán cấu hình
```

### Bước 5 — Mỗi project mới

**macOS / Linux**

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

# MCP servers (optional — chỉ copy nếu project dùng MCP)
cp ~/.claude/templates/project-mcp.json ./.mcp.json

# .gitignore
cat >> .gitignore <<'EOF'

# Claude Code
CLAUDE.local.md
.claude/settings.local.json
.claude/HANDOFF.md
EOF
```

**Windows (PowerShell)**

```powershell
cd C:\path\to\project

# CLAUDE.md mô tả project
Copy-Item "$env:USERPROFILE\.claude\templates\project-CLAUDE.md" ".\CLAUDE.md"

# Note cá nhân (gitignore)
Copy-Item "$env:USERPROFILE\.claude\templates\project-CLAUDE.local.md" ".\CLAUDE.local.md"

# Settings team (commit) + handoff slot (gitignore)
New-Item -ItemType Directory -Force -Path ".claude" | Out-Null
Copy-Item "$env:USERPROFILE\.claude\templates\project-settings.json" ".claude\settings.json"
Copy-Item "$env:USERPROFILE\.claude\templates\HANDOFF.md" ".claude\HANDOFF.md"

# MCP servers (optional — chỉ copy nếu project dùng MCP)
Copy-Item "$env:USERPROFILE\.claude\templates\project-mcp.json" ".\.mcp.json"

# .gitignore (append). -Encoding utf8 bắt buộc trên PS 5.1 (default UTF-16 LE BOM sẽ phá .gitignore).
Add-Content -Path ".gitignore" -Encoding utf8 -Value @"

# Claude Code
CLAUDE.local.md
.claude/settings.local.json
.claude/HANDOFF.md
"@
```

**Windows (CMD)**

```cmd
cd C:\path\to\project

:: CLAUDE.md mô tả project
copy /Y "%USERPROFILE%\.claude\templates\project-CLAUDE.md" ".\CLAUDE.md"

:: Note cá nhân (gitignore)
copy /Y "%USERPROFILE%\.claude\templates\project-CLAUDE.local.md" ".\CLAUDE.local.md"

:: Settings team (commit) + handoff slot (gitignore)
if not exist ".claude" mkdir ".claude"
copy /Y "%USERPROFILE%\.claude\templates\project-settings.json" ".claude\settings.json"
copy /Y "%USERPROFILE%\.claude\templates\HANDOFF.md" ".claude\HANDOFF.md"

:: MCP servers (optional — chỉ copy nếu project dùng MCP)
copy /Y "%USERPROFILE%\.claude\templates\project-mcp.json" ".\.mcp.json"

:: .gitignore (append)
(
echo.
echo # Claude Code
echo CLAUDE.local.md
echo .claude/settings.local.json
echo .claude/HANDOFF.md
) >> .gitignore
```

Sau đó sửa `CLAUDE.md` mô tả: tech stack, lệnh build/test/lint, convention RIÊNG project (KHÔNG lặp lại global).

## 3. File nào KHÔNG đặt ở `~/.claude/` global

| File                    | Vị trí đúng                             | Lý do                           |
| ----------------------- | --------------------------------------- | ------------------------------- |
| `CLAUDE.md` (project)   | `<project>/CLAUDE.md`                   | Context riêng từng repo, COMMIT |
| `CLAUDE.local.md`       | `<project>/CLAUDE.local.md`             | Note cá nhân, **GITIGNORE**     |
| `.mcp.json` (team)      | `<project>/.mcp.json`                   | MCP team-share, COMMIT          |
| `settings.local.json`   | `<project>/.claude/settings.local.json` | Override cá nhân, GITIGNORE     |
| `HANDOFF.md`            | `<project>/.claude/HANDOFF.md`          | Brief chuyển session, GITIGNORE |
| `managed-settings.json` | OS path                                 | Chỉ admin enterprise            |

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

| Cơ chế                 | Mục đích                                                                      |
| ---------------------- | ----------------------------------------------------------------------------- |
| **CLAUDE.md**          | Hướng dẫn cần load **MỌI session** — giữ ngắn (<100 dòng)                     |
| **rules/** auto-import | Rule áp dụng MỌI session                                                       |
| **plugins/**           | Nhóm agents + skills theo domain — install qua `claude plugin install` hoặc junction |
| **hooks**              | Hành động **BẮT BUỘC** chạy mỗi lần (CLAUDE.md là gợi ý, hooks deterministic) |
| **MCP**                | Tool ngoài (Notion, Figma, DB, GitHub…)                                       |
| **`permissions.deny`** | Chặn Claude đọc file nhạy cảm (`.env`, `*.key`) hoặc thư mục lớn (build, lockfile) — đây là cách ChÍNH THỨC, không có `.claudeignore` trong docs |

**Quy tắc vàng**: Mỗi dòng trong CLAUDE.md trả lời được câu hỏi *"Nếu xóa dòng này, Claude có làm sai không?"*. Nếu KHÔNG → xóa.

## 6. Quản lý context window — 4 cấp độ tối ưu

### Cấp 1 — Giảm baseline (token cố định mỗi session)

- CLAUDE.md global gọn (<100 dòng).
- CLAUDE.md project chỉ chứa thông tin RIÊNG project, KHÔNG lặp global.
- Chỉ auto-import rule thực sự cần MỌI session.
- Skill ít dùng → set `disable-model-invocation: true`.
- Disable MCP server không dùng cho phiên hiện tại.
- `permissions.deny` trong `settings.json` chặn Claude đọc lockfile/asset lớn/`dist/`/`node_modules/` (vd: `Read(**/node_modules/**)`, `Read(**/*.lock)`).

### Cấp 2 — Giảm runtime (token tích trong phiên)

- `/clear` aggressive giữa task không liên quan.
- Subagent cho investigation rộng.
- `!command` thay paste output dài.
- `@file` thay copy-paste code.
- `/btw` cho câu hỏi không cần lưu history.
- Output dài → redirect file rồi `tail`/`grep`.
- Tắt thinking khi không cần (`Alt+T`).

### Cấp 3 — Compact thông minh

- Theo dõi `/context` — sweet spot 30-40%, "dumb zone" 40-60%, action ở 60%. Source: [Dex Horthy — MLOps Community](https://youtu.be/YwZR6tc7qYg?t=1541) (thresholds + "dumb zone"), [Thariq via howborisusesclaudecode.com](https://howborisusesclaudecode.com/) (1M model), [Boris Cherny X tweet](https://x.com/bcherny/status/1977163445205450783) (155k auto-compact). Trích dẫn đầy đủ tại [docs/REFERENCE.md §16](docs/REFERENCE.md#16-quản-lý-context-window--chi-tiết).
- Kết thúc 1 phase công việc → `/compact` ngay (đừng đợi auto-compact ~77% / 155k tokens).
- `/compact <chỉ thị>` để hướng (vd: `giữ phần API, drop test debug`).
- [`Compact Instructions`](CLAUDE.md#compact-instructions) trong CLAUDE.md để hướng auto-compact (đã có sẵn trong template).

### Cấp 4 — Session handoff (khi compact không đủ)

- Skill [`/handoff`](plugins/session/skills/handoff/SKILL.md) tự động tạo brief 5-10 dòng.
- Brief save vào `<project>/.claude/HANDOFF.md`.
- Session mới → `Đọc .claude/HANDOFF.md và tiếp tục` thay vì `--resume`.
- **Brief-injection > resume** vì resume kéo theo stale tool output.

## 7. Phiên bản tương thích

Bộ cấu hình này yêu cầu tối thiểu **Claude Code v2.1.111** (do dùng `model: opus[1m]` + `effortLevel: xhigh` — Opus 4.7 cần v2.1.111+). Khuyến nghị **v2.1.117+** để `/model` ghi vào `.claude/settings.local.json` đúng cách khi project pin model khác.

```bash
claude --version
claude update
```

Cụ thể các tính năng cần:
- ✅ v2.0.20+: skills system (v2.1.0 thêm hot-reload + fork sub-agent + `agent` field)
- ✅ v2.1.59+: auto memory (`/memory`)
- ✅ v1.0.81+: output styles built-in (Explanatory, Learning)
- ✅ v2.1.111+: Opus 4.7, `effortLevel: xhigh` (Opus 4.7 exclusive)
- ✅ v2.1.117+: `/model` selection persist across restart kể cả khi project pin model khác

### 7.1 Nếu plan/account không hỗ trợ Opus 4.7 + 1M context

Default repo set `model: "opus[1m]"` + `effortLevel: "xhigh"` — phù hợp Max/Team plan trên Anthropic API. Account khác cần sửa `settings.json`:

| Plan / Provider                | Sửa `model`                                  | Sửa `effortLevel`            |
| ------------------------------ | -------------------------------------------- | ---------------------------- |
| **Pro / Team Standard**        | `"sonnet"` (Opus rate-limit nhanh hơn)       | `"high"` hoặc `"xhigh"`      |
| **Free / không Opus 1M**       | `"opus"` (bỏ `[1m]`) hoặc `"sonnet"`         | `"high"`                     |
| **Bedrock / Vertex / Foundry** | Pin full ID per provider — Bedrock: `"anthropic.claude-opus-4-7"`, Vertex: `"claude-opus-4-7"` (Foundry: check provider docs) | `"high"` (xhigh chỉ Opus 4.7) |
| **Account giới hạn ngân sách** | `"haiku"`                                    | bỏ hoặc để trống (haiku không support effort — setting bị ignore) |

Sau sửa, restart Claude Code (`exit` rồi `claude`) để apply. Verify bằng `/model` và `/effort`.

### 7.2 Dependency cho hooks (`settings.json`)

3 hook trong `settings.json` (PreToolUse chặn lệnh nguy hiểm, PostToolUse auto-format, SessionStart show git status) gọi các tool dưới shell. Cần cài sẵn:

| Tool                             | Bắt buộc                              | macOS / Linux                           | Windows                                                        |
| -------------------------------- | ------------------------------------- | --------------------------------------- | -------------------------------------------------------------- |
| `bash`                           | ✅ Bắt buộc (mọi hook)                | Có sẵn                                  | Cần Git Bash (đi kèm Git for Windows) hoặc WSL                 |
| `python` (3.x)                   | ✅ Bắt buộc (hook parse JSON input)   | Có sẵn (macOS/Linux) hoặc `brew install python` | `winget install Python.Python.3.12` hoặc Microsoft Store |
| `git`                            | ✅ Bắt buộc (SessionStart hook)       | Có sẵn                                  | Git for Windows                                                |
| `jq`                             | ⏸️ Optional (chỉ cần nếu user viết hook custom dùng jq) | `brew install jq` / `apt install jq` | `winget install jqlang.jq` |
| `prettier`                       | ⏸️ Optional (auto-format JS/TS/JSON/MD) | `npm i -g prettier`                     | `npm i -g prettier`                                            |
| `ruff`                           | ⏸️ Optional (auto-format Python code)  | `pip install ruff`                      | `pip install ruff`                                             |
| `gofmt`                          | ⏸️ Optional (auto-format Go)           | Có sẵn khi cài Go                       | Có sẵn khi cài Go                                              |
| `rustfmt`                        | ⏸️ Optional (auto-format Rust)         | `rustup component add rustfmt`          | `rustup component add rustfmt`                                 |

> **Note**: Hook scripts dùng `python` thay `jq` để parse JSON input vì `jq` không có sẵn trên Windows git bash. Khi fork repo và viết hook custom theo style `jq`, thêm `jq` vào dependency.

Hook **silent skip** (không error) nếu tool optional thiếu — đã handle bằng `command -v`. Nhưng nếu thiếu `bash`, `python`, hoặc `git` thì hook fail và Claude Code sẽ log warning trong `/doctor`. Verify nhanh:

```bash
which bash python git    # macOS/Linux
where.exe bash python git    # Windows
```

### 7.3 Defense layers — coverage hook bash-guard

Hook `bash-guard.py` chặn các pattern nguy hiểm sau (verified bằng 119 test case):

| Threat | Coverage | Vector ví dụ |
|---|---|---|
| Đọc file nhạy cảm qua Bash | ✅ | `cat .env`, `python -c "open('.env')"`, `cp .env /tmp`, `< .env` redirect |
| Network exfiltration | ✅ | `curl --data @.env`, `nc < .env`, `socat`, `telnet` |
| Pipe download → execute | ✅ | `curl \| bash`, `eval $(curl)`, `source <(curl)`, 2-step `curl -o /tmp/x && bash /tmp/x` |
| Force push branch | ✅ | `git push --force/-f/--force-with-lease/--force-if-includes`, `git push origin +main`, `git -c push.default=current push` |
| Recursive delete root/home | ✅ | `rm -rf /`, `rm --recursive --force ~`, `find / -delete`, `find ~ -exec rm` |
| Disk wipe | ✅ | `dd of=/dev/sda` (block device write) |
| Fork bomb | ✅ | `:(){:\|:&};:` |

**Sensitive paths được protect** (Read deny + Bash hook):
`.env*`, `*.env`, `.envrc`, `*.pem`, `*.key`, `*.p12`, `*.jks`, `id_rsa*`, `id_ed25519*`, `~/.aws/credentials`, `~/.aws/config`, `~/.netrc`, `~/.npmrc`, `~/.pypirc`, `~/.docker/config.json`, `~/.kube/config`, `**/credentials.json`, `**/serviceAccount*.json`, `**/firebase-adminsdk*.json`.

**Safe metadata commands** (PASS với sensitive path): `ls`, `stat`, `file`, `wc -l`, `find -name/-type`, `realpath`, `dirname`, `basename`, `which`, `type`, `echo`, `printf`. (List metadata, không reveal content.)

**Format hook hardening**: skip nếu file ngoài `$CLAUDE_PROJECT_DIR`. Skip prettier nếu có config `.prettierrc.js/.cjs/.mjs` (RCE risk: `require()` execute code).

**Limits cần biết**:
- Hook là **defense-in-depth deterministic**, không thay thế user judgment với permission `ask`.
- Variable-resolved path không được bắt: `FILE=.env cat $FILE` (cần dynamic shell parsing).
- Quoted path: `cat "/path with space/.env"` — quote có thể phá pattern. Hiếm gặp.
- Hook chỉ chạy với Bash tool. Nếu Claude dùng Read/Edit/Write tool, áp dụng permission rules thay.

Verify hook coverage tại máy local:
```bash
bash ~/.claude/hooks/test-bash-guard.sh    # Expect: Total 119, PASS 119, FAIL 0
```

### 7.4 Eval-driven skill optimization (optional)

Sau khi dùng skills 1 thời gian, có thể measure xem description trigger có chính xác / output có quality không. Theo [agentskills.io/skill-creation/evaluating-skills](https://agentskills.io/skill-creation/evaluating-skills):

**Workflow 5 bước:**
1. **Tạo test cases** — `<skill>/evals/evals.json` với prompt + expected_output + assertions. Template sẵn ở `templates/skill-evals.json`.
2. **Run dual** — mỗi prompt chạy 2 lần: với skill và baseline (no skill / version cũ). Subagent isolation để clean context.
3. **Grade** — assertion check qua LLM hoặc script. Output `grading.json` với pass/fail + evidence.
4. **Aggregate** — `benchmark.json` summary tokens/duration/pass rate. Compute delta with-vs-without skill.
5. **Iterate** — feed eval signals + current SKILL.md vào LLM, ask propose changes. Rerun.

**Khi nào nên eval:**
- Skill **không trigger** đúng prompt user kỳ vọng (vd: nói "review code" mà `/code-review` không invoke)
- Output **inconsistent** giữa các run (cùng prompt, kết quả khác nhau)
- Muốn so sánh skill mới vs version cũ trước khi merge

**Tools:**
- `skill-creator` skill từ [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — automate eval loop end-to-end (split train/validation, parallel runs, propose improvements).
- Manual: copy `templates/skill-evals.json` → `<skill>/evals/evals.json`, customize, run thủ công.

**Lưu ý**: eval chi tiết cần Claude Code session thực với log + multiple runs (model nondeterministic). Đây là tooling NÂNG CAO — không bắt buộc cho usage cơ bản.

## 8. Tài liệu tham khảo

- Tài liệu chính thức: <https://code.claude.com/docs>
- Best practices: <https://code.claude.com/docs/en/best-practices>
- Cheatsheet đầy đủ: xem [`REFERENCE.md`](docs/REFERENCE.md)
- Session management: <https://claude.com/blog/using-claude-code-session-management-and-1m-context>
- Troubleshooting (lỗi phổ biến + fix): xem [`REFERENCE.md` §18 "Common failures & fix"](docs/REFERENCE.md#18-common-failures--fix)
- License: [MIT](LICENSE)
- Đóng góp: [`CONTRIBUTING.md`](.github/CONTRIBUTING.md)
- Lịch sử thay đổi: [`CHANGELOG.md`](CHANGELOG.md)

## 9. Marketplace

Repo này có `marketplace.json` (tại `.claude-plugin/marketplace.json`), cho phép dùng trực tiếp làm plugin marketplace trong Claude Code:

```bash
claude plugin marketplace add https://github.com/MinhThang1009/dotclaude
```

Sau đó install plugin muốn dùng:

```bash
claude plugin install pr-review-toolkit@minhthang-plugins
claude plugin install feature-dev@minhthang-plugins
claude plugin install plan-workflow@minhthang-plugins
# ... hoặc bất kỳ plugin nào trong 38 plugins
```

**38 plugins hiện có** (xem `.claude-plugin/marketplace.json` để đầy đủ):

| Plugin | Loại | Mô tả ngắn |
| --- | --- | --- |
| `pr-review-toolkit` | agents + skills | Review PR: comment, test, type design, silent failures |
| `feature-dev` | agents + skills | Phát triển tính năng: architecture, codebase exploration |
| `commit-commands` | skills | Git workflow: commit, commit-push-pr, clean-gone |
| `debug` | agents + skills | Debug: reproduce → failing test → fix |
| `documentation` | agents | Viết/maintain docs, Next.js specialist |
| `test-toolkit` | agents | Viết test, đánh giá coverage |
| `security-guidance` | agents | Security audit OWASP |
| `performance` | agents | Profiling, dependency audit |
| `code-modernization` | agents | Architecture review, adversarial analysis |
| `code-simplifier` | skills | Refactor + simplification |
| `hookify` | agents + skills | Tạo hooks ngăn unwanted behaviors |
| `frontend-design` | skills | UI distinctive, tránh AI slop |
| `session` | skills | context-check, handoff |
| `claude-md-management` | skills | Audit và cải thiện CLAUDE.md |
| `plugin-dev` | skills | Phát triển plugin (agent/skill/hook/mcp/command) |
| `claude-api` | skills | Anthropic API reference và examples |
| `claude-code-setup` | skills | Setup Claude Code cho project mới |
| `code-review` | agents + skills | Code review chuyên sâu |
| `doc-coauthoring` | agents + skills | Đồng tác giả tài liệu kỹ thuật |
| `docx` | skills | Làm việc với file Word (.docx) |
| `explanatory-output-style` | output-styles | Style output chi tiết, giải thích từng bước |
| `learning-output-style` | output-styles | Style output giải thích để học |
| `mcp-builder` | agents + skills | Xây dựng MCP server |
| `mcp-server-dev` | agents + skills | Phát triển MCP server nâng cao |
| `pdf` | skills | Làm việc với file PDF |
| `playwright` | agents + skills | Test automation với Playwright |
| `pptx` | skills | Làm việc với file PowerPoint (.pptx) |
| `session-report` | skills | Tạo báo cáo tổng kết session |
| `skill-creator` | agents + skills | Tạo và tối ưu skills |
| `theme-factory` | skills | Tạo theme UI |
| `web-artifacts-builder` | skills | Xây dựng web artifacts |
| `webapp-testing` | agents + skills | Test web application |
| `xlsx` | skills | Làm việc với file Excel (.xlsx) |
| `plan-workflow` | skills | 8-phase implementation plan workflow với 3 human gates |
| `subagent-system` | agents + skills | Pipeline multi-agent: checkpoint, chain-verifier, task-partitioner |
| `audit-plan` | skills | Audit plan file: gap detection, dead code, test coverage |
| `logic-audit` | skills + hooks | Audit logic: đọc từng dòng code, tìm bug thật, fix kèm test |
| `verify-then-draw` | agents + skills | Vẽ sơ đồ UML/kiến trúc khớp code thật qua 3 tier gate |

## 10. Cấu trúc nội bộ — lý do thiết kế

Câu hỏi thường gặp:

### 10.1 Tại sao tất cả rules đều auto-load?

5 rules (`communication`, `security`, `verification`, `coding-standards`, `git-workflow`) auto-load mọi session. Coding conventions và git workflow áp dụng cho hầu hết mọi task nên đưa vào rules/ thay vì để user `@`-reference thủ công.

### 10.2 Tại sao [REFERENCE.md](docs/REFERENCE.md) không auto-load vào [CLAUDE.md](CLAUDE.md)?

[REFERENCE.md](docs/REFERENCE.md) = ~2145 dòng, ~166k chars → ~57k tokens (Vietnamese mix ~3 chars/token). Auto-load = ~28% context Sonnet 200k (hoặc ~5.7% Opus 1M) mỗi session. REFERENCE phục vụ **NGƯỜI** tra cứu (mở trên màn hình thứ 2 / web), KHÔNG cho Claude đọc.

### 10.3 Tại sao bỏ `/init-context`?

Overlap với `/init` built-in của Claude Code v2.1+. Đã bỏ để tránh duplicate.

### 10.4 Tại sao commit message tiếng Việt nhưng branch name tiếng Anh?

Branch name vào `git log --oneline` và nhiều tool (Linear, Jira, GitHub Action) parse được khi tiếng Anh chuẩn ASCII. Commit message hiển thị cho dev đọc → tiếng Việt giúp đọc nhanh. Type/scope giữ tiếng Anh để tool Conventional Commit parse được.
