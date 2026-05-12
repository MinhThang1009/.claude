# Schema Manifest MCPB (v0.4)

Được validate theo `github.com/anthropics/mcpb/schemas/mcpb-manifest-v0.4.schema.json`. Schema dùng `additionalProperties: false` — key không xác định sẽ bị từ chối. Thêm `"$schema"` vào manifest để có validation trong editor.

---

## Các Field Cấp Cao Nhất

| Field | Bắt buộc | Mô tả |
|---|---|---|
| `manifest_version` | ✅ | Phiên bản schema. Dùng `"0.4"`. |
| `name` | ✅ | Định danh package (chữ thường, dấu gạch ngang). Phải unique. |
| `version` | ✅ | Phiên bản semver của package CỦA BẠN. |
| `description` | ✅ | Tóm tắt một dòng. Hiển thị trên marketplace. |
| `author` | ✅ | `{name, email?, url?}` |
| `server` | ✅ | Entry point và cấu hình khởi động. Xem bên dưới. |
| `display_name` | | Tên thân thiện với người đọc. Fallback về `name` nếu không có. |
| `long_description` | | Markdown. Hiển thị trên trang chi tiết. |
| `icon` / `icons` | | Đường dẫn đến file icon trong bundle. |
| `homepage` / `repository` / `documentation` / `support` | | Các URL. |
| `license` | | Định danh SPDX. |
| `keywords` | | Mảng chuỗi dùng để tìm kiếm. |
| `user_config` | | Các field cấu hình lúc cài đặt. Xem bên dưới. |
| `compatibility` | | Yêu cầu host/platform/runtime. Xem bên dưới. |
| `tools` / `prompts` | | Danh sách khai báo tùy chọn để hiển thị trên marketplace. Không được thực thi lúc runtime. |
| `tools_generated` / `prompts_generated` | | `true` nếu tool/prompt là dynamic (không thể liệt kê tĩnh). |
| `screenshots` | | Mảng đường dẫn ảnh. |
| `localization` | | Bundle i18n. |
| `privacy_policies` | | Các URL. |

---

## `server` — Cấu Hình Khởi Động

```json
"server": {
  "type": "node",
  "entry_point": "server/index.js",
  "mcp_config": {
    "command": "node",
    "args": ["${__dirname}/server/index.js"],
    "env": {
      "API_KEY": "${user_config.apiKey}",
      "ROOT_DIR": "${user_config.rootDir}"
    }
  }
}
```

| Field | Mô tả |
|---|---|
| `type` | `"node"`, `"python"`, hoặc `"binary"` |
| `entry_point` | Đường dẫn tương đối đến file chính. Chỉ mang tính thông tin. |
| `mcp_config.command` | Executable để khởi động. |
| `mcp_config.args` | Mảng argv. Dùng `${__dirname}` cho đường dẫn tương đối với bundle. |
| `mcp_config.env` | Biến môi trường. Dùng `${user_config.KEY}` để substitute config người dùng. |

**Biến substitution** (chỉ trong `args` và `env`):
- `${__dirname}` — đường dẫn tuyệt đối đến thư mục bundle đã giải nén
- `${user_config.<key>}` — giá trị người dùng nhập lúc cài đặt
- `${HOME}` — thư mục home của người dùng

**Không có env var nào được tự động thêm tiền tố.** Tên env var mà server của bạn đọc chính xác là những gì bạn khai báo trong `mcp_config.env`. Nếu bạn viết `"ROOT_DIR": "${user_config.rootDir}"`, server của bạn đọc `process.env.ROOT_DIR`.

---

## `user_config` — Cài Đặt Lúc Cài Đặt

```json
"user_config": {
  "apiKey": {
    "type": "string",
    "title": "API Key",
    "description": "API key của dịch vụ. Được lưu mã hóa.",
    "sensitive": true,
    "required": true
  },
  "rootDir": {
    "type": "directory",
    "title": "Thư mục root",
    "description": "Thư mục để expose cho server.",
    "default": "${HOME}/Documents"
  },
  "maxResults": {
    "type": "number",
    "title": "Số kết quả tối đa",
    "description": "Số item tối đa trả về mỗi query.",
    "default": 50,
    "min": 1,
    "max": 500
  }
}
```

| Field | Bắt buộc | Mô tả |
|---|---|---|
| `type` | ✅ | `"string"`, `"number"`, `"boolean"`, `"directory"`, `"file"` |
| `title` | ✅ | Nhãn của form. |
| `description` | ✅ | Text hướng dẫn dưới input. |
| `default` | | Giá trị điền sẵn. Hỗ trợ `${HOME}`. |
| `required` | | Nếu `true`, chặn cài đặt cho đến khi được điền. |
| `sensitive` | | Nếu `true`, được lưu trong OS keychain và ẩn trong UI. **KHÔNG phải `secret`** — field đó không tồn tại. |
| `multiple` | | Nếu `true`, người dùng có thể nhập nhiều giá trị (mảng). |
| `min` / `max` | | Giới hạn số (dành cho `type: "number"`). |

Kiểu `directory` và `file` render native OS picker — ưu tiên dùng thay vì free-text path để UX và validation tốt hơn.

---

## `compatibility` — Chặn Cài Đặt

```json
"compatibility": {
  "claude_desktop": ">=1.0.0",
  "platforms": ["darwin", "win32", "linux"],
  "runtimes": { "node": ">=20" }
}
```

| Field | Mô tả |
|---|---|
| `claude_desktop` | Semver range. Chặn cài đặt nếu host cũ hơn. |
| `platforms` | Allowlist hệ điều hành. Tập con của `["darwin", "win32", "linux"]`. |
| `runtimes` | Phiên bản runtime cần thiết, ví dụ `{"node": ">=20"}` hoặc `{"python": ">=3.11"}`. |

---

## Manifest Tối Giản Hợp Lệ

```json
{
  "$schema": "https://raw.githubusercontent.com/anthropics/mcpb/main/schemas/mcpb-manifest-v0.4.schema.json",
  "manifest_version": "0.4",
  "name": "hello",
  "version": "0.1.0",
  "description": "MCPB server tối giản.",
  "author": { "name": "Tên Của Bạn" },
  "server": {
    "type": "node",
    "entry_point": "server/index.js",
    "mcp_config": {
      "command": "node",
      "args": ["${__dirname}/server/index.js"]
    }
  }
}
```

---

## Những Gì MCPB KHÔNG Có

- **Không có block `permissions`.** Không có filesystem/network/process scoping cấp manifest. Server chạy với toàn quyền người dùng. Thực thi ranh giới trong tool handler — xem `local-security.md`.
- **Không có tiền tố env var tự động.** Không có convention `MCPB_CONFIG_*`. Bạn wire config → env tường minh trong `server.mcp_config.env`.
- **Không có field `entry`.** Đó là `server` với `entry_point` bên trong.
- **Không có `minHostVersion`.** Đó là `compatibility.claude_desktop`.
