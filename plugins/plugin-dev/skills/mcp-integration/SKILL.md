---
name: MCP Integration
description: This skill should be used when the user asks to "add MCP server", "integrate MCP", "configure MCP in plugin", "use .mcp.json", "set up Model Context Protocol", "connect external service", mentions "${CLAUDE_PLUGIN_ROOT} with MCP", or discusses MCP server types (SSE, stdio, HTTP, WebSocket). Provides comprehensive guidance for integrating Model Context Protocol servers into Claude Code plugins for external tool and service integration.
---

# Tích hợp MCP cho Claude Code Plugins

## Tổng quan

Model Context Protocol (MCP) cho phép Claude Code plugins tích hợp với các dịch vụ và API bên ngoài bằng cách cung cấp quyền truy cập tool có cấu trúc. Dùng tích hợp MCP để expose các khả năng của dịch vụ bên ngoài thành tool trong Claude Code.

**Các khả năng chính:**
- Kết nối với dịch vụ bên ngoài (databases, APIs, file systems)
- Cung cấp hơn 10 tool liên quan từ một dịch vụ duy nhất
- Xử lý OAuth và các luồng xác thực phức tạp
- Bundle MCP servers với plugins để cài đặt tự động

## Các phương thức cấu hình MCP Server

Plugins có thể bundle MCP servers theo hai cách:

### Phương thức 1: .mcp.json riêng biệt (Khuyến nghị)

Tạo `.mcp.json` tại thư mục gốc của plugin:

```json
{
  "database-tools": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": {
      "DB_URL": "${DB_URL}"
    }
  }
}
```

**Ưu điểm:**
- Tách biệt rõ ràng các mối quan tâm
- Dễ bảo trì hơn
- Phù hợp hơn cho nhiều server

### Phương thức 2: Inline trong plugin.json

Thêm trường `mcpServers` vào plugin.json:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

**Ưu điểm:**
- File cấu hình duy nhất
- Phù hợp cho plugin đơn giản chỉ có một server

## Các loại MCP Server

### stdio (Tiến trình cục bộ)

Thực thi MCP server cục bộ dưới dạng tiến trình con. Phù hợp nhất cho tool cục bộ và server tùy chỉnh.

