---
name: Hook Development
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse/PostToolUse/Stop hook", "validate tool use", "implement prompt-based hooks", "use ${CLAUDE_PLUGIN_ROOT}", "set up event-driven automation", "block dangerous commands", or mentions hook events (PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification). Provides comprehensive guidance for creating and implementing Claude Code plugin hooks with focus on advanced prompt-based hooks API.
version: 0.1.0
---

# Phát triển Hook cho Claude Code Plugins

## Tổng quan

Hook là các script tự động hóa theo sự kiện, thực thi khi có sự kiện Claude Code xảy ra. Dùng hook để xác thực thao tác, áp dụng chính sách, bổ sung ngữ cảnh, và tích hợp công cụ bên ngoài vào quy trình làm việc.

**Khả năng chính:**
- Xác thực lệnh gọi tool trước khi thực thi (PreToolUse)
- Phản ứng với kết quả tool (PostToolUse)
- Áp dụng tiêu chuẩn hoàn thành (Stop, SubagentStop)
- Tải ngữ cảnh dự án (SessionStart)
- Tự động hóa quy trình xuyên suốt vòng đời phát triển

## Loại Hook

### Hook Dựa trên Prompt (Khuyến nghị)

Dùng khả năng ra quyết định của LLM cho việc xác thực nhận biết ngữ cảnh:

```json
{
  "type": "prompt",
  "prompt": "Evaluate if this tool use is appropriate: $TOOL_INPUT",
  "timeout": 30
}
```

**Sự kiện được hỗ trợ:** Stop, SubagentStop, UserPromptSubmit, PreToolUse

**Lợi ích:**
- Ra quyết định nhận biết ngữ cảnh dựa trên lý luận ngôn ngữ tự nhiên
- Logic đánh giá linh hoạt không cần viết bash script
- Xử lý edge case tốt hơn
- Dễ bảo trì và mở rộng

### Hook Lệnh (Command)

Thực thi lệnh bash cho các kiểm tra xác định:

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 60
}
```

**Dùng cho:**
- Xác thực xác định nhanh
- Thao tác hệ thống file
- Tích hợp công cụ bên ngoài
- Kiểm tra quan trọng về hiệu năng

## Định dạng Cấu hình Hook

### Định dạng hooks.json của Plugin

**Dành cho hook plugin** trong `hooks/hooks.json`, dùng định dạng wrapper:

```json
{
  "description": "Mô tả ngắn về các hook (tùy chọn)",
  "hooks": {
    "PreToolUse": [...],
    "Stop": [...],
    "SessionStart": [...]
  }
}
```

**Điểm quan trọng:**
- Trường `description` là tùy chọn
- Trường `hooks` là wrapper bắt buộc chứa các sự kiện hook thực tế
- Đây là **định dạng dành riêng cho plugin**

**Ví dụ:**
```json
{
  "description": "Validation hooks for code quality",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/validate.sh"
          }
        ]
      }
    ]
  }
}
```

### Định dạng Settings (Trực tiếp)

**Dành cho cài đặt người dùng** trong `.claude/settings.json`, dùng định dạng trực tiếp:

```json
{
  "PreToolUse": [...],
  "Stop": [...],
  "SessionStart": [...]
}
```

**Điểm quan trọng:**
- Không có wrapper — sự kiện đặt trực tiếp ở cấp cao nhất
- Không có trường description
- Đây là **định dạng settings**

**Lưu ý quan trọng:** Các ví dụ dưới đây hiển thị cấu trúc sự kiện hook đặt bên trong một trong hai định dạng. Với hooks.json của plugin, bọc chúng trong `{"hooks": {...}}`.

## Sự kiện Hook

### PreToolUse

Thực thi trước khi bất kỳ tool nào chạy. Dùng để phê duyệt, từ chối, hoặc chỉnh sửa lệnh gọi tool.

**Ví dụ (dựa trên prompt):**
```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate file write safety. Check: system paths, credentials, path traversal, sensitive content. Return 'approve' or 'deny'."
        }
      ]
    }
  ]
}
```

**Output cho PreToolUse:**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {"field": "modified_value"}
  },
  "systemMessage": "Explanation for Claude"
}
```

### PostToolUse

Thực thi sau khi tool hoàn thành. Dùng để phản ứng với kết quả, cung cấp phản hồi, hoặc ghi log.

**Ví dụ:**
```json
{
  "PostToolUse": [
    {
      "matcher": "Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Analyze edit result for potential issues: syntax errors, security vulnerabilities, breaking changes. Provide feedback."
        }
      ]
    }
  ]
}
```

**Hành vi output:**
- Exit 0: stdout hiển thị trong transcript
- Exit 2: stderr được phản hồi lại cho Claude
- systemMessage được đưa vào ngữ cảnh

