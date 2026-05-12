# Các Pattern Xác Thực MCP

Hướng dẫn đầy đủ về các phương thức xác thực cho MCP server trong Claude Code plugin.

## Tổng Quan

MCP server hỗ trợ nhiều phương thức xác thực tùy theo loại server và yêu cầu của service. Chọn phương thức phù hợp nhất với use case và yêu cầu bảo mật của bạn.

## OAuth (Tự Động)

### Cách Hoạt Động

Claude Code tự động xử lý toàn bộ OAuth 2.0 flow cho SSE và HTTP server:

1. Người dùng cố dùng MCP tool
2. Claude Code phát hiện cần xác thực
3. Mở browser cho OAuth consent
4. Người dùng ủy quyền trong browser
5. Token được lưu an toàn bởi Claude Code
6. Tự động refresh token

### Cấu Hình

```json
{
  "service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

Không cần cấu hình auth thêm! Claude Code xử lý tất cả.

### Các Service Được Hỗ Trợ

**MCP server đã biết có OAuth:**
- Asana: `https://mcp.asana.com/sse`
- GitHub (khi có sẵn)
- Google services (khi có sẵn)
- Custom OAuth server

### OAuth Scope

OAuth scope do MCP server quy định. Người dùng thấy scope cần thiết trong quá trình consent flow.

**Ghi lại scope cần thiết trong README:**
```markdown
## Xác Thực

Plugin này yêu cầu các quyền Asana sau:
- Đọc task và project
- Tạo và cập nhật task
- Truy cập dữ liệu workspace
```

### Lưu Trữ Token

Token được lưu an toàn bởi Claude Code:
- Không thể truy cập bởi plugin
- Mã hóa khi lưu trữ
- Tự động refresh
- Xóa khi đăng xuất

### Xử Lý Sự Cố OAuth

**Authentication loop:**
- Xóa token đã cache (đăng xuất và đăng nhập lại)
- Kiểm tra OAuth redirect URL
- Xác minh cấu hình OAuth của server

**Vấn đề về scope:**
- Người dùng có thể cần cấp quyền lại cho scope mới
- Kiểm tra tài liệu server về scope cần thiết

**Token hết hạn:**
- Claude Code tự động refresh
- Nếu refresh thất bại, nhắc xác thực lại

## Xác Thực Dựa Trên Token

### Bearer Token

Phổ biến nhất cho HTTP và WebSocket server.

**Cấu hình:**
```json
{
  "api": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

**Biến môi trường:**
```bash
export API_TOKEN="your-secret-token-here"
```

### API Key

Thay thế cho Bearer token, thường dùng trong custom header.

**Cấu hình:**
```json
{
  "api": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "X-API-Key": "${API_KEY}",
      "X-API-Secret": "${API_SECRET}"
    }
  }
}
```

### Custom Header

Một số service dùng custom header để xác thực.

**Cấu hình:**
```json
{
  "service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "X-Auth-Token": "${AUTH_TOKEN}",
      "X-User-ID": "${USER_ID}",
      "X-Tenant-ID": "${TENANT_ID}"
    }
  }
}
```

### Ghi Lại Yêu Cầu Token

Luôn ghi lại trong README:

```markdown
## Cài Đặt

### Biến Môi Trường Cần Thiết

Đặt các biến môi trường này trước khi dùng plugin:

\`\`\`bash
export API_TOKEN="your-token-here"
export API_SECRET="your-secret-here"
\`\`\`

### Lấy Token

1. Truy cập https://api.example.com/tokens
2. Tạo API token mới
3. Copy token và secret
4. Đặt biến môi trường như trên

### Quyền Token

API token cần các quyền sau:
- Quyền đọc resource
- Quyền ghi để tạo item
- Quyền xóa (tùy chọn, cho thao tác dọn dẹp)
\`\`\`
```

## Xác Thực Biến Môi Trường (stdio)

### Truyền Credential vào Server

Với stdio server, truyền credential qua biến môi trường:

