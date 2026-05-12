---
name: build-mcpb
description: This skill should be used when the user wants to "package an MCP server", "bundle an MCP", "make an MCPB", "ship a local MCP server", "distribute a local MCP", discusses ".mcpb files", mentions bundling a Node or Python runtime with their MCP server, or needs an MCP server that interacts with the local filesystem, desktop apps, or OS and must be installable without the user having Node/Python set up.
version: 0.1.0
---

# Xây dựng MCPB (Bundled Local MCP Server)

MCPB là MCP server local **đóng gói kèm runtime**. User cài một file; chạy mà không cần Node, Python, hoặc bất kỳ toolchain nào trên máy họ. Đây là cách được chấp thuận để phân phối local MCP servers.

> MCPB là con đường phân phối **thứ cấp**. Anthropic khuyến nghị remote MCP servers để listing trong directory — xem https://claude.com/docs/connectors/building/what-to-build.

**Dùng MCPB khi server phải chạy trên máy user** — đọc local files, drive desktop app, nói chuyện với localhost services, OS-level APIs. Nếu server của bạn chỉ gọi cloud APIs, hầu như chắc chắn bạn muốn remote HTTP server thay vào đó (xem `build-mcp-server`). Đừng chịu thuế MCPB packaging cho thứ có thể là một URL.

---

## Bundle MCPB chứa gì

```
my-server.mcpb              (zip archive)
├── manifest.json           ← identity, entry point, config schema, compatibility
├── server/                 ← code MCP server của bạn
│   ├── index.js
│   └── node_modules/       ← dependencies bundled (hoặc vendored)
└── icon.png
```

Host đọc `manifest.json`, chạy `server.mcp_config.command` như **stdio** MCP server, và pipe messages. Từ góc nhìn code của bạn, nó giống hệt local stdio server — sự khác biệt duy nhất là packaging.

---

## Manifest

```json
{
  "$schema": "https://raw.githubusercontent.com/anthropics/mcpb/main/schemas/mcpb-manifest-v0.4.schema.json",
  "manifest_version": "0.4",
  "name": "local-files",
  "version": "0.1.0",
  "description": "Read, search, and watch files on the local filesystem.",
  "author": { "name": "Your Name" },
  "server": {
    "type": "node",
    "entry_point": "server/index.js",
    "mcp_config": {
      "command": "node",
      "args": ["${__dirname}/server/index.js"],
      "env": {
        "ROOT_DIR": "${user_config.rootDir}"
      }
    }
  },
  "user_config": {
    "rootDir": {
      "type": "directory",
      "title": "Root directory",
      "description": "Directory to expose. Defaults to ~/Documents.",
      "default": "${HOME}/Documents",
      "required": true
    }
  },
  "compatibility": {
    "claude_desktop": ">=1.0.0",
    "platforms": ["darwin", "win32", "linux"]
  }
}
```

**`server.type`** — `node`, `python`, hoặc `binary`. Chỉ mang tính thông tin; lệnh thực tế đến từ `mcp_config`.

**`server.mcp_config`** — lệnh/args/env literal để spawn. Dùng `${__dirname}` cho bundle-relative paths và `${user_config.<key>}` để substitute install-time config. **Không có auto-prefix** — tên env var mà server của bạn đọc là chính xác những gì bạn đặt trong `env`.

**`user_config`** — cài đặt install-time được surface trong UI của host. `type: "directory"` render native folder picker. `sensitive: true` lưu trong OS keychain. Xem `references/manifest-schema.md` để biết tất cả các fields.

---

## Server code: giống local stdio

Bản thân server là stdio MCP server tiêu chuẩn. Không có gì đặc thù MCPB trong tool logic.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { homedir } from "node:os";

// ROOT_DIR đến từ những gì bạn đặt trong server.mcp_config.env của manifest — không có auto-prefix
const ROOT = (process.env.ROOT_DIR ?? join(homedir(), "Documents"));

const server = new McpServer({ name: "local-files", version: "0.1.0" });