### Stop

Thực thi khi agent chính cân nhắc dừng. Dùng để xác thực tính hoàn chỉnh.

**Ví dụ:**
```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Verify task completion: tests run, build succeeded, questions answered. Return 'approve' to stop or 'block' with reason to continue."
        }
      ]
    }
  ]
}
```

**Output quyết định:**
```json
{
  "decision": "approve|block",
  "reason": "Explanation",
  "systemMessage": "Additional context"
}
```

### SubagentStop

Thực thi khi subagent cân nhắc dừng. Dùng để đảm bảo subagent đã hoàn thành nhiệm vụ.

Tương tự hook Stop, nhưng dành cho subagent.

### UserPromptSubmit

Thực thi khi người dùng gửi prompt. Dùng để thêm ngữ cảnh, xác thực, hoặc chặn prompt.

**Ví dụ:**
```json
{
  "UserPromptSubmit": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Check if prompt requires security guidance. If discussing auth, permissions, or API security, return relevant warnings."
        }
      ]
    }
  ]
}
```

### SessionStart

Thực thi khi phiên Claude Code bắt đầu. Dùng để tải ngữ cảnh và thiết lập môi trường.

**Ví dụ:**
```json
{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh"
        }
      ]
    }
  ]
}
```

**Khả năng đặc biệt:** Duy trì biến môi trường bằng `$CLAUDE_ENV_FILE`:
```bash
echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
```

Xem `examples/load-context.sh` để biết ví dụ đầy đủ.

### SessionEnd

Thực thi khi phiên kết thúc. Dùng để dọn dẹp, ghi log, và lưu trạng thái.

### PreCompact

Thực thi trước khi nén ngữ cảnh. Dùng để thêm thông tin quan trọng cần giữ lại.

### Notification

Thực thi khi Claude gửi thông báo. Dùng để phản ứng với thông báo người dùng.

## Định dạng Output của Hook

### Output Chuẩn (Tất cả Hook)

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message for Claude"
}
```

- `continue`: Nếu false, dừng xử lý (mặc định true)
- `suppressOutput`: Ẩn output khỏi transcript (mặc định false)
- `systemMessage`: Thông điệp hiển thị cho Claude

### Exit Code

- `0` - Thành công (stdout hiển thị trong transcript)
- `2` - Lỗi chặn (stderr phản hồi lại cho Claude)
- Khác - Lỗi không chặn

## Định dạng Input của Hook

Tất cả hook nhận JSON qua stdin với các trường chung:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "permission_mode": "ask|allow",
  "hook_event_name": "PreToolUse"
}
```

**Trường dành riêng cho từng sự kiện:**

- **PreToolUse/PostToolUse:** `tool_name`, `tool_input`, `tool_result`
- **UserPromptSubmit:** `user_prompt`
- **Stop/SubagentStop:** `reason`

Truy cập các trường trong prompt bằng `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT`, v.v.

## Biến Môi trường

Có sẵn trong tất cả hook lệnh:

- `$CLAUDE_PROJECT_DIR` - Đường dẫn gốc dự án
- `$CLAUDE_PLUGIN_ROOT` - Thư mục plugin (dùng cho path di động)
- `$CLAUDE_ENV_FILE` - Chỉ SessionStart: duy trì biến môi trường tại đây
- `$CLAUDE_CODE_REMOTE` - Được đặt nếu chạy trong ngữ cảnh remote

**Luôn dùng ${CLAUDE_PLUGIN_ROOT} trong lệnh hook để đảm bảo tính di động:**

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
}
```

## Cấu hình Hook Plugin

Trong plugin, định nghĩa hook trong `hooks/hooks.json`:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate file write safety"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Verify task completion"
        }
      ]
    }
  ],
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh",
          "timeout": 10
        }
      ]
    }
  ]
}
```

Hook plugin được hợp nhất với hook của người dùng và chạy song song.

## Matcher

### Khớp Tên Tool

**Khớp chính xác:**
```json
"matcher": "Write"
```

**Nhiều tool:**
```json
"matcher": "Read|Write|Edit"
```

**Wildcard (tất cả tool):**
```json
"matcher": "*"
```

**Regex pattern:**
```json
"matcher": "mcp__.*__delete.*"  // Tất cả MCP delete tool
```

**Lưu ý:** Matcher phân biệt chữ hoa/thường.

### Các Pattern Phổ biến

```json
// Tất cả MCP tool
"matcher": "mcp__.*"

// MCP tool của một plugin cụ thể
"matcher": "mcp__plugin_asana_.*"

// Tất cả thao tác file
"matcher": "Read|Write|Edit"

// Chỉ lệnh Bash
"matcher": "Bash"
```

## Thực hành Bảo mật Tốt nhất

### Xác thực Input