```json
{
  "database": {
    "command": "python",
    "args": ["-m", "mcp_server_db"],
    "env": {
      "DATABASE_URL": "${DATABASE_URL}",
      "DB_USER": "${DB_USER}",
      "DB_PASSWORD": "${DB_PASSWORD}"
    }
  }
}
```

### Biến Môi Trường Người Dùng

```bash
# Người dùng đặt trong shell của họ
export DATABASE_URL="postgresql://localhost/mydb"
export DB_USER="myuser"
export DB_PASSWORD="mypassword"
```

### Template Tài Liệu

```markdown
## Cấu Hình Database

Đặt các biến môi trường sau:

\`\`\`bash
export DATABASE_URL="postgresql://host:port/database"
export DB_USER="username"
export DB_PASSWORD="password"
\`\`\`

Hoặc tạo file `.env` (thêm vào `.gitignore`):

\`\`\`
DATABASE_URL=postgresql://localhost:5432/mydb
DB_USER=myuser
DB_PASSWORD=mypassword
\`\`\`

Load bằng: \`source .env\` hoặc \`export $(cat .env | xargs)\`
\`\`\`
```

## Dynamic Header

### Script Helper cho Header

Với token thay đổi hoặc hết hạn, dùng script helper:

```json
{
  "api": {
    "type": "sse",
    "url": "https://api.example.com",
    "headersHelper": "${CLAUDE_PLUGIN_ROOT}/scripts/get-headers.sh"
  }
}
```

**Script (get-headers.sh):**
```bash
#!/bin/bash
# Tạo authentication header động

# Lấy token mới
TOKEN=$(get-fresh-token-from-somewhere)

# Output JSON header
cat <<EOF
{
  "Authorization": "Bearer $TOKEN",
  "X-Timestamp": "$(date -Iseconds)"
}
EOF
```

### Use Case cho Dynamic Header

- Token thời gian ngắn cần refresh
- Token có HMAC signature
- Xác thực dựa trên thời gian
- Chọn tenant/workspace động

## Best Practices Bảo Mật

### NÊN

✅ **Dùng biến môi trường:**
```json
{
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

✅ **Ghi lại các biến cần thiết trong README**

✅ **Luôn dùng HTTPS/WSS**

✅ **Triển khai token rotation**

✅ **Lưu token an toàn (env var, không phải file)**

✅ **Để OAuth xử lý xác thực khi có sẵn**

### KHÔNG NÊN

❌ **Hardcode token:**
```json
{
  "headers": {
    "Authorization": "Bearer sk-abc123..."  // KHÔNG BAO GIỜ!
  }
}
```

❌ **Commit token lên git**

❌ **Chia sẻ token trong tài liệu**

❌ **Dùng HTTP thay vì HTTPS**

❌ **Lưu token trong file plugin**

❌ **Log token hoặc header nhạy cảm**

## Các Pattern Multi-Tenancy

### Chọn Workspace/Tenant

**Qua biến môi trường:**
```json
{
  "api": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "X-Workspace-ID": "${WORKSPACE_ID}"
    }
  }
}
```

**Qua URL:**
```json
{
  "api": {
    "type": "http",
    "url": "https://${TENANT_ID}.api.example.com/mcp"
  }
}
```

### Cấu Hình Per-User

Người dùng đặt workspace của riêng họ:

```bash
export WORKSPACE_ID="my-workspace-123"
export TENANT_ID="my-company"
```

## Xử Lý Sự Cố Xác Thực

### Vấn Đề Thường Gặp

**401 Unauthorized:**
- Kiểm tra token được đặt đúng
- Xác minh token chưa hết hạn
- Kiểm tra token có đủ quyền
- Đảm bảo format header đúng

**403 Forbidden:**
- Token hợp lệ nhưng thiếu quyền
- Kiểm tra scope/quyền
- Xác minh workspace/tenant ID
- Có thể cần phê duyệt admin

**Token không tìm thấy:**
```bash
# Kiểm tra biến môi trường đã được đặt
echo $API_TOKEN

# Nếu trống, đặt lại
export API_TOKEN="your-token"
```

**Token sai format:**
```json
// Đúng
"Authorization": "Bearer sk-abc123"