**Cấu hình:**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
    "env": {
      "LOG_LEVEL": "debug"
    }
  }
}
```

**Trường hợp sử dụng:**
- Truy cập file system
- Kết nối database cục bộ
- MCP server tùy chỉnh
- MCP server đóng gói dạng NPM

**Quản lý tiến trình:**
- Claude Code spawn và quản lý tiến trình
- Giao tiếp qua stdin/stdout
- Kết thúc khi Claude Code thoát

### SSE (Server-Sent Events)

Kết nối với MCP server được host sẵn có hỗ trợ OAuth. Phù hợp nhất cho cloud services.

**Cấu hình:**
```json
{
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  }
}
```

**Trường hợp sử dụng:**
- MCP server được host chính thức (Asana, GitHub, v.v.)
- Cloud services có MCP endpoint
- Xác thực dựa trên OAuth
- Không cần cài đặt cục bộ

**Xác thực:**
- Luồng OAuth được xử lý tự động
- Người dùng được nhắc xác thực lần đầu sử dụng
- Token được Claude Code quản lý

### HTTP (REST API)

Kết nối với MCP server dạng RESTful có xác thực bằng token.

**Cấu hình:**
```json
{
  "api-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "X-Custom-Header": "value"
    }
  }
}
```

**Trường hợp sử dụng:**
- MCP server dựa trên REST API
- Xác thực bằng token
- API backend tùy chỉnh
- Tương tác phi trạng thái

### WebSocket (Thời gian thực)

Kết nối với MCP server WebSocket cho giao tiếp hai chiều thời gian thực.

**Cấu hình:**
```json
{
  "realtime-service": {
    "type": "ws",
    "url": "wss://mcp.example.com/ws",
    "headers": {
      "Authorization": "Bearer ${TOKEN}"
    }
  }
}
```

**Trường hợp sử dụng:**
- Streaming dữ liệu thời gian thực
- Kết nối liên tục
- Push notification từ server
- Yêu cầu độ trễ thấp

## Mở rộng biến môi trường

Tất cả cấu hình MCP đều hỗ trợ thay thế biến môi trường:

**${CLAUDE_PLUGIN_ROOT}** - Thư mục plugin (luôn dùng để đảm bảo tính di động):
```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server"
}
```

**Biến môi trường người dùng** - Từ shell của người dùng:
```json
{
  "env": {
    "API_KEY": "${MY_API_KEY}",
    "DATABASE_URL": "${DB_URL}"
  }
}
```

**Best practice:** Ghi lại tất cả biến môi trường bắt buộc trong README của plugin.

## Đặt tên MCP Tool

Khi MCP server cung cấp tool, chúng được tự động thêm prefix:

**Format:** `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`

**Ví dụ:**
- Plugin: `asana`
- Server: `asana`
- Tool: `create_task`
- **Tên đầy đủ:** `mcp__plugin_asana_asana__asana_create_task`

### Dùng MCP Tool trong Commands

Pre-allow các MCP tool cụ thể trong frontmatter của command:

```markdown
---
allowed-tools: [
  "mcp__plugin_asana_asana__asana_create_task",
  "mcp__plugin_asana_asana__asana_search_tasks"
]
---
```

**Wildcard (dùng hạn chế):**
```markdown
---
allowed-tools: ["mcp__plugin_asana_asana__*"]
---
```

**Best practice:** Pre-allow tool cụ thể, không dùng wildcard, vì lý do bảo mật.

## Quản lý vòng đời

**Khởi động tự động:**
- MCP server khởi động khi plugin được bật
- Kết nối được thiết lập trước lần sử dụng tool đầu tiên
- Cần restart khi thay đổi cấu hình

**Vòng đời:**
1. Plugin tải
2. Cấu hình MCP được phân tích
3. Tiến trình server được khởi động (stdio) hoặc kết nối được thiết lập (SSE/HTTP/WS)
4. Tool được phát hiện và đăng ký
5. Tool có thể dùng dưới dạng `mcp__plugin_...__...`

**Xem các server:**
Dùng lệnh `/mcp` để xem tất cả server kể cả server do plugin cung cấp.

## Các pattern xác thực

### OAuth (SSE/HTTP)

OAuth được Claude Code xử lý tự động:

```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse"
}
```

Người dùng xác thực trên trình duyệt lần đầu sử dụng. Không cần cấu hình thêm.

### Dựa trên Token (Headers)

Token tĩnh hoặc từ biến môi trường:

```json
{
  "type": "http",
  "url": "https://api.example.com",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

Ghi lại các biến môi trường bắt buộc trong README.

### Biến môi trường (stdio)

Truyền cấu hình cho MCP server:

```json
{
  "command": "python",
  "args": ["-m", "my_mcp_server"],
  "env": {
    "DATABASE_URL": "${DB_URL}",
    "API_KEY": "${API_KEY}",
    "LOG_LEVEL": "info"
  }
}
```

## Các pattern tích hợp

### Pattern 1: Simple Tool Wrapper

Commands dùng MCP tool với tương tác người dùng:

```markdown
# Command: create-item.md
---
allowed-tools: ["mcp__plugin_name_server__create_item"]
---

Steps:
1. Gather item details from user
2. Use mcp__plugin_name_server__create_item
3. Confirm creation
```

**Dùng khi:** Cần thêm validation hoặc tiền xử lý trước khi gọi MCP.

### Pattern 2: Autonomous Agent

Agent dùng MCP tool một cách tự động:

```markdown
# Agent: data-analyzer.md

Analysis Process:
1. Query data via mcp__plugin_db_server__query
2. Process and analyze results
3. Generate insights report
```

**Dùng khi:** Workflow MCP nhiều bước không cần tương tác người dùng.

### Pattern 3: Multi-Server Plugin

Tích hợp nhiều MCP server:

```json
{
  "github": {
    "type": "sse",
    "url": "https://mcp.github.com/sse"
  },
  "jira": {
    "type": "sse",
    "url": "https://mcp.jira.com/sse"
  }
}
```

**Dùng khi:** Workflow trải dài trên nhiều dịch vụ.

## Best Practices bảo mật

### Dùng HTTPS/WSS

Luôn dùng kết nối bảo mật:

```json
✅ "url": "https://mcp.example.com/sse"
❌ "url": "http://mcp.example.com/sse"
```

### Quản lý Token

**NÊN:**
- ✅ Dùng biến môi trường cho token
- ✅ Ghi lại các env var bắt buộc trong README
- ✅ Để luồng OAuth xử lý xác thực

**KHÔNG NÊN:**
- ❌ Hardcode token trong cấu hình
- ❌ Commit token lên git
- ❌ Chia sẻ token trong tài liệu

### Phạm vi Permission

Pre-allow chỉ những MCP tool cần thiết:

```markdown
✅ allowed-tools: [
  "mcp__plugin_api_server__read_data",
  "mcp__plugin_api_server__create_item"
]

❌ allowed-tools: ["mcp__plugin_api_server__*"]
```

## Xử lý lỗi

### Lỗi kết nối

Xử lý khi MCP server không khả dụng:
- Cung cấp hành vi fallback trong commands
- Thông báo cho người dùng về vấn đề kết nối
- Kiểm tra URL server và cấu hình

### Lỗi gọi Tool

Xử lý khi thao tác MCP thất bại:
- Validate đầu vào trước khi gọi MCP tool
- Cung cấp thông báo lỗi rõ ràng
- Kiểm tra rate limiting và quota

### Lỗi cấu hình

Validate cấu hình MCP:
- Test kết nối server trong quá trình phát triển
- Validate cú pháp JSON
- Kiểm tra các biến môi trường bắt buộc

## Cân nhắc về hiệu năng

### Lazy Loading

MCP server kết nối theo yêu cầu:
- Không phải tất cả server kết nối khi khởi động
- Lần sử dụng tool đầu tiên kích hoạt kết nối
- Connection pooling được quản lý tự động

### Batching

Gộp các request tương tự khi có thể:

```
# Tốt: Một query với bộ lọc
tasks = search_tasks(project="X", assignee="me", limit=50)

# Tránh: Nhiều query riêng lẻ
for id in task_ids:
    task = get_task(id)
```

## Kiểm thử tích hợp MCP

### Kiểm thử cục bộ

1. Cấu hình MCP server trong `.mcp.json`
2. Cài đặt plugin cục bộ (`.claude-plugin/`)
3. Chạy `/mcp` để xác minh server xuất hiện
4. Kiểm thử các lời gọi tool trong commands
5. Kiểm tra log `claude --debug` để phát hiện lỗi kết nối

### Checklist xác thực

- [ ] Cấu hình MCP là JSON hợp lệ
- [ ] URL server đúng và có thể truy cập
- [ ] Các biến môi trường bắt buộc được ghi lại
- [ ] Tool xuất hiện trong output `/mcp`
- [ ] Xác thực hoạt động (OAuth hoặc token)
- [ ] Lời gọi tool thành công từ commands
- [ ] Các trường hợp lỗi được xử lý ổn thỏa

## Debug

### Bật Debug Logging

```bash
claude --debug
```

Chú ý tìm:
- Các lần thử kết nối MCP server
- Log phát hiện tool
- Luồng xác thực
- Lỗi gọi tool

### Các vấn đề thường gặp

**Server không kết nối được:**
- Kiểm tra URL có đúng không
- Xác minh server đang chạy (stdio)
- Kiểm tra kết nối mạng
- Xem lại cấu hình xác thực

**Tool không khả dụng:**
- Xác minh server đã kết nối thành công
- Kiểm tra tên tool khớp chính xác
- Chạy `/mcp` để xem các tool có sẵn
- Restart Claude Code sau khi thay đổi cấu hình

**Xác thực thất bại:**
- Xóa auth token đã cache
- Xác thực lại
- Kiểm tra phạm vi và quyền của token
- Xác minh các biến môi trường đã được đặt

## Tham chiếu nhanh

### Các loại MCP Server

| Loại | Transport | Phù hợp cho | Xác thực |
|------|-----------|-------------|----------|
| stdio | Process | Tool cục bộ, server tùy chỉnh | Env vars |
| SSE | HTTP | Dịch vụ được host, cloud API | OAuth |
| HTTP | REST | API backend, xác thực token | Tokens |
| ws | WebSocket | Thời gian thực, streaming | Tokens |

### Checklist cấu hình

- [ ] Loại server được chỉ định (stdio/SSE/HTTP/ws)
- [ ] Các trường theo loại được điền đủ (command hoặc url)
- [ ] Xác thực được cấu hình
- [ ] Các biến môi trường được ghi lại
- [ ] Dùng HTTPS/WSS (không dùng HTTP/WS)
- [ ] Dùng ${CLAUDE_PLUGIN_ROOT} cho các path

### Best Practices

**NÊN:**
- ✅ Dùng ${CLAUDE_PLUGIN_ROOT} cho path di động
- ✅ Ghi lại các biến môi trường bắt buộc
- ✅ Dùng kết nối bảo mật (HTTPS/WSS)
- ✅ Pre-allow MCP tool cụ thể trong commands
- ✅ Kiểm thử tích hợp MCP trước khi publish
- ✅ Xử lý lỗi kết nối và lỗi tool một cách ổn thỏa

**KHÔNG NÊN:**
- ❌ Hardcode đường dẫn tuyệt đối
- ❌ Commit credentials lên git
- ❌ Dùng HTTP thay vì HTTPS
- ❌ Pre-allow tất cả tool bằng wildcard
- ❌ Bỏ qua xử lý lỗi
- ❌ Quên ghi lại hướng dẫn cài đặt

## Tài nguyên bổ sung

### Các file tham chiếu

Để biết thông tin chi tiết, tham khảo:

- **`references/server-types.md`** - Tìm hiểu sâu về từng loại server
- **`references/authentication.md`** - Các pattern xác thực và OAuth
- **`references/tool-usage.md`** - Dùng MCP tool trong commands và agents

### Các cấu hình ví dụ

Ví dụ hoạt động trong `examples/`:

- **`stdio-server.json`** - MCP server stdio cục bộ
- **`sse-server.json`** - SSE server được host với OAuth
- **`http-server.json`** - REST API với xác thực token

### Tài nguyên bên ngoài

- **Tài liệu MCP chính thức**: <https://modelcontextprotocol.io/>
- **Tài liệu Claude Code MCP**: <https://docs.claude.com/en/docs/claude-code/mcp>
- **MCP SDK**: @modelcontextprotocol/sdk
- **Kiểm thử**: Dùng `claude --debug` và lệnh `/mcp`

## Quy trình triển khai

Để thêm tích hợp MCP vào plugin:

1. Chọn loại MCP server (stdio, SSE, HTTP, ws)
2. Tạo `.mcp.json` tại thư mục gốc plugin với cấu hình
3. Dùng ${CLAUDE_PLUGIN_ROOT} cho tất cả tham chiếu file
4. Ghi lại các biến môi trường bắt buộc trong README
5. Kiểm thử cục bộ với lệnh `/mcp`
6. Pre-allow MCP tool trong các command liên quan
7. Xử lý xác thực (OAuth hoặc token)
8. Kiểm thử các trường hợp lỗi (lỗi kết nối, lỗi xác thực)
9. Ghi lại tích hợp MCP trong README của plugin

Ưu tiên stdio cho server tùy chỉnh/cục bộ, SSE cho dịch vụ được host có OAuth.
