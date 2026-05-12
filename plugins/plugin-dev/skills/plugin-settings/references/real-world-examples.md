# Ví Dụ Thực Tế về Plugin Settings

Phân tích chi tiết cách các plugin production sử dụng pattern `.claude/plugin-name.local.md`.

## Plugin multi-agent-swarm

### Cấu Trúc File Settings

**.claude/multi-agent-swarm.local.md:**

```markdown
---
agent_name: auth-implementation
task_number: 3.5
pr_number: 1234
coordinator_session: team-leader
enabled: true
dependencies: ["Task 3.4"]
additional_instructions: "Use JWT tokens, not sessions"
---

# Task: Implement Authentication

Build JWT-based authentication for the REST API.

## Requirements
- JWT token generation and validation
- Refresh token flow
- Secure password hashing

## Success Criteria
- Auth endpoints implemented
- Tests passing (100% coverage)
- PR created and CI green
- Documentation updated

## Coordination
Depends on Task 3.4 (user model).
Report status to 'team-leader' session.
```

### Cách Sử Dụng

**File:** `hooks/agent-stop-notification.sh`

**Mục đích:** Gửi thông báo cho coordinator khi agent trở thành idle

**Triển khai:**

```bash
#!/bin/bash
set -euo pipefail

SWARM_STATE_FILE=".claude/multi-agent-swarm.local.md"

# Thoát nhanh nếu không có swarm đang hoạt động
if [[ ! -f "$SWARM_STATE_FILE" ]]; then
  exit 0
fi

# Phân tích frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SWARM_STATE_FILE")

# Trích xuất cấu hình
COORDINATOR_SESSION=$(echo "$FRONTMATTER" | grep '^coordinator_session:' | sed 's/coordinator_session: *//' | sed 's/^"\(.*\)"$/\1/')
AGENT_NAME=$(echo "$FRONTMATTER" | grep '^agent_name:' | sed 's/agent_name: *//' | sed 's/^"\(.*\)"$/\1/')
TASK_NUMBER=$(echo "$FRONTMATTER" | grep '^task_number:' | sed 's/task_number: *//' | sed 's/^"\(.*\)"$/\1/')
PR_NUMBER=$(echo "$FRONTMATTER" | grep '^pr_number:' | sed 's/pr_number: *//' | sed 's/^"\(.*\)"$/\1/')
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')

# Kiểm tra có bật không
if [[ "$ENABLED" != "true" ]]; then
  exit 0
fi

# Gửi thông báo cho coordinator
NOTIFICATION="🤖 Agent ${AGENT_NAME} (Task ${TASK_NUMBER}, PR #${PR_NUMBER}) is idle."

if tmux has-session -t "$COORDINATOR_SESSION" 2>/dev/null; then
  tmux send-keys -t "$COORDINATOR_SESSION" "$NOTIFICATION" Enter
  sleep 0.5
  tmux send-keys -t "$COORDINATOR_SESSION" Enter
fi

exit 0
```

**Các pattern chính:**
1. **Thoát nhanh** (dòng 7–9): Trả về ngay nếu file không tồn tại
2. **Trích xuất trường** (dòng 11–17): Phân tích từng trường frontmatter
3. **Kiểm tra enabled** (dòng 19–21): Tôn trọng flag enabled
4. **Hành động dựa trên settings** (dòng 23–29): Dùng coordinator_session để gửi thông báo

### Tạo File

**File:** `commands/launch-swarm.md`

File settings được tạo trong quá trình khởi chạy swarm với:

```bash
cat > "$WORKTREE_PATH/.claude/multi-agent-swarm.local.md" <<EOF
---
agent_name: $AGENT_NAME
task_number: $TASK_ID
pr_number: TBD
coordinator_session: $COORDINATOR_SESSION
enabled: true
dependencies: [$DEPENDENCIES]
additional_instructions: "$EXTRA_INSTRUCTIONS"
---

# Task: $TASK_DESCRIPTION

$TASK_DETAILS
EOF
```

### Cập Nhật

Số PR được cập nhật sau khi tạo PR:

```bash
# Cập nhật trường pr_number
sed "s/^pr_number: .*/pr_number: $PR_NUM/" \
  ".claude/multi-agent-swarm.local.md" > temp.md
mv temp.md ".claude/multi-agent-swarm.local.md"
```

