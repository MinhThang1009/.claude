# Các Loại MCP Server: Tham Khảo Chuyên Sâu

Tài liệu tham khảo đầy đủ về tất cả loại MCP server được hỗ trợ trong Claude Code plugin.

## stdio (Standard Input/Output)

### Tổng Quan

Thực thi MCP server local dưới dạng child process với giao tiếp qua stdin/stdout. Lựa chọn tốt nhất cho local tool, custom server và NPM package.

### Cấu Hình

**Cơ bản:**
```json
{
  "my-server": {
    "command": "npx",
    "args": ["-y", "my-mcp-server"]
  }
}
```

**Với môi trường:**
```json
{
  "my-server": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/custom-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": {
      "API_KEY": "${MY_API_KEY}",
      "LOG_LEVEL": "debug",
      "DATABASE_URL": "${DB_URL}"
    }
  }
}
```

### Process Lifecycle

1. **Startup**: Claude Code spawn process với `command` và `args`
2. **Giao tiếp**: JSON-RPC message qua stdin/stdout
3. **Lifecycle**: Process chạy suốt session Claude Code
4. **Shutdown**: Process bị terminate khi Claude Code thoát

### Use Case

**NPM Package:**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
  }
}
```

**Custom Script:**
```json
{
  "custom": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server.js",
    "args": ["--verbose"]
  }
}
```

**Python Server:**
```json
{
  "python-server": {
    "command": "python",
    "args": ["-m", "my_mcp_server"],
    "env": {
      "PYTHONUNBUFFERED": "1"
    }
  }
}
```

### Best Practices

1. **Dùng absolute path hoặc ${CLAUDE_PLUGIN_ROOT}**
2. **Đặt PYTHONUNBUFFERED cho Python server**
3. **Truyền cấu hình qua args hoặc env, không phải stdin**
4. **Xử lý server crash gracefully**
5. **Log vào stderr, không phải stdout (stdout dành cho MCP protocol)**

### Xử Lý Sự Cố

**Server không khởi động:**
- Kiểm tra command tồn tại và có thể thực thi
- Xác minh file path đúng
- Kiểm tra quyền
- Xem log `claude --debug`

**Giao tiếp thất bại:**
- Đảm bảo server dùng stdin/stdout đúng cách
- Kiểm tra các câu lệnh print/console.log lạc chỗ
- Xác minh JSON-RPC format

## SSE (Server-Sent Events)

### Tổng Quan

Kết nối tới hosted MCP server qua HTTP với server-sent event để stream. Tốt nhất cho cloud service và OAuth authentication.

### Cấu Hình

**Cơ bản:**
```json
{
  "hosted-service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

**Với header:**
```json
{
  "service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "X-API-Version": "v1",
      "X-Client-ID": "${CLIENT_ID}"
    }
  }
}
```

### Connection Lifecycle

1. **Khởi tạo**: Thiết lập HTTP connection tới URL
2. **Handshake**: Đàm phán MCP protocol
3. **Streaming**: Server gửi event qua SSE
4. **Request**: Client gửi HTTP POST cho tool call
5. **Reconnect**: Tự động kết nối lại khi ngắt

### Xác Thực

**OAuth (Tự động):**
```json
{
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  }
}
```

Claude Code xử lý OAuth flow:
1. Người dùng được nhắc xác thực lần đầu sử dụng
2. Mở browser cho OAuth flow
3. Token được lưu an toàn
4. Tự động refresh token

**Custom Header:**
```json
{
  "service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

### Use Case

**Service Chính Thức:**
- Asana: `https://mcp.asana.com/sse`
- GitHub: `https://mcp.github.com/sse`
- Các hosted MCP server khác

**Custom Hosted Server:**
Deploy MCP server của riêng bạn và expose qua HTTPS + SSE.

### Best Practices

1. **Luôn dùng HTTPS, không bao giờ HTTP**
2. **Để OAuth xử lý xác thực khi có sẵn**
3. **Dùng biến môi trường cho token**
4. **Xử lý connection failure gracefully**
5. **Ghi lại OAuth scope cần thiết**

### Xử Lý Sự Cố

**Connection refused:**
- Kiểm tra URL đúng và có thể truy cập
- Xác minh HTTPS certificate hợp lệ
- Kiểm tra kết nối mạng
- Xem cài đặt firewall

**OAuth thất bại:**
- Xóa token đã cache
- Kiểm tra OAuth scope
- Xác minh redirect URL
- Xác thực lại

## HTTP (REST API)

### Tổng Quan

Kết nối tới RESTful MCP server qua HTTP request tiêu chuẩn. Tốt nhất cho token-based auth và stateless interaction.

### Cấu Hình

**Cơ bản:**
```json
{
  "api": {
    "type": "http",
    "url": "https://api.example.com/mcp"
  }
}
```

**Với xác thực:**
```json
{
  "api": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "Content-Type": "application/json",
      "X-API-Version": "2024-01-01"
    }
  }
}
```

### Request/Response Flow

1. **Tool Discovery**: GET để khám phá tool có sẵn
2. **Tool Invocation**: POST với tên tool và tham số
3. **Response**: JSON response với kết quả hoặc lỗi
4. **Stateless**: Mỗi request độc lập

### Xác Thực

**Token-Based:**
```json
{
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

**API Key:**
```json
{
  "headers": {
    "X-API-Key": "${API_KEY}"
  }
}
```

**Custom Auth:**
```json
{
  "headers": {
    "X-Auth-Token": "${AUTH_TOKEN}",
    "X-User-ID": "${USER_ID}"
  }
}
```

### Use Case

- REST API backend
- Internal service
- Microservice
- Serverless function

### Best Practices

1. **Dùng HTTPS cho tất cả kết nối**
2. **Lưu token trong biến môi trường**
3. **Triển khai retry logic cho transient failure**
4. **Xử lý rate limiting**
5. **Đặt timeout phù hợp**

### Xử Lý Sự Cố

**HTTP error:**
- 401: Kiểm tra authentication header
- 403: Xác minh quyền
- 429: Triển khai rate limiting
- 500: Kiểm tra server log

**Vấn đề timeout:**
- Tăng timeout nếu cần
- Kiểm tra hiệu suất server
- Tối ưu triển khai tool

## WebSocket (Real-time)

### Tổng Quan

Kết nối tới MCP server qua WebSocket cho giao tiếp hai chiều real-time. Tốt nhất cho streaming và ứng dụng độ trễ thấp.

### Cấu Hình

**Cơ bản:**
```json
{
  "realtime": {
    "type": "ws",
    "url": "wss://mcp.example.com/ws"
  }
}
```

**Với xác thực:**
```json
{
  "realtime": {
    "type": "ws",
    "url": "wss://mcp.example.com/ws",
    "headers": {
      "Authorization": "Bearer ${TOKEN}",
      "X-Client-ID": "${CLIENT_ID}"
    }
  }
}
```

### Connection Lifecycle

1. **Handshake**: WebSocket upgrade request
2. **Connection**: Kênh hai chiều persistent
3. **Message**: JSON-RPC qua WebSocket
4. **Heartbeat**: Keep-alive message
5. **Reconnect**: Tự động khi ngắt

### Use Case

- Stream dữ liệu real-time
- Cập nhật và thông báo trực tiếp
- Chỉnh sửa cộng tác
- Tool call độ trễ thấp
- Push notification từ server

### Best Practices

1. **Dùng WSS (secure WebSocket), không bao giờ WS**
2. **Triển khai heartbeat/ping-pong**
3. **Xử lý reconnection logic**
4. **Buffer message trong thời gian ngắt kết nối**
5. **Đặt connection timeout**

### Xử Lý Sự Cố

**Connection drop:**
- Triển khai reconnection logic
- Kiểm tra độ ổn định mạng
- Xác minh server hỗ trợ WebSocket
- Xem cài đặt firewall

**Message delivery:**
- Triển khai message acknowledgment
- Xử lý message không theo thứ tự
- Buffer trong thời gian ngắt kết nối

## Ma Trận So Sánh

| Tính năng | stdio | SSE | HTTP | WebSocket |
|---------|-------|-----|------|-----------|
| **Transport** | Process | HTTP/SSE | HTTP | WebSocket |
| **Chiều** | Hai chiều | Server→Client | Request/Response | Hai chiều |
| **State** | Stateful | Stateful | Stateless | Stateful |
| **Auth** | Env var | OAuth/Header | Header | Header |
| **Use Case** | Local tool | Cloud service | REST API | Real-time |
| **Latency** | Thấp nhất | Trung bình | Trung bình | Thấp |
| **Cài đặt** | Dễ | Trung bình | Dễ | Trung bình |
| **Reconnect** | Process respawn | Tự động | N/A | Tự động |

## Chọn Loại Phù Hợp

**Dùng stdio khi:**
- Chạy local tool hoặc custom server
- Cần latency thấp nhất
- Làm việc với file system hoặc local database
- Phân phối server kèm plugin

**Dùng SSE khi:**
- Kết nối với hosted service
- Cần OAuth authentication
- Dùng MCP server chính thức (Asana, GitHub)
- Muốn tự động reconnect

**Dùng HTTP khi:**
- Tích hợp với REST API
- Cần stateless interaction
- Dùng token-based auth
- Pattern request/response đơn giản

**Dùng WebSocket khi:**
- Cần cập nhật real-time
- Xây dựng tính năng cộng tác
- Độ trễ là ưu tiên
- Cần streaming hai chiều

## Chuyển Đổi Giữa Các Loại

### Từ stdio sang SSE

**Trước (stdio):**
```json
{
  "local-server": {
    "command": "node",
    "args": ["server.js"]
  }
}
```

**Sau (SSE - deploy server):**
```json
{
  "hosted-server": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

### Từ HTTP sang WebSocket

**Trước (HTTP):**
```json
{
  "api": {
    "type": "http",
    "url": "https://api.example.com/mcp"
  }
}
```

**Sau (WebSocket):**
```json
{
  "realtime": {
    "type": "ws",
    "url": "wss://api.example.com/ws"
  }
}
```

Lợi ích: Cập nhật real-time, latency thấp hơn, giao tiếp hai chiều.

## Cấu Hình Nâng Cao

### Nhiều Server

Kết hợp các loại khác nhau:

```json
{
  "local-db": {
    "command": "npx",
    "args": ["-y", "mcp-server-sqlite", "./data.db"]
  },
  "cloud-api": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  },
  "internal-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

### Cấu Hình Có Điều Kiện

Dùng biến môi trường để chuyển server:

```json
{
  "api": {
    "type": "http",
    "url": "${API_URL}",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

Đặt giá trị khác nhau cho dev/prod:
- Dev: `API_URL=http://localhost:8080/mcp`
- Prod: `API_URL=https://api.production.com/mcp`

## Cân Nhắc Bảo Mật

### Bảo Mật Stdio

- Validate đường dẫn command
- Không thực thi lệnh do người dùng cung cấp
- Hạn chế quyền truy cập biến môi trường
- Hạn chế quyền truy cập file system

### Bảo Mật Mạng

- Luôn dùng HTTPS/WSS
- Validate SSL certificate
- Không bỏ qua xác minh certificate
- Dùng lưu trữ token an toàn

### Quản Lý Token

- Không bao giờ hardcode token
- Dùng biến môi trường
- Rotate token thường xuyên
- Triển khai token refresh
- Ghi lại scope cần thiết

## Kết Luận

Chọn loại MCP server dựa trên use case:
- **stdio** cho local, custom, hoặc NPM-packaged server
- **SSE** cho hosted service với OAuth
- **HTTP** cho REST API với token auth
- **WebSocket** cho giao tiếp hai chiều real-time

Kiểm thử kỹ lưỡng và xử lý lỗi gracefully để tích hợp MCP bền vững.
