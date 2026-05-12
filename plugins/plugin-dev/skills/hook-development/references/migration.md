# Chuyển từ Hook Cơ Bản sang Hook Nâng Cao

Hướng dẫn này chỉ cách chuyển từ command hook cơ bản sang prompt hook nâng cao để dễ bảo trì và linh hoạt hơn.

## Tại Sao Cần Chuyển?

Prompt hook có một số ưu điểm:

- **Reasoning ngôn ngữ tự nhiên**: LLM hiểu context và intent
- **Xử lý edge case tốt hơn**: Thích ứng với tình huống bất ngờ
- **Không cần bash scripting**: Đơn giản hơn để viết và bảo trì
- **Validation linh hoạt hơn**: Xử lý được logic phức tạp mà không cần code

## Ví Dụ Chuyển Đổi: Bash Command Validation

### Trước (Command Hook Cơ Bản)

**Cấu hình:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "bash validate-bash.sh"
        }
      ]
    }
  ]
}
```

**Script (validate-bash.sh):**
```bash
#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command')

# Logic validation hard-coded
if [[ "$command" == *"rm -rf"* ]]; then
  echo "Dangerous command detected" >&2
  exit 2
fi
```

**Vấn đề:**
- Chỉ kiểm tra đúng pattern "rm -rf"
- Không bắt các biến thể như `rm -fr` hoặc `rm -r -f`
- Bỏ sót các lệnh nguy hiểm khác (`dd`, `mkfs`, v.v.)
- Không nhận thức được context
- Cần kiến thức bash scripting

### Sau (Prompt Hook Nâng Cao)

**Cấu hình:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Command: $TOOL_INPUT.command. Analyze for: 1) Destructive operations (rm -rf, dd, mkfs, etc) 2) Privilege escalation (sudo) 3) Network operations without user consent. Return 'approve' or 'deny' with explanation.",
          "timeout": 15
        }
      ]
    }
  ]
}
```

**Lợi ích:**
- Bắt được tất cả biến thể và pattern
- Hiểu intent, không chỉ chuỗi ký tự nguyên văn
- Không cần file script
- Dễ mở rộng với tiêu chí mới
- Quyết định nhận thức context
- Giải thích bằng ngôn ngữ tự nhiên khi từ chối

## Ví Dụ Chuyển Đổi: File Write Validation

### Trước (Command Hook Cơ Bản)

**Cấu hình:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "bash validate-write.sh"
        }
      ]
    }
  ]
}
```

**Script (validate-write.sh):**
```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Kiểm tra path traversal
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
  exit 2
fi

# Kiểm tra system path
if [[ "$file_path" == "/etc/"* ]] || [[ "$file_path" == "/sys/"* ]]; then
  echo '{"decision": "deny", "reason": "System file"}' >&2
  exit 2
fi
```

**Vấn đề:**
- Pattern path hard-coded
- Không hiểu symlink
- Bỏ sót edge case (ví dụ: `/etc` vs `/etc/`)
- Không xem xét nội dung file

### Sau (Prompt Hook Nâng Cao)

**Cấu hình:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "File path: $TOOL_INPUT.file_path. Content preview: $TOOL_INPUT.content (first 200 chars). Verify: 1) Not system directories (/etc, /sys, /usr) 2) Not credentials (.env, tokens, secrets) 3) No path traversal 4) Content doesn't expose secrets. Return 'approve' or 'deny'."
        }
      ]
    }
  ]
}
```

**Lợi ích:**
- Nhận thức context (xem xét cả nội dung)
- Xử lý symlink và edge case
- Hiểu tự nhiên về "system directory"
- Có thể phát hiện secret trong nội dung
- Dễ mở rộng tiêu chí

## Khi Nào Nên Giữ Command Hook

Command hook vẫn có chỗ đứng:

### 1. Kiểm Tra Hiệu Suất Deterministic

```bash
#!/bin/bash
# Kiểm tra kích thước file nhanh chóng
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null)

if [ "$size" -gt 10000000 ]; then
  echo '{"decision": "deny", "reason": "File too large"}' >&2
  exit 2
fi
```

**Dùng command hook khi:** Validation thuần toán học hoặc deterministic.

### 2. Tích Hợp Tool Bên Ngoài

```bash
#!/bin/bash
# Chạy security scanner
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
scan_result=$(security-scanner "$file_path")

if [ "$?" -ne 0 ]; then
  echo "Security scan failed: $scan_result" >&2
  exit 2
fi
```

