# REFERENCE — Cheatsheet Claude Code

> File này KHÔNG load vào session — chỉ để bạn tra cứu khi cần. Tổng hợp từ docs chính thức `code.claude.com/docs` (2026), blog `claude.com`, MindStudio, ClaudeFast, GitHub `anthropics/claude-code`. Cập nhật cho Claude Code v2.1.x trở lên.

## Mục lục

1. [Lệnh CLI](#1-lệnh-cli)
2. [CLI flags](#2-cli-flags)
3. [Slash commands trong session](#3-slash-commands-trong-session)
4. [Phím tắt](#4-phím-tắt)
5. [Prefix message](#5-prefix-trong-message)
6. [Magic words & effort levels](#6-magic-words--effort-levels)
7. [Cấu trúc `.claude/`](#7-cấu-trúc-claude)
8. [SKILL.md frontmatter](#8-skillmd-frontmatter)
9. [Subagent frontmatter](#9-subagent-frontmatter)
10. [Output styles](#10-output-styles-built-in)
11. [settings.json — keys hay dùng](#11-settingsjson--keys-hay-dùng)
12. [Environment variables](#12-environment-variables)
13. [Hook events đầy đủ](#13-hook-events--đầy-đủ-29-event)
14. [Hook handler types](#14-hook-handler-types-5-loại)
15. [Workflow patterns](#15-workflow-patterns)
16. [Quản lý context window — chi tiết](#16-quản-lý-context-window--chi-tiết)
17. [Session management & handoff](#17-session-management--handoff)
18. [Common failures & fix](#18-common-failures--fix)
19. [Khi nào dùng feature nào](#19-khi-nào-dùng-feature-nào)
20. [Tài liệu chính thức](#20-tài-liệu-chính-thức)
21. [Checklist & mẹo cuối](#21-checklist--mẹo-cuối)

---

## 1. Lệnh CLI

| Lệnh | Mục đích |
|---|---|
| `claude` | Mở session interactive trong thư mục hiện tại |
| `claude "<query>"` | Session với prompt khởi đầu |
| `claude -p "<query>"` | Non-interactive (1-shot) — dùng trong CI/script |
| `cat file \| claude -p "<q>"` | Process piped content |
| `claude -c` | Tiếp session gần nhất (alias `--continue`) ⚠️ kéo theo stale context |
| `claude -c -p "<q>"` | Continue qua SDK |
| `claude -r "<session>" "<q>"` | Resume session theo ID/name (alias `--resume`) |
| `claude --version` | Xem version |
| `claude update` | Cập nhật |
| `claude install [version]` | Cài/cài lại native binary (`stable`, `latest`, hoặc `2.1.x`) |
| `claude doctor` | Chẩn đoán cấu hình |
| `claude auth login` | Đăng nhập (`--email`, `--sso`, `--console`) |
| `claude auth logout` | Đăng xuất |
| `claude auth status` | Trạng thái auth (JSON; `--text` cho human-readable) |
| `claude agents` | List subagent đã cấu hình |
| `claude auto-mode defaults` | Print built-in rules auto-mode classifier (JSON) |
| `claude auto-mode config` | Print effective config (với settings đã apply) |
| `claude auto-mode critique` | AI feedback trên custom allow/soft_deny rules |
| `claude mcp add <name> <url>` | Thêm MCP server |
| `claude mcp list` | List MCP server |
| `claude mcp remove <name>` | Xóa MCP server |
| `claude mcp serve` | Expose Claude Code như MCP server |
| `claude plugin install <name>@<marketplace>` | Cài plugin từ marketplace |
| `claude plugin list` | List plugin đã cài |
| `claude project purge [path]` | Xóa local state của project (transcripts, debug log…). Flags: `--dry-run`, `-y`, `-i`, `--all` |
| `claude remote-control` | Chạy server mode cho Remote Control từ claude.ai/app |
| `claude setup-token` | Tạo long-lived OAuth token cho CI |
| `claude ultrareview [target]` | Non-interactive ultrareview. Flags: `--json`, `--timeout <minutes>` |

> **Brief-injection > resume**: với session dài, mở session mới và paste handoff brief thường tốt hơn `--resume` vì resume kéo theo stale tool output, file content cũ. Tham khảo skill `/handoff`.

---

## 2. CLI flags

### Khởi tạo & input
| Flag | Mục đích |
|---|---|
| `-p`, `--print` | Print mode (non-interactive, 1-shot) |
| `-c`, `--continue` | Tiếp session gần nhất trong dir hiện tại |
| `-r`, `--resume <id\|name>` | Resume session theo ID/name |
| `--fork-session` | Khi resume, tạo session ID mới (giữ nguyên session cũ) |
| `--from-pr <number\|url>` | Resume session liên kết với PR cụ thể |
| `--add-dir <path>` | Thêm thư mục làm việc cho session |
| `--bare` | Minimal mode — skip auto-discovery hooks/skills/plugins/MCP/CLAUDE.md (dùng cho script tốc độ cao) |
| `--init-only` | Chạy `Setup` + `SessionStart` hooks rồi exit |
| `--init` | Chạy Setup hooks với matcher `init` (chỉ trong `-p` mode) |

### Model & effort
| Flag | Mục đích |
|---|---|
| `--model <alias\|id>` | `opus`, `sonnet`, `haiku`, hoặc full ID (`claude-opus-4-7`) |
| `--effort <level>` | `low`, `medium`, `high`, `xhigh`, `max` (max chỉ Opus 4.6+) |
| `--fallback-model <alias>` | Fallback khi default overload (chỉ print mode) |
| `--betas <header>` | Beta header cho API (chỉ API key user) |

### Permission & tool
| Flag | Mục đích |
|---|---|
| `--permission-mode <mode>` | `default`, `auto`, `plan`, `bypassPermissions` |
| `--dangerously-skip-permissions` | = `--permission-mode bypassPermissions` ⚠️ chỉ trong sandbox |
| `--allow-dangerously-skip-permissions` | Cho phép `bypassPermissions` trong Shift+Tab cycle |
| `--allowedTools "<rules>"` | Pre-approve tool/lệnh không hỏi |
| `--disallowedTools "<rules>"` | Loại tool khỏi context |
| `--tools "<rules>"` | Giới hạn tool có thể dùng |
| `--disable-slash-commands` | Tắt mọi skill + command |

### System prompt
| Flag | Mục đích |
|---|---|
| `--system-prompt "<text>"` | **Thay thế** toàn bộ system prompt |
| `--system-prompt-file <path>` | Thay thế từ file |
| `--append-system-prompt "<text>"` | Append vào default system prompt |
| `--append-system-prompt-file <path>` | Append từ file |
| `--exclude-dynamic-system-prompt-sections` | Move per-machine sections (cwd, env, git status) khỏi system prompt → cải thiện prompt-cache |

### Subagent
| Flag | Mục đích |
|---|---|
| `--agent <name>` | Chỉ định agent cho session |
| `--agents '<json>'` | Define subagent động (JSON) |

### Output & debug
| Flag | Mục đích |
|---|---|
| `--output-format json\|stream-json\|text` | Format output (chỉ `-p` mode) |
| `--include-hook-events` | Include hook events trong stream (`stream-json`) |
| `--include-partial-messages` | Include partial streaming events |
| `--verbose` | Verbose logging, show full turn-by-turn output |
| `--debug [<categories>]` | Bật debug — vd `"api,mcp,!file"` |
| `--debug-file <path>` | Ghi debug log vào file |
| `--mcp-debug` | Debug MCP riêng |

### IDE & integration
| Flag | Mục đích |
|---|---|
| `--ide` | Auto-connect IDE khi startup |
| `--chrome` | Bật Chrome integration |
| `--no-chrome` | Tắt Chrome integration cho session |

### Session & execution control
| Flag | Mục đích |
|---|---|
| `--name`, `-n` | Đặt tên session (hiện trong `/resume` và terminal title) |
| `--session-id <id>` | Dùng session ID cụ thể |
| `--max-turns <N>` | Giới hạn số agentic turn (chỉ print mode) |
| `--max-budget-usd <N>` | Giới hạn chi phí API (USD, chỉ print mode) |
| `--json-schema <schema>` | Output JSON theo schema (chỉ print mode) |
| `--input-format text\|stream-json` | Format input cho print mode |
| `--no-session-persistence` | Không lưu session ra disk (chỉ print mode) |
| `--maintenance` | Chạy Setup hooks matcher `maintenance` (chỉ print mode) |
| `--settings <path\|json>` | Load settings từ file hoặc inline JSON |
| `--setting-sources <list>` | Chọn scope settings: `user`, `project`, `local` |

### MCP & plugin
| Flag | Mục đích |
|---|---|
| `--mcp-config <path\|json>` | Load MCP server từ file/JSON |
| `--strict-mcp-config` | Chỉ dùng MCP từ `--mcp-config`, bỏ qua config khác |
| `--plugin-dir <path>` | Load plugin từ thư mục hoặc `.zip` (session-only) |
| `--plugin-url <url>` | Fetch plugin `.zip` từ URL (session-only) |

### Cloud & worktree
| Flag | Mục đích |
|---|---|
| `--remote "<task>"` | Tạo web session mới trên claude.ai |
| `--remote-control`, `--rc` | Bật Remote Control cho session |
| `--teleport` | Pull web session vào terminal local |
| `--worktree`, `-w` | Chạy trong isolated git worktree |
| `--tmux` | Tạo tmux session cho worktree (cần `--worktree`) |
| `--teammate-mode auto\|in-process\|tmux` | Hiển thị agent team teammate |

### Channels (research preview)
| Flag | Mục đích |
|---|---|
| `--channels <list>` | MCP channel notifications (`plugin:<name>@<marketplace>`) |
| `--dangerously-load-development-channels` | Cho channel ngoài allowlist |

---

## 3. Slash commands trong session

> Type `/` để xem full list, `/<letters>` để filter. `<arg>` = required, `[arg]` = optional. Marked **[Skill]** = bundled skill (Claude có thể auto-invoke).

### Quản lý session & context
| Lệnh | Mục đích |
|---|---|
| `/help` | List commands |
| `/clear` | XÓA HẲN context, reset session. Aliases: `/reset`, `/new` |
| `/compact [instructions]` | Nén context. VD: `/compact giữ phần API change, drop test debug` |
| `/context` | Visualize context usage + tối ưu suggestion |
| `/rewind` | Rollback conversation/code, hoặc "Summarize from here" (alias `Esc Esc`, `/checkpoint`) |
| `/branch [name]` | Phân nhánh session (giữ nguyên session cũ). Alias `/fork` |
| `/btw <question>` | Hỏi nhanh không vào history (overlay dismissible) |
| `/resume [session]` | Resume theo ID/name. Alias `/continue` |
| `/rename [name]` | Đặt tên session (auto-gen nếu để trống) |
| `/exit` | Thoát CLI. Alias `/quit` |
| `/desktop` | Continue trong Desktop app (macOS/Windows). Alias `/app` |
| `/teleport` | Pull web session vào terminal. Alias `/tp` |
| `/copy [N]` | Copy response thứ N gần nhất (mặc định 1) |
| `/export [filename]` | Export conversation thành plain text |

### Memory & rules
| Lệnh | Mục đích |
|---|---|
| `/memory` | Edit CLAUDE.md, auto-memory |
| `/init` | Tạo CLAUDE.md cho project (`CLAUDE_CODE_NEW_INIT=1` để interactive flow) |

### Cấu hình
| Lệnh | Mục đích |
|---|---|
| `/config` | Settings UI (theme, model, output style…). Alias `/settings` |
| `/permissions` | Sửa allow/ask/deny rule. Alias `/allowed-tools` |
| `/hooks` | Xem hook configurations |
| `/mcp` | Manage MCP server, OAuth |
| `/skills` | List skill có sẵn |
| `/agents` | Manage subagent (interactive create/edit) |
| `/model [model]` | Đổi model. Mũi tên trái/phải để adjust effort |
| `/effort [level]` | `low`/`medium`/`high`/`xhigh`/`max`/`auto`. `low|medium|high|xhigh` persist; `max` session-only |
| `/output-style` | Đổi output style |
| `/output-style:new` | Tạo style mới với Claude help |
| `/keybindings` | Sửa keybindings |
| `/terminal-setup` | Cấu hình Shift+Enter cho terminal |
| `/sandbox` | Toggle sandbox mode |
| `/theme` | Đổi color theme |
| `/color [name\|hex]` | Set màu prompt bar |
| `/statusline` | Cấu hình status line |
| `/fast [on\|off]` | Toggle fast mode (chỉ Opus 4.6, giá 2.5× standard) |
| `/voice` | Toggle voice dictation |
| `/privacy-settings` | View/update privacy (Pro/Max) |

### Plan & workflow
| Lệnh | Mục đích |
|---|---|
| `/plan [description]` | Vào plan mode (Claude chỉ đọc, không sửa) |
| `Shift+Tab` ×2 | Toggle plan mode |
| `Shift+Tab` ×1 | Toggle auto-accept mode |

### Bundled skills (Claude có thể auto-invoke)
| Lệnh | Mục đích |
|---|---|
| `/batch <instruction>` | **[Skill]** Orchestrate large-scale change song song qua git worktree |
| `/claude-api` | **[Skill]** Load API reference cho ngôn ngữ project |
| `/debug [description]` | **[Skill]** Bật debug logging + troubleshoot |
| `/loop [interval] [prompt]` | **[Skill]** Chạy prompt lặp định kỳ. VD `/loop 5m check deploy`. Alias `/proactive` |
| `/simplify [focus]` | **[Skill]** Spawn 3 review agent, fix issue |
| `/security-review` | **[Skill]** Phân tích git diff tìm lỗ hổng |

### Cloud & remote
| Lệnh | Mục đích |
|---|---|
| `/remote-control` | Bật remote control session từ claude.ai/app. Alias `/rc` |
| `/remote-env` | Cấu hình remote env cho web session |
| `/web-setup` | Connect GitHub cho Claude Code on the web |
| `/autofix-pr [prompt]` | Spawn web session auto-fix PR |
| `/ultraplan <prompt>` | Draft plan trong browser, execute remotely |
| `/schedule [description]` | Tạo/edit/list/run routine định kỳ. Alias `/routines` |
| `/install-github-app` | Cài Claude GitHub Actions |
| `/install-slack-app` | Cài Claude Slack |
| `/setup-bedrock` | Cấu hình Amazon Bedrock |
| `/setup-vertex` | Cấu hình Google Vertex AI |

### Tasks & monitoring
| Lệnh | Mục đích |
|---|---|
| `/tasks` | List/manage background tasks. Alias `/bashes` |
| `/diff` | Interactive diff viewer (uncommitted + per-turn) |
| `/cost` | Token usage statistics |
| `/usage` | Plan limit + rate limit |
| `/stats` | Daily usage, sessions, streaks |
| `/status` | Settings (Status tab) |
| `/insights` | Report sessions, friction patterns |

### Plugin
| Lệnh | Mục đích |
|---|---|
| `/plugin` | Browser plugin marketplace |
| `/reload-plugins` | Reload plugin không restart |

### Khác
| Lệnh | Mục đích |
|---|---|
| `/login`, `/logout` | Auth |
| `/upgrade` | Upgrade plan |
| `/extra-usage` | Cấu hình extra usage khi hit rate limit |
| `/passes` | Share free week với bạn |
| `/feedback [report]` | Submit feedback. Alias `/bug` |
| `/release-notes` | Xem changelog |
| `/team-onboarding` | Generate onboarding guide từ usage history |
| `/powerup` | Quick interactive lessons về Claude Code features |
| `/mobile` | QR code download Claude mobile. Aliases `/ios`, `/android` |
| `/stickers` | Order Claude Code stickers |
| `/ide` | Manage IDE integrations |
| `/chrome` | Cấu hình Claude in Chrome |

### Thêm lệnh mới (v2.1.83+)
| Lệnh | Mục đích |
|---|---|
| `/add-dir <path>` | Thêm thư mục làm việc cho session hiện tại |
| `/doctor` | Chẩn đoán cấu hình, nhấn `f` để Claude auto-fix |
| `/fewer-permission-prompts` | **[Skill]** Scan transcript → thêm allowlist vào `.claude/settings.json` |
| `/focus` | Toggle focus view (chỉ hiện prompt cuối + response cuối) |
| `/heapdump` | Ghi heap snapshot + memory breakdown (debug OOM) |
| `/recap` | Tóm tắt 1 dòng session hiện tại (auto chạy sau 3+ phút idle) |
| `/review [PR]` | Review PR locally (nhẹ hơn `/ultrareview`) |
| `/tui [default\|fullscreen]` | Đổi UI renderer (`fullscreen` = flicker-free alt-screen) |
| `/ultrareview [PR]` | Multi-agent code review chạy trên cloud sandbox |

### Đã loại bỏ / deprecated
- `/vim` — Removed v2.1.92. Dùng `/config` → Editor mode
- `/pr-comments` — Removed v2.1.91. Hỏi Claude trực tiếp xem PR comments

### MCP prompts
MCP server có thể expose prompt thành command: `/mcp__<server>__<prompt>`.

---

## 4. Phím tắt

### Điều hướng & ngắt
| Phím | Tác dụng |
|---|---|
| `Esc` | Dừng Claude (giữ context) |
| `Esc` ×2 | Mở rewind menu |
| `Ctrl+C` | Thoát hẳn |
| `Ctrl+D` | Logout / exit |

### Soạn message
| Phím | Tác dụng |
|---|---|
| `Shift+Enter` (sau `/terminal-setup`) | Newline |
| `\` + `Enter` | Newline (universal fallback) |
| `Ctrl+J` | Insert newline |
| `Option+Enter` (macOS) | Newline |
| `Ctrl+G` | Mở `$EDITOR` để soạn message dài |
| `Ctrl+V` | Paste image từ clipboard (KHÔNG `Cmd+V`) |
| `Shift+drag` | Drag file vào input |

### Modes (Shift+Tab cycle)
| Mode | Mô tả |
|---|---|
| Edit (default) | Hỏi trước khi modify |
| Auto-accept (`Shift+Tab`×1) | Tự sửa file không hỏi |
| Plan (`Shift+Tab`×2) | Chỉ research, không sửa |
| `bypassPermissions` (nếu bật `--allow-dangerously-skip-permissions`) | Skip mọi permission ⚠️ |

### Text editing (readline)
| Phím | Tác dụng |
|---|---|
| `Ctrl+A` | Đầu dòng |
| `Ctrl+E` | Cuối dòng |
| `Ctrl+K` | Xóa đến cuối dòng |
| `Ctrl+U` | Xóa đến đầu dòng |
| `Ctrl+W` | Xóa word trước |
| `Ctrl+Y` | Paste text đã xóa |
| `Alt+B` / `Alt+F` | Lùi/tiến 1 word |

> Vim mode: bật qua `/config` → Editor mode → `vim`. Full vi keybindings (NORMAL/INSERT/VISUAL).

### Khác
| Phím | Tác dụng |
|---|---|
| `Ctrl+O` | Toggle transcript viewer |
| `Ctrl+R` | Reverse search command history (cycle scope: `Ctrl+S`) |
| `Ctrl+T` | Toggle task list |
| `Ctrl+B` | Background task đang chạy (tmux user: nhấn 2 lần) |
| `Ctrl+L` | Redraw screen |
| `Ctrl+F` ×2 trong 3s | Kill mọi background agent |
| `Alt+T` | Toggle extended thinking |
| `Alt+O` | Toggle fast mode |
| `Cmd/Ctrl+Click` PR link | Mở PR trong browser |

### Transcript viewer (khi `Ctrl+O` mở)
| Phím | Tác dụng |
|---|---|
| `[` | Ghi conversation vào scrollback (dùng Cmd+F tìm) |
| `v` | Mở trong `$VISUAL`/`$EDITOR` |
| `q` / `Esc` | Thoát viewer |

---

## 5. Prefix trong message

| Prefix | Tác dụng |
|---|---|
| `!<command>` | Chạy bash, output → context (không qua LLM) |
| `@<file>` | Reference file vào context |
| `@<directory>/` | Reference cả thư mục |
| `@<url>` | Fetch URL (cần allow domain) |
| `#<note>` | Save vào memory (deprecated v2.1+, dùng `/memory`) |
| `&<task>` | Background task trên Cloud Code (Pro/Max) |

### Tính năng input mới (v2.1.83+)

- **Shell mode**: gõ `!` ở đầu prompt → chạy lệnh trực tiếp, real-time output, không cần Claude approve. `Ctrl+B` để background. `Escape`/`Backspace` thoát.
- **Prompt suggestions**: gợi ý xám xuất hiện sau khi mở session hoặc Claude trả lời. `Tab`/`→` accept, `Enter` accept + submit. Tắt: `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=false` hoặc `/config`.

---

## 6. Magic words & effort levels

### Magic words trong prompt

Chỉ **`ultrathink`** được nhận diện là keyword (kích hoạt budget ~32k thinking tokens). Các cụm `think`, `think hard`, `megathink`… là **plain text**, không trigger thinking budget đặc biệt — dùng `/effort` thay.

### `/effort` levels (chính thức 2026)
| Level | Model mặc định | Ghi chú |
|---|---|---|
| `low` | — | Không thinking |
| `medium` | — | Thinking nhẹ |
| `high` | Opus 4.6, Sonnet 4.6 | Default cho hầu hết model |
| `xhigh` | Opus 4.7 | Chỉ Opus 4.7; model khác fallback → `high` |
| `max` | — | Tối đa, chỉ Opus 4.6+ session, session-only |
| `auto` | — | Reset model default |

`low`/`medium`/`high`/`xhigh` persist qua session; `max` session-only (trừ khi set qua `CLAUDE_CODE_EFFORT_LEVEL` env var). `Alt+T` toggle thinking. `Alt+O` toggle fast mode. `MAX_THINKING_TOKENS=0` để tắt hoàn toàn. `CLAUDE_CODE_EFFORT_LEVEL` env var override tất cả.

Opus 4.7 dùng **adaptive reasoning** (thinking tùy bước, không cố định budget). Opus 4.6/Sonnet 4.6 dùng fixed budget. Tắt adaptive: `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`.

---

## 7. Cấu trúc `.claude/`

### Project (`<project>/`)
```
CLAUDE.md                        # Hướng dẫn project, COMMIT git
CLAUDE.local.md                  # Note cá nhân, GITIGNORE
.mcp.json                        # MCP server cho team, COMMIT
.claudeignore                    # File Claude bỏ qua khi đọc, COMMIT
.worktreeinclude                 # File gitignore cần copy vào worktree
.claude/
├── settings.json                # Setting team, COMMIT
├── settings.local.json          # Setting cá nhân, GITIGNORE auto
├── HANDOFF.md                   # (Optional) Brief chuyển session, GITIGNORE
├── rules/*.md                   # Topic rule, có thể path-gated
├── skills/<name>/SKILL.md       # Skill project
├── commands/*.md                # (Legacy, merge với skills v2.1.101+)
├── agents/*.md                  # Subagent project
├── output-styles/*.md           # Output style project
├── hooks/*.{sh,py,js}           # Hook scripts
└── agent-memory/<name>/         # Persistent memory cho subagent
```

### Global (`~/.claude/`)
```
CLAUDE.md                        # Áp dụng MỌI project
settings.json                    # Setting global cá nhân
~/.claude.json                   # App state, OAuth, MCP cá nhân (auto, KHÔNG sửa tay)
keybindings.json                 # Phím tắt custom
rules/*.md
skills/<name>/SKILL.md
commands/*.md
agents/*.md
output-styles/*.md
agent-memory/<name>/
themes/<name>.json               # Custom color theme (v2.1.118+)
projects/<project-hash>/
└── memory/                      # Auto memory, KHÔNG sửa tay
```

### Enterprise / managed
```
CLAUDE.md                        # Org-wide instructions, không thể exclude
managed-settings.json            # Org-wide policy, override mọi thứ
managed-mcp.json                 # MCP server bắt buộc
```
- macOS: `/Library/Application Support/ClaudeCode/`
- Linux: `/etc/claude-code/`
- Windows: `C:\ProgramData\ClaudeCode\`

### Session memory (auto, đọc-only)
```
~/.claude/projects/<hash>/<session>/session_memory   # Backing store cho /compact
```

---

## 8. SKILL.md frontmatter

```yaml
---
name: <kebab-case>                    # Optional (default = tên folder). Lowercase, số, hyphen, max 64 ký tự
description: <what + when>            # Recommended — Claude dùng để auto-invoke
allowed-tools: Read Grep Bash(git:*)  # Space-separated, comma-separated, hoặc YAML list
disable-model-invocation: false       # true → chỉ user gọi (không Claude tự load)
user-invocable: true                  # false → chỉ Claude gọi (ẩn khỏi /menu)
argument-hint: "<gợi ý đối số>"
arguments:                            # Named positional args → dùng $name trong body
  - name: target
  - name: scope
when_to_use: "<trigger phrases>"      # Bổ sung description, giúp auto-invoke chính xác hơn
paths: ["src/**/*.ts", "*.config.*"]  # Glob patterns giới hạn khi nào skill activate
model: opus|sonnet|haiku|inherit
context: fork                         # fork → run trong subagent isolated
agent: Explore|Plan|general-purpose   # Subagent type khi context: fork
effort: low|medium|high|xhigh|max
shell: bash|powershell                # Shell cho !`command` blocks
hooks:
  PreToolUse: ...
once: false                           # true → chạy 1 lần per session rồi remove (chỉ skill)
---

Nội dung markdown — instructions cho Claude khi skill được gọi.

$ARGUMENTS                            # Full argument string
$ARGUMENTS[N]                         # Argument thứ N (0-based)
$0, $1, $2                            # Positional args (shell-style quoting)
$name                                 # Named arg (từ `arguments` frontmatter)
!`<bash command>`                     # Chạy bash, output inject vào prompt
@<file>                               # Reference file
${CLAUDE_SESSION_ID}                  # Env var substitution
${CLAUDE_EFFORT}                      # Effort level hiện tại
${CLAUDE_SKILL_DIR}                   # Thư mục chứa SKILL.md
```

**Rules**:
- `name`: lowercase-kebab-case, NO consecutive hyphens, NO leading/trailing hyphen.
- `description`: third-person nếu tiếng Anh ("This skill should be used when…"). Tiếng Việt OK ("Dùng khi…"). Tránh behavioral instructions ("Always respond in JSON") trong description — đó vào body.
- `allowed-tools` ≠ permission bypass. Global `deny` vẫn thắng.

**Tip giảm context**:
- Set `disable-model-invocation: true` cho skill ít dùng → chỉ load khi user gọi explicit (description + body đều không vào context startup).
- Skill có `disable-model-invocation: false` (default): description vào context lúc startup, body load on-demand khi Claude quyết định gọi.

---

## 9. Subagent frontmatter

```yaml
---
name: <kebab-case>                    # Required
description: <khi nào delegate>       # Required
tools: Read, Grep, Glob, Bash         # Optional — omit thì inherit thread tools
model: opus|sonnet|haiku|inherit      # Optional, default inherit
isolation: worktree                   # Optional — copy isolated repo qua git worktree
skills: [my-skill, another-skill]     # Optional — pre-load skills vào subagent
disallowedTools: [WebFetch]           # Optional — block tools cụ thể
maxTurns: 20                          # Optional — giới hạn số turn
permissionMode: plan                  # Optional — default|acceptEdits|plan|auto|bypassPermissions
memory: project                       # Optional — user|project|local
background: false                     # Optional — true = non-blocking execution
effort: high                          # Optional — low|medium|high|xhigh|max
color: "#4A90D9"                      # Optional — màu hiển thị trong UI
---

System prompt cho subagent (toàn bộ markdown body sau frontmatter).
```

Lưu ý:
- Subagent **chỉ nhận system prompt này** (không có default Claude Code system prompt).
- Subagent có **context window riêng** — không ăn context chính.
- `cd` trong subagent KHÔNG persist qua tool call.
- Khi `isolation: worktree`, subagent chạy trong git worktree riêng → không ảnh hưởng main working tree.
- Model override chỉ áp dụng trong turn đó, không lưu vào settings.

---

## 10. Output styles (built-in)

3 style mặc định (set qua `/output-style <name>` hoặc `outputStyle` trong settings):

| Style | Mô tả | Token cost |
|---|---|---|
| `Default` | System prompt mặc định cho coding | Thấp |
| `Explanatory` | Thêm "★ Insight" giáo dục về implementation choice | +20-40% |
| `Learning` | Pair-programming mode, để `TODO(human)` cho user code phần chiến lược | Cao nhất |

Custom style trong `~/.claude/output-styles/<name>.md` hoặc `<project>/.claude/output-styles/<name>.md`:

```yaml
---
name: My Style
description: Brief description shown in /config picker
keep-coding-instructions: true        # default: false; true → giữ default coding instructions
---

# Hướng dẫn style
...
```

> **Quan trọng**: Output style THAY THẾ phần software-engineering của default system prompt (nếu `keep-coding-instructions: false`). CLAUDE.md thì BỔ SUNG, không thay thế. `--append-system-prompt` cũng append, không replace.

---

## 11. settings.json — keys hay dùng

```jsonc
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "claude-opus-4-7",
  "outputStyle": "Default",            // hoặc "Explanatory", "Learning", custom name
  "language": "vietnamese",            // for voice dictation language
  "theme": "dark-daltonized",          // theme

  "attribution": {
    "commit": "",                      // Tắt Co-Authored-By Claude
    "pr": ""
  },

  "permissions": {
    "allow":   ["Bash(git status)", "Read(**)"],
    "ask":     ["Bash(git push:*)", "Edit(**)"],
    "deny":    ["Bash(rm -rf /*)", "Read(.env)"]
  },

  "hooks": {
    "PreToolUse":   [...],
    "PostToolUse":  [...],
    "SessionStart": [...],
    // ... 29 events available, see Section 13
  },

  "env": {
    "MAX_THINKING_TOKENS": "0",
    "MAX_MCP_OUTPUT_TOKENS": "10000"   // default 10k, tăng nếu cần (max 500k)
  },

  // Memory / context
  "autoMemoryEnabled": true,
  "claudeMdExcludes": ["**/node_modules/**/CLAUDE.md"],

  // Skills override
  "skillOverrides": {
    "some-skill-name": {
      "disable-model-invocation": true  // Tắt auto-invoke cho skill bên thứ 3
    }
  },

  // MCP project
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["memory", "github"],
  "disabledMcpjsonServers": ["filesystem"],

  // Sandbox
  "sandbox": { "enabled": false },

  // File suggestion
  "fileSuggestion": {
    "type": "command",
    "command": "~/.claude/file-suggestion.sh"
  },

  // Cleanup
  "cleanupPeriodDays": 30,
  "plansDirectory": "./plans",
  "showClearContextOnPlanAccept": true,
  "autoUpdatesChannel": "latest",        // "stable" | "latest"

  // Auto mode
  "autoMode": {
    "environment": ["$defaults", "Source control: github.com/my-org"],
    "allow": ["$defaults"],            // Override block rules
    "soft_deny": ["$defaults"]         // Override allow rules
  },

  // Editor & UI
  "editorMode": "normal",             // "normal" | "vim"
  "effortLevel": "high",              // "low" | "medium" | "high" | "xhigh"
  "tui": "default",                   // "default" | "fullscreen" (alt-screen)
  "viewMode": "default",              // "default" | "verbose" | "focus"
  "defaultShell": "bash",             // "bash" | "powershell"
  "awaitSummaryEnabled": true,        // Session recap sau idle
  "showThinkingSummaries": false,     // Show extended thinking summaries
  "showTurnDuration": true,

  // Memory
  "autoMemoryDirectory": "~/.claude/memory",

  // Voice + UI
  "voiceEnabled": false,              // DEPRECATED — dùng voice.enabled
  "spinnerVerbs": { "mode": "append", "verbs": ["Cooking", "Architecting"] },
  "spinnerTipsEnabled": true,
  "prefersReducedMotion": false,

  // Status line
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  },

  // Auth & model routing
  "apiKeyHelper": "~/.claude/get-api-key.sh",  // Script trả về API key
  "agent": "my-custom-agent",          // Chạy main thread như subagent cụ thể
  "modelOverrides": {                  // Map model → provider-specific ID
    "claude-opus-4-7": "arn:aws:bedrock:..."
  },
  "alwaysThinkingEnabled": false,      // true = force extended thinking mọi response
  "preferredNotifChannel": "auto",     // auto|terminal_bell|iterm2|notifications_disabled

  // Worktree
  "worktree": {
    "symlinkDirectories": ["node_modules", ".cache"],  // Symlink thay vì copy
    "sparsePaths": ["src/", "tests/"]  // Sparse checkout cho monorepo
  },

  // Proxy & network
  "skipWebFetchPreflight": false,      // true = skip WebFetch domain safety check

  // Hook safety (managed-only)
  "disableAllHooks": false,             // Tắt mọi hook (debug)
  "allowManagedHooksOnly": false,       // (managed) chỉ managed hooks
  "allowManagedPermissionRulesOnly": false  // (managed) chỉ managed perm rules
}
```

### Permission rule syntax
- `Bash(git status)` — lệnh chính xác
- `Bash(git status:*)` — lệnh + bất kỳ args
- `Bash(git *)` — bất kỳ subcommand bắt đầu bằng `git`
- `Read(.env)` — file cụ thể
- `Read(**)` — mọi file
- `Read(./secrets/**)` — recursive trong dir
- `Edit(*.ts)` — pattern theo extension
- `WebFetch(*)` — bất kỳ URL
- `WebFetch(domain:example.com)` — domain cụ thể
- `Agent(Explore)` — subagent type cụ thể
- `Agent(my-custom-agent)` — custom subagent

Compound commands (`&&`, `||`) được split — mỗi phần match riêng. Process wrapper (`timeout`, `nice`, `nohup`, `stdbuf`, `xargs`) tự strip khi match.

---

## 12. Environment variables

| Var | Mục đích |
|---|---|
| `ANTHROPIC_API_KEY` | API key (nếu không OAuth) |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Override alias `opus` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Override alias `sonnet` |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Override alias `haiku` |
| `MAX_THINKING_TOKENS` | Cap thinking tokens (0 = disable) |
| `MAX_MCP_OUTPUT_TOKENS` | Cap MCP output (default 10k, tăng nếu cần) |
| `MCP_TIMEOUT` | Timeout MCP server start (ms) |
| `CLAUDE_PROJECT_DIR` | Path project root (auto, đọc trong hook) |
| `CLAUDE_SESSION_ID` | ID session hiện tại (auto, dùng trong hook/skill) |
| `CLAUDE_TOOL_INPUT` | JSON input của tool (trong hook) |
| `CLAUDE_TOOL_INPUT_COMMAND` | Bash command (trong hook PreToolUse:Bash) |
| `CLAUDE_TOOL_INPUT_FILE_PATH` | File path (trong hook Edit/Write) |
| `CLAUDE_CODE_NEW_INIT=1` | Bật `/init` interactive multi-phase |
| `CLAUDE_CODE_TASK_LIST_ID` | ID persistent cho task list |
| `CLAUDE_CODE_USE_BEDROCK=1` | Dùng Amazon Bedrock |
| `CLAUDE_CODE_USE_VERTEX=1` | Dùng Google Vertex AI |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` | Dùng PowerShell thay bash trên Windows |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable analytics |
| `CLAUDE_CODE_DEBUG_LOGS_DIR` | Dir cho debug logs |
| `CLAUDE_CODE_SIMPLE` | Set bởi `--bare` flag |
| `ANTHROPIC_BASE_URL` | Override API endpoint (proxy/gateway) |
| `ANTHROPIC_MODEL` | Override model mặc định |
| `ANTHROPIC_AUTH_TOKEN` | Custom Authorization header |
| `CLAUDE_CODE_EFFORT_LEVEL` | Override effort level (ưu tiên cao nhất) |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` | Tắt adaptive reasoning (Opus 4.7) |
| `CLAUDE_CODE_DISABLE_THINKING` | Tắt extended thinking |
| `CLAUDE_CODE_SHELL` | Override shell detection |
| `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION` | Bật/tắt prompt suggestions (default `true`) |
| `ENABLE_TOOL_SEARCH` | MCP tool search: `true` (always on), `auto` (>10% context), `auto:N` (custom %), `false` (load hết) |
| `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` | Max parallel tool execution (default 10) |
| `API_TIMEOUT_MS` | API timeout (default 600000 = 10 phút) |
| `BASH_DEFAULT_TIMEOUT_MS` | Bash timeout (default 120000 = 2 phút) |
| `BASH_MAX_TIMEOUT_MS` | Bash max timeout (default 600000) |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | Context window cho auto-compaction |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Trigger auto-compact (default ~95%) |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | Override context window size |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model cho subagent |
| `CLAUDECODE` | Set trong spawned shells (dùng để detect Claude env) |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | Tắt auto memory |
| `CLAUDE_CODE_GIT_BASH_PATH` | Path tới Git Bash (Windows) |
| `CLAUDE_CODE_NO_FLICKER` | `1` = bật fullscreen rendering mặc định |
| `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` | `1` = force classic renderer |
| `CLAUDE_CODE_SCROLL_SPEED` | Tốc độ cuộn mouse (1-20, default auto) |
| `CLAUDE_CODE_DISABLE_MOUSE` | `1` = tắt mouse capture (giữ flicker-free, cho phép native text select) |
| `HTTPS_PROXY` / `HTTP_PROXY` | Proxy cho network requests |
| `NO_PROXY` | Domains bỏ qua proxy (space hoặc comma-separated) |
| `CLAUDE_CODE_CERT_STORE` | CA cert source: `bundled` (default), `system`, `both` |
| `NODE_EXTRA_CA_CERTS` | Path tới custom CA cert file |
| `CLAUDE_CONFIG_DIR` | Override đường dẫn ~/.claude |
| `CLAUDE_CODE_MAX_RETRIES` | Số lần retry khi API fail (default 10) |
| `DISABLE_TELEMETRY` | Tắt toàn bộ telemetry/metrics |
| `DISABLE_ERROR_REPORTING` | Tắt Sentry error reporting |
| `DISABLE_PROMPT_CACHING` | `1` = tắt prompt caching |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` = bật agent teams (experimental) |
| `ANTHROPIC_VERTEX_PROJECT_ID` | GCP project ID cho Vertex AI |
| `CLOUD_ML_REGION` | Region cho Vertex AI (vd: `us-east5`, `global`) |
| `ANTHROPIC_FOUNDRY_RESOURCE` | Azure Foundry resource name |
| `ANTHROPIC_FOUNDRY_API_KEY` | Azure Foundry API key |
| `ANTHROPIC_BEDROCK_BASE_URL` | Override Bedrock endpoint URL |
| `ANTHROPIC_VERTEX_BASE_URL` | Override Vertex AI endpoint URL |
| `ANTHROPIC_FOUNDRY_BASE_URL` | Override Foundry endpoint URL |
| `ANTHROPIC_CUSTOM_MODEL_OPTION` | Custom model ID cho `/model` picker |
| `ANTHROPIC_CUSTOM_MODEL_OPTION_NAME` | Display name cho custom model |
| `ANTHROPIC_BETAS` | Comma-separated beta header values |
| `ANTHROPIC_CUSTOM_HEADERS` | Custom HTTP headers (`Name: Value`) |
| `CLAUDE_CODE_CLIENT_CERT` | Path tới mTLS client certificate |
| `CLAUDE_CODE_CLIENT_KEY` | Path tới mTLS client key |
| `CLAUDE_CODE_DISABLE_FAST_MODE` | `1` = tắt fast mode hoàn toàn |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | `1` = tắt 1M context window |
| `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT` | `1` = system prompt ngắn hơn (Opus 4.7) |
| `CLAUDE_CODE_SKIP_PROMPT_HISTORY` | `1` = không lưu transcript ra disk |
| `BASH_MAX_OUTPUT_LENGTH` | Max ký tự bash output |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | Token limit cho file reads |
| `CLAUDE_CODE_DEBUG_LOG_LEVEL` | Log level: `verbose`\|`debug`\|`info`\|`warn`\|`error` |

---

## 13. Hook events — đầy đủ 29 event

Hook chạy DETERMINISTIC (KHÔNG phụ thuộc Claude nhớ rule). Định nghĩa trong `settings.json`, plugin, hoặc skill/agent frontmatter.

### Per-session
| Event | Khi fire | Matcher |
|---|---|---|
| `SessionStart` | Đầu session/resume | `startup`, `resume`, `clear`, `compact` |
| `Setup` | `--init-only` hoặc `-p --init/--maintenance` | `init`, `maintenance` |
| `SessionEnd` | Cuối session | `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` |

### Per-turn
| Event | Khi fire | Matcher |
|---|---|---|
| `UserPromptSubmit` | Mỗi message user | (none) |
| `UserPromptExpansion` | Khi command expand thành prompt | command names — có thể block expansion |
| `Stop` | Claude finish response | (none) |
| `StopFailure` | Turn end vì API error | `rate_limit`, `authentication_failed`, `oauth_org_not_allowed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown` |

### Per-tool-call (agentic loop)
| Event | Khi fire | Matcher |
|---|---|---|
| `PreToolUse` | Trước tool call | tool name, vd `Bash`, `Edit\|Write`, `mcp__.*` |
| `PermissionRequest` | Khi permission dialog xuất hiện | tool name |
| `PermissionDenied` | Khi tool bị auto-mode classifier deny | tool name — return `{retry: true}` cho phép retry |
| `PostToolUse` | Sau tool call thành công | tool name |
| `PostToolUseFailure` | Sau tool call fail | tool name |
| `PostToolBatch` | Sau batch tool call song song xong | (none) |

### Subagent & task
| Event | Khi fire | Matcher |
|---|---|---|
| `SubagentStart` | Subagent spawn | agent type (`Explore`, `Plan`, `general-purpose`, custom) |
| `SubagentStop` | Subagent finish | agent type |
| `TaskCreated` | Task được tạo qua TaskCreate | (none) |
| `TaskCompleted` | Task được mark complete | (none) |

### Compact
| Event | Khi fire | Matcher |
|---|---|---|
| `PreCompact` | Trước compact | `manual`, `auto` |
| `PostCompact` | Sau compact xong | `manual`, `auto` |

### Async events (notification, file, config…)
| Event | Khi fire | Matcher |
|---|---|---|
| `Notification` | Claude gửi notification | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_complete`, `elicitation_response` |
| `TeammateIdle` | Agent team teammate idle | (none) |
| `InstructionsLoaded` | CLAUDE.md / `.claude/rules/*.md` được load | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| `ConfigChange` | Config file thay đổi trong session | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `CwdChanged` | Working dir thay đổi (`cd`) | (none) — useful cho direnv |
| `FileChanged` | File watch trên disk thay đổi | filenames, vd `.envrc\|.env` |
| `WorktreeCreate` | Tạo worktree (`--worktree` hoặc `isolation: "worktree"`) | (none) |
| `WorktreeRemove` | Xóa worktree | (none) |
| `Elicitation` | MCP server xin input | MCP server name |
| `ElicitationResult` | User trả lời elicitation | MCP server name |

### Matcher syntax
| Format | Đánh giá là | Ví dụ |
|---|---|---|
| `"*"`, `""`, omit | Match tất cả | Fire mọi occurrence |
| Chữ/digit/`_`/`\|` | Exact string hoặc list | `Bash`, `Edit\|Write` |
| Có ký tự khác | JS regex | `^Notebook`, `mcp__memory__.*` |

### Filter chi tiết với `if`
Trong hook handler, dùng `if` (permission rule syntax):
```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "if": "Bash(git push *)",          // Chỉ fire khi Bash command match git push
      "command": "/path/to/safety.sh"
    }
  ]
}
```

---

## 14. Hook handler types (5 loại)

```jsonc
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          // Type 1: command — shell command
          {
            "type": "command",
            "command": "/path/to/handler.sh",
            "timeout": 30,                // default 600s
            "async": false,               // chạy background không block
            "asyncRewake": false,         // background + wake Claude khi exit 2
            "shell": "bash"               // hoặc "powershell" trên Windows
          },
          // Type 2: http — POST request
          {
            "type": "http",
            "url": "http://localhost:8080/hook",
            "headers": { "Authorization": "Bearer $TOKEN" },
            "allowedEnvVars": ["TOKEN"]
          },
          // Type 3: mcp_tool — call MCP tool
          {
            "type": "mcp_tool",
            "server": "my_server",
            "tool": "security_scan",
            "input": { "file_path": "${tool_input.file_path}" }
          },
          // Type 4: prompt — LLM evaluation single-turn
          {
            "type": "prompt",
            "prompt": "Should this command run? $ARGUMENTS",
            "timeout": 30
          },
          // Type 5: agent — subagent decision (experimental)
          {
            "type": "agent",
            "prompt": "Verify $ARGUMENTS",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### Hook output (command/http)

Exit `0` = OK. Exit `2` = block tool, stderr → Claude. Stdout JSON cho control flow:
```json
{
  "decision": "allow|block|approve",
  "reason": "...",
  "updatedInput": { ... },
  "additionalContext": "...",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "..."
  }
}
```

---

## 15. Workflow patterns

### Pattern 1 — Explore → Plan → Code → Commit
```
1. Plan mode (Shift+Tab×2): "đọc src/auth, hiểu flow OAuth"
2. Plan mode: "viết plan thêm Google OAuth"
3. Exit plan: "implement plan, viết test, run test"
4. /commit
```

### Pattern 2 — Writer / Reviewer (2 session)
- Session A: implement.
- Session B (fresh context): review code A vừa viết.
- Session A: address feedback từ B.

### Pattern 3 — TDD (2 session)
- A: viết test cho spec.
- B (fresh): viết code pass test.

### Pattern 4 — Investigation (subagent)
- Main: "use a subagent to investigate how X works".
- Subagent đọc nhiều file, return summary ngắn.
- Main giữ context sạch để implement.

### Pattern 5 — Fan-out (parallel review)
```bash
git diff main --name-only > files.txt
for file in $(cat files.txt); do
  claude -p "review $file for security issues" \
    --allowedTools "Read,Grep" \
    --output-format json >> reviews.jsonl
done
```

### Pattern 6 — Worktree parallel
```bash
git worktree add ../proj-feat-a feat/a
git worktree add ../proj-feat-b feat/b
# Mở 2 terminal, claude trong mỗi worktree
```

### Pattern 7 — Brief-injection (long-running task)
- Session 1: làm việc, gần đầy context (>70%).
- `/handoff --save` → ghi `<project>/.claude/HANDOFF.md`.
- Thoát, mở session mới: `claude` (KHÔNG `--continue`).
- Prompt đầu: `Đọc .claude/HANDOFF.md và tiếp tục.`

### Pattern 8 — Bulk migration (`/batch`)
```
/batch migrate src/ from class components to hooks
```
→ Claude phân chia thành 5-30 unit, spawn 1 background agent / unit, mỗi cái mở PR riêng. Yêu cầu git repo.

### Pattern 9 — Loop monitoring
```
/loop 5m check if deploy finished, alert me when status changes
```

---

## 16. Quản lý context window — chi tiết

### Tại sao quan trọng

Mọi best practice xoay quanh 1 ràng buộc: **context window đầy nhanh, performance giảm khi đầy**. Mỗi message re-read toàn bộ history → cost grow exponential trong agentic session. Ở 80%+ context, Claude bắt đầu "quên" instruction sớm, lặp sai lầm cũ. Boris Cherny (tech lead Claude Code) giữ CLAUDE.md ~2,500 tokens.

### Ngưỡng hành động

| % context | Hành động |
|---|---|
| <40% | 🟢 Sweet spot, làm việc bình thường |
| 40-60% | 🟢 OK, để ý task lớn sắp tới |
| 60-70% | 🟡 Sau khi xong phase tiếp theo → `/compact` |
| 70-80% | 🟠 `/compact` HOẶC `/handoff + /clear` ngay |
| 80-95% | 🔴 DỪNG. Brief-injection sang session mới |
| 95%+ | Auto-compact firing — chất lượng đã giảm rồi |

### `/compact` vs `/clear`

| `/compact` | `/clear` |
|---|---|
| Nén history thành summary, GIỮ tiếp | XÓA HẲN history, fresh start |
| Cùng task, cần thread | Sang task khác, không cần lịch sử |
| Lossy nhưng có thread | Sạch hoàn toàn |
| Có thể `/compact <chỉ thị>` để hướng | Không nén, viết lại brief |

### Customize compaction

Thêm vào `CLAUDE.md`:
```markdown
## Compact Instructions
Khi compact, giữ:
- Files đã sửa (full path) + lý do từng file
- Quyết định kiến trúc đã chốt
- Lệnh build/test/lint của project
- Việc đang dở dang + bước tiếp theo
Bỏ: tool output dài, dead-end debugging.
```

Hoặc gọi runtime: `/compact tập trung phần auth, drop test debugging`.

### Giảm baseline (token cố định mỗi session)

| Nhóm | Giảm bằng cách |
|---|---|
| CLAUDE.md global | Giữ <100 dòng. Test "nếu xóa dòng này, Claude có làm sai không?" — không → xóa |
| CLAUDE.md project | Tương tự, focus vào convention RIÊNG project, KHÔNG lặp lại global |
| `rules/*.md` import | Chỉ import rule áp dụng MỌI session. Còn lại để `@`-reference khi cần |
| Skill descriptions | `disable-model-invocation: true` cho skill ít dùng → chỉ load khi user gọi |
| MCP tools | Disable MCP server không dùng cho phiên này. MCP v2.1+ deferred default — chỉ tool name load |
| `.claudeignore` | Loại file không bao giờ cần (lockfile, build output, asset binary...) |
| `--bare` flag | Skip auto-discovery cho script (hooks, skills, plugins, MCP, CLAUDE.md) |
| `--exclude-dynamic-system-prompt-sections` | Move per-machine sections → cải thiện prompt-cache |

### Giảm runtime (token tích lũy trong session)

- **`/clear` aggressive** giữa task không liên quan.
- **Subagent** cho investigation rộng (`use a subagent to ...`) — context riêng, return summary.
- **`!command`** thay vì paste output dài: `!grep -r "TODO" src/ | head -20` thay vì paste cả 500 line.
- **`@file`** thay vì copy-paste code (file content load 1 lần, không inflate qua mỗi turn).
- **`/btw <q>`** cho câu hỏi không cần lưu history.
- **Prompt ngắn**: front-load constraint, tránh "give me 3 options" (3× output tokens).
- **`/effort low`** khi không cần thinking nặng.
- Output dài (build log, test result, JSON >5KB) → redirect ra file rồi `tail`/`grep`:
  ```bash
  npm test > /tmp/test.log 2>&1; tail -50 /tmp/test.log
  ```

### Kiểm tra cái gì đang ăn token

```
/context
```
Output breakdown:
- System prompt
- Tools (built-in + MCP — MCP eats nhiều nếu nhiều server)
- Memory (CLAUDE.md + rules)
- Skills (descriptions)
- Conversation (messages + tool output + file content)

Mỗi nhóm chiếm % rõ ràng — fix nhóm > 15% trước.

### Gì survive `/compact`, gì mất

- **Survive**: project-root CLAUDE.md (re-read từ disk), auto memory (200 dòng hoặc 25KB đầu tiên)
- **Mất**: nested CLAUDE.md (sub-dir) — chỉ reload khi Claude đọc file trong dir đó
- **Mất**: skill descriptions chưa invoke — chỉ skills đã gọi trong session được giữ
- **Mất**: path-scoped rules — chỉ reload khi file matching được đọc lại
- **Mất**: conversation-only instructions (thêm vào CLAUDE.md nếu muốn persist)

---

## 17. Session management & handoff

### Khi nào dùng cái nào

```
Sắp đầy context, vẫn làm tiếp cùng task ──► /compact (có instructions)
Sắp đầy context, sang task khác ──────────► /handoff --save → /clear → brief mới
Câu hỏi nhanh không cần lưu ──────────────► /btw
Một message bị sai hướng ─────────────────► Esc Esc → rollback
Khôi phục trạng thái phiên trước ─────────► claude --continue (rủi ro stale data)
                                          HOẶC brief-injection (sạch hơn)
Fan-out task song song ───────────────────► claude -p ... background
Task riêng biệt cần context riêng ────────► subagent
Bulk migration nhiều file ────────────────► /batch
```

### Anti-pattern resume long session

Theo Anthropic blog `using-claude-code-session-management-and-1m-context` và bài "Stop Resuming Long Sessions, Brief Them Instead":
- Session dài tích lũy nhiều **noise > signal** (stale `ls`, file content cũ, deliberation đã đóng).
- `--continue` kéo theo cả mớ noise đó. Model treat tất cả là current.
- **Brief-injection**: viết 5-7 dòng (state, decisions+why, constraints, open items, next), inject vào session mới.

Brief template:
```markdown
Context phiên này:
- Đang làm: <branch/PR>, mục tiêu <X>
- Đã chốt: <decision A> vì <lý do>; <decision B> vì <lý do>
- Constraint: <perf, compat, security>
- File chính: <path1>, <path2>
- Đã thử nhưng không work: <approach C>
- Bước tiếp: <action cụ thể>
```

### Workflow handoff khuyến nghị

1. Khi `/context` >65%, hoặc kết thúc 1 phase công việc → gọi skill `/handoff` hoặc nói "viết handoff brief".
2. Save về `.claude/HANDOFF.md` (cần thêm vào `.gitignore` — xem Section 21 checklist).
3. `/compact giữ brief, drop debugging history` HOẶC `/clear` rồi prompt mới: `Đọc .claude/HANDOFF.md và tiếp tục từ "Bước tiếp"`.
4. Cuối ngày / cuối session → update HANDOFF.md → `git status` → commit work.

### Bad-compact recovery

Triệu chứng:
- Sau compact, Claude lặp lại sai lầm session trước.
- Claude "quên" file vừa sửa.
- Claude hỏi lại quyết định đã chốt.

Cách xử lý:
1. KHÔNG `/compact` lần nữa (compact context bẩn = bẩn tiếp).
2. Đọc lại HANDOFF.md cũ (nếu có) hoặc git log để khôi phục state.
3. `/clear`, mở session mới, brief-inject thủ công.

### Lỗi context-related

| Lỗi | Nguyên nhân thường gặp | Fix |
|---|---|---|
| `Internal server error (500)` consistent | Context quá lớn | `/compact` hoặc fresh session |
| `ECONNRESET` / `EPIPE` | Processing time-out vì context lớn | Tương tự |
| "Chat has reached its limit" | Hard context limit | `/clear` + brief-injection |
| Auto-compact "thrashing error" | 1 file/output quá lớn → context refill ngay sau compact | Loại file đó (`.claudeignore`) hoặc `/clear` |

---

## 18. Common failures & fix

| Pattern | Triệu chứng | Fix |
|---|---|---|
| Kitchen sink session | Context bẩn, Claude lú | `/clear` giữa task khác nhau |
| Correction loop | Sửa 2-3 lần vẫn sai | `/clear` + reprompt với info đã học |
| Bloated CLAUDE.md | Claude bỏ qua rule | Prune dòng, target <100 |
| Trust without verify | Code "chạy" nhưng buggy | Test/screenshot verify mọi output |
| Infinite exploration | Claude đọc 100 file | Scope narrow hoặc subagent |
| Vague prompt | Output sai intent | Context cụ thể hơn (file, ví dụ, constraint) |
| Hung MCP eating context | 30%+ baseline cho MCP không dùng | `claude mcp list` + disable cái không cần |
| Bad compact | Lặp sai lầm sau compact | `/clear` + brief-injection thay vì compact lại |
| "Help me refactor X" vague | Multi-turn clarification → token waste | Mô tả constraint + acceptance criteria upfront |
| MCP tool fail "not connected" | Hook MCP fire trước khi server connect | `SessionStart`/`Setup` hooks expect lỗi này lần đầu |

---

## 19. Khi nào dùng feature nào

| Cần | Dùng |
|---|---|
| Hướng dẫn load mọi session | `CLAUDE.md` (giữ <100 dòng) |
| Hướng dẫn theo chủ đề | `rules/*.md` (auto-import OR `@`-reference khi cần) |
| Workflow tái sử dụng (gọi `/`) | `skills/<name>/SKILL.md` |
| Task isolated context | Subagent (`agents/*.md`) |
| Hành động BẮT BUỘC chạy mỗi lần | Hook (`settings.json`) — deterministic |
| Tool ngoài (Notion, GitHub, DB) | MCP server |
| Permission tinh chỉnh | `permissions` trong settings |
| Persistent across sessions | Auto memory (Claude tự ghi) |
| Sandbox an toàn | `/sandbox` hoặc `sandbox: true` |
| Cộng tác nhiều agent | Subagents + agent teams |
| Run khi máy tắt | `/schedule` (cloud routine) |
| Style trả lời khác | `/output-style` (built-in: Default/Explanatory/Learning) |
| Loại file Claude khỏi đọc | `.claudeignore` |
| Bulk migration parallel | `/batch <instruction>` |
| Auto-fix PR khi CI fail | `/autofix-pr` |
| Watch external event | `/loop <interval> <prompt>` |
| Audit security trên diff | `/security-review` |
| Mở Claude Code từ URL | Deep link: `claude-cli://open?q=<prompt>&cwd=<path>` |
| Tắt deep link handler | `disableDeepLinkRegistration: "disable"` trong settings |

---

## 20. Tài liệu chính thức

### Anthropic docs
- Overview: <https://code.claude.com/docs/en/overview>
- Best practices: <https://code.claude.com/docs/en/best-practices>
- Memory: <https://code.claude.com/docs/en/memory>
- Skills: <https://code.claude.com/docs/en/skills>
- Subagents: <https://code.claude.com/docs/en/sub-agents>
- Hooks: <https://code.claude.com/docs/en/hooks>
- Hooks guide: <https://code.claude.com/docs/en/hooks-guide>
- Settings: <https://code.claude.com/docs/en/settings>
- Permissions: <https://code.claude.com/docs/en/permissions>
- Output styles: <https://code.claude.com/docs/en/output-styles>
- Model config & effort: <https://code.claude.com/docs/en/model-config>
- MCP: <https://code.claude.com/docs/en/mcp>
- CLI reference: <https://code.claude.com/docs/en/cli-reference>
- Commands reference: <https://code.claude.com/docs/en/commands>
- Environment variables: <https://code.claude.com/docs/en/env-vars>
- Tools reference: <https://code.claude.com/docs/en/tools-reference>
- Interactive mode: <https://code.claude.com/docs/en/interactive-mode>
- Checkpointing: <https://code.claude.com/docs/en/checkpointing>
- Reduce token usage: <https://code.claude.com/docs/en/reduce-token-usage>
- How Claude Code works: <https://code.claude.com/docs/en/how-claude-code-works>
- Manage sessions: <https://code.claude.com/docs/en/manage-sessions>
- Plugins reference: <https://code.claude.com/docs/en/plugins-reference>
- Agent SDK: <https://code.claude.com/docs/en/agent-sdk/overview>
- Slash commands SDK: <https://code.claude.com/docs/en/agent-sdk/slash-commands>
- `.claude` directory: <https://code.claude.com/docs/en/claude-directory>
- Auto mode config: <https://code.claude.com/docs/en/auto-mode-config>
- Permission modes: <https://code.claude.com/docs/en/permission-modes>
- Common workflows: <https://code.claude.com/docs/en/common-workflows>
- Ultraplan: <https://code.claude.com/docs/en/ultraplan>
- Ultrareview: <https://code.claude.com/docs/en/ultrareview>
- Routines: <https://code.claude.com/docs/en/routines>
- Agent teams: <https://code.claude.com/docs/en/agent-teams>
- Channels: <https://code.claude.com/docs/en/channels>
- Fast mode: <https://code.claude.com/docs/en/fast-mode>
- Desktop app: <https://code.claude.com/docs/en/desktop>
- Claude Code on the web: <https://code.claude.com/docs/en/claude-code-on-the-web>
- Remote control: <https://code.claude.com/docs/en/remote-control>
- Computer use (CLI): <https://code.claude.com/docs/en/computer-use>
- Keybindings: <https://code.claude.com/docs/en/keybindings>
- Voice dictation: <https://code.claude.com/docs/en/voice-dictation>
- Fullscreen rendering: <https://code.claude.com/docs/en/fullscreen>
- Sandboxing: <https://code.claude.com/docs/en/sandboxing>
- Plugins: <https://code.claude.com/docs/en/plugins>
- Scheduled tasks: <https://code.claude.com/docs/en/scheduled-tasks>
- Changelog: <https://code.claude.com/docs/en/changelog>
- What's new: <https://code.claude.com/docs/en/whats-new/index>
- Errors reference: <https://code.claude.com/docs/en/errors>
- LLM-friendly index: <https://code.claude.com/docs/llms.txt>
- Context window — Anthropic API: <https://platform.claude.com/docs/en/build-with-claude/context-windows>
- Engineering blog: <https://www.anthropic.com/engineering>
- Session management blog: <https://claude.com/blog/using-claude-code-session-management-and-1m-context>
- Prompting best practices: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>

### Cộng đồng tham khảo

- Anthropics Claude Code repo: <https://github.com/anthropics/claude-code>
- Awesome Claude Code: <https://github.com/hesreallyhim/awesome-claude-code>
- ClaudeLog: <https://claudelog.com>
- ClaudeFast guides: <https://claudefa.st/blog>
- MindStudio Claude Code blog: <https://www.mindstudio.ai/blog>

---

## 21. Checklist & mẹo cuối

### Đầu mỗi project mới
- [ ] Copy template vào project root: `cp ~/.claude/templates/project-CLAUDE.md ./CLAUDE.md`
- [ ] Sửa CLAUDE.md mô tả tech stack, lệnh build/test, convention RIÊNG project
- [ ] Tạo `.claudeignore` loại file lớn không cần (`dist/`, `node_modules/`, `*.lock`, `coverage/`, asset binary)
- [ ] Tạo `<project>/.claude/settings.json` từ template
- [ ] `echo "CLAUDE.local.md" >> .gitignore` + `echo ".claude/settings.local.json" >> .gitignore` + `echo ".claude/HANDOFF.md" >> .gitignore`
- [ ] `claude doctor` để verify

### Đầu mỗi session
- [ ] Brief 1-2 câu mục tiêu phiên này
- [ ] `/context` xem baseline
- [ ] Nếu có `.claude/HANDOFF.md` từ phiên trước → đọc

### Trong session
- [ ] Plan trước cho task >3 file (`/plan` hoặc Shift+Tab×2)
- [ ] Verify mọi output (test, lint, screenshot)
- [ ] Subagent cho investigation
- [ ] Commit thường xuyên (checkpoint để revert)
- [ ] Theo dõi `/context` — <40% sweet spot, >60% nên action
- [ ] Sửa 2 lần vẫn sai → `/clear` + reprompt, đừng spam correction
- [ ] `/effort high` hoặc `ultrathink` cho task khó (architecture, debug heisenbug, refactor lớn)

### Cuối session
- [ ] `/handoff --save` nếu việc còn dở
- [ ] Commit work in-progress hoặc stash
- [ ] Update `<project>/CLAUDE.md` nếu phát hiện convention mới đáng ghi

### Định kỳ (hàng tháng)
- [ ] Review `~/.claude/CLAUDE.md` — bỏ dòng không còn cần
- [ ] Review `~/.claude/skills/` — skill nào không dùng → bỏ hoặc set `disable-model-invocation: true`
- [ ] `git log` của repo `~/.claude/` — xem evolve thế nào (worth committing)
- [ ] `claude update`
- [ ] `/insights` xem session pattern, friction points

### Mẹo cuối
1. **Đầu tư vào CLAUDE.md** — file này compound theo thời gian.
2. **Hook > rule trong CLAUDE.md** — thứ phải xảy ra MỌI lần thì hook deterministic, đừng tin LLM nhớ rule.
3. **Plan trước cho task >3 file** — `/plan` hoặc Shift+Tab×2.
4. **Verify mọi output** — test, lint, screenshot. KHÔNG ship cái không verify được.
5. **Subagent cho investigation** — giữ context chính sạch.
6. **Commit thường xuyên** — checkpoint để revert nếu Claude đi sai hướng.
7. **Brief-injection > resume** cho session dài.
8. **`/compact` proactive** sau mỗi phase, đừng đợi auto-compact 95%.
9. **`/effort high`** hoặc `ultrathink` cho task khó.
10. **CLAUDE.md riêng project + global** — global = preference cá nhân, project = context project.
