# REFERENCE — Cheatsheet Claude Code

> File này KHÔNG load vào session — chỉ để bạn tra cứu khi cần. Tổng hợp từ docs chính thức [code.claude.com/docs](https://code.claude.com/docs) (2026), blog [claude.com](https://www.claude.com/blog), [MindStudio](https://www.mindstudio.ai/blog), [ClaudeFast](https://claudefa.st/blog), GitHub [anthropics/claude-code](https://github.com/anthropics/claude-code). Cập nhật cho Claude Code v2.1.x trở lên.

## Mục lục

1. [Lệnh CLI](#1-lệnh-cli)
2. [CLI flags](#2-cli-flags)
   - [2.1 Khởi tạo & input](#21-khởi-tạo--input)
   - [2.2 Model & effort](#22-model--effort)
   - [2.3 Permission & tool](#23-permission--tool)
   - [2.4 System prompt](#24-system-prompt)
   - [2.5 Subagent](#25-subagent)
   - [2.6 Output & debug](#26-output--debug)
   - [2.7 IDE & integration](#27-ide--integration)
   - [2.8 Session & execution control](#28-session--execution-control)
   - [2.9 MCP & plugin](#29-mcp--plugin)
   - [2.10 Cloud & worktree](#210-cloud--worktree)
   - [2.11 Channels (research preview)](#211-channels-research-preview)
3. [Slash commands trong session](#3-slash-commands-trong-session)
   - [3.1 Quản lý session & context](#31-quản-lý-session--context)
   - [3.2 Memory & rules](#32-memory--rules)
   - [3.3 Cấu hình](#33-cấu-hình)
   - [3.4 Plan & workflow](#34-plan--workflow)
   - [3.5 Bundled skills (Claude có thể auto-invoke)](#35-bundled-skills-claude-có-thể-auto-invoke)
   - [3.6 Cloud & remote](#36-cloud--remote)
   - [3.7 Tasks & monitoring](#37-tasks--monitoring)
   - [3.8 Plugin](#38-plugin)
   - [3.9 Khác](#39-khác)
   - [3.10 Thêm lệnh mới (v2.1+)](#310-thêm-lệnh-mới-v21)
   - [3.11 Đã loại bỏ / deprecated](#311-đã-loại-bỏ--deprecated)
   - [3.12 MCP prompts](#312-mcp-prompts)
4. [Phím tắt](#4-phím-tắt)
   - [4.1 Điều hướng & ngắt](#41-điều-hướng--ngắt)
   - [4.2 Soạn message](#42-soạn-message)
   - [4.3 Modes (Shift+Tab cycle)](#43-modes-shifttab-cycle)
   - [4.4 Text editing (readline)](#44-text-editing-readline)
   - [4.5 Khác](#45-khác)
   - [4.6 Transcript viewer (khi `Ctrl+O` mở)](#46-transcript-viewer-khi-ctrlo-mở)
5. [Prefix trong message](#5-prefix-trong-message)
   - [5.1 Tính năng input mới (v2.1+)](#51-tính-năng-input-mới-v21)
6. [Magic words & effort levels](#6-magic-words--effort-levels)
   - [6.1 Magic words trong prompt](#61-magic-words-trong-prompt)
   - [6.2 `/effort` levels (chính thức 2026)](#62-effort-levels-chính-thức-2026)
7. [Cấu trúc `.claude/`](#7-cấu-trúc-claude)
   - [7.1 Project (`<project>/`)](#71-project-project)
   - [7.2 Global (`~/.claude/`)](#72-global-claude)
   - [7.3 Enterprise / managed](#73-enterprise--managed)
   - [7.4 Session memory (auto, đọc-only)](#74-session-memory-auto-đọc-only)
8. [SKILL.md frontmatter](#8-skillmd-frontmatter)
9. [Subagent frontmatter](#9-subagent-frontmatter)
   - [9.1 Agent teams (experimental, v2.1.32+)](#91-agent-teams-experimental-v2132)
10. [Output styles (built-in)](#10-output-styles-built-in)
11. [settings.json — keys hay dùng](#11-settingsjson--keys-hay-dùng)
    - [11.1 Permission rule syntax](#111-permission-rule-syntax)
12. [Environment variables](#12-environment-variables)
13. [Hook events — đầy đủ 29 event](#13-hook-events--đầy-đủ-29-event)
    - [13.1 Per-session](#131-per-session)
    - [13.2 Per-turn](#132-per-turn)
    - [13.3 Per-tool-call (agentic loop)](#133-per-tool-call-agentic-loop)
    - [13.4 Subagent & task](#134-subagent--task)
    - [13.5 Compact](#135-compact)
    - [13.6 Async events (notification, file, config…)](#136-async-events-notification-file-config)
    - [13.7 Matcher syntax](#137-matcher-syntax)
    - [13.8 Filter chi tiết với `if`](#138-filter-chi-tiết-với-if)
14. [Hook handler types (5 loại)](#14-hook-handler-types-5-loại)
    - [14.1 Hook output (command/http)](#141-hook-output-commandhttp)
15. [Workflow patterns](#15-workflow-patterns)
    - [15.1 Pattern 1 — Explore → Plan → Code → Commit](#151-pattern-1--explore--plan--code--commit)
    - [15.2 Pattern 2 — Writer / Reviewer (2 session)](#152-pattern-2--writer--reviewer-2-session)
    - [15.3 Pattern 3 — TDD (2 session)](#153-pattern-3--tdd-2-session)
    - [15.4 Pattern 4 — Investigation (subagent)](#154-pattern-4--investigation-subagent)
    - [15.5 Pattern 5 — Fan-out (parallel review)](#155-pattern-5--fan-out-parallel-review)
    - [15.6 Pattern 6 — Worktree parallel](#156-pattern-6--worktree-parallel)
    - [15.7 Pattern 7 — Brief-injection (long-running task)](#157-pattern-7--brief-injection-long-running-task)
    - [15.8 Pattern 8 — Bulk migration (`/batch`)](#158-pattern-8--bulk-migration-batch)
    - [15.9 Pattern 9 — Loop monitoring](#159-pattern-9--loop-monitoring)
16. [Quản lý context window — chi tiết](#16-quản-lý-context-window--chi-tiết)
    - [16.1 Tầm quan trọng](#161-tầm-quan-trọng)
    - [16.2 Ngưỡng hành động](#162-ngưỡng-hành-động)
    - [16.3 `/compact` vs `/clear`](#163-compact-vs-clear)
    - [16.4 Customize compaction](#164-customize-compaction)
    - [16.5 Giảm baseline (token cố định mỗi session)](#165-giảm-baseline-token-cố-định-mỗi-session)
    - [16.6 Giảm runtime (token tích lũy trong session)](#166-giảm-runtime-token-tích-lũy-trong-session)
    - [16.7 Phân tích token usage](#167-phân-tích-token-usage)
    - [16.8 Prompt caching (auto trong Claude Code)](#168-prompt-caching-auto-trong-claude-code)
    - [16.9 Quy tắc survive sau `/compact`](#169-quy-tắc-survive-sau-compact)
17. [Session management & handoff](#17-session-management--handoff)
    - [17.1 Lựa chọn `/compact` vs `/clear` vs `/handoff`](#171-lựa-chọn-compact-vs-clear-vs-handoff)
    - [17.2 Anti-pattern resume long session](#172-anti-pattern-resume-long-session)
    - [17.3 Workflow handoff khuyến nghị](#173-workflow-handoff-khuyến-nghị)
    - [17.4 Bad-compact recovery](#174-bad-compact-recovery)
    - [17.5 Lỗi context-related](#175-lỗi-context-related)
18. [Common failures & fix](#18-common-failures--fix)
19. [Hướng dẫn chọn feature](#19-hướng-dẫn-chọn-feature)
20. [Tài liệu chính thức](#20-tài-liệu-chính-thức)
    - [20.1 Setup & onboarding](#201-setup--onboarding)
    - [20.2 Memory & context](#202-memory--context)
    - [20.3 Models, effort & fast mode](#203-models-effort--fast-mode)
    - [20.4 Skills, subagents & output styles](#204-skills-subagents--output-styles)
    - [20.5 Hooks, permissions & sandboxing](#205-hooks-permissions--sandboxing)
    - [20.6 Configuration](#206-configuration)
    - [20.7 Commands & CLI](#207-commands--cli)
    - [20.8 MCP & plugins](#208-mcp--plugins)
    - [20.9 Cloud, web & UI](#209-cloud-web--ui)
    - [20.10 IDE integration](#2010-ide-integration)
    - [20.11 CI/CD & deployment](#2011-cicd--deployment)
    - [20.12 Cloud providers](#2012-cloud-providers)
    - [20.13 SDK](#2013-sdk)
    - [20.14 Enterprise & admin](#2014-enterprise--admin)
    - [20.15 Security & compliance](#2015-security--compliance)
    - [20.16 Troubleshooting & errors](#2016-troubleshooting--errors)
    - [20.17 Manage Claude (platform API)](#2017-manage-claude-platform-api)
    - [20.18 Index & release notes](#2018-index--release-notes)
    - [20.19 Blogs & engineering writing](#2019-blogs--engineering-writing)
    - [20.20 Cộng đồng tham khảo](#2020-cộng-đồng-tham-khảo)
21. [Checklist & mẹo cuối](#21-checklist--mẹo-cuối)
    - [21.1 Đầu mỗi project mới](#211-đầu-mỗi-project-mới)
    - [21.2 Đầu mỗi session](#212-đầu-mỗi-session)
    - [21.3 Trong session](#213-trong-session)
    - [21.4 Cuối session](#214-cuối-session)
    - [21.5 Định kỳ (hàng tháng)](#215-định-kỳ-hàng-tháng)
    - [21.6 Mẹo cuối](#216-mẹo-cuối)

---

## 1. Lệnh CLI

| Lệnh                                         | Mục đích                                                                                       |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `claude`                                     | Mở session interactive trong thư mục hiện tại                                                  |
| `claude "<query>"`                           | Session với prompt khởi đầu                                                                    |
| `claude -p "<query>"`                        | Non-interactive (1-shot) — dùng trong CI/script                                                |
| `cat file \| claude -p "<q>"`                | Process piped content                                                                          |
| `claude -c`                                  | Tiếp session gần nhất (alias `--continue`) ⚠️ kéo theo stale context                            |
| `claude -c -p "<q>"`                         | Continue qua SDK                                                                               |
| `claude -r "<session>" "<q>"`                | Resume session theo ID/name (alias `--resume`)                                                 |
| `claude --version`                           | Xem version                                                                                    |
| `claude update`                              | Cập nhật                                                                                       |
| `claude install [version]`                   | Cài/cài lại native binary (`stable`, `latest`, hoặc `2.1.x`)                                   |
| `claude doctor`                              | Chẩn đoán cấu hình                                                                             |
| `claude auth login`                          | Đăng nhập (`--email`, `--sso`, `--console`)                                                    |
| `claude auth logout`                         | Đăng xuất                                                                                      |
| `claude auth status`                         | Trạng thái auth (JSON; `--text` cho human-readable)                                            |
| `claude agents`                              | List subagent đã cấu hình                                                                      |
| `claude auto-mode defaults`                  | Print built-in rules auto-mode classifier (JSON)                                               |
| `claude auto-mode config`                    | Print effective config (với settings đã apply)                                                 |
| `claude auto-mode critique`                  | AI feedback trên custom allow/soft_deny rules                                                  |
| `claude mcp add <name> <url>`                | Thêm MCP server                                                                                |
| `claude mcp list`                            | List MCP server                                                                                |
| `claude mcp remove <name>`                   | Xóa MCP server                                                                                 |
| `claude mcp serve`                           | Expose Claude Code như MCP server                                                              |
| `claude plugin install <name>@<marketplace>` | Cài plugin từ marketplace                                                                      |
| `claude plugin list`                         | List plugin đã cài                                                                             |
| `claude project purge [path]`                | Xóa local state của project (transcripts, debug log…). Flags: `--dry-run`, `-y`, `-i`, `--all` |
| `claude remote-control`                      | Chạy server mode cho Remote Control từ claude.ai/app                                           |
| `claude setup-token`                         | Tạo long-lived OAuth token cho CI                                                              |
| `claude ultrareview [target]`                | Non-interactive ultrareview. Flags: `--json`, `--timeout <minutes>`                            |

> **Brief-injection > resume**: với session dài, mở session mới và paste handoff brief thường tốt hơn `--resume` vì resume kéo theo stale tool output, file content cũ. Tham khảo skill `/handoff`.

---

## 2. CLI flags

### 2.1 Khởi tạo & input
| Flag                        | Mục đích                                                                                           |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| `-p`, `--print`             | Print mode (non-interactive, 1-shot)                                                               |
| `-c`, `--continue`          | Tiếp session gần nhất trong dir hiện tại                                                           |
| `-r`, `--resume <id\|name>` | Resume session theo ID/name                                                                        |
| `--fork-session`            | Khi resume, tạo session ID mới (giữ nguyên session cũ)                                             |
| `--from-pr <number\|url>`   | Resume session liên kết với PR cụ thể                                                              |
| `--add-dir <path>`          | Thêm thư mục làm việc cho session                                                                  |
| `--bare`                    | Minimal mode — skip auto-discovery hooks/skills/plugins/MCP/CLAUDE.md (dùng cho script tốc độ cao) |
| `--init-only`               | Chạy `Setup` + `SessionStart` hooks rồi exit                                                       |
| `--init`                    | Chạy Setup hooks với matcher `init` (chỉ trong `-p` mode)                                          |

### 2.2 Model & effort
| Flag                       | Mục đích                                                                                                             |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `--model <alias\|id>`      | `opus`, `sonnet`, `haiku`, `best`, `default`, `opusplan`, `opus[1m]`, `sonnet[1m]`, hoặc full ID (`claude-opus-4-7`) |
| `--effort <level>`         | `low`, `medium`, `high`, `xhigh`, `max`                                                                              |
| `--fallback-model <alias>` | Fallback khi default overload (chỉ print mode)                                                                       |
| `--betas <header>`         | Beta header cho API (chỉ API key user)                                                                               |

**Model aliases**:

| Alias      | Ý nghĩa                                          |
| ---------- | ------------------------------------------------ |
| `default`  | Reset về model recommended cho account type      |
| `best`     | Model mạnh nhất (currently = `opus`)             |
| `opusplan` | Opus cho plan mode, Sonnet cho execution         |
| `[1m]`     | 1M context window (chỉ Opus 4.7/4.6, Sonnet 4.6) |

**Provider mapping**:

| Provider                   | `opus`   | `sonnet`   |
| -------------------------- | -------- | ---------- |
| Anthropic API              | Opus 4.7 | Sonnet 4.6 |
| Bedrock / Vertex / Foundry | Opus 4.6 | Sonnet 4.5 |

> Pin version: `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL`.

**Default model theo plan**:
- **Max / Team Premium** → Opus 4.7
- **Pro / Team Standard / Enterprise / Anthropic API** → Sonnet 4.6
- **Bedrock / Vertex / Foundry** → Sonnet 4.5

#### Models hiện được hỗ trợ (Anthropic API, tính đến 2026-05)

> Source chính thức: [platform.claude.com/docs/en/about-claude/models/overview](https://platform.claude.com/docs/en/about-claude/models/overview)

**Latest**:
| Model      | Alias    | Model ID            | Context | Max output | Effort levels          | Pricing (in/out per MTok) |
| ---------- | -------- | ------------------- | ------- | ---------- | ---------------------- | ------------------------- |
| Opus 4.7   | `opus`   | `claude-opus-4-7`   | 1M      | 128k       | low/med/high/xhigh/max | $5 / $25                  |
| Sonnet 4.6 | `sonnet` | `claude-sonnet-4-6` | 1M      | 64k        | low/med/high/max       | $3 / $15                  |
| Haiku 4.5  | `haiku`  | `claude-haiku-4-5`  | 200k    | 64k        | —                      | $1 / $5                   |

**Legacy (vẫn hỗ trợ, nên migrate)**:
| Model      | Model ID            | Context | Max output | Effort           | Pricing   |
| ---------- | ------------------- | ------- | ---------- | ---------------- | --------- |
| Opus 4.6   | `claude-opus-4-6`   | 1M      | 128k       | low/med/high/max | $5 / $25  |
| Opus 4.5   | `claude-opus-4-5`   | 200k    | 64k        | —                | $5 / $25  |
| Opus 4.1   | `claude-opus-4-1`   | 200k    | 32k        | —                | $15 / $75 |
| Sonnet 4.5 | `claude-sonnet-4-5` | 200k    | 64k        | —                | $3 / $15  |

**Deprecated (sẽ retire 2026-06-15)**:
| Model    | Model ID            | Context | Max output |
| -------- | ------------------- | ------- | ---------- |
| Sonnet 4 | `claude-sonnet-4-0` | 200k    | 64k        |
| Opus 4   | `claude-opus-4-0`   | 200k    | 32k        |

**Ghi chú**:
- **Thinking modes** (theo [docs models/overview](https://platform.claude.com/docs/en/about-claude/models/overview)):
  - Opus 4.7: chỉ adaptive (không extended thinking)
  - Sonnet 4.6: có cả adaptive + extended
  - Haiku 4.5: chỉ extended (không adaptive)
- Effort levels chỉ hỗ trợ Opus 4.7, Opus 4.6, Sonnet 4.6. Model khác bỏ qua flag `--effort`.
- 1M context: chỉ Opus 4.7/4.6, Sonnet 4.6. Append `[1m]` khi muốn dùng (vd `claude-opus-4-7[1m]`).
- Trên Bedrock/Vertex/Foundry: alias `opus` → Opus 4.6, `sonnet` → Sonnet 4.5 (không phải latest). Pin bằng `ANTHROPIC_DEFAULT_OPUS_MODEL`/`_SONNET_MODEL` để control version.
- Set model trong settings.json: `"model": "claude-opus-4-1"` hoặc `"model": "opus"` (alias auto-update).
- Claude 3.x family (3 Haiku/Sonnet/Opus, 3.5, 3.7) đã retire — không liệt kê.

### 2.3 Permission & tool
| Flag                                   | Mục đích                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------ |
| `--permission-mode <mode>`             | `default`, `acceptEdits`, `auto`, `plan`, `dontAsk`, `bypassPermissions` |
| `--dangerously-skip-permissions`       | = `--permission-mode bypassPermissions` ⚠️ chỉ trong sandbox              |
| `--allow-dangerously-skip-permissions` | Cho phép `bypassPermissions` trong Shift+Tab cycle                       |
| `--allowedTools "<rules>"`             | Pre-approve tool/lệnh không hỏi                                          |
| `--disallowedTools "<rules>"`          | Loại tool khỏi context                                                   |
| `--tools "<rules>"`                    | Giới hạn tool có thể dùng                                                |
| `--disable-slash-commands`             | Tắt mọi skill + command                                                  |

### 2.4 System prompt
| Flag                                       | Mục đích                                                                                     |
| ------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `--system-prompt "<text>"`                 | **Thay thế** toàn bộ system prompt                                                           |
| `--system-prompt-file <path>`              | Thay thế từ file                                                                             |
| `--append-system-prompt "<text>"`          | Append vào default system prompt                                                             |
| `--append-system-prompt-file <path>`       | Append từ file                                                                               |
| `--exclude-dynamic-system-prompt-sections` | Move per-machine sections (cwd, env, git status) khỏi system prompt → cải thiện prompt-cache |

### 2.5 Subagent
| Flag                | Mục đích                    |
| ------------------- | --------------------------- |
| `--agent <name>`    | Chỉ định agent cho session  |
| `--agents '<json>'` | Define subagent động (JSON) |

### 2.6 Output & debug
| Flag                                      | Mục đích                                         |
| ----------------------------------------- | ------------------------------------------------ |
| `--output-format json\|stream-json\|text` | Format output (chỉ `-p` mode)                    |
| `--include-hook-events`                   | Include hook events trong stream (`stream-json`) |
| `--include-partial-messages`              | Include partial streaming events                 |
| `--verbose`                               | Verbose logging, show full turn-by-turn output   |
| `--debug [<categories>]`                  | Bật debug — vd `"api,mcp,!file"`                 |
| `--debug-file <path>`                     | Ghi debug log vào file                           |
| `--mcp-debug`                             | Debug MCP riêng                                  |

### 2.7 IDE & integration
| Flag          | Mục đích                           |
| ------------- | ---------------------------------- |
| `--ide`       | Auto-connect IDE khi startup       |
| `--chrome`    | Bật Chrome integration             |
| `--no-chrome` | Tắt Chrome integration cho session |

### 2.8 Session & execution control
| Flag                               | Mục đích                                                 |
| ---------------------------------- | -------------------------------------------------------- |
| `--name`, `-n`                     | Đặt tên session (hiện trong `/resume` và terminal title) |
| `--session-id <id>`                | Dùng session ID cụ thể                                   |
| `--max-turns <N>`                  | Giới hạn số agentic turn (chỉ print mode)                |
| `--max-budget-usd <N>`             | Giới hạn chi phí API (USD, chỉ print mode)               |
| `--json-schema <schema>`           | Output JSON theo schema (chỉ print mode)                 |
| `--input-format text\|stream-json` | Format input cho print mode                              |
| `--no-session-persistence`         | Không lưu session ra disk (chỉ print mode)               |
| `--maintenance`                    | Chạy Setup hooks matcher `maintenance` (chỉ print mode)  |
| `--settings <path\|json>`          | Load settings từ file hoặc inline JSON                   |
| `--setting-sources <list>`         | Chọn scope settings: `user`, `project`, `local`          |

### 2.9 MCP & plugin
| Flag                        | Mục đích                                           |
| --------------------------- | -------------------------------------------------- |
| `--mcp-config <path\|json>` | Load MCP server từ file/JSON                       |
| `--strict-mcp-config`       | Chỉ dùng MCP từ `--mcp-config`, bỏ qua config khác |
| `--plugin-dir <path>`       | Load plugin từ thư mục hoặc `.zip` (session-only)  |
| `--plugin-url <url>`        | Fetch plugin `.zip` từ URL (session-only)          |

### 2.10 Cloud & worktree
| Flag                                     | Mục đích                                         |
| ---------------------------------------- | ------------------------------------------------ |
| `--remote "<task>"`                      | Tạo web session mới trên claude.ai               |
| `--remote-control`, `--rc`               | Bật Remote Control cho session                   |
| `--teleport`                             | Pull web session vào terminal local              |
| `--worktree`, `-w`                       | Chạy trong isolated git worktree                 |
| `--tmux`                                 | Tạo tmux session cho worktree (cần `--worktree`) |
| `--teammate-mode auto\|in-process\|tmux` | Hiển thị agent team teammate                     |

### 2.11 Channels (research preview)
| Flag                                      | Mục đích                                                  |
| ----------------------------------------- | --------------------------------------------------------- |
| `--channels <list>`                       | MCP channel notifications (`plugin:<name>@<marketplace>`) |
| `--dangerously-load-development-channels` | Cho channel ngoài allowlist                               |

---

## 3. Slash commands trong session

> Type `/` để xem full list, `/<letters>` để filter. `<arg>` = required, `[arg]` = optional. Marked **[Skill]** = bundled skill (Claude có thể auto-invoke).

### 3.1 Quản lý session & context
| Lệnh                      | Mục đích                                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `/help`                   | List commands                                                                                                |
| `/clear`                  | XÓA HẲN context, reset session. Aliases: `/reset`, `/new`                                                    |
| `/compact [instructions]` | Nén context. VD: `/compact giữ phần API change, drop test debug`                                             |
| `/context`                | Visualize context usage + tối ưu suggestion                                                                  |
| `/rewind`                 | Rollback conversation/code, hoặc "Summarize from here". Aliases: `/checkpoint`, `/undo`. Phím tắt: `Esc Esc` |
| `/branch [name]`          | Phân nhánh session (giữ nguyên session cũ). Alias `/fork`                                                    |
| `/btw <question>`         | Hỏi nhanh không vào history (overlay dismissible)                                                            |
| `/resume [session]`       | Resume theo ID/name. Alias `/continue`                                                                       |
| `/rename [name]`          | Đặt tên session (auto-gen nếu để trống)                                                                      |
| `/exit`                   | Thoát CLI. Alias `/quit`                                                                                     |
| `/desktop`                | Continue trong Desktop app (macOS/Windows). Alias `/app`                                                     |
| `/teleport`               | Pull web session vào terminal. Alias `/tp`                                                                   |
| `/copy [N]`               | Copy response thứ N gần nhất (mặc định 1)                                                                    |
| `/export [filename]`      | Export conversation thành plain text                                                                         |

### 3.2 Memory & rules
| Lệnh      | Mục đích                                                                 |
| --------- | ------------------------------------------------------------------------ |
| `/memory` | Edit CLAUDE.md, auto-memory                                              |
| `/init`   | Tạo CLAUDE.md cho project (`CLAUDE_CODE_NEW_INIT=1` để interactive flow) |

### 3.3 Cấu hình
| Lệnh                      | Mục đích                                                                                              |
| ------------------------- | ----------------------------------------------------------------------------------------------------- |
| `/config`                 | Settings UI (theme, model, output style…). Alias `/settings`                                          |
| `/permissions`            | Sửa allow/ask/deny rule. Alias `/allowed-tools`                                                       |
| `/hooks`                  | Xem hook configurations                                                                               |
| `/mcp`                    | Manage MCP server, OAuth                                                                              |
| `/skills`                 | List skill có sẵn                                                                                     |
| `/agents`                 | Manage subagent (interactive create/edit)                                                             |
| `/model [model]`          | Đổi model. Mũi tên trái/phải để adjust effort                                                         |
| `/effort [level]`         | `low`/`medium`/`high`/`xhigh`/`max`/`auto`. `low`/`medium`/`high`/`xhigh` persist; `max` session-only |
| `/output-style`           | Đổi output style                                                                                      |
| `/output-style:new`       | Tạo style mới với Claude help                                                                         |
| `/keybindings`            | Sửa keybindings                                                                                       |
| `/terminal-setup`         | Cấu hình Shift+Enter cho terminal                                                                     |
| `/sandbox`                | Toggle sandbox mode                                                                                   |
| `/theme`                  | Đổi color theme                                                                                       |
| `/color [name\|hex]`      | Set màu prompt bar                                                                                    |
| `/statusline`             | Cấu hình status line                                                                                  |
| `/fast [on\|off]`         | Toggle fast mode (chỉ Opus 4.6, tốc độ 2.5× nhanh hơn, giá $30/$150 per MTok ≈ 6× standard)           |
| `/voice [hold\|tap\|off]` | Toggle voice dictation, hoặc enable theo mode. Requires Claude.ai account                             |
| `/privacy-settings`       | View/update privacy (Pro/Max)                                                                         |

### 3.4 Plan & workflow
| Lệnh                  | Mục đích                                  |
| --------------------- | ----------------------------------------- |
| `/plan [description]` | Vào plan mode (Claude chỉ đọc, không sửa) |
| `Shift+Tab` ×2        | Toggle plan mode                          |
| `Shift+Tab` ×1        | Toggle auto-accept mode                   |

### 3.5 Bundled skills (Claude có thể auto-invoke)
| Lệnh                        | Mục đích                                                                            |
| --------------------------- | ----------------------------------------------------------------------------------- |
| `/batch <instruction>`      | **[Skill]** Orchestrate large-scale change song song qua git worktree               |
| `/claude-api`               | **[Skill]** Load API reference cho ngôn ngữ project                                 |
| `/debug [description]`      | **[Skill]** Bật debug logging + troubleshoot                                        |
| `/loop [interval] [prompt]` | **[Skill]** Chạy prompt lặp định kỳ. VD `/loop 5m check deploy`. Alias `/proactive` |
| `/simplify [focus]`         | **[Skill]** Spawn 3 review agent, fix issue                                         |
| `/security-review`          | **[Skill]** Phân tích git diff tìm lỗ hổng                                          |

### 3.6 Cloud & remote
| Lệnh                      | Mục đích                                                 |
| ------------------------- | -------------------------------------------------------- |
| `/remote-control`         | Bật remote control session từ claude.ai/app. Alias `/rc` |
| `/remote-env`             | Cấu hình remote env cho web session                      |
| `/web-setup`              | Connect GitHub cho Claude Code on the web                |
| `/autofix-pr [prompt]`    | Spawn web session auto-fix PR                            |
| `/ultraplan <prompt>`     | Draft plan trong browser, execute remotely               |
| `/schedule [description]` | Tạo/edit/list/run routine định kỳ. Alias `/routines`     |
| `/install-github-app`     | Cài Claude GitHub Actions                                |
| `/install-slack-app`      | Cài Claude Slack                                         |
| `/setup-bedrock`          | Cấu hình Amazon Bedrock                                  |
| `/setup-vertex`           | Cấu hình Google Vertex AI                                |

### 3.7 Tasks & monitoring
| Lệnh        | Mục đích                                                                             |
| ----------- | ------------------------------------------------------------------------------------ |
| `/tasks`    | List/manage background tasks. Alias `/bashes`                                        |
| `/diff`     | Interactive diff viewer (uncommitted + per-turn)                                     |
| `/usage`    | Session cost, plan limits, activity stats. Aliases: `/cost`, `/stats` (mở Stats tab) |
| `/status`   | Settings (Status tab)                                                                |
| `/insights` | Report sessions, friction patterns                                                   |

### 3.8 Plugin
| Lệnh              | Mục đích                    |
| ----------------- | --------------------------- |
| `/plugin`         | Browser plugin marketplace  |
| `/reload-plugins` | Reload plugin không restart |

### 3.9 Khác
| Lệnh                 | Mục đích                                                   |
| -------------------- | ---------------------------------------------------------- |
| `/login`, `/logout`  | Auth                                                       |
| `/upgrade`           | Upgrade plan                                               |
| `/extra-usage`       | Cấu hình extra usage khi hit rate limit                    |
| `/passes`            | Share free week với bạn                                    |
| `/feedback [report]` | Submit feedback. Alias `/bug`                              |
| `/release-notes`     | Xem changelog                                              |
| `/team-onboarding`   | Generate onboarding guide từ usage history                 |
| `/powerup`           | Quick interactive lessons về Claude Code features          |
| `/mobile`            | QR code download Claude mobile. Aliases `/ios`, `/android` |
| `/stickers`          | Order Claude Code stickers                                 |
| `/ide`               | Manage IDE integrations                                    |
| `/chrome`            | Cấu hình Claude in Chrome                                  |

### 3.10 Thêm lệnh mới (v2.1+)
| Lệnh                         | Mục đích                                                                 |
| ---------------------------- | ------------------------------------------------------------------------ |
| `/add-dir <path>`            | Thêm thư mục làm việc cho session hiện tại                               |
| `/doctor`                    | Chẩn đoán cấu hình, nhấn `f` để Claude auto-fix                          |
| `/fewer-permission-prompts`  | **[Skill]** Scan transcript → thêm allowlist vào `.claude/settings.json` |
| `/focus`                     | Toggle focus view (chỉ hiện prompt cuối + response cuối)                 |
| `/heapdump`                  | Ghi heap snapshot + memory breakdown (debug OOM)                         |
| `/recap`                     | Tóm tắt 1 dòng session hiện tại (auto chạy sau 3+ phút idle)             |
| `/review [PR]`               | Review PR locally (nhẹ hơn `/ultrareview`)                               |
| `/tui [default\|fullscreen]` | Đổi UI renderer (`fullscreen` = flicker-free alt-screen)                 |
| `/ultrareview [PR]`          | Multi-agent code review chạy trên cloud sandbox                          |

### 3.11 Đã loại bỏ / deprecated
- `/vim` — Removed v2.1.92. Dùng `/config` → Editor mode
- `/pr-comments` — Removed v2.1.91. Hỏi Claude trực tiếp xem PR comments

### 3.12 MCP prompts
MCP server có thể expose prompt thành command: `/mcp__<server>__<prompt>`.

---

## 4. Phím tắt

### 4.1 Điều hướng & ngắt
| Phím     | Tác dụng                  |
| -------- | ------------------------- |
| `Esc`    | Dừng Claude (giữ context) |
| `Esc` ×2 | Mở rewind menu            |
| `Ctrl+C` | Thoát hẳn                 |
| `Ctrl+D` | Logout / exit             |

### 4.2 Soạn message
| Phím                                            | Tác dụng                                          |
| ----------------------------------------------- | ------------------------------------------------- |
| `Shift+Enter` (sau `/terminal-setup`)           | Newline                                           |
| `\` + `Enter`                                   | Newline (universal fallback)                      |
| `Ctrl+J`                                        | Insert newline                                    |
| `Option+Enter` (macOS)                          | Newline                                           |
| `Ctrl+G`                                        | Mở `$EDITOR` để soạn message dài                  |
| `Ctrl+V` / `Cmd+V` (iTerm2) / `Alt+V` (Windows) | Paste image từ clipboard — chèn `[Image #N]` chip |
| `Shift+drag`                                    | Drag file vào input                               |

### 4.3 Modes (Shift+Tab cycle)
| Mode                                                                 | Mô tả                   |
| -------------------------------------------------------------------- | ----------------------- |
| Edit (default)                                                       | Hỏi trước khi modify    |
| Auto-accept (`Shift+Tab`×1)                                          | Tự sửa file không hỏi   |
| Plan (`Shift+Tab`×2)                                                 | Chỉ research, không sửa |
| `bypassPermissions` (nếu bật `--allow-dangerously-skip-permissions`) | Skip mọi permission ⚠️   |

### 4.4 Text editing (readline)
| Phím              | Tác dụng          |
| ----------------- | ----------------- |
| `Ctrl+A`          | Đầu dòng          |
| `Ctrl+E`          | Cuối dòng         |
| `Ctrl+K`          | Xóa đến cuối dòng |
| `Ctrl+U`          | Xóa đến đầu dòng  |
| `Ctrl+W`          | Xóa word trước    |
| `Ctrl+Y`          | Paste text đã xóa |
| `Alt+B` / `Alt+F` | Lùi/tiến 1 word   |

> Vim mode: bật qua `/config` → Editor mode → `vim`. Full vi keybindings (NORMAL/INSERT/VISUAL).

### 4.5 Khác
| Phím                     | Tác dụng                                               |
| ------------------------ | ------------------------------------------------------ |
| `Ctrl+O`                 | Toggle transcript viewer                               |
| `Ctrl+R`                 | Reverse search command history (cycle scope: `Ctrl+S`) |
| `Ctrl+T`                 | Toggle task list                                       |
| `Ctrl+B`                 | Background task đang chạy (tmux user: nhấn 2 lần)      |
| `Ctrl+L`                 | Redraw screen                                          |
| `Ctrl+X Ctrl+K` (chord)  | Kill mọi background agent (action `chat:killAgents`)   |
| `Alt+T`                  | Toggle extended thinking                               |
| `Alt+O`                  | Toggle fast mode                                       |
| `Cmd/Ctrl+Click` PR link | Mở PR trong browser                                    |

### 4.6 Transcript viewer (khi `Ctrl+O` mở)
| Phím        | Tác dụng                                         |
| ----------- | ------------------------------------------------ |
| `[`         | Ghi conversation vào scrollback (dùng Cmd+F tìm) |
| `/`         | Search trong transcript (v2.1+)                  |
| `v`         | Mở trong `$VISUAL`/`$EDITOR`                     |
| `q` / `Esc` | Thoát viewer                                     |

---

## 5. Prefix trong message

| Prefix          | Tác dụng                                           |
| --------------- | -------------------------------------------------- |
| `!<command>`    | Chạy bash, output → context (không qua LLM)        |
| `@<file>`       | Reference file vào context                         |
| `@<directory>/` | Reference cả thư mục                               |
| `@<url>`        | Fetch URL (cần allow domain)                       |
| `#<note>`       | Save vào memory (deprecated v2.1+, dùng `/memory`) |
| `&<task>`       | Background task trên Cloud Code (Pro/Max)          |

### 5.1 Tính năng input mới (v2.1+)

- **Shell mode**: gõ `!` ở đầu prompt → chạy lệnh trực tiếp, real-time output, không cần Claude approve. `Ctrl+B` để background. `Escape`/`Backspace` thoát.
- **Prompt suggestions**: gợi ý xám xuất hiện sau khi mở session hoặc Claude trả lời. `Tab`/`→` accept, `Enter` accept + submit. Tắt: `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=false` hoặc `/config`.

---

## 6. Magic words & effort levels

### 6.1 Magic words trong prompt

Chỉ **`ultrathink`** được nhận diện là keyword — Claude Code thêm in-context instruction request deeper reasoning **cho turn đó**, KHÔNG đổi effort level gửi lên API. Các cụm `think`, `think hard`, `megathink`… là **plain text**, không trigger gì đặc biệt — dùng `/effort` thay.

### 6.2 `/effort` levels (chính thức 2026)
| Level    | Model mặc định       | Ghi chú                                        |
| -------- | -------------------- | ---------------------------------------------- |
| `low`    | —                    | Không thinking                                 |
| `medium` | —                    | Thinking nhẹ                                   |
| `high`   | Opus 4.6, Sonnet 4.6 | Default cho Opus 4.6/Sonnet 4.6                |
| `xhigh`  | Opus 4.7             | Default Opus 4.7. Model khác fallback → `high` |
| `max`    | —                    | Tối đa (Opus 4.7/4.6/Sonnet 4.6), session-only |
| `auto`   | —                    | Reset model default                            |

**Persistence**:
- `low`/`medium`/`high`/`xhigh` persist qua session
- `max` session-only (trừ khi set qua `CLAUDE_CODE_EFFORT_LEVEL` env var)

**Toggle keys**: `Alt+T` thinking, `Alt+O` fast mode

**Disable**: `MAX_THINKING_TOKENS=0` tắt hoàn toàn

**Override**: `CLAUDE_CODE_EFFORT_LEVEL` env var ưu tiên cao nhất

Opus 4.7 dùng **adaptive reasoning** (thinking tùy bước, không cố định budget). Opus 4.6/Sonnet 4.6 dùng fixed budget. Tắt adaptive: `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`.

---

## 7. Cấu trúc `.claude/`

### 7.1 Project (`<project>/`)
```text
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

### 7.2 Global (`~/.claude/`)
```text
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

### 7.3 Enterprise / managed
```text
CLAUDE.md                        # Org-wide instructions, không thể exclude
managed-settings.json            # Org-wide policy, override mọi thứ
managed-mcp.json                 # MCP server bắt buộc
```
- macOS: `/Library/Application Support/ClaudeCode/`
- Linux: `/etc/claude-code/`
- Windows: `C:\ProgramData\ClaudeCode\`

### 7.4 Session memory (auto, đọc-only)
```text
~/.claude/projects/<hash>/<session>/session_memory   # Backing store cho /compact
```

---

## 8. SKILL.md frontmatter

```yaml
---
name: <kebab-case>                    # Optional (default = tên folder). Lowercase, số, hyphen, max 64 ký tự
description: <what + when>            # Recommended — Claude dùng để auto-invoke
allowed-tools: Read Grep Bash(git:*)  # Space-separated string HOẶC YAML list (KHÔNG comma-separated)
disable-model-invocation: false       # true → chỉ user gọi (không Claude tự load)
user-invocable: true                  # false → chỉ Claude gọi (ẩn khỏi /menu)
argument-hint: "<gợi ý đối số>"
arguments: [target, scope]            # Space-separated string ("target scope") HOẶC YAML list. Map vị trí → $target, $scope
when_to_use: "<trigger phrases>"      # Bổ sung description, giúp auto-invoke chính xác hơn
paths: "src/**/*.ts, *.config.*"      # Comma-separated string HOẶC YAML list. Skill chỉ activate khi file match pattern
model: opus|sonnet|haiku|inherit
context: fork                         # fork → run trong subagent isolated
agent: Explore|Plan|general-purpose   # Subagent type khi context: fork
effort: low|medium|high|xhigh|max
shell: bash|powershell                # Shell cho !`command` blocks. powershell yêu cầu CLAUDE_CODE_USE_POWERSHELL_TOOL=1
hooks:
  PreToolUse: ...
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

> Template skill chính thức + Agent Skills specification: <https://github.com/anthropics/skills> (`template/` cho skeleton, `spec/` cho schema reference).

**Rules**:
- `name`: lowercase-kebab-case, NO consecutive hyphens, NO leading/trailing hyphen.
- `description` + `when_to_use`: combined cap **1,536 ký tự** trong skill listing (ưu tiên use case quan trọng nhất ở đầu).
- Khuyến cáo style: third-person nếu tiếng Anh ("This skill should be used when…"). Tiếng Việt OK ("Dùng khi…"). Tránh behavioral instructions ("Always respond in JSON") trong description — đó vào body.
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
tools: Read, Grep, Glob, Bash         # Optional — comma-separated tên tool thuần. Omit = inherit. Exception: Agent(worker, researcher) cho phép allowlist subagent types (chỉ khi run as main thread qua --agent)
model: opus|sonnet|haiku|inherit      # Optional, default inherit. Cũng accept full ID (claude-opus-4-7)
isolation: worktree                   # Optional — copy isolated repo qua git worktree
skills: [my-skill, another-skill]     # Optional — pre-load full skill content vào subagent context lúc startup
disallowedTools: [WebFetch]           # Optional — deny tools cụ thể (loại khỏi inherited list)
maxTurns: 20                          # Optional — giới hạn số agentic turn
permissionMode: plan                  # Optional — default|acceptEdits|auto|dontAsk|bypassPermissions|plan
mcpServers: [slack]                   # Optional — MCP servers scoped cho subagent (string ref hoặc inline def)
hooks:                                # Optional — lifecycle hooks scoped riêng cho subagent. Plugin subagent IGNORE field này
  PreToolUse: [...]
memory: project                       # Optional — user|project|local. Bật persistent memory
background: false                     # Optional — true = run as background task mặc định
effort: high                          # Optional — low|medium|high|xhigh|max (model-dependent)
color: red|blue|green|yellow|purple|orange|pink|cyan  # Optional — display color trong task list
initialPrompt: "Audit security..."    # Optional — auto-submit first user turn khi run as main session (--agent)
---

System prompt cho subagent (toàn bộ markdown body sau frontmatter).
```

Lưu ý:
- Subagent **chỉ nhận system prompt này** (không có default Claude Code system prompt; chỉ + basic env như cwd).
- Subagent có **context window riêng** — không ăn context chính.
- `cd` trong subagent KHÔNG persist qua tool call.
- Khi `isolation: worktree`, subagent chạy trong git worktree riêng → không ảnh hưởng main working tree.
- Model override chỉ áp dụng trong turn đó, không lưu vào settings.

### 9.1 Agent teams (experimental, v2.1.32+)

Khác subagent (chỉ report về main agent), agent teams cho phép multiple teammates chạy parallel **trong cùng session**, communicate trực tiếp với nhau qua shared task list + mailbox. Use case: parallel review, debugging với competing hypotheses, cross-layer coordination.

**Enable** (mặc định OFF):
```json
// settings.json
{
  "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" }
}
```

**Architecture**:
- **Lead**: main session điều phối — fixed cho lifetime team (không transfer leadership)
- **Teammates**: separate Claude Code instances, mỗi teammate có context riêng (load CLAUDE.md/MCP/skills, KHÔNG inherit lead history; chỉ nhận spawn prompt)
- **Task list**: shared, file-locking khi claim → tránh race condition
- **Mailbox**: inter-teammate messaging tự động delivery (no polling)

**Display modes** — 2 modes chính thức (theo [docs agent-teams](https://code.claude.com/docs/en/agent-teams)):
- **In-process**: tất cả teammates render trong main terminal (mọi terminal đều work)
- **Split panes**: tách pane riêng cho mỗi teammate (yêu cầu tmux HOẶC iTerm2 + `it2` CLI; iTerm2 cần enable Python API trong Settings → General → Magic)

**Setting `teammateMode`** — 3 values control routing logic:
- `"auto"` (default): split panes nếu đang chạy **trong tmux session**, ngược lại in-process
- `"in-process"`: force in-process
- `"tmux"`: enable split-pane mode, **auto-detect** tmux vs iTerm2 theo terminal hiện tại

CLI override 1 session: `claude --teammate-mode in-process`.

**Tool `SendMessage`**: chỉ available cho lead/teammates khi env var bật. Send message theo tên teammate (lead assign tên lúc spawn). Reach all = send từng message một.

**Storage** (auto-managed, ĐỪNG sửa tay):
- `~/.claude/teams/<team-name>/config.json` — runtime state (session IDs, tmux pane IDs, members array)
- `~/.claude/tasks/<team-name>/` — shared task list

**Subagent định nghĩa làm teammate**: reference subagent type khi spawn (vd "spawn teammate using security-reviewer agent type"). Honor `tools` allowlist + `model`. **Lưu ý**: `skills` và `mcpServers` trong subagent frontmatter **KHÔNG applied** khi run as teammate (teammate load skills/MCP từ project + user settings như session thường).

**Hooks scoped cho team** (xem section 13):
- `TeammateIdle`: exit code 2 = giữ teammate working thay vì idle
- `TaskCreated`: exit code 2 = block creation + send feedback
- `TaskCompleted`: exit code 2 = block completion + send feedback

**Key bindings (UI)**:
- `Shift+Down`: cycle teammates → wrap về lead
- `Enter`: view teammate session
- `Escape`: interrupt teammate's current turn
- `Ctrl+T`: toggle shared task list

**Limits**:
- 1 team/session, no nested teams (teammate không spawn được team mới)
- `/resume` và `/rewind` KHÔNG restore in-process teammates → nói lead spawn lại
- Permissions set lúc spawn (inherit lead) — đổi từng teammate sau spawn được, nhưng không set per-teammate lúc spawn
- Split panes KHÔNG support trong VS Code integrated terminal, Windows Terminal, Ghostty
- Token cost cao: mỗi teammate là full Claude instance — recommended 3-5 teammates/team, 5-6 tasks/teammate

**Plan-approval flow**: nếu yêu cầu teammate plan trước (vd "require plan approval"), teammate work trong read-only plan mode → submit plan → lead review (autonomously, có thể guide qua prompt vd "only approve plans with test coverage") → approve/reject → revise loop.

**Cleanup**: nói "clean up the team" với lead. KHÔNG để teammate cleanup (context không đầy đủ).

---

## 10. Output styles (built-in)

3 style mặc định (set qua `/output-style <name>` hoặc `outputStyle` trong settings):

| Style         | Mô tả                                                                 | Token cost |
| ------------- | --------------------------------------------------------------------- | ---------- |
| `Default`     | System prompt mặc định cho coding                                     | Thấp       |
| `Explanatory` | Thêm "★ Insight" giáo dục về implementation choice                    | +20-40%    |
| `Learning`    | Pair-programming mode, để `TODO(human)` cho user code phần chiến lược | Cao nhất   |

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
  // "includeCoAuthoredBy": false,     // DEPRECATED — dùng attribution.commit = "" thay vì


  "permissions": {
    "defaultMode": "default",            // default|acceptEdits|plan|auto|dontAsk|bypassPermissions
    "allow":   ["Bash(git status)", "Read(**)"],
    "ask":     ["Bash(git push:*)", "Edit(**)"],
    "deny":    ["Bash(rm -rf /*)", "Read(.env)"],
    "additionalDirectories": ["~/shared-libs"],  // Thêm dir vào allowlist (ngoài cwd)
    "disableBypassPermissionsMode": "disable"    // (managed) value `"disable"` string (không phải boolean) — chặn user bật bypass
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

  // Skills override (v2.1.129+) — value là string visibility, KHÔNG phải object
  "skillOverrides": {
    "legacy-context": "name-only",       // "on" | "name-only" | "user-invocable-only" | "off"
    "deploy": "off"
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
  "plansDirectory": "./plans",            // Default: ~/.claude/plans
  "showClearContextOnPlanAccept": true,   // Default: false
  "autoUpdatesChannel": "latest",         // "stable" | "latest"

  // Auto mode
  "autoMode": {
    "environment": ["$defaults", "Source control: github.com/my-org"],
    "allow": ["$defaults"],            // Override block rules
    "soft_deny": ["$defaults"]         // Override allow rules
  },

  // Editor & UI
  "editorMode": "normal",             // "normal" | "vim"
  "effortLevel": "high",              // "low" | "medium" | "high" | "xhigh" (KHÔNG accept "max" — chỉ env var/CLI)
  "tui": "default",                   // "default" | "fullscreen" (alt-screen)
  "viewMode": "default",              // "default" | "verbose" | "focus"
  "defaultShell": "bash",             // "bash" | "powershell"
  "awaySummaryEnabled": true,         // Session recap sau idle (default true)
  "showThinkingSummaries": false,     // Show extended thinking summaries
  "showTurnDuration": true,
  "teammateMode": "auto",             // "auto" | "in-process" | "tmux" — routing logic teammate (auto = split panes nếu trong tmux session, ngược lại in-process; tmux = enable split-pane, auto-detect tmux vs iTerm2). Chỉ effect khi CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

  // Memory
  "autoMemoryDirectory": "~/.claude/memory",

  // Voice + UI
  "voice": { "enabled": true, "mode": "tap", "autoSubmit": false },  // /voice tự ghi
  // "voiceEnabled": false,           // DEPRECATED — dùng voice.enabled ở trên thay vì
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
  "preferredNotifChannel": "auto",     // auto|terminal_bell|iterm2|iterm2_with_bell|kitty|ghostty|notifications_disabled

  // Worktree
  "worktree": {
    "symlinkDirectories": ["node_modules", ".cache"],  // Symlink thay vì copy
    "sparsePaths": ["src/", "tests/"]  // Sparse checkout cho monorepo
  },

  // Proxy & network
  "skipWebFetchPreflight": false,      // true = skip WebFetch domain safety check
  "disableRemoteControl": false,       // (v2.1+) tắt Remote Control feature từ claude.ai/app

  // Hook safety (managed-only)
  "disableAllHooks": false,             // Tắt mọi hook (debug)
  "allowManagedHooksOnly": false,       // (managed) chỉ managed hooks
  "allowManagedPermissionRulesOnly": false  // (managed) chỉ managed perm rules
}
```

### 11.1 Permission rule syntax
- `Bash(git status)` — lệnh chính xác
- `Bash(git status:*)` — lệnh + bất kỳ args
- `Bash(git *)` — bất kỳ subcommand bắt đầu bằng `git`
- `Read(.env)` — file cụ thể
- `Read(**)` — mọi file
- `Read(./secrets/**)` — recursive trong dir
- `Edit(*.ts)` — pattern theo extension
- `WebFetch(*)` — bất kỳ URL
- `WebFetch(domain:example.com)` — domain cụ thể
- `WebFetch(domain:*.example.com)` — bất kỳ subdomain
- `Agent(Explore)` — subagent type cụ thể
- `Agent(my-custom-agent)` — custom subagent
- `MCP(github)` — MCP server theo tên

**Wildcard** (semantics khác nhau theo tool):
- `Read()`/`Edit()` (gitignore-style): `*` = single segment (không cross `/`), `**` = recursive
- `Bash()` (glob loose): `*` = match bất kỳ chuỗi ký tự kể cả khoảng trắng, span nhiều argument
- `WebFetch(domain:*.example.com)`: `*` = bất kỳ subdomain

**Path prefix** trong `Read()`/`Edit()`:

| Prefix             | Ý nghĩa                       | Ví dụ                                          |
| ------------------ | ----------------------------- | ---------------------------------------------- |
| `./` hoặc không có | Project-relative              | `Read(./src/**)` = file trong `<project>/src/` |
| `/`                | Project-relative (alias `./`) | `Read(/src/**)` = giống `./src/**`             |
| `//`               | Absolute từ filesystem root   | `Read(//etc/hosts)` = `/etc/hosts` thực        |
| `~/`               | Home dir                      | `Read(~/.zshrc)` = `$HOME/.zshrc`              |

**Evaluation order** (first match wins): `deny` → `ask` → `allow` → default.

> **Note**: `Task` tool đã rename thành `Agent` (rename trong v2.1.x). `Task(...)` rules cũ vẫn work như alias, nhưng nên dùng tên mới `Agent(<type>)`.

Compound commands (`&&`, `||`) được split — mỗi phần match riêng. Process wrapper (`timeout`, `time`, `nice`, `nohup`, `stdbuf`, `xargs`) tự strip khi match.

---

## 12. Environment variables

| Var                                        | Mục đích                                                                                                                                       |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `ANTHROPIC_API_KEY`                        | API key (nếu không OAuth)                                                                                                                      |
| `ANTHROPIC_DEFAULT_OPUS_MODEL`             | Override alias `opus`                                                                                                                          |
| `ANTHROPIC_DEFAULT_SONNET_MODEL`           | Override alias `sonnet`                                                                                                                        |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL`            | Override alias `haiku`                                                                                                                         |
| `MAX_THINKING_TOKENS`                      | Cap thinking tokens (0 = disable)                                                                                                              |
| `MAX_MCP_OUTPUT_TOKENS`                    | Cap MCP output (default 10k, tăng nếu cần)                                                                                                     |
| `MCP_TIMEOUT`                              | Timeout MCP server start (ms)                                                                                                                  |
| `CLAUDE_PROJECT_DIR`                       | Path project root (set tự động trong hook context, dùng trong hook script)                                                                     |
| `CLAUDE_CODE_SESSION_ID`                   | ID session hiện tại (set trong Bash/PowerShell tool subprocesses; cũng dùng trong skill `${CLAUDE_SESSION_ID}` substitution)                   |
| `CLAUDE_CODE_NEW_INIT=1`                   | Bật `/init` interactive multi-phase                                                                                                            |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`        | Bật PowerShell thay bash trên Windows (cũng yêu cầu khi skill có `shell: powershell`)                                                          |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable analytics                                                                                                                              |
| `CLAUDE_CODE_DEBUG_LOGS_DIR`               | Dir cho debug logs                                                                                                                             |
| `CLAUDE_CODE_SIMPLE`                       | `1` = minimal system prompt + chỉ Bash/Read/Edit tools. Cũng tự set bởi `--bare` flag                                                          |
| `ANTHROPIC_BASE_URL`                       | Override API endpoint (proxy/gateway)                                                                                                          |
| `ANTHROPIC_MODEL`                          | Override model mặc định                                                                                                                        |
| `ANTHROPIC_AUTH_TOKEN`                     | Custom Authorization header                                                                                                                    |
| `CLAUDE_CODE_EFFORT_LEVEL`                 | Override effort level (ưu tiên cao nhất). Accept `low`/`medium`/`high`/`xhigh`/`max`/`auto` — env var là cách duy nhất để set persistent `max` |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`  | Tắt adaptive reasoning (chỉ Opus 4.6 và Sonnet 4.6; Opus 4.7 không hỗ trợ disable, luôn dùng adaptive)                                         |
| `CLAUDE_CODE_DISABLE_THINKING`             | Tắt extended thinking                                                                                                                          |
| `CLAUDE_CODE_SHELL`                        | Override shell detection                                                                                                                       |
| `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION`     | Bật/tắt prompt suggestions (default `true`)                                                                                                    |
| `ENABLE_TOOL_SEARCH`                       | MCP tool search: `true` (always on), `auto` (>10% context), `auto:N` (custom %), `false` (load hết)                                            |
| `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`     | Max parallel tool execution (default 10)                                                                                                       |
| `API_TIMEOUT_MS`                           | API timeout (default 600000 = 10 phút)                                                                                                         |
| `BASH_DEFAULT_TIMEOUT_MS`                  | Bash timeout (default 120000 = 2 phút)                                                                                                         |
| `BASH_MAX_TIMEOUT_MS`                      | Bash max timeout (default 600000)                                                                                                              |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW`          | Context window cho auto-compaction                                                                                                             |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`          | Trigger auto-compact (default 95%)                                                                                                             |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS`           | Override context window size — CHỈ effect khi `DISABLE_COMPACT=1` (constraint cứng từ docs)                                                    |
| `CLAUDE_CODE_SUBAGENT_MODEL`               | Model cho subagent                                                                                                                             |
| `CLAUDECODE`                               | Set trong spawned shells (dùng để detect Claude env)                                                                                           |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY`          | Tắt auto memory                                                                                                                                |
| `CLAUDE_CODE_GIT_BASH_PATH`                | Path tới Git Bash (Windows)                                                                                                                    |
| `CLAUDE_CODE_NO_FLICKER`                   | `1` = bật fullscreen rendering mặc định                                                                                                        |
| `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN`     | `1` = force classic renderer                                                                                                                   |
| `CLAUDE_CODE_SCROLL_SPEED`                 | Tốc độ cuộn mouse (1-20, default auto)                                                                                                         |
| `CLAUDE_CODE_DISABLE_MOUSE`                | `1` = tắt mouse capture (giữ flicker-free, cho phép native text select)                                                                        |
| `HTTPS_PROXY` / `HTTP_PROXY`               | Proxy cho network requests                                                                                                                     |
| `NO_PROXY`                                 | Domains bỏ qua proxy (space hoặc comma-separated)                                                                                              |
| `CLAUDE_CODE_CERT_STORE`                   | CA cert source: `bundled,system` (default — load cả hai), `bundled`, `system`                                                                  |
| `NODE_EXTRA_CA_CERTS`                      | Path tới custom CA cert file                                                                                                                   |
| `CLAUDE_CONFIG_DIR`                        | Override đường dẫn ~/.claude                                                                                                                   |
| `CLAUDE_CODE_MAX_RETRIES`                  | Số lần retry khi API fail (default 10)                                                                                                         |
| `DISABLE_TELEMETRY`                        | Tắt toàn bộ telemetry/metrics                                                                                                                  |
| `CLAUDE_CODE_ENABLE_TELEMETRY`             | `1` = bật telemetry (default tùy plan/region). Override `DISABLE_TELEMETRY`                                                                    |
| `OTEL_METRICS_EXPORTER`                    | OpenTelemetry metrics exporter (vd `otlp`, `prometheus`)                                                                                       |
| `OTEL_EXPORTER_OTLP_ENDPOINT`              | OpenTelemetry endpoint URL                                                                                                                     |
| `DISABLE_AUTOUPDATER`                      | `1` = tắt auto-update CLI                                                                                                                      |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS`        | Refresh interval (ms) cho `apiKeyHelper` script (default tùy script return)                                                                    |
| `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS`     | `1` = bỏ git workflow khỏi system prompt (giảm baseline)                                                                                       |
| `DISABLE_ERROR_REPORTING`                  | Tắt Sentry error reporting                                                                                                                     |
| `DISABLE_PROMPT_CACHING`                   | `1` = tắt prompt caching (ưu tiên hơn per-model)                                                                                               |
| `DISABLE_PROMPT_CACHING_OPUS`              | `1` = tắt prompt caching cho Opus                                                                                                              |
| `DISABLE_PROMPT_CACHING_SONNET`            | `1` = tắt prompt caching cho Sonnet                                                                                                            |
| `DISABLE_PROMPT_CACHING_HAIKU`             | `1` = tắt prompt caching cho Haiku                                                                                                             |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`     | `1` = bật agent teams (experimental)                                                                                                           |
| `ANTHROPIC_VERTEX_PROJECT_ID`              | GCP project ID cho Vertex AI                                                                                                                   |
| `CLOUD_ML_REGION`                          | Region cho Vertex AI (vd: `us-east5`, `global`)                                                                                                |
| `ANTHROPIC_FOUNDRY_RESOURCE`               | Azure Foundry resource name                                                                                                                    |
| `ANTHROPIC_FOUNDRY_API_KEY`                | Azure Foundry API key                                                                                                                          |
| `ANTHROPIC_BEDROCK_BASE_URL`               | Override Bedrock endpoint URL                                                                                                                  |
| `ANTHROPIC_VERTEX_BASE_URL`                | Override Vertex AI endpoint URL                                                                                                                |
| `ANTHROPIC_FOUNDRY_BASE_URL`               | Override Foundry endpoint URL                                                                                                                  |
| `ANTHROPIC_CUSTOM_MODEL_OPTION`            | Custom model ID cho `/model` picker                                                                                                            |
| `ANTHROPIC_CUSTOM_MODEL_OPTION_NAME`       | Display name cho custom model                                                                                                                  |
| `ANTHROPIC_BETAS`                          | Comma-separated beta header values                                                                                                             |
| `ANTHROPIC_CUSTOM_HEADERS`                 | Custom HTTP headers (`Name: Value`)                                                                                                            |
| `CLAUDE_CODE_CLIENT_CERT`                  | Path tới mTLS client certificate                                                                                                               |
| `CLAUDE_CODE_CLIENT_KEY`                   | Path tới mTLS client key                                                                                                                       |
| `CLAUDE_CODE_DISABLE_FAST_MODE`            | `1` = tắt fast mode hoàn toàn                                                                                                                  |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT`           | `1` = tắt 1M context window                                                                                                                    |
| `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT`         | `1` = system prompt ngắn hơn (Opus 4.7)                                                                                                        |
| `CLAUDE_CODE_SKIP_PROMPT_HISTORY`          | `1` = không lưu transcript ra disk                                                                                                             |
| `BASH_MAX_OUTPUT_LENGTH`                   | Max ký tự bash output                                                                                                                          |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS`  | Token limit cho file reads                                                                                                                     |
| `CLAUDE_CODE_DEBUG_LOG_LEVEL`              | Log level: `verbose`\|`debug`\|`info`\|`warn`\|`error`                                                                                         |

---

## 13. Hook events — đầy đủ 29 event

Hook chạy DETERMINISTIC (KHÔNG phụ thuộc Claude nhớ rule). Định nghĩa trong `settings.json`, plugin, hoặc skill/agent frontmatter.

### 13.1 Per-session
| Event          | Khi fire                                     | Matcher                                                                                  |
| -------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `SessionStart` | Đầu session/resume                           | `startup`, `resume`, `clear`, `compact`                                                  |
| `Setup`        | `--init-only` hoặc `-p --init/--maintenance` | `init`, `maintenance`                                                                    |
| `SessionEnd`   | Cuối session                                 | `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` |

### 13.2 Per-turn
| Event                 | Khi fire                        | Matcher                                                                                                                                            |
| --------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `UserPromptSubmit`    | Mỗi message user                | (none)                                                                                                                                             |
| `UserPromptExpansion` | Khi command expand thành prompt | command names — có thể block expansion                                                                                                             |
| `Stop`                | Claude finish response          | (none)                                                                                                                                             |
| `StopFailure`         | Turn end vì API error           | `rate_limit`, `authentication_failed`, `oauth_org_not_allowed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown` |

### 13.3 Per-tool-call (agentic loop)
| Event                | Khi fire                              | Matcher                                           |
| -------------------- | ------------------------------------- | ------------------------------------------------- |
| `PreToolUse`         | Trước tool call                       | tool name, vd `Bash`, `Edit\|Write`, `mcp__.*`    |
| `PermissionRequest`  | Khi permission dialog xuất hiện       | tool name                                         |
| `PermissionDenied`   | Khi tool bị auto-mode classifier deny | tool name — return `{retry: true}` cho phép retry |
| `PostToolUse`        | Sau tool call thành công              | tool name                                         |
| `PostToolUseFailure` | Sau tool call fail                    | tool name                                         |
| `PostToolBatch`      | Sau batch tool call song song xong    | (none)                                            |

### 13.4 Subagent & task
| Event           | Khi fire                                            | Matcher                                                   |
| --------------- | --------------------------------------------------- | --------------------------------------------------------- |
| `SubagentStart` | Subagent spawn                                      | agent type (`Explore`, `Plan`, `general-purpose`, custom) |
| `SubagentStop`  | Subagent finish                                     | agent type                                                |
| `TaskCreated`   | Task được tạo trong shared task list của agent team | (none) — exit code 2 = block creation + send feedback     |
| `TaskCompleted` | Task được mark complete                             | (none) — exit code 2 = block completion + send feedback   |

### 13.5 Compact
| Event         | Khi fire         | Matcher          |
| ------------- | ---------------- | ---------------- |
| `PreCompact`  | Trước compact    | `manual`, `auto` |
| `PostCompact` | Sau compact xong | `manual`, `auto` |

### 13.6 Async events (notification, file, config…)
| Event                | Khi fire                                                 | Matcher                                                                                                                  |
| -------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `Notification`       | Claude gửi notification                                  | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_complete`, `elicitation_response` |
| `TeammateIdle`       | Agent team teammate sắp idle                             | (none) — exit code 2 = giữ teammate tiếp tục làm việc thay vì idle                                                       |
| `InstructionsLoaded` | CLAUDE.md / `.claude/rules/*.md` được load               | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`                                             |
| `ConfigChange`       | Config file thay đổi trong session                       | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills`                                       |
| `CwdChanged`         | Working dir thay đổi (`cd`)                              | (none) — useful cho direnv                                                                                               |
| `FileChanged`        | File watch trên disk thay đổi                            | filenames, vd `.envrc\|.env`                                                                                             |
| `WorktreeCreate`     | Tạo worktree (`--worktree` hoặc `isolation: "worktree"`) | (none)                                                                                                                   |
| `WorktreeRemove`     | Xóa worktree                                             | (none)                                                                                                                   |
| `Elicitation`        | MCP server xin input                                     | MCP server name                                                                                                          |
| `ElicitationResult`  | User trả lời elicitation                                 | MCP server name                                                                                                          |

### 13.7 Matcher syntax
| Format             | Đánh giá là            | Ví dụ                          |
| ------------------ | ---------------------- | ------------------------------ |
| `"*"`, `""`, omit  | Match tất cả           | Fire mọi occurrence            |
| Chữ/digit/`_`/`\|` | Exact string hoặc list | `Bash`, `Edit\|Write`          |
| Có ký tự khác      | JS regex               | `^Notebook`, `mcp__memory__.*` |

### 13.8 Filter chi tiết với `if`
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

### 14.1 Hook output (command/http)

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

### 15.1 Pattern 1 — Explore → Plan → Code → Commit
```text
1. Plan mode (Shift+Tab×2): "đọc src/auth, hiểu flow OAuth"
2. Plan mode: "viết plan thêm Google OAuth"
3. Exit plan: "implement plan, viết test, run test"
4. /commit
```

### 15.2 Pattern 2 — Writer / Reviewer (2 session)
- Session A: implement.
- Session B (fresh context): review code A vừa viết.
- Session A: address feedback từ B.

### 15.3 Pattern 3 — TDD (2 session)
- A: viết test cho spec.
- B (fresh): viết code pass test.

### 15.4 Pattern 4 — Investigation (subagent)
- Main: "use a subagent to investigate how X works".
- Subagent đọc nhiều file, return summary ngắn.
- Main giữ context sạch để implement.

### 15.5 Pattern 5 — Fan-out (parallel review)
```bash
git diff main --name-only > files.txt
for file in $(cat files.txt); do
  claude -p "review $file for security issues" \
    --allowedTools "Read,Grep" \
    --output-format json >> reviews.jsonl
done
```

### 15.6 Pattern 6 — Worktree parallel
```bash
git worktree add ../proj-feat-a feat/a
git worktree add ../proj-feat-b feat/b
# Mở 2 terminal, claude trong mỗi worktree
```

### 15.7 Pattern 7 — Brief-injection (long-running task)
- Session 1: làm việc, gần đầy context (>70%).
- `/handoff --save` → ghi `<project>/.claude/HANDOFF.md`.
- Thoát, mở session mới: `claude` (KHÔNG `--continue`).
- Prompt đầu: `Đọc .claude/HANDOFF.md và tiếp tục.`

### 15.8 Pattern 8 — Bulk migration (`/batch`)
```text
/batch migrate src/ from class components to hooks
```
→ Claude phân chia thành 5-30 unit, spawn 1 background agent / unit, mỗi cái mở PR riêng. Yêu cầu git repo.

### 15.9 Pattern 9 — Loop monitoring
```text
/loop 5m check if deploy finished, alert me when status changes
```

---

## 16. Quản lý context window — chi tiết

### 16.1 Tầm quan trọng

Mọi best practice xoay quanh 1 ràng buộc: **context window đầy nhanh, performance giảm khi đầy**. Mỗi message re-read toàn bộ history → cost grow exponential trong agentic session. Ở 80%+ context, Claude bắt đầu "quên" instruction sớm, lặp sai lầm cũ. Boris Cherny (tech lead Claude Code) giữ CLAUDE.md ~2,500 tokens.

### 16.2 Ngưỡng hành động

| % context | Hành động                                    |
| --------- | -------------------------------------------- |
| <40%      | 🟢 Sweet spot, làm việc bình thường          |
| 40-60%    | 🟢 OK, để ý task lớn sắp tới                 |
| 60-70%    | 🟡 Sau khi xong phase tiếp theo → `/compact` |
| 70-80%    | 🟠 `/compact` HOẶC `/handoff + /clear` ngay  |
| 80-95%    | 🔴 DỪNG. Brief-injection sang session mới    |
| 95%+      | Auto-compact firing — chất lượng đã giảm rồi |

### 16.3 `/compact` vs `/clear`

| `/compact`                           | `/clear`                          |
| ------------------------------------ | --------------------------------- |
| Nén history thành summary, GIỮ tiếp  | XÓA HẲN history, fresh start      |
| Cùng task, cần thread                | Sang task khác, không cần lịch sử |
| Lossy nhưng có thread                | Sạch hoàn toàn                    |
| Có thể `/compact <chỉ thị>` để hướng | Không nén, viết lại brief         |

### 16.4 Customize compaction

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

### 16.5 Giảm baseline (token cố định mỗi session)

| Nhóm                                       | Giảm bằng cách                                                                               |
| ------------------------------------------ | -------------------------------------------------------------------------------------------- |
| CLAUDE.md global                           | Giữ <100 dòng. Test "nếu xóa dòng này, Claude có làm sai không?" — không → xóa               |
| CLAUDE.md project                          | Tương tự, focus vào convention RIÊNG project, KHÔNG lặp lại global                           |
| `rules/*.md` import                        | Chỉ import rule áp dụng MỌI session. Còn lại để `@`-reference khi cần                        |
| Skill descriptions                         | `disable-model-invocation: true` cho skill ít dùng → chỉ load khi user gọi                   |
| MCP tools                                  | Disable MCP server không dùng cho phiên này. MCP v2.1+ deferred default — chỉ tool name load |
| `.claudeignore`                            | Loại file không bao giờ cần (lockfile, build output, asset binary...)                        |
| `--bare` flag                              | Skip auto-discovery cho script (hooks, skills, plugins, MCP, CLAUDE.md)                      |
| `--exclude-dynamic-system-prompt-sections` | Move per-machine sections → cải thiện prompt-cache                                           |

### 16.6 Giảm runtime (token tích lũy trong session)

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

### 16.7 Phân tích token usage

```text
/context
```
Output breakdown:
- System prompt
- Tools (built-in + MCP — MCP eats nhiều nếu nhiều server)
- Memory (CLAUDE.md + rules)
- Skills (descriptions)
- Conversation (messages + tool output + file content)

Mỗi nhóm chiếm % rõ ràng — fix nhóm > 15% trước.

### 16.8 Prompt caching (auto trong Claude Code)

Claude Code dùng prompt caching tự động để giảm cost cho conversation dài. Cache prefix giống nhau giữa các turn → read **0.1× giá input** thay vì full price. Cache TTL mặc định 5 phút (sliding window — refresh mỗi lần dùng).

| Cache TTL        | Write cost  | Read cost  |
| ---------------- | ----------- | ---------- |
| 5 phút (default) | 1.25× input | 0.1× input |
| 1 giờ            | 2× input    | 0.1× input |

**Min cacheable size** (prompt nhỏ hơn ngưỡng = không cache, không error):
- Opus 4.7/4.6/4.5, Haiku 4.5: **4,096 token**
- Sonnet 4.6, Haiku 3.5: **2,048 token**
- Model khác: **1,024 token**

**Disable** (env var):
- `DISABLE_PROMPT_CACHING=1` — tắt toàn bộ (ưu tiên hơn per-model)
- `DISABLE_PROMPT_CACHING_OPUS=1` / `_SONNET=1` / `_HAIKU=1` — tắt theo model

**Best practice cho cache hit rate cao**:
- Static content (system prompt, tool defs, large context, CLAUDE.md) phải đứng TRƯỚC user messages — KHÔNG xen timestamp/per-request data vào giữa.
- Conversation dài: cache breakpoint tự động dịch về turn mới nhất; content cũ read từ cache.
- Monitor: check field `usage` trong response API — `cache_read_input_tokens` (đọc từ cache), `cache_creation_input_tokens` (viết mới), `input_tokens` (không cache, charged full price).

**Khi cache hit thấp** (cost tăng bất ngờ):
- CLAUDE.md đổi giữa session → invalidate toàn bộ cache.
- Skill/subagent prompt thay đổi giữa turn.
- Reorder hoặc inject content vào giữa system prompt.
- Compact xong → cache phải build lại từ đầu.

### 16.9 Quy tắc survive sau `/compact`

- **Survive**: project-root CLAUDE.md (re-read từ disk), auto memory (re-injected từ disk; MEMORY.md cap 200 dòng/25KB lúc load)
- **Survive (capped)**: skills đã invoke — re-attach sau summary, mỗi skill giữ **5,000 token đầu**, tổng **25,000 token** (oldest dropped first)
- **Mất**: nested CLAUDE.md (sub-dir) — chỉ reload khi Claude đọc file trong dir đó
- **Mất**: skill descriptions chưa invoke — chỉ skills đã gọi trong session được giữ
- **Mất**: path-scoped rules — chỉ reload khi file matching được đọc lại
- **Mất**: conversation-only instructions (thêm vào CLAUDE.md nếu muốn persist)

---

## 17. Session management & handoff

### 17.1 Lựa chọn `/compact` vs `/clear` vs `/handoff`

```text
Sắp đầy context, vẫn làm tiếp cùng task ──► /compact (có instructions)
Sắp đầy context, sang task khác ──────────► /handoff --save → /clear → brief mới
Câu hỏi nhanh không cần lưu ──────────────► /btw
Một message bị sai hướng ─────────────────► Esc Esc → mở rewind menu (5 options)
Khôi phục trạng thái phiên trước ─────────► claude --continue (rủi ro stale data)
                                          HOẶC brief-injection (sạch hơn)
Fan-out task song song ───────────────────► claude -p ... background
Task riêng biệt cần context riêng ────────► subagent
Bulk migration nhiều file ────────────────► /batch
```

### 17.2 Anti-pattern resume long session

Theo Anthropic blog [Using Claude Code session management and 1M context](https://claude.com/blog/using-claude-code-session-management-and-1m-context):
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

### 17.3 Workflow handoff khuyến nghị

1. Khi `/context` >65%, hoặc kết thúc 1 phase công việc → gọi skill `/handoff` hoặc nói "viết handoff brief".
2. Save về `.claude/HANDOFF.md` (cần thêm vào `.gitignore` — xem Section 21 checklist).
3. `/compact giữ brief, drop debugging history` HOẶC `/clear` rồi prompt mới: `Đọc .claude/HANDOFF.md và tiếp tục từ "Bước tiếp"`.
4. Cuối ngày / cuối session → update HANDOFF.md → `git status` → commit work.

### 17.4 Bad-compact recovery

Triệu chứng:
- Sau compact, Claude lặp lại sai lầm session trước.
- Claude "quên" file vừa sửa.
- Claude hỏi lại quyết định đã chốt.

Cách xử lý:
1. KHÔNG `/compact` lần nữa (compact context bẩn = bẩn tiếp).
2. Đọc lại HANDOFF.md cũ (nếu có) hoặc git log để khôi phục state.
3. `/clear`, mở session mới, brief-inject thủ công.

### 17.5 Lỗi context-related

| Lỗi                                              | Nguyên nhân thường gặp                                              | Fix                                                  |
| ------------------------------------------------ | ------------------------------------------------------------------- | ---------------------------------------------------- |
| `Prompt is too long`                             | Vượt context window khi auto-compact bị tắt                         | Bật auto-compact, `/compact` thủ công, hoặc `/clear` |
| `Error during compaction: Conversation too long` | Compaction fail vì conversation quá lớn                             | `/clear` + brief-injection thay vì compact lại       |
| `Internal server error (500)`                    | Lỗi infrastructure (KHÔNG phải do context). Retry hoặc check status | Đợi rồi retry, không phải lý do để compact           |
| `ECONNRESET` / `EPIPE`                           | Lỗi network (KHÔNG phải context)                                    | Check kết nối, proxy, VPN                            |
| Auto-compact "thrashing"                         | 1 file/output quá lớn → context refill ngay sau compact             | Loại file đó (`.claudeignore`) hoặc `/clear`         |

---

## 18. Common failures & fix

| Pattern                       | Triệu chứng                                                                             | Fix                                                                           |
| ----------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Kitchen sink session          | Context bẩn, Claude lú                                                                  | `/clear` giữa task khác nhau                                                  |
| Correction loop               | Sửa 2-3 lần vẫn sai                                                                     | `/clear` + reprompt với info đã học                                           |
| Bloated CLAUDE.md             | Claude bỏ qua rule                                                                      | Prune dòng, target <100                                                       |
| Trust without verify          | Code "chạy" nhưng buggy                                                                 | Test/screenshot verify mọi output                                             |
| Infinite exploration          | Claude đọc 100 file                                                                     | Scope narrow hoặc subagent                                                    |
| Vague prompt                  | Output sai intent                                                                       | Context cụ thể hơn (file, ví dụ, constraint)                                  |
| Hung MCP eating context       | 30%+ baseline khi `ENABLE_TOOL_SEARCH=false` (deferred load mặc định = chỉ ~120 tokens) | `claude mcp list` + disable cái không cần, hoặc giữ `ENABLE_TOOL_SEARCH=auto` |
| Bad compact                   | Lặp sai lầm sau compact                                                                 | `/clear` + brief-injection thay vì compact lại                                |
| "Help me refactor X" vague    | Multi-turn clarification → token waste                                                  | Mô tả constraint + acceptance criteria upfront                                |
| MCP tool fail "not connected" | Hook MCP fire trước khi server connect                                                  | `SessionStart`/`Setup` hooks expect lỗi này lần đầu                           |

---

## 19. Hướng dẫn chọn feature

| Cần                             | Dùng                                                     |
| ------------------------------- | -------------------------------------------------------- |
| Hướng dẫn load mọi session      | `CLAUDE.md` (giữ <100 dòng)                              |
| Hướng dẫn theo chủ đề           | `rules/*.md` (auto-import OR `@`-reference khi cần)      |
| Workflow tái sử dụng (gọi `/`)  | `skills/<name>/SKILL.md`                                 |
| Task isolated context           | Subagent (`agents/*.md`)                                 |
| Hành động BẮT BUỘC chạy mỗi lần | Hook (`settings.json`) — deterministic                   |
| Tool ngoài (Notion, GitHub, DB) | MCP server                                               |
| Permission tinh chỉnh           | `permissions` trong settings                             |
| Persistent across sessions      | Auto memory (Claude tự ghi)                              |
| Sandbox an toàn                 | `/sandbox` hoặc `sandbox: true`                          |
| Cộng tác nhiều agent            | Subagents + agent teams                                  |
| Run khi máy tắt                 | `/schedule` (cloud routine)                              |
| Style trả lời khác              | `/output-style` (built-in: Default/Explanatory/Learning) |
| Loại file Claude khỏi đọc       | `.claudeignore`                                          |
| Bulk migration parallel         | `/batch <instruction>`                                   |
| Auto-fix PR khi CI fail         | `/autofix-pr`                                            |
| Watch external event            | `/loop <interval> <prompt>`                              |
| Audit security trên diff        | `/security-review`                                       |
| Mở Claude Code từ URL           | Deep link: `claude-cli://open?q=<prompt>&cwd=<path>`     |
| Tắt deep link handler           | `disableDeepLinkRegistration: "disable"` trong settings  |

---

## 20. Tài liệu chính thức

### 20.1 Setup & onboarding
- Overview: <https://code.claude.com/docs/en/overview>
- Quickstart: <https://code.claude.com/docs/en/quickstart>
- How Claude Code works: <https://code.claude.com/docs/en/how-claude-code-works>
- Features overview: <https://code.claude.com/docs/en/features-overview>
- Platforms: <https://code.claude.com/docs/en/platforms>
- Setup: <https://code.claude.com/docs/en/setup>
- `.claude` directory: <https://code.claude.com/docs/en/claude-directory>
- Best practices: <https://code.claude.com/docs/en/best-practices>

### 20.2 Memory & context
- Memory: <https://code.claude.com/docs/en/memory>
- Checkpointing: <https://code.claude.com/docs/en/checkpointing>
- Manage sessions: <https://code.claude.com/docs/en/sessions>
- Reduce token usage: <https://code.claude.com/docs/en/costs#reduce-token-usage>
- Context window (platform API): <https://platform.claude.com/docs/en/build-with-claude/context-windows>
- Prompt caching (platform): <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>

### 20.3 Models, effort & fast mode
- Model config & effort: <https://code.claude.com/docs/en/model-config>
- Models overview (platform): <https://platform.claude.com/docs/en/about-claude/models/overview>
- Fast mode: <https://code.claude.com/docs/en/fast-mode>

### 20.4 Skills, subagents & output styles
- Skills: <https://code.claude.com/docs/en/skills>
- Subagents: <https://code.claude.com/docs/en/sub-agents>
- Agent teams: <https://code.claude.com/docs/en/agent-teams>
- Output styles: <https://code.claude.com/docs/en/output-styles>

### 20.5 Hooks, permissions & sandboxing
- Hooks: <https://code.claude.com/docs/en/hooks>
- Hooks guide: <https://code.claude.com/docs/en/hooks-guide>
- Permissions: <https://code.claude.com/docs/en/permissions>
- Permission modes: <https://code.claude.com/docs/en/permission-modes>
- Sandboxing: <https://code.claude.com/docs/en/sandboxing>
- Auto mode config: <https://code.claude.com/docs/en/auto-mode-config>

### 20.6 Configuration
- Settings: <https://code.claude.com/docs/en/settings>
- Environment variables: <https://code.claude.com/docs/en/env-vars>
- Keybindings: <https://code.claude.com/docs/en/keybindings>
- Statusline: <https://code.claude.com/docs/en/statusline>
- Terminal config: <https://code.claude.com/docs/en/terminal-config>
- Network config: <https://code.claude.com/docs/en/network-config>
- LLM gateway: <https://code.claude.com/docs/en/llm-gateway>

### 20.7 Commands & CLI
- CLI reference: <https://code.claude.com/docs/en/cli-reference>
- Commands reference: <https://code.claude.com/docs/en/commands>
- Tools reference: <https://code.claude.com/docs/en/tools-reference>
- Interactive mode: <https://code.claude.com/docs/en/interactive-mode>
- Voice dictation: <https://code.claude.com/docs/en/voice-dictation>
- Fullscreen rendering: <https://code.claude.com/docs/en/fullscreen>
- Common workflows: <https://code.claude.com/docs/en/common-workflows>
- Ultraplan: <https://code.claude.com/docs/en/ultraplan>
- Ultrareview: <https://code.claude.com/docs/en/ultrareview>
- Routines: <https://code.claude.com/docs/en/routines>
- Code review: <https://code.claude.com/docs/en/code-review>

### 20.8 MCP & plugins
- MCP: <https://code.claude.com/docs/en/mcp>
- Plugins: <https://code.claude.com/docs/en/plugins>
- Plugins reference: <https://code.claude.com/docs/en/plugins-reference>
- Discover plugins: <https://code.claude.com/docs/en/discover-plugins>
- Plugin marketplaces: <https://code.claude.com/docs/en/plugin-marketplaces>
- Channels: <https://code.claude.com/docs/en/channels>
- Channels reference: <https://code.claude.com/docs/en/channels-reference>

### 20.9 Cloud, web & UI
- Desktop app: <https://code.claude.com/docs/en/desktop>
- Desktop quickstart: <https://code.claude.com/docs/en/desktop-quickstart>
- Claude Code on the web: <https://code.claude.com/docs/en/claude-code-on-the-web>
- Web quickstart: <https://code.claude.com/docs/en/web-quickstart>
- Remote control: <https://code.claude.com/docs/en/remote-control>
- Computer use (CLI): <https://code.claude.com/docs/en/computer-use>
- Chrome (beta): <https://code.claude.com/docs/en/chrome>
- Slack: <https://code.claude.com/docs/en/slack>
- Scheduled tasks: <https://code.claude.com/docs/en/scheduled-tasks>
- Desktop scheduled tasks: <https://code.claude.com/docs/en/desktop-scheduled-tasks>
- Web scheduled tasks: <https://code.claude.com/docs/en/web-scheduled-tasks>

### 20.10 IDE integration
- VS Code: <https://code.claude.com/docs/en/vs-code>
- JetBrains: <https://code.claude.com/docs/en/jetbrains>

### 20.11 CI/CD & deployment
- GitHub Actions: <https://code.claude.com/docs/en/github-actions>
- GitHub Enterprise Server: <https://code.claude.com/docs/en/github-enterprise-server>
- GitLab CI/CD: <https://code.claude.com/docs/en/gitlab-ci-cd>
- Devcontainer: <https://code.claude.com/docs/en/devcontainer>
- Headless: <https://code.claude.com/docs/en/headless>

### 20.12 Cloud providers
- Amazon Bedrock: <https://code.claude.com/docs/en/amazon-bedrock>
- Google Vertex AI: <https://code.claude.com/docs/en/google-vertex-ai>
- Microsoft Foundry: <https://code.claude.com/docs/en/microsoft-foundry>

### 20.13 SDK
- Agent SDK overview: <https://code.claude.com/docs/en/agent-sdk/overview>
- Slash commands SDK: <https://code.claude.com/docs/en/agent-sdk/slash-commands>

### 20.14 Enterprise & admin
- Admin setup: <https://code.claude.com/docs/en/admin-setup>
- Authentication: <https://code.claude.com/docs/en/authentication>
- Analytics: <https://code.claude.com/docs/en/analytics>
- Manage costs: <https://code.claude.com/docs/en/costs>
- Monitoring usage: <https://code.claude.com/docs/en/monitoring-usage>
- Server-managed settings: <https://code.claude.com/docs/en/server-managed-settings>
- Third-party integrations: <https://code.claude.com/docs/en/third-party-integrations>
- Code review (CI integration): <https://code.claude.com/docs/en/code-review>

### 20.15 Security & compliance
- Security: <https://code.claude.com/docs/en/security>
- Zero data retention: <https://code.claude.com/docs/en/zero-data-retention>
- Data usage: <https://code.claude.com/docs/en/data-usage>
- Legal and compliance: <https://code.claude.com/docs/en/legal-and-compliance>

### 20.16 Troubleshooting & errors
- Errors reference: <https://code.claude.com/docs/en/errors>
- Troubleshooting: <https://code.claude.com/docs/en/troubleshooting>
- Troubleshoot install: <https://code.claude.com/docs/en/troubleshoot-install>

### 20.17 Manage Claude (platform API)
- Rate limits API: <https://platform.claude.com/docs/en/manage-claude/rate-limits-api>
- Usage cost API: <https://platform.claude.com/docs/en/manage-claude/usage-cost-api>
- Claude Code analytics API: <https://platform.claude.com/docs/en/manage-claude/claude-code-analytics-api>

### 20.18 Index & release notes
- Changelog: <https://code.claude.com/docs/en/changelog>
- What's new: <https://code.claude.com/docs/en/whats-new/index>
- LLM-friendly index (Claude Code): <https://code.claude.com/docs/llms.txt>
- LLM-friendly index (platform): <https://docs.anthropic.com/llms.txt>

### 20.19 Blogs & engineering writing
- Engineering blog: <https://www.anthropic.com/engineering>
- Session management blog: <https://claude.com/blog/using-claude-code-session-management-and-1m-context>
- Prompting best practices (platform): <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>

### 20.20 Cộng đồng tham khảo

- Anthropics Claude Code repo: <https://github.com/anthropics/claude-code>
- Official plugin marketplace (Anthropic-curated): <https://github.com/anthropics/claude-plugins-official> — cài bằng `/plugin install <name>@claude-plugins-official` (chứa `code-review`, `commit-commands`, `feature-dev`, `mcp-server-dev`, `plugin-dev`, `pr-review-toolkit`, `frontend-design`, các LSP plugin)
- Anthropic skills examples + spec: <https://github.com/anthropics/skills> — `/plugin marketplace add anthropics/skills` rồi install `document-skills` hoặc `example-skills`. Có `spec/` (Agent Skills specification) và `template/` (skill template chính thức)
- Awesome Claude Code: <https://github.com/hesreallyhim/awesome-claude-code>
- ClaudeLog: <https://claudelog.com>
- ClaudeFast guides: <https://claudefa.st/blog>
- MindStudio Claude Code blog: <https://www.mindstudio.ai/blog>

---

## 21. Checklist & mẹo cuối

### 21.1 Đầu mỗi project mới
- [ ] Copy template vào project root: `cp ~/.claude/templates/project-CLAUDE.md ./CLAUDE.md`
- [ ] Sửa CLAUDE.md mô tả tech stack, lệnh build/test, convention RIÊNG project
- [ ] Tạo `.claudeignore` loại file lớn không cần (`dist/`, `node_modules/`, `*.lock`, `coverage/`, asset binary)
- [ ] Tạo `<project>/.claude/settings.json` từ template
- [ ] `echo "CLAUDE.local.md" >> .gitignore` + `echo ".claude/settings.local.json" >> .gitignore` + `echo ".claude/HANDOFF.md" >> .gitignore`
- [ ] `claude doctor` để verify

### 21.2 Đầu mỗi session
- [ ] Brief 1-2 câu mục tiêu phiên này
- [ ] `/context` xem baseline
- [ ] Nếu có `.claude/HANDOFF.md` từ phiên trước → đọc

### 21.3 Trong session
- [ ] Plan trước cho task >3 file (`/plan` hoặc Shift+Tab×2)
- [ ] Verify mọi output (test, lint, screenshot)
- [ ] Subagent cho investigation
- [ ] Commit thường xuyên (checkpoint để revert)
- [ ] Theo dõi `/context` — <40% sweet spot, >60% nên action
- [ ] Sửa 2 lần vẫn sai → `/clear` + reprompt, đừng spam correction
- [ ] `/effort high` hoặc `ultrathink` cho task khó (architecture, debug heisenbug, refactor lớn)

### 21.4 Cuối session
- [ ] `/handoff --save` nếu việc còn dở
- [ ] Commit work in-progress hoặc stash
- [ ] Update `<project>/CLAUDE.md` nếu phát hiện convention mới đáng ghi

### 21.5 Định kỳ (hàng tháng)
- [ ] Review `~/.claude/CLAUDE.md` — bỏ dòng không còn cần
- [ ] Review `~/.claude/skills/` — skill nào không dùng → bỏ hoặc set `disable-model-invocation: true`
- [ ] `git log` của repo `~/.claude/` — xem evolve thế nào (worth committing)
- [ ] `claude update`
- [ ] `/insights` xem session pattern, friction points

### 21.6 Mẹo cuối
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
