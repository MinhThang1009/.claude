# Server capabilities — phần còn lại của spec

Các tính năng ngoài ba primitive cốt lõi. Hầu hết là tùy chọn, một số gần như miễn phí nhưng mang lại nhiều giá trị.

---

## `instructions` — injection vào system prompt

Một dòng config, được đưa thẳng vào system prompt của Claude. Dùng cho gợi ý sử dụng tool không vừa vào mô tả từng tool riêng lẻ.

```typescript
const server = new McpServer(
  { name: "my-server", version: "1.0.0" },
  { instructions: "Always call search_items before get_item — IDs aren't guessable." },
);
```

```python
mcp = FastMCP("my-server", instructions="Always call search_items before get_item — IDs aren't guessable.")
```

Đây là one-liner có đòn bẩy cao nhất trong spec. Nếu Claude liên tục dùng tool sai, hãy đặt cách sửa vào đây.

---

## Sampling — ủy thác LLM call cho host

Nếu logic tool của bạn cần LLM inference (tóm tắt, phân loại, sinh nội dung), đừng ship model client riêng. Hãy nhờ host làm.

```typescript
// Bên trong một tool handler
const result = await extra.sendRequest({
  method: "sampling/createMessage",
  params: {
    messages: [{ role: "user", content: { type: "text", text: `Summarize: ${doc}` } }],
    maxTokens: 500,
  },
}, CreateMessageResultSchema);
```

```python
# fastmcp
response = await ctx.sample("Summarize this document", context=doc)
```

**Yêu cầu client hỗ trợ** — kiểm tra `clientCapabilities.sampling` trước. Gợi ý về model preference được match bằng substring (`"claude-3-5"` khớp với mọi variant Claude 3.5).

---

## Roots — truy vấn ranh giới workspace

Thay vì hardcode thư mục root, hãy hỏi host thư mục nào user đã phê duyệt.

```typescript
const caps = server.getClientCapabilities();
if (caps?.roots) {
  const { roots } = await server.server.listRoots();
  // roots: [{ uri: "file:///home/user/project", name: "My Project" }]
}
```

```python
roots = await ctx.list_roots()
```

Đặc biệt liên quan đến MCPB local server — xem `build-mcpb/references/local-security.md`.

---

## Logging — có cấu trúc, theo level

Tốt hơn stderr cho remote server. Client có thể lọc theo level.

```typescript
// Trong một tool handler
await extra.sendNotification({
  method: "notifications/message",
  params: { level: "info", logger: "my-tool", data: { msg: "Processing", count: 42 } },
});
```

```python
await ctx.info("Processing", count=42)   # cũng có: ctx.debug, ctx.warning, ctx.error
```

Level theo syslog: `debug`, `info`, `notice`, `warning`, `error`, `critical`, `alert`, `emergency`. Client đặt mức tối thiểu qua `logging/setLevel`.

---

## Progress — cho tool chạy lâu

Client gửi `progressToken` trong request `_meta`. Server emit progress notification theo token đó.

```typescript
async (args, extra) => {
  const token = extra._meta?.progressToken;
  for (let i = 0; i < 100; i++) {
    if (token !== undefined) {
      await extra.sendNotification({
        method: "notifications/progress",
        params: { progressToken: token, progress: i, total: 100, message: `Step ${i}` },
      });
    }
    await doStep(i);
  }
  return { content: [{ type: "text", text: "Done" }] };
}
```

```python
async def long_task(ctx: Context) -> str:
    for i in range(100):
        await ctx.report_progress(progress=i, total=100, message=f"Step {i}")
        await do_step(i)
    return "Done"
```

---

## Cancellation — tôn trọng abort signal

Tool chạy lâu nên kiểm tra `AbortSignal` do SDK cung cấp:

```typescript
async (args, extra) => {
  for (const item of items) {
    if (extra.signal.aborted) throw new Error("Cancelled");
    await process(item);
  }
}
```

fastmcp xử lý việc này qua asyncio cancellation — không cần kiểm tra tường minh nếu handler của bạn properly async.

---

## Completion — autocomplete cho prompt arg

Nếu bạn đã đăng ký prompt hoặc resource template có argument, bạn có thể cung cấp autocomplete:

```typescript
server.registerPrompt("query", {
  argsSchema: {
    table: completable(z.string(), async (partial) => tables.filter(t => t.startsWith(partial))),
  },
}, ...);
```

Ưu tiên thấp trừ khi prompt của bạn có nhiều giá trị hợp lệ.

---

## Capability nào cần client hỗ trợ?

| Tính năng | Server khai báo | Client phải hỗ trợ | Fallback nếu không |
|---|---|---|---|
| `instructions` | ngầm định | — | — (luôn hoạt động) |
| Logging | `logging: {}` | — | stderr |
| Progress | — | gửi `progressToken` | bỏ qua silently |
| Sampling | — | `sampling: {}` | tự mang LLM |
| Elicitation | — | `elicitation: {}` | trả text, nhờ Claude chuyển tiếp |
| Roots | — | `roots: {}` | config env var |

Kiểm tra client caps qua `server.getClientCapabilities()` (TS) hoặc `ctx.session.client_params.capabilities` (fastmcp) trước khi dùng ba cái cuối.
