# Các Use Case Hook Nâng Cao

Tài liệu tham khảo này bao gồm các pattern hook nâng cao và kỹ thuật cho workflow tự động hóa phức tạp.

## Validation Đa Giai Đoạn

Kết hợp command hook và prompt hook để validation theo lớp:

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

**Use case:** Kiểm tra deterministic nhanh, theo sau là phân tích thông minh

**Ví dụ quick-check.sh:**
```bash
#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command')

# Chấp thuận ngay các lệnh an toàn
if [[ "$command" =~ ^(ls|pwd|echo|date|whoami)$ ]]; then
  exit 0
fi

# Để prompt hook xử lý các trường hợp phức tạp
exit 0
```

Command hook phê duyệt nhanh các lệnh rõ ràng là an toàn, trong khi prompt hook phân tích mọi thứ còn lại.

## Thực Thi Hook Có Điều Kiện

Thực thi hook dựa trên môi trường hoặc context:

```bash
#!/bin/bash
# Chỉ chạy trong môi trường CI
if [ -z "$CI" ]; then
  echo '{"continue": true}' # Bỏ qua khi không phải CI
  exit 0
fi

# Chạy logic validation trong CI
input=$(cat)
# ... validation code ...
```

**Use case:**
- Hành vi khác nhau trong CI so với local development
- Validation đặc thù của project
- Quy tắc đặc thù của người dùng

**Ví dụ: Bỏ qua một số kiểm tra cho trusted user:**
```bash
#!/bin/bash
# Bỏ qua kiểm tra chi tiết cho admin user
if [ "$USER" = "admin" ]; then
  exit 0
fi

# Validation đầy đủ cho người dùng khác
input=$(cat)
# ... validation code ...
```

## Hook Chaining qua State

Chia sẻ state giữa các hook bằng file tạm:

```bash
# Hook 1: Phân tích và lưu state
#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command')

# Phân tích lệnh
risk_level=$(calculate_risk "$command")
echo "$risk_level" > /tmp/hook-state-$$

exit 0
```

```bash
# Hook 2: Dùng state đã lưu
#!/bin/bash
risk_level=$(cat /tmp/hook-state-$$ 2>/dev/null || echo "unknown")

if [ "$risk_level" = "high" ]; then
  echo "High risk operation detected" >&2
  exit 2
fi
```

**Quan trọng:** Cách này chỉ hoạt động với sequential hook event (ví dụ: PreToolUse rồi PostToolUse), không phải hook song song.

## Cấu Hình Hook Động

Thay đổi hành vi hook dựa trên cấu hình project:

```bash
#!/bin/bash
cd "$CLAUDE_PROJECT_DIR" || exit 1

# Đọc config đặc thù của project
if [ -f ".claude-hooks-config.json" ]; then
  strict_mode=$(jq -r '.strict_mode' .claude-hooks-config.json)

  if [ "$strict_mode" = "true" ]; then
    # Áp dụng validation nghiêm ngặt
    # ...
  else
    # Áp dụng validation nhẹ nhàng hơn
    # ...
  fi
fi
```

**Ví dụ .claude-hooks-config.json:**
```json
{
  "strict_mode": true,
  "allowed_commands": ["ls", "pwd", "grep"],
  "forbidden_paths": ["/etc", "/sys"]
}
```

## Prompt Hook Nhận Thức Context

Dùng transcript và context session để ra quyết định thông minh:

```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Review the full transcript at $TRANSCRIPT_PATH. Check: 1) Were tests run after code changes? 2) Did the build succeed? 3) Were all user questions answered? 4) Is there any unfinished work? Return 'approve' only if everything is complete."
        }
      ]
    }
  ]
}
```

LLM có thể đọc file transcript và đưa ra quyết định nhận thức context.

## Tối Ưu Hiệu Suất

### Cache Kết Quả Validation