Luôn xác thực input trong hook lệnh:

```bash
#!/bin/bash
set -euo pipefail

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

# Xác thực định dạng tên tool
if [[ ! "$tool_name" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo '{"decision": "deny", "reason": "Invalid tool name"}' >&2
  exit 2
fi
```

### An toàn Path

Kiểm tra path traversal và file nhạy cảm:

```bash
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Từ chối path traversal
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
  exit 2
fi

# Từ chối file nhạy cảm
if [[ "$file_path" == *".env"* ]]; then
  echo '{"decision": "deny", "reason": "Sensitive file"}' >&2
  exit 2
fi
```

Xem `examples/validate-write.sh` và `examples/validate-bash.sh` để biết ví dụ đầy đủ.

### Đặt Nháy Tất cả Biến

```bash
# TỐT: Có nháy
echo "$file_path"
cd "$CLAUDE_PROJECT_DIR"

# XẤU: Không nháy (nguy cơ injection)
echo $file_path
cd $CLAUDE_PROJECT_DIR
```

### Đặt Timeout Phù hợp

```json
{
  "type": "command",
  "command": "bash script.sh",
  "timeout": 10
}
```

**Mặc định:** Hook lệnh (60s), Hook prompt (30s)

## Cân nhắc về Hiệu năng

### Thực thi Song song

Tất cả hook khớp chạy **song song**:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {"type": "command", "command": "check1.sh"},  // Song song
        {"type": "command", "command": "check2.sh"},  // Song song
        {"type": "prompt", "prompt": "Validate..."}   // Song song
      ]
    }
  ]
}
```

**Hàm ý thiết kế:**
- Các hook không thấy output của nhau
- Thứ tự không xác định
- Thiết kế để độc lập

### Tối ưu hóa

1. Dùng hook lệnh cho kiểm tra xác định nhanh
2. Dùng hook prompt cho lý luận phức tạp
3. Cache kết quả xác thực trong file tạm
4. Giảm thiểu I/O trong đường dẫn hot path

## Hook Kích hoạt Tạm thời

Tạo hook kích hoạt có điều kiện bằng cách kiểm tra flag file hoặc cấu hình:

**Pattern: Kích hoạt bằng flag file**
```bash
#!/bin/bash
# Chỉ kích hoạt khi flag file tồn tại
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-strict-validation"

if [ ! -f "$FLAG_FILE" ]; then
  # Flag không có, bỏ qua xác thực
  exit 0
fi

# Flag có, chạy xác thực
input=$(cat)
# ... logic xác thực ...
```

**Pattern: Kích hoạt dựa trên cấu hình**
```bash
#!/bin/bash
# Kiểm tra cấu hình để kích hoạt
CONFIG_FILE="$CLAUDE_PROJECT_DIR/.claude/plugin-config.json"

if [ -f "$CONFIG_FILE" ]; then
  enabled=$(jq -r '.strictMode // false' "$CONFIG_FILE")
  if [ "$enabled" != "true" ]; then
    exit 0  # Chưa bật, bỏ qua
  fi
fi

# Đã bật, chạy logic hook
input=$(cat)
# ... logic hook ...
```

**Trường hợp dùng:**
- Bật xác thực nghiêm ngặt chỉ khi cần
- Hook debug tạm thời
- Hành vi hook dành riêng cho dự án
- Feature flag cho hook

**Thực hành tốt nhất:** Ghi lại cơ chế kích hoạt trong README của plugin để người dùng biết cách bật/tắt hook tạm thời.

## Vòng đời và Giới hạn của Hook

### Hook Được Tải Khi Bắt đầu Phiên

**Quan trọng:** Hook được tải khi phiên Claude Code bắt đầu. Thay đổi cấu hình hook yêu cầu khởi động lại Claude Code.

**Không thể hot-swap hook:**
- Chỉnh sửa `hooks/hooks.json` sẽ không ảnh hưởng đến phiên hiện tại
- Thêm script hook mới sẽ không được nhận ra
- Thay đổi lệnh/prompt hook sẽ không cập nhật
- Phải khởi động lại Claude Code: thoát và chạy `claude` lại

**Để kiểm tra thay đổi hook:**
1. Chỉnh sửa cấu hình hoặc script hook
2. Thoát phiên Claude Code
3. Khởi động lại: `claude` hoặc `cc`
4. Cấu hình hook mới được tải
5. Kiểm tra hook với `claude --debug`

### Xác thực Hook Khi Khởi động

Hook được xác thực khi Claude Code khởi động:
- JSON không hợp lệ trong hooks.json gây lỗi tải
- Script thiếu gây ra cảnh báo
- Lỗi cú pháp được báo cáo trong chế độ debug

Dùng lệnh `/hooks` để xem các hook đã tải trong phiên hiện tại.

## Debug Hook

### Bật Chế độ Debug

```bash
claude --debug
```

Tìm kiếm đăng ký hook, log thực thi, JSON input/output, và thông tin thời gian.

### Kiểm tra Script Hook

Kiểm tra hook lệnh trực tiếp:

```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "/test"}}' | \
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh

echo "Exit code: $?"
```

### Xác thực JSON Output

Đảm bảo hook xuất ra JSON hợp lệ:

```bash
output=$(./your-hook.sh < test-input.json)
echo "$output" | jq .
```

## Tham chiếu Nhanh

### Tóm tắt Sự kiện Hook

| Sự kiện | Khi nào | Dùng cho |
|---------|---------|----------|
| PreToolUse | Trước tool | Xác thực, chỉnh sửa |
| PostToolUse | Sau tool | Phản hồi, ghi log |
| UserPromptSubmit | Input người dùng | Ngữ cảnh, xác thực |
| Stop | Agent dừng | Kiểm tra tính hoàn chỉnh |
| SubagentStop | Subagent xong | Xác thực nhiệm vụ |
| SessionStart | Phiên bắt đầu | Tải ngữ cảnh |
| SessionEnd | Phiên kết thúc | Dọn dẹp, ghi log |
| PreCompact | Trước compact | Giữ lại ngữ cảnh |
| Notification | Người dùng được thông báo | Ghi log, phản ứng |

### Thực hành Tốt nhất

**NÊN:**
- ✅ Dùng hook dựa trên prompt cho logic phức tạp
- ✅ Dùng ${CLAUDE_PLUGIN_ROOT} để đảm bảo tính di động
- ✅ Xác thực tất cả input trong hook lệnh
- ✅ Đặt nháy tất cả biến bash
- ✅ Đặt timeout phù hợp
- ✅ Trả về JSON output có cấu trúc
- ✅ Kiểm tra hook kỹ lưỡng

**KHÔNG NÊN:**
- ❌ Dùng đường dẫn hardcoded
- ❌ Tin tưởng input người dùng mà không xác thực
- ❌ Tạo hook chạy lâu
- ❌ Dựa vào thứ tự thực thi hook
- ❌ Chỉnh sửa trạng thái toàn cục một cách không thể đoán trước
- ❌ Ghi log thông tin nhạy cảm

## Tài nguyên Bổ sung

### File Tham chiếu

Để biết pattern chi tiết và kỹ thuật nâng cao, tham khảo:

- **`references/patterns.md`** - Các pattern hook phổ biến (8+ pattern đã được chứng minh)
- **`references/migration.md`** - Chuyển từ hook cơ bản sang nâng cao
- **`references/advanced.md`** - Trường hợp dùng nâng cao và kỹ thuật

### Script Hook Ví dụ

Ví dụ hoạt động trong `examples/`:

- **`validate-write.sh`** - Ví dụ xác thực ghi file
- **`validate-bash.sh`** - Ví dụ xác thực lệnh Bash
- **`load-context.sh`** - Ví dụ tải ngữ cảnh SessionStart

### Script Tiện ích

Công cụ phát triển trong `scripts/`:

- **`validate-hook-schema.sh`** - Xác thực cấu trúc và cú pháp hooks.json
- **`test-hook.sh`** - Kiểm tra hook với input mẫu trước khi triển khai
- **`hook-linter.sh`** - Kiểm tra script hook về vấn đề phổ biến và thực hành tốt nhất

### Tài nguyên Bên ngoài

- **Tài liệu chính thức**: <https://docs.claude.com/en/docs/claude-code/hooks>
- **Ví dụ**: Xem plugin security-guidance trong marketplace
- **Kiểm tra**: Dùng `claude --debug` để xem log chi tiết
- **Xác thực**: Dùng `jq` để xác thực JSON output của hook

## Quy trình Triển khai

Để triển khai hook trong một plugin:

1. Xác định các sự kiện cần hook vào (PreToolUse, Stop, SessionStart, v.v.)
2. Quyết định giữa hook dựa trên prompt (linh hoạt) hay hook lệnh (xác định)
3. Viết cấu hình hook trong `hooks/hooks.json`
4. Với hook lệnh, tạo script hook
5. Dùng ${CLAUDE_PLUGIN_ROOT} cho tất cả tham chiếu file
6. Xác thực cấu hình với `scripts/validate-hook-schema.sh hooks/hooks.json`
7. Kiểm tra hook với `scripts/test-hook.sh` trước khi triển khai
8. Kiểm tra trong Claude Code với `claude --debug`
9. Ghi lại hook trong README của plugin

Ưu tiên hook dựa trên prompt cho hầu hết trường hợp. Dành hook lệnh cho kiểm tra quan trọng về hiệu năng hoặc xác định.
