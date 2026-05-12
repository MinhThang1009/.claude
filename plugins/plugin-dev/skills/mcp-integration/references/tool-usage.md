# Sử Dụng MCP Tool trong Command và Agent

Hướng dẫn đầy đủ về cách sử dụng MCP tool hiệu quả trong command và agent của Claude Code plugin.

## Tổng Quan

Sau khi MCP server được cấu hình, các tool của nó trở nên khả dụng với tiền tố `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`. Dùng các tool này trong command và agent giống như Claude Code tool tích hợp sẵn.

## Quy Ước Đặt Tên Tool

### Format

```
mcp__plugin_<plugin-name>_<server-name>__<tool-name>
```

### Ví Dụ

**Plugin Asana với server asana:**
- `mcp__plugin_asana_asana__asana_create_task`
- `mcp__plugin_asana_asana__asana_search_tasks`
- `mcp__plugin_asana_asana__asana_get_project`

**Plugin tùy chỉnh với database server:**
- `mcp__plugin_myplug_database__query`
- `mcp__plugin_myplug_database__execute`
- `mcp__plugin_myplug_database__list_tables`

### Khám Phá Tên Tool

**Dùng lệnh `/mcp`:**
```bash
/mcp
```

Lệnh này hiển thị:
- Tất cả MCP server có sẵn
- Tool do mỗi server cung cấp
- Schema và mô tả tool
- Tên tool đầy đủ để dùng trong cấu hình

## Sử Dụng Tool trong Command

### Pre-Allow Tool

Khai báo MCP tool trong frontmatter của command:

```markdown
---
description: Create a new Asana task
allowed-tools: [
  "mcp__plugin_asana_asana__asana_create_task"
]
---

# Create Task Command

To create a task:
1. Gather task details from user
2. Use mcp__plugin_asana_asana__asana_create_task with the details
3. Confirm creation to user
```

### Nhiều Tool

```markdown
---
allowed-tools: [
  "mcp__plugin_asana_asana__asana_create_task",
  "mcp__plugin_asana_asana__asana_search_tasks",
  "mcp__plugin_asana_asana__asana_get_project"
]
---
```

### Wildcard (Dùng Tiết Kiệm)

```markdown
---
allowed-tools: ["mcp__plugin_asana_asana__*"]
---
```

**Lưu ý:** Chỉ dùng wildcard nếu command thực sự cần truy cập tất cả tool từ một server.

### Hướng Dẫn Dùng Tool trong Command

**Ví dụ command:**
```markdown
---
description: Search and create Asana tasks
allowed-tools: [
  "mcp__plugin_asana_asana__asana_search_tasks",
  "mcp__plugin_asana_asana__asana_create_task"
]
---

# Asana Task Management

## Searching Tasks

To search for tasks:
1. Use mcp__plugin_asana_asana__asana_search_tasks
2. Provide search filters (assignee, project, etc.)
3. Display results to user

## Creating Tasks

To create a task:
1. Gather task details:
   - Title (required)
   - Description
   - Project
   - Assignee
   - Due date
2. Use mcp__plugin_asana_asana__asana_create_task
3. Show confirmation with task link
```

## Sử Dụng Tool trong Agent

### Cấu Hình Agent

Agent có thể dùng MCP tool tự chủ mà không cần pre-allow:

```markdown
---
name: asana-status-updater
description: This agent should be used when the user asks to "update Asana status", "generate project report", or "sync Asana tasks"
model: inherit
color: blue
---

## Role

Autonomous agent for generating Asana project status reports.

## Process

1. **Query tasks**: Use mcp__plugin_asana_asana__asana_search_tasks to get all tasks
2. **Analyze progress**: Calculate completion rates and identify blockers
3. **Generate report**: Create formatted status update
4. **Update Asana**: Use mcp__plugin_asana_asana__asana_create_comment to post report

## Available Tools

The agent has access to all Asana MCP tools without pre-approval.
```

### Quyền Truy Cập Tool của Agent

Agent có quyền truy cập tool rộng hơn command:
- Có thể dùng bất kỳ tool nào Claude xác định là cần thiết
- Không cần danh sách pre-allow
- Nên ghi lại các tool thường dùng

## Các Pattern Gọi Tool

### Pattern 1: Gọi Tool Đơn Giản

Gọi một tool kèm validation:

```markdown
Các bước:
1. Validate người dùng đã cung cấp trường bắt buộc
2. Gọi mcp__plugin_api_server__create_item với dữ liệu đã validate
3. Kiểm tra lỗi
4. Hiển thị xác nhận
```

### Pattern 2: Tool Tuần Tự

Chuỗi nhiều lần gọi tool:

```markdown
Các bước:
1. Tìm kiếm item hiện có: mcp__plugin_api_server__search
2. Nếu không tìm thấy, tạo mới: mcp__plugin_api_server__create
3. Thêm metadata: mcp__plugin_api_server__update_metadata
4. Trả về ID item cuối cùng
```