## Plugin ralph-loop

### Cấu Trúc File Settings

**.claude/ralph-loop.local.md:**

```markdown
---
iteration: 1
max_iterations: 10
completion_promise: "All tests passing and build successful"
started_at: "2025-01-15T14:30:00Z"
---

Fix all the linting errors in the project.
Make sure tests pass after each fix.
Document any changes needed in CLAUDE.md.
```

### Cách Sử Dụng

**File:** `hooks/stop-hook.sh`

**Mục đích:** Ngăn session thoát và đưa output của Claude trở lại làm input

**Triển khai:**

```bash
#!/bin/bash
set -euo pipefail

RALPH_STATE_FILE=".claude/ralph-loop.local.md"

# Thoát nhanh nếu không có vòng lặp đang hoạt động
if [[ ! -f "$RALPH_STATE_FILE" ]]; then
  exit 0
fi

# Phân tích frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$RALPH_STATE_FILE")

# Trích xuất cấu hình
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
COMPLETION_PROMISE=$(echo "$FRONTMATTER" | grep '^completion_promise:' | sed 's/completion_promise: *//' | sed 's/^"\(.*\)"$/\1/')

# Kiểm tra số iteration tối đa
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "🛑 Ralph loop: Đạt số iteration tối đa ($MAX_ITERATIONS)."
  rm "$RALPH_STATE_FILE"
  exit 0
fi

# Lấy transcript và kiểm tra completion promise
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')
LAST_OUTPUT=$(grep '"role":"assistant"' "$TRANSCRIPT_PATH" | tail -1 | jq -r '.message.content | map(select(.type == "text")) | map(.text) | join("\n")')

# Kiểm tra completion
if [[ "$COMPLETION_PROMISE" != "null" ]] && [[ -n "$COMPLETION_PROMISE" ]]; then
  PROMISE_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe 's/.*?<promise>(.*?)<\/promise>.*/$1/s; s/^\s+|\s+$//g')

  if [[ "$PROMISE_TEXT" = "$COMPLETION_PROMISE" ]]; then
    echo "✅ Ralph loop: Phát hiện hoàn thành"
    rm "$RALPH_STATE_FILE"
    exit 0
  fi
fi

# Tiếp tục vòng lặp — tăng iteration
NEXT_ITERATION=$((ITERATION + 1))

# Trích xuất prompt từ body markdown
PROMPT_TEXT=$(awk '/^---$/{i++; next} i>=2' "$RALPH_STATE_FILE")

# Cập nhật iteration counter
TEMP_FILE="${RALPH_STATE_FILE}.tmp.$$"
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" "$RALPH_STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$RALPH_STATE_FILE"

# Chặn thoát và đưa prompt trở lại
jq -n \
  --arg prompt "$PROMPT_TEXT" \
  --arg msg "🔄 Ralph iteration $NEXT_ITERATION" \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'

exit 0
```

**Các pattern chính:**
1. **Thoát nhanh** (dòng 7–9): Bỏ qua nếu không hoạt động
2. **Theo dõi iteration** (dòng 11–20): Đếm và áp dụng giới hạn iteration tối đa
3. **Phát hiện promise** (dòng 25–33): Kiểm tra tín hiệu hoàn thành trong output
4. **Trích xuất prompt** (dòng 38): Đọc body markdown làm prompt tiếp theo
5. **Cập nhật trạng thái** (dòng 40–43): Tăng iteration theo kiểu atomic
6. **Tiếp tục vòng lặp** (dòng 45–53): Chặn thoát và đưa prompt trở lại

### Tạo File

**File:** `scripts/setup-ralph-loop.sh`

```bash
#!/bin/bash
PROMPT="$1"
MAX_ITERATIONS="${2:-0}"
COMPLETION_PROMISE="${3:-}"

# Tạo state file
cat > ".claude/ralph-loop.local.md" <<EOF
---
iteration: 1
max_iterations: $MAX_ITERATIONS
completion_promise: "$COMPLETION_PROMISE"
started_at: "$(date -Iseconds)"
---

$PROMPT
EOF

echo "Đã khởi tạo ralph loop: .claude/ralph-loop.local.md"
```

## So Sánh Các Pattern