```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
cache_key=$(echo -n "$file_path" | md5sum | cut -d' ' -f1)
cache_file="/tmp/hook-cache-$cache_key"

# Kiểm tra cache
if [ -f "$cache_file" ]; then
  cache_age=$(($(date +%s) - $(stat -f%m "$cache_file" 2>/dev/null || stat -c%Y "$cache_file")))
  if [ "$cache_age" -lt 300 ]; then  # Cache 5 phút
    cat "$cache_file"
    exit 0
  fi
fi

# Thực hiện validation
result='{"decision": "approve"}'

# Cache kết quả
echo "$result" > "$cache_file"
echo "$result"
```

### Tối Ưu Thực Thi Song Song

Vì hook chạy song song, thiết kế chúng độc lập với nhau:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "bash check-size.sh",      // Độc lập
          "timeout": 2
        },
        {
          "type": "command",
          "command": "bash check-path.sh",      // Độc lập
          "timeout": 2
        },
        {
          "type": "prompt",
          "prompt": "Check content safety",     // Độc lập
          "timeout": 10
        }
      ]
    }
  ]
}
```

Cả ba hook chạy đồng thời, giảm tổng latency.

## Workflow Xuyên Event

Phối hợp hook qua các event khác nhau:

**SessionStart - Thiết lập tracking:**
```bash
#!/bin/bash
# Khởi tạo session tracking
echo "0" > /tmp/test-count-$$
echo "0" > /tmp/build-count-$$
```

**PostToolUse - Track event:**
```bash
#!/bin/bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

if [ "$tool_name" = "Bash" ]; then
  command=$(echo "$input" | jq -r '.tool_result')
  if [[ "$command" == *"test"* ]]; then
    count=$(cat /tmp/test-count-$$ 2>/dev/null || echo "0")
    echo $((count + 1)) > /tmp/test-count-$$
  fi
fi
```

**Stop - Verify dựa trên tracking:**
```bash
#!/bin/bash
test_count=$(cat /tmp/test-count-$$ 2>/dev/null || echo "0")

if [ "$test_count" -eq 0 ]; then
  echo '{"decision": "block", "reason": "No tests were run"}' >&2
  exit 2
fi
```

## Tích Hợp Hệ Thống Bên Ngoài

### Thông báo Slack

```bash
#!/bin/bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
decision="blocked"

# Gửi thông báo lên Slack
curl -X POST "$SLACK_WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"Hook ${decision} ${tool_name} operation\"}" \
  2>/dev/null

echo '{"decision": "deny"}' >&2
exit 2
```

### Ghi log vào Database

```bash
#!/bin/bash
input=$(cat)

# Ghi log vào database
psql "$DATABASE_URL" -c "INSERT INTO hook_logs (event, data) VALUES ('PreToolUse', '$input')" \
  2>/dev/null

exit 0
```

### Thu thập Metrics

```bash
#!/bin/bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

# Gửi metrics lên hệ thống monitoring
echo "hook.pretooluse.${tool_name}:1|c" | nc -u -w1 statsd.local 8125

exit 0
```

## Các Pattern Bảo Mật

### Rate Limiting

```bash
#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command')

# Theo dõi tần suất lệnh
rate_file="/tmp/hook-rate-$$"
current_minute=$(date +%Y%m%d%H%M)

if [ -f "$rate_file" ]; then
  last_minute=$(head -1 "$rate_file")
  count=$(tail -1 "$rate_file")

  if [ "$current_minute" = "$last_minute" ]; then
    if [ "$count" -gt 10 ]; then
      echo '{"decision": "deny", "reason": "Rate limit exceeded"}' >&2
      exit 2
    fi
    count=$((count + 1))
  else
    count=1
  fi
else
  count=1
fi

echo "$current_minute" > "$rate_file"
echo "$count" >> "$rate_file"

exit 0
```

### Audit Logging

```bash
#!/bin/bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
timestamp=$(date -Iseconds)