### Pattern 3: Batch Operation

Nhiều lần gọi với cùng tool:

```markdown
Các bước:
1. Lấy danh sách item cần xử lý
2. Với mỗi item:
   - Gọi mcp__plugin_api_server__update_item
   - Theo dõi thành công/thất bại
3. Báo cáo tóm tắt kết quả
```

### Pattern 4: Xử Lý Lỗi

Xử lý lỗi graceful:

```markdown
Các bước:
1. Thử gọi mcp__plugin_api_server__get_data
2. Nếu lỗi (rate limit, network, v.v.):
   - Chờ và thử lại (tối đa 3 lần)
   - Nếu vẫn thất bại, thông báo người dùng
   - Gợi ý kiểm tra cấu hình
3. Khi thành công, xử lý dữ liệu
```

## Tham Số Tool

### Hiểu Tool Schema

Mỗi MCP tool có schema định nghĩa tham số. Xem bằng `/mcp`.

**Ví dụ schema:**
```json
{
  "name": "asana_create_task",
  "description": "Create a new Asana task",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Task title"
      },
      "notes": {
        "type": "string",
        "description": "Task description"
      },
      "workspace": {
        "type": "string",
        "description": "Workspace GID"
      }
    },
    "required": ["name", "workspace"]
  }
}
```

### Gọi Tool với Tham Số

Claude tự động cấu trúc tool call dựa trên schema:

```typescript
// Claude generates this internally
{
  toolName: "mcp__plugin_asana_asana__asana_create_task",
  input: {
    name: "Review PR #123",
    notes: "Code review for new feature",
    workspace: "12345",
    assignee: "67890",
    due_on: "2025-01-15"
  }
}
```

### Validate Tham Số

**Trong command, validate trước khi gọi:**

```markdown
Các bước:
1. Kiểm tra tham số bắt buộc:
   - Tiêu đề không rỗng
   - Workspace ID được cung cấp
   - Ngày hết hạn đúng format (YYYY-MM-DD)
2. Nếu validation thất bại, yêu cầu người dùng cung cấp dữ liệu thiếu
3. Nếu validation pass, gọi MCP tool
4. Xử lý lỗi tool gracefully
```

## Xử Lý Response

### Response Thành Công

```markdown
Các bước:
1. Gọi MCP tool
2. Khi thành công:
   - Trích xuất dữ liệu liên quan từ response
   - Format để hiển thị cho người dùng
   - Cung cấp thông báo xác nhận
   - Bao gồm link hoặc ID liên quan
```

### Response Lỗi

```markdown
Các bước:
1. Gọi MCP tool
2. Khi lỗi:
   - Kiểm tra loại lỗi (auth, rate limit, validation, v.v.)
   - Cung cấp thông báo lỗi hữu ích
   - Gợi ý các bước khắc phục
   - Không để lộ chi tiết lỗi nội bộ cho người dùng
```

### Thành Công Một Phần

```markdown
Các bước:
1. Batch operation với nhiều lần gọi MCP
2. Theo dõi thành công và thất bại riêng biệt
3. Báo cáo tóm tắt:
   - "Đã xử lý thành công 8 trong 10 item"
   - "Item thất bại: [item1, item2] do [lý do]"
   - Gợi ý thử lại hoặc can thiệp thủ công
```

## Tối Ưu Hiệu Suất

### Batch Request

**Tốt: Query đơn với filter**
```markdown
Các bước:
1. Gọi mcp__plugin_api_server__search với filter:
   - project_id: "123"
   - status: "active"
   - limit: 100
2. Xử lý tất cả kết quả
```

**Tránh: Nhiều query riêng lẻ**
```markdown
Các bước:
1. Với mỗi item ID:
   - Gọi mcp__plugin_api_server__get_item
   - Xử lý item
```

### Cache Kết Quả

```markdown
Các bước:
1. Gọi thao tác MCP tốn kém: mcp__plugin_api_server__analyze
2. Lưu kết quả trong biến để tái sử dụng
3. Dùng kết quả đã cache cho các thao tác tiếp theo
4. Chỉ fetch lại khi dữ liệu thay đổi
```

### Gọi Tool Song Song

Khi các tool không phụ thuộc vào nhau, gọi song song:

```markdown
Các bước:
1. Thực hiện gọi song song (Claude xử lý tự động):
   - mcp__plugin_api_server__get_project
   - mcp__plugin_api_server__get_users
   - mcp__plugin_api_server__get_tags
2. Chờ tất cả hoàn thành
3. Kết hợp kết quả
```

## Best Practices Tích Hợp

### Trải Nghiệm Người Dùng

**Cung cấp feedback:**
```markdown
Các bước:
1. Thông báo người dùng: "Đang tìm kiếm Asana task..."
2. Gọi mcp__plugin_asana_asana__asana_search_tasks
3. Hiển thị tiến độ: "Tìm thấy 15 task, đang phân tích..."
4. Trình bày kết quả
```

