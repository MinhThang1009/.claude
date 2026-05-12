---
name: plugin-settings
description: This skill should be used when the user asks about "plugin settings", "store plugin configuration", "user-configurable plugin", ".local.md files", "plugin state files", "read YAML frontmatter", "per-project plugin settings", or wants to make plugin behavior configurable. Documents the .claude/plugin-name.local.md pattern for storing plugin-specific configuration with YAML frontmatter and markdown content.
version: 0.1.0
---

# Pattern Plugin Settings cho Claude Code Plugins

## Tổng quan

Plugins có thể lưu cài đặt do user cấu hình và state trong files `.claude/plugin-name.local.md` trong project directory. Pattern này dùng YAML frontmatter cho structured configuration và markdown content cho prompts hoặc context bổ sung.

**Các đặc điểm chính:**
- Vị trí file: `.claude/plugin-name.local.md` trong project root
- Cấu trúc: YAML frontmatter + markdown body
- Mục đích: Per-project plugin configuration và state
- Cách dùng: Đọc từ hooks, commands, và agents
- Lifecycle: Do user quản lý (không trong git, nên có trong `.gitignore`)

## Cấu trúc File

### Template cơ bản

```markdown
---
enabled: true
setting1: value1
setting2: value2
numeric_setting: 42
list_setting: ["item1", "item2"]
---

# Additional Context

Markdown body này có thể chứa:
- Task descriptions
- Additional instructions
- Prompts để feed lại cho Claude
- Documentation hoặc notes
```

### Ví dụ: Plugin State File

**.claude/my-plugin.local.md:**
```markdown
---
enabled: true
strict_mode: false
max_retries: 3
notification_level: info
coordinator_session: team-leader
---

# Plugin Configuration

This plugin is configured for standard validation mode.
Contact @team-lead with questions.
```

## Đọc Settings Files

### Từ Hooks (Bash Scripts)

**Pattern: Kiểm tra tồn tại và parse frontmatter**

```bash
#!/bin/bash
set -euo pipefail

# Define state file path
STATE_FILE=".claude/my-plugin.local.md"

# Quick exit if file doesn't exist
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0  # Plugin not configured, skip
fi

# Parse YAML frontmatter (between --- markers)
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")

# Extract individual fields
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//' | sed 's/^"\(.*\)"$/\1/')
STRICT_MODE=$(echo "$FRONTMATTER" | grep '^strict_mode:' | sed 's/strict_mode: *//' | sed 's/^"\(.*\)"$/\1/')

# Check if enabled
if [[ "$ENABLED" != "true" ]]; then
  exit 0  # Disabled
fi

# Use configuration in hook logic
if [[ "$STRICT_MODE" == "true" ]]; then
  # Apply strict validation
  # ...
fi
```

Xem `examples/read-settings-hook.sh` để biết complete working example.

### Từ Commands

Commands có thể đọc settings files để customize behavior:

```markdown
---
description: Process data with plugin
allowed-tools: ["Read", "Bash"]
---

# Process Command

Steps:
1. Check if settings exist at `.claude/my-plugin.local.md`
2. Read configuration using Read tool
3. Parse YAML frontmatter to extract settings
4. Apply settings to processing logic
5. Execute with configured behavior
```

### Từ Agents

Agents có thể tham chiếu settings trong instructions của họ:

```markdown
---
name: configured-agent
description: Agent adapts theo project settings
---

Kiểm tra plugin settings tại `.claude/my-plugin.local.md`.
Nếu có, parse YAML frontmatter và điều chỉnh behavior theo:
- enabled: Plugin có active không
- mode: Processing mode (strict, standard, lenient)
- Các configuration fields bổ sung
```

## Kỹ thuật Parsing

### Extract Frontmatter

```bash
# Extract mọi thứ giữa các marker ---
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")
```

### Đọc từng Field

**String fields:**
```bash
VALUE=$(echo "$FRONTMATTER" | grep '^field_name:' | sed 's/field_name: *//' | sed 's/^"\(.*\)"$/\1/')
```

**Boolean fields:**
```bash
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')
# So sánh: if [[ "$ENABLED" == "true" ]]; then
```

**Numeric fields:**
```bash
MAX=$(echo "$FRONTMATTER" | grep '^max_value:' | sed 's/max_value: *//')
# Dùng: if [[ $MAX -gt 100 ]]; then
```

### Đọc Markdown Body

Extract nội dung sau `---` thứ hai:

```bash
# Lấy mọi thứ sau closing ---
BODY=$(awk '/^---$/{i++; next} i>=2' "$FILE")
```