server.registerTool(
  "list_files",
  {
    description: "List files in a directory under the configured root.",
    inputSchema: { path: z.string().default(".") },
    annotations: { readOnlyHint: true },
  },
  async ({ path }) => {
    const entries = await readdir(join(ROOT, path), { withFileTypes: true });
    const list = entries.map(e => ({ name: e.name, dir: e.isDirectory() }));
    return { content: [{ type: "text", text: JSON.stringify(list, null, 2) }] };
  },
);

server.registerTool(
  "read_file",
  {
    description: "Read a file's contents. Path is relative to the configured root.",
    inputSchema: { path: z.string() },
    annotations: { readOnlyHint: true },
  },
  async ({ path }) => {
    const text = await readFile(join(ROOT, path), "utf8");
    return { content: [{ type: "text", text }] };
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Sandboxing hoàn toàn là trách nhiệm của bạn.** Không có sandbox ở cấp manifest — process chạy với full user privileges. Validate paths, từ chối escape khỏi `ROOT`, allowlist spawns. Xem `references/local-security.md`.

Trước khi hardcode `ROOT` từ config env var, kiểm tra xem host có hỗ trợ `roots/list` không — cách native theo spec để lấy user-approved directories. Xem `references/local-security.md` để biết pattern.

---

## Build pipeline

### Node

```bash
npm install
npx esbuild src/index.ts --bundle --platform=node --outfile=server/index.js
# hoặc: copy node_modules wholesale nếu native deps khó bundle
npx @anthropic-ai/mcpb pack
```

`mcpb pack` zip directory và validate `manifest.json` theo schema.

### Python

```bash
pip install -t server/vendor -r requirements.txt
npx @anthropic-ai/mcpb pack
```

Vendor dependencies vào subdirectory và prepend vào `sys.path` trong entry script. Native extensions (numpy, v.v.) phải được build cho từng target platform — tránh native deps nếu có thể.

---

## MCPB không có sandbox — security là trách nhiệm của bạn

Khác với mobile app stores, MCPB KHÔNG enforce permissions. Manifest không có block `permissions` — server chạy với full user privileges. `references/local-security.md` là tài liệu phải đọc, không phải optional. Mọi path phải được validate, mọi spawn phải được allowlist, vì không có gì dừng bạn ở platform level.

Nếu bạn đến đây kỳ vọng filesystem/network scoping từ manifest: nó không tồn tại. Tự build trong tool handlers.

Nếu công việc duy nhất của server là gọi cloud API, dừng lại — đó là remote server mặc áo MCPB. User không được lợi gì từ việc chạy nó local, và bạn đang chịu gánh nặng local-security vô lý do.

---

## MCPB + UI widgets

MCPB servers có thể phục vụ UI resources giống hệt remote MCP apps — widget mechanism là transport-agnostic. File picker local duyệt disk thực, dialog điều khiển native app, v.v.

Widget authoring được đề cập trong skill **`build-mcp-app`**; hoạt động tương tự ở đây. Sự khác biệt duy nhất là nơi server chạy.

---

## Testing

```bash
# Tạo manifest tương tác (lần đầu)
npx @anthropic-ai/mcpb init

# Chạy server trực tiếp qua stdio, thử với inspector
npx @modelcontextprotocol/inspector node server/index.js

# Validate manifest theo schema, rồi pack
npx @anthropic-ai/mcpb validate
npx @anthropic-ai/mcpb pack

# Ký để phân phối
npx @anthropic-ai/mcpb sign dist/local-files.mcpb

# Cài đặt: kéo file .mcpb vào Claude Desktop
```

Test trên máy **không có** dev toolchain của bạn trước khi ship. Các lỗi "Works on my machine" trong MCPB hầu như luôn truy về một dependency không thực sự được bundled.

---

## Reference files

- `references/manifest-schema.md` — tham chiếu đầy đủ các field trong `manifest.json`
- `references/local-security.md` — path traversal, sandboxing, least privilege