**Xử lý thao tác lâu:**
```markdown
Các bước:
1. Cảnh báo người dùng: "Thao tác này có thể mất một phút..."
2. Chia nhỏ thành các bước nhỏ hơn với cập nhật
3. Hiển thị tiến độ từng bước
4. Tóm tắt cuối khi hoàn thành
```

### Thông Báo Lỗi

**Good error messages:**
```
❌ "Could not create task. Please check:
   1. You're logged into Asana
   2. You have access to workspace 'Engineering'
   3. The project 'Q1 Goals' exists"
```

**Poor error messages:**
```
❌ "Error: MCP tool returned 403"
```

### Tài Liệu Hóa

**Document MCP tool usage in command:**
```markdown
## MCP Tools Used

This command uses the following Asana MCP tools:
- **asana_search_tasks**: Search for tasks matching criteria
- **asana_create_task**: Create new task with details
- **asana_update_task**: Update existing task properties

Ensure you're authenticated to Asana before running this command.
```

## Kiểm Thử Việc Dùng Tool

### Kiểm Thử Local

1. **Cấu hình MCP server** trong `.mcp.json`
2. **Cài plugin local** trong `.claude-plugin/`
3. **Xác minh tool có sẵn** với `/mcp`
4. **Kiểm thử command** dùng tool
5. **Kiểm tra debug output**: `claude --debug`

### Kịch Bản Kiểm Thử

**Kiểm thử gọi thành công:**
```markdown
Các bước:
1. Tạo dữ liệu test trong service bên ngoài
2. Chạy command query dữ liệu này
3. Xác minh kết quả trả về đúng
```

**Kiểm thử trường hợp lỗi:**
```markdown
Các bước:
1. Kiểm thử khi thiếu authentication
2. Kiểm thử với tham số không hợp lệ
3. Kiểm thử với resource không tồn tại
4. Xác minh xử lý lỗi graceful
```

**Kiểm thử edge case:**
```markdown
Các bước:
1. Kiểm thử với kết quả rỗng
2. Kiểm thử với kết quả tối đa
3. Kiểm thử với ký tự đặc biệt
4. Kiểm thử với truy cập đồng thời
```

## Các Pattern Phổ Biến

### Pattern: CRUD Operation

```markdown
---
allowed-tools: [
  "mcp__plugin_api_server__create_item",
  "mcp__plugin_api_server__read_item",
  "mcp__plugin_api_server__update_item",
  "mcp__plugin_api_server__delete_item"
]
---

# Item Management

## Create
Use create_item with required fields...

## Read
Use read_item with item ID...

## Update
Use update_item with item ID and changes...

## Delete
Use delete_item with item ID (ask for confirmation first)...
```

### Pattern: Tìm Kiếm và Xử Lý

```markdown
Các bước:
1. **Tìm kiếm**: mcp__plugin_api_server__search với filter
2. **Lọc**: Áp dụng filter local bổ sung nếu cần
3. **Biến đổi**: Xử lý từng kết quả
4. **Trình bày**: Format và hiển thị cho người dùng
```

### Pattern: Workflow Nhiều Bước

```markdown
Các bước:
1. **Chuẩn bị**: Thu thập tất cả thông tin cần thiết
2. **Validate**: Kiểm tra tính đầy đủ của dữ liệu
3. **Thực thi**: Chuỗi MCP tool call:
   - Tạo resource cha
   - Tạo resource con
   - Liên kết các resource
   - Thêm metadata
4. **Xác minh**: Xác nhận tất cả bước thành công
5. **Báo cáo**: Cung cấp tóm tắt cho người dùng
```

## Xử Lý Sự Cố

### Tool Không Khả Dụng

**Kiểm tra:**
- MCP server được cấu hình đúng
- Server đã kết nối (kiểm tra `/mcp`)
- Tên tool khớp chính xác (phân biệt chữ hoa/thường)
- Restart Claude Code sau khi thay đổi config

### Gọi Tool Thất Bại

**Kiểm tra:**
- Authentication hợp lệ
- Tham số khớp tool schema
- Tham số bắt buộc được cung cấp
- Kiểm tra log `claude --debug`

### Vấn Đề Hiệu Suất

**Kiểm tra:**
- Batch query thay vì gọi riêng lẻ
- Cache kết quả khi phù hợp
- Không thực hiện tool call không cần thiết
- Gọi song song khi có thể

## Kết Luận

Sử dụng MCP tool hiệu quả đòi hỏi:
1. **Hiểu tool schema** qua `/mcp`
2. **Pre-allow tool** trong command phù hợp
3. **Xử lý lỗi gracefully**
4. **Tối ưu hiệu suất** với batch và cache
5. **Cung cấp UX tốt** với feedback và thông báo lỗi rõ ràng
6. **Kiểm thử kỹ lưỡng** trước khi deploy

Tuân theo các pattern này để tích hợp MCP tool bền vững trong command và agent của plugin.