# Append vào audit log
echo "$timestamp | $USER | $tool_name | $input" >> ~/.claude/audit.log

exit 0
```

### Phát Hiện Secret

```bash
#!/bin/bash
input=$(cat)
content=$(echo "$input" | jq -r '.tool_input.content')

# Kiểm tra các pattern secret phổ biến
if echo "$content" | grep -qE "(api[_-]?key|password|secret|token).{0,20}['\"]?[A-Za-z0-9]{20,}"; then
  echo '{"decision": "deny", "reason": "Potential secret detected in content"}' >&2
  exit 2
fi

exit 0
```

## Kiểm Thử Hook Nâng Cao

### Unit Testing Script Hook

```bash
# test-hook.sh
#!/bin/bash

# Test 1: Phê duyệt lệnh an toàn
result=$(echo '{"tool_input": {"command": "ls"}}' | bash validate-bash.sh)
if [ $? -eq 0 ]; then
  echo "✓ Test 1 passed"
else
  echo "✗ Test 1 failed"
fi

# Test 2: Chặn lệnh nguy hiểm
result=$(echo '{"tool_input": {"command": "rm -rf /"}}' | bash validate-bash.sh)
if [ $? -eq 2 ]; then
  echo "✓ Test 2 passed"
else
  echo "✗ Test 2 failed"
fi
```

### Integration Testing

Tạo test scenario để kiểm thử toàn bộ hook workflow:

```bash
# integration-test.sh
#!/bin/bash

# Thiết lập môi trường test
export CLAUDE_PROJECT_DIR="/tmp/test-project"
export CLAUDE_PLUGIN_ROOT="$(pwd)"
mkdir -p "$CLAUDE_PROJECT_DIR"

# Test SessionStart hook
echo '{}' | bash hooks/session-start.sh
if [ -f "/tmp/session-initialized" ]; then
  echo "✓ SessionStart hook works"
else
  echo "✗ SessionStart hook failed"
fi

# Dọn dẹp
rm -rf "$CLAUDE_PROJECT_DIR"
```

## Best Practices cho Hook Nâng Cao

1. **Giữ hook độc lập**: Đừng dựa vào thứ tự thực thi
2. **Dùng timeout**: Đặt giới hạn phù hợp cho từng loại hook
3. **Xử lý lỗi gracefully**: Cung cấp thông báo lỗi rõ ràng
4. **Ghi lại độ phức tạp**: Giải thích các pattern nâng cao trong README
5. **Kiểm thử kỹ lưỡng**: Bao phủ edge case và failure mode
6. **Theo dõi hiệu suất**: Track thời gian thực thi hook
7. **Version control cấu hình**: Dùng version control cho hook config
8. **Cung cấp escape hatch**: Cho phép người dùng bypass hook khi cần

## Các Lỗi Thường Gặp

### Giả định thứ tự hook

```bash
# TỆ: Giả định hook chạy theo thứ tự cụ thể
# Hook 1 lưu state, Hook 2 đọc nó
# Có thể fail vì hook chạy song song!
```

### Hook chạy quá lâu

```bash
# TỆ: Hook mất 2 phút để chạy
sleep 120
# Sẽ timeout và chặn workflow
```

### Exception không được bắt

```bash
# TỆ: Script crash với input bất ngờ
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
cat "$file_path"  # Fail nếu file không tồn tại
```

### Xử lý lỗi đúng cách

```bash
# TỐT: Xử lý lỗi gracefully
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
if [ ! -f "$file_path" ]; then
  echo '{"continue": true, "systemMessage": "File not found, skipping check"}' >&2
  exit 0
fi
```

## Kết Luận

Các pattern hook nâng cao cho phép tự động hóa phức tạp trong khi duy trì độ tin cậy và hiệu suất. Dùng các kỹ thuật này khi hook cơ bản không đủ, nhưng luôn ưu tiên sự đơn giản và khả năng bảo trì.