// Sai
"Authorization": "sk-abc123"
```

### Debug Xác Thực

**Bật chế độ debug:**
```bash
claude --debug
```

Tìm kiếm:
- Giá trị authentication header (đã sanitize)
- Tiến trình OAuth flow
- Lần thử refresh token
- Lỗi xác thực

**Kiểm tra xác thực riêng lẻ:**
```bash
# Test HTTP endpoint
curl -H "Authorization: Bearer $API_TOKEN" \
     https://api.example.com/mcp/health

# Phải trả về 200 OK
```

## Các Pattern Migration

### Từ Hardcoded sang Biến Môi Trường

**Trước:**
```json
{
  "headers": {
    "Authorization": "Bearer sk-hardcoded-token"
  }
}
```

**Sau:**
```json
{
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

**Các bước migration:**
1. Thêm biến môi trường vào README plugin
2. Cập nhật cấu hình để dùng ${VAR}
3. Kiểm thử với biến đã đặt
4. Xóa giá trị hardcoded
5. Commit thay đổi

### Từ Basic Auth sang OAuth

**Trước:**
```json
{
  "headers": {
    "Authorization": "Basic ${BASE64_CREDENTIALS}"
  }
}
```

**Sau:**
```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse"
}
```

**Lợi ích:**
- Bảo mật tốt hơn
- Không quản lý credential
- Tự động refresh token
- Quyền có scope

## Xác Thực Nâng Cao

### Mutual TLS (mTLS)

Một số service enterprise yêu cầu certificate của client.

**Không được hỗ trợ trực tiếp trong cấu hình MCP.**

**Workaround:** Bọc trong stdio server xử lý mTLS:

```json
{
  "secure-api": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/mtls-wrapper",
    "args": ["--cert", "${CLIENT_CERT}", "--key", "${CLIENT_KEY}"],
    "env": {
      "API_URL": "https://secure.example.com"
    }
  }
}
```

### JWT Token

Tạo JWT token động với headers helper:

```bash
#!/bin/bash
# generate-jwt.sh

# Tạo JWT (dùng library hoặc API call)
JWT=$(generate-jwt-token)

echo "{\"Authorization\": \"Bearer $JWT\"}"
```

```json
{
  "headersHelper": "${CLAUDE_PLUGIN_ROOT}/scripts/generate-jwt.sh"
}
```

### HMAC Signature

Với API yêu cầu ký request:

```bash
#!/bin/bash
# generate-hmac.sh

TIMESTAMP=$(date -Iseconds)
SIGNATURE=$(echo -n "$TIMESTAMP" | openssl dgst -sha256 -hmac "$SECRET_KEY" | cut -d' ' -f2)

cat <<EOF
{
  "X-Timestamp": "$TIMESTAMP",
  "X-Signature": "$SIGNATURE",
  "X-API-Key": "$API_KEY"
}
EOF
```

## Tóm Tắt Best Practices

### Cho Developer Plugin

1. **Ưu tiên OAuth** khi service hỗ trợ
2. **Dùng biến môi trường** cho token
3. **Ghi lại tất cả biến cần thiết** trong README
4. **Cung cấp hướng dẫn cài đặt** có ví dụ
5. **Không bao giờ commit credential**
6. **Chỉ dùng HTTPS/WSS**
7. **Kiểm thử xác thực kỹ lưỡng**

### Cho Người Dùng Plugin

1. **Đặt biến môi trường** trước khi dùng plugin
2. **Giữ token an toàn** và riêng tư
3. **Rotate token thường xuyên**
4. **Dùng token khác nhau** cho dev/prod
5. **Không commit file .env** lên git
6. **Xem lại OAuth scope** trước khi ủy quyền

## Kết Luận

Chọn phương thức xác thực phù hợp với yêu cầu MCP server:
- **OAuth** cho cloud service (dễ dùng nhất cho người dùng)
- **Bearer token** cho API service
- **Biến môi trường** cho stdio server
- **Dynamic header** cho authentication flow phức tạp

Luôn ưu tiên bảo mật và cung cấp tài liệu cài đặt rõ ràng cho người dùng.