| Tính năng | multi-agent-swarm | ralph-loop |
|-----------|-------------------|--------------|
| **File** | `.claude/multi-agent-swarm.local.md` | `.claude/ralph-loop.local.md` |
| **Mục đích** | Trạng thái điều phối agent | Trạng thái iteration vòng lặp |
| **Frontmatter** | Metadata agent | Cấu hình vòng lặp |
| **Body** | Phân công task | Prompt cần lặp |
| **Cập nhật** | Số PR, trạng thái | Iteration counter |
| **Xóa** | Thủ công hoặc khi hoàn thành | Khi thoát vòng lặp |
| **Hook** | Stop (thông báo) | Stop (kiểm soát vòng lặp) |

## Nguyên Tắc Tốt Nhất Từ Plugin Thực Tế

### 1. Pattern Thoát Nhanh

Cả hai plugin đều kiểm tra sự tồn tại của file trước:

```bash
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0  # Không hoạt động
fi
```

**Tại sao:** Tránh lỗi khi plugin chưa được cấu hình và thực thi nhanh hơn.

### 2. Flag Enabled

Cả hai dùng trường `enabled` để kiểm soát tường minh:

```yaml
enabled: true
```

**Tại sao:** Cho phép tắt tạm thời mà không cần xóa file.

### 3. Cập Nhật Atomic

Cả hai dùng temp file + atomic move:

```bash
TEMP_FILE="${FILE}.tmp.$$"
sed "s/^field: .*/field: $NEW_VALUE/" "$FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$FILE"
```

**Tại sao:** Ngăn file bị hỏng nếu process bị gián đoạn.

### 4. Xử Lý Dấu Nháy

Cả hai đều strip dấu nháy bao quanh từ giá trị YAML:

```bash
sed 's/^"\(.*\)"$/\1/'
```

**Tại sao:** YAML cho phép cả `field: value` và `field: "value"`.

### 5. Xử Lý Lỗi

Cả hai xử lý file thiếu/hỏng khéo léo:

```bash
if [[ ! -f "$FILE" ]]; then
  exit 0  # Không lỗi, chỉ là chưa cấu hình
fi

if [[ -z "$CRITICAL_FIELD" ]]; then
  echo "File settings bị hỏng" >&2
  rm "$FILE"  # Dọn dẹp
  exit 0
fi
```

**Tại sao:** Thất bại khéo léo thay vì crash.

## Anti-Pattern Cần Tránh

### ❌ Đường Dẫn Hardcoded

```bash
# XẤU
FILE="/Users/alice/.claude/my-plugin.local.md"

# TỐT
FILE=".claude/my-plugin.local.md"
```

### ❌ Biến Không Đặt Trong Dấu Nháy

```bash
# XẤU
echo $VALUE

# TỐT
echo "$VALUE"
```

### ❌ Cập Nhật Không Atomic

```bash
# XẤU: Có thể làm hỏng file nếu bị gián đoạn
sed -i "s/field: .*/field: $VALUE/" "$FILE"

# TỐT: Atomic
TEMP_FILE="${FILE}.tmp.$$"
sed "s/field: .*/field: $VALUE/" "$FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$FILE"
```

### ❌ Không Có Giá Trị Mặc Định

```bash
# XẤU: Thất bại nếu trường thiếu
if [[ $MAX -gt 100 ]]; then
  # MAX có thể trống!
fi

# TỐT: Cung cấp giá trị mặc định
MAX=${MAX:-10}
```

### ❌ Bỏ Qua Trường Hợp Biên

```bash
# XẤU: Giả sử đúng 2 marker ---
sed -n '/^---$/,/^---$/{ /^---$/d; p; }'

# TỐT: Xử lý --- trong body
awk '/^---$/{i++; next} i>=2'  # Cho body
```

## Kết Luận

Pattern `.claude/plugin-name.local.md` cung cấp:
- Cấu hình đơn giản, có thể đọc được bởi con người
- Thân thiện với version control (gitignored)
- Settings theo từng project
- Dễ phân tích bằng tool bash tiêu chuẩn
- Hỗ trợ cả cấu hình có cấu trúc (YAML) và nội dung tự do (markdown)

Dùng pattern này cho bất kỳ plugin nào cần hành vi có thể cấu hình bởi người dùng hoặc lưu trữ trạng thái bền vững.