**Dùng command hook khi:** Tích hợp với tool bên ngoài cung cấp câu trả lời có/không.

### 3. Kiểm Tra Rất Nhanh (< 50ms)

```bash
#!/bin/bash
# Kiểm tra regex nhanh
command=$(echo "$input" | jq -r '.tool_input.command')

if [[ "$command" =~ ^(ls|pwd|echo)$ ]]; then
  exit 0  # Lệnh an toàn
fi
```

**Dùng command hook khi:** Hiệu suất là ưu tiên và logic đơn giản.

## Cách Tiếp Cận Kết Hợp

Kết hợp cả hai cho validation đa giai đoạn:

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/quick-check.sh",
          "timeout": 5
        },
        {
          "type": "prompt",
          "prompt": "Deep analysis of bash command: $TOOL_INPUT",
          "timeout": 15
        }
      ]
    }
  ]
}
```

Command hook thực hiện kiểm tra deterministic nhanh, trong khi prompt hook xử lý reasoning phức tạp.

## Checklist Chuyển Đổi

Khi chuyển đổi hook:

- [ ] Xác định logic validation trong command hook
- [ ] Chuyển các pattern hard-coded sang tiêu chí ngôn ngữ tự nhiên
- [ ] Kiểm thử với các edge case mà hook cũ bỏ sót
- [ ] Xác minh LLM hiểu đúng intent
- [ ] Đặt timeout phù hợp (thường 15–30 giây cho prompt hook)
- [ ] Tài liệu hóa hook mới trong README
- [ ] Xóa hoặc archive các file script cũ

## Mẹo Chuyển Đổi

1. **Bắt đầu với một hook**: Đừng chuyển tất cả cùng lúc
2. **Kiểm thử kỹ lưỡng**: Xác minh prompt hook bắt được những gì command hook bắt được
3. **Tìm điểm cải tiến**: Dùng việc chuyển đổi như cơ hội để nâng cao validation
4. **Giữ script để tham khảo**: Archive script cũ phòng khi cần tham chiếu logic
5. **Ghi lại lý do**: Giải thích tại sao prompt hook tốt hơn trong README

## Ví Dụ Chuyển Đổi Đầy Đủ

### Cấu Trúc Plugin Gốc

```
my-plugin/
├── .claude-plugin/plugin.json
├── hooks/hooks.json
└── scripts/
    ├── validate-bash.sh
    ├── validate-write.sh
    └── check-tests.sh
```

### Sau Khi Chuyển Đổi

```
my-plugin/
├── .claude-plugin/plugin.json
├── hooks/hooks.json      # Bây giờ dùng prompt hook
└── scripts/              # Archive hoặc xóa
    └── archive/
        ├── validate-bash.sh
        ├── validate-write.sh
        └── check-tests.sh
```

### hooks.json Đã Cập Nhật

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate bash command safety: destructive ops, privilege escalation, network access"
        }
      ]
    },
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate file write safety: system paths, credentials, path traversal, content secrets"
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
          "prompt": "Verify tests were run if code was modified"
        }
      ]
    }
  ]
}
```

**Kết quả:** Đơn giản hơn, dễ bảo trì hơn, mạnh mẽ hơn.

## Các Pattern Chuyển Đổi Phổ Biến

### Pattern: String Contains → Ngôn Ngữ Tự Nhiên

**Trước:**
```bash
if [[ "$command" == *"sudo"* ]]; then
  echo "Privilege escalation" >&2
  exit 2
fi
```

**Sau:**
```
"Check for privilege escalation (sudo, su, etc)"
```

### Pattern: Regex → Intent

**Trước:**
```bash
if [[ "$file" =~ \.(env|secret|key|token)$ ]]; then
  echo "Credential file" >&2
  exit 2
fi
```

**Sau:**
```
"Verify not writing to credential files (.env, secrets, keys, tokens)"
```

### Pattern: Nhiều Điều Kiện → Danh Sách Tiêu Chí

**Trước:**
```bash
if [ condition1 ] || [ condition2 ] || [ condition3 ]; then
  echo "Invalid" >&2
  exit 2
fi
```

**Sau:**
```
"Check: 1) condition1 2) condition2 3) condition3. Deny if any fail."
```

## Kết Luận

Chuyển sang prompt hook giúp plugin dễ bảo trì, linh hoạt và mạnh mẽ hơn. Giữ lại command hook cho kiểm tra deterministic và tích hợp tool bên ngoài.
