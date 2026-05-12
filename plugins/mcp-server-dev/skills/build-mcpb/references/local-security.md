# Bảo Mật MCP Local

**MCPB không cung cấp sandbox.** Không có block `permissions` trong manifest, không có filesystem scoping, không có network allowlist được platform thực thi. Tiến trình server chạy với toàn quyền của người dùng — nó có thể đọc bất kỳ file nào người dùng có thể đọc, khởi động bất kỳ tiến trình nào, gọi bất kỳ network endpoint nào.

Claude điều khiển nó. Sự kết hợp đó có nghĩa là: **input của tool là untrusted**, dù chúng đến từ một AI mà người dùng tin tưởng. Một trang web bị prompt-inject có thể khiến Claude gọi tool `delete_file` của bạn với một path bạn không hề có ý định.

Tool handler của bạn là lớp bảo vệ duy nhất. Mọi thứ bên dưới đều nói về việc tự xây dựng lớp bảo vệ đó.

---

## Path Traversal

Lỗi #1 trong local MCP server. Nếu bạn nhận parameter là path rồi join với root, **hãy resolve và kiểm tra containment**.

```typescript
import { resolve, relative, isAbsolute } from "node:path";

function safeJoin(root: string, userPath: string): string {
  const full = resolve(root, userPath);
  const rel = relative(root, full);
  if (rel.startsWith("..") || isAbsolute(rel)) {
    throw new Error(`Path escapes root: ${userPath}`);
  }
  return full;
}
```

`resolve` chuẩn hóa `..`, các segment symlink, v.v. `relative` cho bạn biết liệu kết quả có thoát khỏi root không. Đừng chỉ dùng `String.includes("..")` — cách đó bỏ sót các escape dạng encoded và symlink.

**Tương đương Python:**

```python
from pathlib import Path

def safe_join(root: Path, user_path: str) -> Path:
    full = (root / user_path).resolve()
    if not full.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes root: {user_path}")
    return full
```

---

## Roots — Hỏi Host, Đừng Hardcode

Trước khi hardcode `ROOT` từ config env var, kiểm tra xem host có hỗ trợ `roots/list` không. Đây là cách spec-native để lấy ranh giới workspace đã được người dùng phê duyệt.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

const server = new McpServer({ name: "...", version: "..." });

let allowedRoots: string[] = [];
server.server.oninitialized = async () => {
  const caps = server.getClientCapabilities();
  if (caps?.roots) {
    const { roots } = await server.server.listRoots();
    allowedRoots = roots.map(r => new URL(r.uri).pathname);
  } else {
    allowedRoots = [process.env.ROOT_DIR ?? process.cwd()];
  }
};
```

```python
# fastmcp — bên trong một tool handler
async def my_tool(ctx: Context) -> str:
    try:
        roots = await ctx.list_roots()
        allowed = [urlparse(r.uri).path for r in roots]
    except Exception:
        allowed = [os.environ.get("ROOT_DIR", os.getcwd())]
```

Nếu roots có sẵn, hãy dùng chúng. Nếu không, fallback về config. Dù thế nào, hãy validate mọi path so với tập allowed.

---

## Command Injection

Nếu bạn spawn tiến trình, **đừng bao giờ truyền input người dùng qua shell**.

```typescript
// ❌ thảm họa
exec(`git log ${branch}`);

// ✅ array-args, không shell
execFile("git", ["log", branch]);
```

Nếu bạn đang wrap CLI, hãy build toàn bộ argv dưới dạng array. Validate từng flag theo allowlist nếu tool nhận flag.

---

## Chỉ Đọc Theo Mặc Định

Tách read và write thành tool riêng biệt. Hầu hết workflow chỉ cần read. Một tool chỉ đọc không thể bị vũ khí hóa để gây mất dữ liệu dù Claude bị đánh lừa gọi với bất kỳ argument nào.

```
list_files   ← an toàn để gọi tự do
read_file    ← an toàn để gọi tự do
write_file   ← tool riêng, kiểm tra riêng
delete_file  ← cân nhắc không ship luôn
```

Kết hợp với tool annotation — `readOnlyHint: true` trên mọi read tool, `destructiveHint: true` trên delete/overwrite tool. Host hiển thị những thứ này trong permission UI (auto-approve read, confirm-dialog destructive). Xem `../build-mcp-server/references/tool-design.md`.

Nếu bạn ship write/delete, cân nhắc yêu cầu xác nhận tường minh qua elicitation (xem `../build-mcp-server/references/elicitation.md`) hoặc widget xác nhận (xem `build-mcp-app`) để người dùng phê duyệt từng lần gọi destructive.

---

## Giới Hạn Tài Nguyên

Claude sẽ vui vẻ yêu cầu đọc file log 4GB. Hãy giới hạn mọi thứ:

```typescript
const MAX_BYTES = 1_000_000;
const buf = await readFile(path);
if (buf.length > MAX_BYTES) {
  return {
    content: [{
      type: "text",
      text: `File is ${buf.length} bytes — too large. Showing first ${MAX_BYTES}:\n\n`
            + buf.subarray(0, MAX_BYTES).toString("utf8"),
    }],
  };
}
```

Tương tự với directory listing (giới hạn số entry), kết quả search (giới hạn số match), và bất kỳ thứ gì không có giới hạn.

---

## Secret

- **Config secret** (`sensitive: true` trong `user_config` của manifest): host lưu trong OS keychain, truyền qua env var. Đừng log chúng. Đừng đưa chúng vào tool result.
- **Đừng bao giờ lưu secret trong file plaintext.** Nếu tích hợp keychain của host không đủ, tự dùng `keytar` (Node) / `keyring` (Python).
- **Tool result đi vào chat transcript.** Bất cứ thứ gì bạn trả về, người dùng (và bất kỳ log export nào) đều có thể thấy. Hãy redact trước khi trả về.

---

## Checklist Trước Khi Ship

- [ ] Mọi path parameter đều qua kiểm tra containment
- [ ] Không dùng `exec()` / `shell=True` — chỉ dùng `execFile` / array-argv
- [ ] Write/delete tách khỏi read tool; annotation `readOnlyHint`/`destructiveHint` đã set
- [ ] Giới hạn kích thước cho file read, độ dài listing, kết quả search
- [ ] Secret không bao giờ được log hoặc trả về trong tool result
- [ ] Đã test với input thù địch: `../../etc/passwd`, `; rm -rf ~`, file 10GB
