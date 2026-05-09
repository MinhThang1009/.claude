# Bộ cấu hình Global cho Claude Code (`~/.claude/`)

[![CI](https://github.com/MinhThang1009/dotclaude/actions/workflows/ci.yml/badge.svg)](https://github.com/MinhThang1009/dotclaude/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Tổng hợp từ tài liệu chính thức Anthropic ([code.claude.com](https://code.claude.com/docs), [platform.claude.com](https://platform.claude.com/docs)), [Engineering Blog](https://www.anthropic.com/engineering), [blog claude.com](https://www.claude.com/blog), [MindStudio](https://www.mindstudio.ai/blog), [ClaudeFast](https://claudefa.st/blog), và best practices cộng đồng GitHub. Áp dụng MỌI project. Tối ưu cho **dev người Việt** — tiếng Việt cho comment/log/commit, tiếng Anh chuẩn convention cho identifier.

> 👉 Lần đầu xem repo? Đọc [**INTRODUCTION.md**](INTRODUCTION.md) cho overview ngắn 1 phút.

> 📅 **Đã verify**: 2026-05-09 vs Claude Code v2.1.138 + Opus 4.7. Model ID, version-gating, env var, slash command, hook event đã cross-check với [docs Anthropic](https://code.claude.com/docs) + [raw CHANGELOG](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md).
>
> ⚠️ **Một số nội dung có thể outdated** khi Anthropic ship version mới hoặc deprecate model. Phát hiện sai sót → submit issue/PR tại [github.com/MinhThang1009/dotclaude/issues](https://github.com/MinhThang1009/dotclaude/issues). Xem [CONTRIBUTING.md](CONTRIBUTING.md) cho quy trình. Lịch sử thay đổi: [CHANGELOG.md](CHANGELOG.md).

## 1. Cấu trúc thư mục sau khi cài

```text
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
├── hooks/                          # Hook scripts (gọi từ settings.json)
│   ├── bash-guard.py               # Engine pattern matching (Python) — defense layer chính
│   ├── bash-guard.sh               # Wrapper minimal gọi python
│   ├── format-on-edit.sh           # PostToolUse: prettier/ruff/gofmt/rustfmt (skip nếu file ngoài project)
│   └── test-bash-guard.sh          # Regression test 97 case (dev-only, có thể xóa)
└── templates/                      # Template COPY vào TỪNG project / skill mới
    ├── project-CLAUDE.md           # → <project>/CLAUDE.md
    ├── project-CLAUDE.local.md     # → <project>/CLAUDE.local.md
    ├── project-settings.json       # → <project>/.claude/settings.json
    ├── project-mcp.json            # → <project>/.mcp.json
    ├── HANDOFF.md                  # → <project>/.claude/HANDOFF.md (gitignored)
    └── skill-evals.json            # → <skill>/evals/evals.json (eval-driven optimize)
```

**Baseline tokens** — đo thực tế bằng `/context` (Opus 4.7 1M context, snapshot session start):

| Category                      | Tokens     | % of 1M   |
| ----------------------------- | ---------- | --------- |
| System prompt                 | 8,500      | 0.8%      |
| System tools                  | 12,100     | 1.2%      |
| Memory files                  | 6,200      | 0.6%      |
| ├── `CLAUDE.md`               | 2,300      | —         |
| ├── `rules/security`          | 2,100      | —         |
| └── `rules/communication`     | 1,800      | —         |
| Skills                        | 939        | <0.1%     |
| Custom agents                 | 590        | <0.1%     |
| ├── `security-auditor`        | 177        | —         |
| ├── `architect`               | 150        | —         |
| ├── `code-reviewer`           | 135        | —         |
| └── `test-writer`             | 128        | —         |
| Messages (start)              | 13         | <0.1%     |
| **Total used (start)**        | **28,342** | **~2.8%** |
| Autocompact buffer (reserved) | 33,000     | 3.3%      |
| Free space                    | 938,658    | 93.9%     |

**Ghi chú**:
- Vietnamese tokenize ~2.3 chars/token cho prose (kém hiệu quả hơn English ~4 chars/token); baseline 28.3k cao hơn config English (~10-15k) là expected.
- 2 references còn lại ([`coding-standards.md`](references/coding-standards.md), [`git-workflow.md`](references/git-workflow.md)) chỉ load khi `@`-reference → KHÔNG ăn baseline.
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

**macOS / Linux**

```bash
mkdir -p ~/.claude
cp -r dotclaude/. ~/.claude/
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude" | Out-Null
# -Force trên Get-ChildItem mới include được hidden file (.gitignore...)
Get-ChildItem -Path dotclaude -Force | Copy-Item -Destination "$env:USERPROFILE\.claude\" -Recurse -Force
```

**Windows (CMD)**

```cmd
if not exist "%USERPROFILE%\.claude" mkdir "%USERPROFILE%\.claude"
xcopy /E /I /Y /H dotclaude\* "%USERPROFILE%\.claude\"
```

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
| **rules/** auto-import | Rule áp dụng MỌI session — chỉ 1-2 file thật cần                              |
| **references/**        | Rule theo chủ đề — `@`-reference khi cần (tiết kiệm context)                  |
| **skills/**            | Workflow tái sử dụng — load **ON-DEMAND** khi gọi                             |
| **agents/**            | Task chuyên biệt cần **context window riêng**                                 |
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

- Theo dõi `/context` — sweet spot <40%, action ở >60%.
- Kết thúc 1 phase công việc → `/compact ngay` (đừng đợi auto ở 95%).
- `/compact <chỉ thị>` để hướng (vd: `giữ phần API, drop test debug`).
- "Compact Instructions" trong CLAUDE.md để hướng auto-compact (đã có sẵn trong template).

### Cấp 4 — Session handoff (khi compact không đủ)

- Skill [`/handoff`](skills/handoff/SKILL.md) tự động tạo brief 5-10 dòng.
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
| **Account giới hạn ngân sách** | `"haiku"`                                    | `"medium"` (haiku không support effort) |

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

Hook `bash-guard.py` chặn các pattern nguy hiểm sau (verified bằng 97 test case):

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
bash ~/.claude/hooks/test-bash-guard.sh    # Expect: Total 97, PASS 97, FAIL 0
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
- Cheatsheet đầy đủ: xem [`REFERENCE.md`](REFERENCE.md)
- Session management: <https://claude.com/blog/using-claude-code-session-management-and-1m-context>

## 9. Cấu trúc nội bộ — lý do thiết kế

Câu hỏi thường gặp:

### 9.1 Tại sao chỉ import 2 rules thay vì 4?

Baseline context tính tiền theo mỗi message. 4 rules = thêm ~6000 tokens × mỗi turn × cả phiên = lãng phí. Chỉ import 2 rule áp dụng MỌI turn (`communication`, `security`); 2 rule còn lại để Claude đọc khi cần (qua REFERENCE hoặc user `@`-reference).

### 9.2 Tại sao [REFERENCE.md](REFERENCE.md) không auto-load vào [CLAUDE.md](CLAUDE.md)?

[REFERENCE.md](REFERENCE.md) = ~2050 dòng, ~158k chars → ~55k tokens (Vietnamese prose ~2.3 chars/token, code blocks/tables ~3-4 chars/token, mix ~2.9). Auto-load = ~28% context Sonnet 200k (hoặc ~5.5% Opus 1M) mỗi session. REFERENCE phục vụ **NGƯỜI** tra cứu (mở trên màn hình thứ 2 / web), KHÔNG cho Claude đọc.

### 9.3 Tại sao bỏ `/init-context`?

Overlap với `/init` built-in của Claude Code v2.1+. Đã bỏ để tránh duplicate.

### 9.4 Tại sao commit message tiếng Việt nhưng branch name tiếng Anh?

Branch name vào `git log --oneline` và nhiều tool (Linear, Jira, GitHub Action) parse được khi tiếng Anh chuẩn ASCII. Commit message hiển thị cho dev đọc → tiếng Việt giúp đọc nhanh. Type/scope giữ tiếng Anh để tool Conventional Commit parse được.
