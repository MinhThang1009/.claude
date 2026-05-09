# Claude Code CLI — Lệnh quan trọng

> Lọc từ [commands reference](https://code.claude.com/docs/en/commands). Chỉ giữ lệnh hay dùng + bundled skills đáng nhớ.

## Session setup

| Lệnh | Chức năng |
|---|---|
| `/init` | Tạo CLAUDE.md starter từ codebase. Thêm `CLAUDE_CODE_NEW_INIT=1` cho interactive flow (skills, hooks, memory) |
| `/memory` | Xem/sửa CLAUDE.md + toggle auto-memory |
| `/permissions` | Quản lý allow/deny/ask rules + xem auto mode denials |
| `/agents` | Tạo/sửa/xóa subagents |
| `/mcp` | Quản lý MCP server connections |
| `/hooks` | Xem hook configurations |
| `/config` | Theme, model, output style, preferences |

## Trong session

| Lệnh | Chức năng |
|---|---|
| `/plan` | Chuyển plan mode — explore trước khi edit |
| `/model` | Đổi model (left/right arrows chỉnh effort) |
| `/effort` | Chỉnh effort level (`low`/`medium`/`high`/`xhigh`/`max`) |
| `/fast` | Toggle fast mode (Opus 4.6 output nhanh hơn) |
| `/context` | Visualize context usage — grid + optimization suggestions |
| `/compact` | Compact context, optional focus: `/compact Focus on API changes` |
| `/btw` | Side question — không vào history, không tốn context |
| `/diff` | Interactive diff viewer — uncommitted changes + per-turn diffs |

## Quality check

| Lệnh | Chức năng |
|---|---|
| `/simplify` | **Bundled skill** — review recent files, fix quality + efficiency |
| `/review` | Review PR locally |
| `/security-review` | Security pass read-only |
| `/ultrareview` | Multi-agent deep code review trên cloud |

## Undo / Navigate

| Lệnh | Chức năng |
|---|---|
| `/rewind` | Rollback code + conversation đến checkpoint. Aliases: `/undo`, `/checkpoint` |
| `/clear` | Reset context hoàn toàn. Alias: `/reset` |
| `/resume` | Quay lại session cũ. Alias: `/continue` |
| `/branch` | Fork conversation tại điểm hiện tại |
| `/rename` | Đặt tên session để tìm lại dễ |

## Scale / Automate

| Lệnh | Chức năng |
|---|---|
| `/batch` | **Bundled skill** — parallel changes across codebase (worktree per unit, auto PR) |
| `/loop` | Chạy prompt lặp lại theo interval: `/loop 5m check deploy` |
| `/fewer-permission-prompts` | **Bundled skill** — scan transcripts, auto-add allowlist |
| `/claude-api` | **Bundled skill** — Claude API reference + migrate model versions |

## Debug / Utility

| Lệnh | Chức năng |
|---|---|
| `/doctor` | Diagnose installation + settings |
| `/debug` | Enable debug logging + troubleshoot |
| `/feedback` | Report bug kèm session context |
| `/copy` | Copy response cuối ra clipboard. `/copy 2` = response trước |
| `/export` | Export conversation thành text file |
| `/skills` | Xem danh sách skills available |

## Nên nhớ nhất (dùng hàng ngày)

`/plan` · `/compact` · `/btw` · `/clear` · `/rewind` · `/context` · `/simplify` · `/diff`

## CLI flags (chạy từ terminal)

| Flag | Chức năng |
|---|---|
| `claude -p "prompt"` | Chạy non-interactive (CI, scripts, batch) |
| `claude --continue` | Resume session gần nhất |
| `claude --resume` | Chọn session từ danh sách |
| `claude --worktree name` | Mở session trong isolated git worktree |
| `claude --permission-mode auto` | Chạy với auto mode (background safety checks) |
| `claude --permission-mode plan` | Bắt đầu luôn ở plan mode |
| `claude --agent name` | Chạy main session với subagent definition |
| `claude --add-dir path` | Thêm working directory cho file access |
| `claude --output-format json` | Output JSON (dùng với `-p` cho scripts) |
| `claude --allowedTools "Edit,Bash(npm test *)"` | Giới hạn tools cho session |
| `claude agents` | List tất cả agents (không cần mở session) |
| `claude mcp list` | List MCP servers đã cấu hình |
