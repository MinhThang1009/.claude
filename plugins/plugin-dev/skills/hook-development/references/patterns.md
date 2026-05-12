# Các Pattern Hook Phổ Biến

Tài liệu tham khảo này cung cấp các pattern phổ biến, đã được kiểm chứng để triển khai Claude Code hook. Dùng các pattern này làm điểm bắt đầu cho các use case hook thông thường.

## Pattern 1: Security Validation

Chặn ghi file nguy hiểm bằng prompt hook:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "File path: $TOOL_INPUT.file_path. Verify: 1) Not in /etc or system directories 2) Not .env or credentials 3) Path doesn't contain '..' traversal. Return 'approve' or 'deny'."
        }
      ]
    }
  ]
}
```

**Dùng cho:** Ngăn ghi vào file nhạy cảm hoặc thư mục hệ thống.

## Pattern 2: Test Enforcement

Đảm bảo test được chạy trước khi dừng:

```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Review transcript. If code was modified (Write/Edit tools used), verify tests were executed. If no tests were run, block with reason 'Tests must be run after code changes'."
        }
      ]
    }
  ]
}
```

**Dùng cho:** Đảm bảo tiêu chuẩn chất lượng và ngăn công việc chưa hoàn chỉnh.

## Pattern 3: Context Loading

Load context đặc thù của project lúc bắt đầu session:

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

**Ví dụ script (load-context.sh):**
```bash
#!/bin/bash
cd "$CLAUDE_PROJECT_DIR" || exit 1

# Phát hiện loại project
if [ -f "package.json" ]; then
  echo "📦 Node.js project detected"
  echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
elif [ -f "Cargo.toml" ]; then
  echo "🦀 Rust project detected"
  echo "export PROJECT_TYPE=rust" >> "$CLAUDE_ENV_FILE"
fi
```

**Dùng cho:** Tự động phát hiện và cấu hình thiết lập đặc thù của project.

## Pattern 4: Notification Logging

Ghi log tất cả notification để kiểm tra hoặc phân tích:

```json
{
  "Notification": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/log-notification.sh"
        }
      ]
    }
  ]
}
```

**Dùng cho:** Theo dõi notification của người dùng hoặc tích hợp với hệ thống logging bên ngoài.

## Pattern 5: MCP Tool Monitoring

Giám sát và validate việc sử dụng MCP tool:

```json
{
  "PreToolUse": [
    {
      "matcher": "mcp__.*__delete.*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Deletion operation detected. Verify: Is this deletion intentional? Can it be undone? Are there backups? Return 'approve' only if safe."
        }
      ]
    }
  ]
}
```

**Dùng cho:** Bảo vệ khỏi các thao tác MCP destructive.

## Pattern 6: Build Verification

Đảm bảo project được build sau khi thay đổi code:

```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Check if code was modified. If Write/Edit tools were used, verify the project was built (npm run build, cargo build, etc). If not built, block and request build."
        }
      ]
    }
  ]
}
```

**Dùng cho:** Bắt lỗi build trước khi commit hoặc kết thúc công việc.

## Pattern 7: Permission Confirmation

Hỏi người dùng trước các thao tác nguy hiểm:

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Command: $TOOL_INPUT.command. If command contains 'rm', 'delete', 'drop', or other destructive operations, return 'ask' to confirm with user. Otherwise 'approve'."
        }
      ]
    }
  ]
}
```

**Dùng cho:** Xác nhận từ người dùng trước các lệnh có thể destructive.

## Pattern 8: Code Quality Checks

Chạy linter hoặc formatter khi edit file:

```json
{
  "PostToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/check-quality.sh"
        }
      ]
    }
  ]
}
```

**Ví dụ script (check-quality.sh):**
```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Chạy linter nếu áp dụng được
if [[ "$file_path" == *.js ]] || [[ "$file_path" == *.ts ]]; then
  npx eslint "$file_path" 2>&1 || true
fi
```

**Dùng cho:** Tự động đảm bảo chất lượng code.

## Kết Hợp Pattern

Kết hợp nhiều pattern để bảo vệ toàn diện:

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
    },
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate bash command safety"
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
          "prompt": "Verify tests run and build succeeded"
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
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh"
        }
      ]
    }
  ]
}
```

Cách này cung cấp bảo vệ và tự động hóa nhiều lớp.

## Pattern 9: Hook Kích Hoạt Tạm Thời

Tạo hook chỉ chạy khi được bật rõ ràng qua flag file:

```bash
#!/bin/bash
# Hook chỉ hoạt động khi flag file tồn tại
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-security-scan"

if [ ! -f "$FLAG_FILE" ]; then
  # Thoát nhanh khi bị vô hiệu hóa
  exit 0
fi

# Flag hiện diện, chạy validation
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Chạy security scan
security-scanner "$file_path"
```

**Kích hoạt:**
```bash
# Bật hook
touch .enable-security-scan

# Tắt hook
rm .enable-security-scan
```

**Dùng cho:**
- Hook debug tạm thời
- Feature flag cho development
- Validation đặc thù project theo opt-in
- Kiểm tra tốn hiệu năng chỉ khi cần

**Lưu ý:** Phải restart Claude Code sau khi tạo/xóa flag file để hook nhận thấy thay đổi.

## Pattern 10: Hook Điều Khiển Bởi Cấu Hình

Dùng JSON config để điều khiển hành vi hook:

```bash
#!/bin/bash
CONFIG_FILE="$CLAUDE_PROJECT_DIR/.claude/my-plugin.local.json"

# Đọc cấu hình
if [ -f "$CONFIG_FILE" ]; then
  strict_mode=$(jq -r '.strictMode // false' "$CONFIG_FILE")
  max_file_size=$(jq -r '.maxFileSize // 1000000' "$CONFIG_FILE")
else
  # Giá trị mặc định
  strict_mode=false
  max_file_size=1000000
fi

# Bỏ qua nếu không ở strict mode
if [ "$strict_mode" != "true" ]; then
  exit 0
fi

# Áp dụng giới hạn đã cấu hình
input=$(cat)
file_size=$(echo "$input" | jq -r '.tool_input.content | length')

if [ "$file_size" -gt "$max_file_size" ]; then
  echo '{"decision": "deny", "reason": "File exceeds configured size limit"}' >&2
  exit 2
fi
```

**File cấu hình (.claude/my-plugin.local.json):**
```json
{
  "strictMode": true,
  "maxFileSize": 500000,
  "allowedPaths": ["/tmp", "/home/user/projects"]
}
```

**Dùng cho:**
- Hành vi hook có thể cấu hình bởi người dùng
- Thiết lập per-project
- Quy tắc đặc thù của team
- Tiêu chí validation động