## Các Pattern Phổ biến

### Pattern 1: Temporarily Active Hooks

Dùng settings file để kiểm soát kích hoạt hook:

```bash
#!/bin/bash
STATE_FILE=".claude/security-scan.local.md"

# Thoát nhanh nếu chưa cấu hình
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# Đọc enabled flag
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')

if [[ "$ENABLED" != "true" ]]; then
  exit 0  # Đã disabled
fi

# Chạy hook logic
# ...
```

**Use case:** Enable/disable hooks mà không cần edit hooks.json (yêu cầu restart).

### Pattern 2: Agent State Management

Lưu agent-specific state và configuration:

**.claude/multi-agent-swarm.local.md:**
```markdown
---
agent_name: auth-agent
task_number: 3.5
pr_number: 1234
coordinator_session: team-leader
enabled: true
dependencies: ["Task 3.4"]
---

# Task Assignment

Implement JWT authentication cho API.

**Success Criteria:**
- Authentication endpoints đã tạo
- Tests passing
- PR đã tạo và CI green
```

Đọc từ hooks để coordinate agents:

```bash
AGENT_NAME=$(echo "$FRONTMATTER" | grep '^agent_name:' | sed 's/agent_name: *//')
COORDINATOR=$(echo "$FRONTMATTER" | grep '^coordinator_session:' | sed 's/coordinator_session: *//')

# Gửi notification đến coordinator
tmux send-keys -t "$COORDINATOR" "Agent $AGENT_NAME completed task" Enter
```

### Pattern 3: Configuration-Driven Behavior

**.claude/my-plugin.local.md:**
```markdown
---
validation_level: strict
max_file_size: 1000000
allowed_extensions: [".js", ".ts", ".tsx"]
enable_logging: true
---

# Validation Configuration

Strict mode đã kích hoạt cho project này.
Tất cả writes được validate theo security policies.
```

Dùng trong hooks hoặc commands:

```bash
LEVEL=$(echo "$FRONTMATTER" | grep '^validation_level:' | sed 's/validation_level: *//')

case "$LEVEL" in
  strict)
    # Áp dụng strict validation
    ;;
  standard)
    # Áp dụng standard validation
    ;;
  lenient)
    # Áp dụng lenient validation
    ;;
esac
```

## Tạo Settings Files

### Từ Commands

Commands có thể tạo settings files:

```markdown
# Setup Command

Các bước:
1. Hỏi user về configuration preferences
2. Tạo `.claude/my-plugin.local.md` với YAML frontmatter
3. Set các giá trị phù hợp dựa trên user input
4. Thông báo user đã lưu settings
5. Nhắc user restart Claude Code để hooks nhận ra thay đổi
```

### Template Generation

Cung cấp template trong plugin README:

```markdown
## Configuration

Tạo `.claude/my-plugin.local.md` trong project của bạn:

\`\`\`markdown
---
enabled: true
mode: standard
max_retries: 3
---

# Plugin Configuration

Các settings của bạn đang active.
\`\`\`

Sau khi tạo hoặc chỉnh sửa, restart Claude Code để thay đổi có hiệu lực.
```

## Best Practices

### Đặt tên File

Nên làm:
- Dùng format `.claude/plugin-name.local.md`
- Khớp tên plugin chính xác
- Dùng suffix `.local.md` cho user-local files

Không nên làm:
- Dùng directory khác (không phải `.claude/`)
- Đặt tên không nhất quán
- Dùng `.md` không có `.local` (có thể bị commit)

### Gitignore

Luôn thêm vào `.gitignore`:

```gitignore
.claude/*.local.md
.claude/*.local.json
```

Document điều này trong plugin README.

### Defaults

Cung cấp sensible defaults khi settings file không tồn tại:

```bash
if [[ ! -f "$STATE_FILE" ]]; then
  # Dùng defaults
  ENABLED=true
  MODE=standard
else
  # Đọc từ file
  # ...
fi
```

### Validation

Validate settings values:

```bash
MAX=$(echo "$FRONTMATTER" | grep '^max_value:' | sed 's/max_value: *//')

# Validate numeric range
if ! [[ "$MAX" =~ ^[0-9]+$ ]] || [[ $MAX -lt 1 ]] || [[ $MAX -gt 100 ]]; then
  echo "⚠️  Invalid max_value in settings (must be 1-100)" >&2
  MAX=10  # Dùng default
fi
```

### Yêu cầu Restart

**Quan trọng:** Thay đổi settings yêu cầu Claude Code restart.

Document trong README của bạn:

```markdown
## Thay đổi Settings

Sau khi edit `.claude/my-plugin.local.md`:
1. Lưu file
2. Thoát Claude Code
3. Restart: `claude` hoặc `cc`
4. Settings mới sẽ được load
```

Hooks không thể hot-swap trong session.

## Security Considerations

### Sanitize User Input

Khi viết settings files từ user input:

```bash
# Escape quotes trong user input
SAFE_VALUE=$(echo "$USER_INPUT" | sed 's/"/\\"/g')

# Ghi vào file
cat > "$STATE_FILE" <<EOF
---
user_setting: "$SAFE_VALUE"
---
EOF
```

### Validate File Paths

Nếu settings chứa file paths:

```bash
FILE_PATH=$(echo "$FRONTMATTER" | grep '^data_file:' | sed 's/data_file: *//')

# Kiểm tra path traversal
if [[ "$FILE_PATH" == *".."* ]]; then
  echo "⚠️  Invalid path in settings (path traversal)" >&2
  exit 2
fi
```

### Permissions

Settings files nên:
- Chỉ readable bởi user (`chmod 600`)
- Không được commit vào git
- Không được chia sẻ giữa các users

## Ví dụ Thực tế

### Plugin multi-agent-swarm

**.claude/multi-agent-swarm.local.md:**
```markdown
---
agent_name: auth-implementation
task_number: 3.5
pr_number: 1234
coordinator_session: team-leader
enabled: true
dependencies: ["Task 3.4"]
additional_instructions: Use JWT tokens, not sessions
---

# Task: Implement Authentication

Build JWT-based authentication cho REST API.
Coordinate với auth-agent về shared types.
```

**Hook usage (agent-stop-notification.sh):**
- Kiểm tra file tồn tại (dòng 15-18: thoát nhanh nếu không có)
- Parse frontmatter để lấy coordinator_session, agent_name, enabled
- Gửi notifications đến coordinator nếu enabled
- Cho phép quick activation/deactivation qua `enabled: true/false`

### Plugin ralph-loop

**.claude/ralph-loop.local.md:**
```markdown
---
iteration: 1
max_iterations: 10
completion_promise: "All tests passing and build successful"
---

Fix all the linting errors in the project.
Make sure tests pass after each fix.
```

**Hook usage (stop-hook.sh):**
- Kiểm tra file tồn tại (dòng 15-18: thoát nhanh nếu không active)
- Đọc iteration count và max_iterations
- Extract completion_promise để xác định loop termination
- Đọc body như prompt để feed lại
- Cập nhật iteration count mỗi vòng lặp

## Quick Reference

### Vị trí File

```
project-root/
└── .claude/
    └── plugin-name.local.md
```

### Parsing Frontmatter

```bash
# Extract frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")

# Đọc field
VALUE=$(echo "$FRONTMATTER" | grep '^field:' | sed 's/field: *//' | sed 's/^"\(.*\)"$/\1/')
```

### Parsing Body

```bash
# Extract body (sau second ---)
BODY=$(awk '/^---$/{i++; next} i>=2' "$FILE")
```

### Pattern Thoát nhanh

```bash
if [[ ! -f ".claude/my-plugin.local.md" ]]; then
  exit 0  # Chưa cấu hình
fi
```

## Tài nguyên Bổ sung

### Reference Files

Để biết implementation patterns chi tiết:

- **`references/parsing-techniques.md`** - Hướng dẫn đầy đủ để parse YAML frontmatter và markdown bodies
- **`references/real-world-examples.md`** - Deep dive vào implementations của multi-agent-swarm và ralph-loop

### Example Files

Working examples trong `examples/`:

- **`read-settings-hook.sh`** - Hook đọc và dùng settings
- **`create-settings-command.md`** - Command tạo settings file
- **`example-settings.md`** - Template settings file

### Utility Scripts

Development tools trong `scripts/`:

- **`validate-settings.sh`** - Validate cấu trúc settings file
- **`parse-frontmatter.sh`** - Extract frontmatter fields

## Implementation Workflow

Để thêm settings vào plugin:

1. Thiết kế settings schema (field nào, types, defaults)
2. Tạo template file trong plugin documentation
3. Thêm gitignore entry cho `.claude/*.local.md`
4. Implement settings parsing trong hooks/commands
5. Dùng quick-exit pattern (kiểm tra file tồn tại, kiểm tra enabled field)
6. Document settings trong plugin README kèm template
7. Nhắc users rằng thay đổi yêu cầu Claude Code restart

Tập trung giữ settings đơn giản và cung cấp defaults tốt khi settings file không tồn tại.
