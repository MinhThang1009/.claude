# ext-apps messaging — widget ↔ host ↔ server

Package `@modelcontextprotocol/ext-apps` cung cấp class `App` (phía browser) và các helper `registerAppTool`/`registerAppResource` (phía server). Messaging là hai chiều và persistent.

## Khởi tạo

```js
const app = new App(
  { name: "MyWidget", version: "1.0.0" },
  {},                       // capabilities
  { autoResize: true },     // options
);
```

`autoResize: true` kết nối một `ResizeObserver` phát ra `ui/notifications/size-changed` để chiều cao iframe của host bám theo nội dung đã render. Nếu không thiết lập, frame sẽ có chiều cao cố định và các render cao sẽ bị cắt bớt — hãy bật khi widget có chiều cao phụ thuộc vào dữ liệu.

---

## Widget → Host

### `app.sendMessage({ role, content })`

Inject một message hiển thị vào cuộc hội thoại. Đây là cách hành động của người dùng trở thành lượt conversation.

```js
app.sendMessage({
  role: "user",
  content: [{ type: "text", text: "User selected order #1234" }],
});
```

Message xuất hiện trong chat và Claude phản hồi lại. Dùng `role: "user"` — widget nói thay mặt người dùng.

### `app.updateModelContext({ content })`

Cập nhật context của Claude **không hiển thị** — không có chat bubble. Dùng cho trạng thái cần thông báo cho Claude nhưng không đáng xuất hiện thành bubble.

```js
app.updateModelContext({
  content: [{ type: "text", text: "Currently viewing: orders from last 30 days" }],
});
```

### `app.callServerTool({ name, arguments })`

Gọi trực tiếp một tool trên MCP server, bỏ qua Claude. Trả về kết quả của tool.

```js
const result = await app.callServerTool({
  name: "fetch_order_details",
  arguments: { orderId: "1234" },
});
```

Dùng cho các lần fetch dữ liệu không cần reasoning của Claude — phân trang, tra cứu chi tiết, refresh.

### `app.openLink({ url })`

Mở một URL trong tab browser mới, thông qua host. **Bắt buộc** cho mọi điều hướng ra ngoài — sandbox iframe chặn `window.open()` và `<a target="_blank">`.

```js
await app.openLink({ url: "https://example.com/cart" });
```

Với các anchor trong HTML đã render, chặn click:

```js
card.querySelector("a").addEventListener("click", (e) => {
  e.preventDefault();
  app.openLink({ url: e.currentTarget.href });
});
```

### `app.downloadFile({ name, mimeType, content })`

Download thông qua host (sandbox chặn `<a download>` trực tiếp). `content` là chuỗi base64.

```js
const csv = rows.map((r) => Object.values(r).join(",")).join("\n");
app.downloadFile({
  name: "export.csv",
  mimeType: "text/csv",
  content: btoa(unescape(encodeURIComponent(csv))),
});
```

### `app.requestDisplayMode({ mode })`

Yêu cầu host chuyển widget giữa `"inline"`, `"pip"`, hoặc `"fullscreen"`. Kiểm tra `getHostContext().availableDisplayModes` trước; ẩn control nếu mode không được cung cấp. Host phản hồi bằng cách bắn `onhostcontextchanged` với `displayMode` và `containerDimensions` mới — re-render ở kích thước mới.

```js
if (app.getHostContext()?.availableDisplayModes?.includes("fullscreen")) {
  expandBtn.hidden = false;
  expandBtn.onclick = () => app.requestDisplayMode({ mode: "fullscreen" });
}
```

---

## Host → Widget

### `app.ontoolresult = ({ content }) => {...}`

Bắn khi giá trị trả về của tool handler được pipe tới widget. Đây là đường dẫn dữ liệu vào chính.

```js
app.ontoolresult = ({ content }) => {
  const data = JSON.parse(content[0].text);
  renderUI(data);
};
```

**Thiết lập TRƯỚC `await app.connect()`** — kết quả có thể đến ngay sau khi kết nối.

### `app.ontoolinput = ({ arguments }) => {...}`

Bắn với các arguments mà Claude đã truyền vào tool. Hữu ích nếu widget cần biết những gì đã được yêu cầu (ví dụ: highlight từ khóa tìm kiếm).

### `app.ontoolinputpartial = ({ arguments }) => {...}` / `app.ontoolcancelled = () => {...}`

`ontoolinputpartial` bắn trong khi Claude vẫn đang stream arguments — dùng để hiển thị skeleton ("Đang chuẩn bị: <title>…") trước khi kết quả đến. `ontoolcancelled` bắn nếu cuộc gọi bị hủy; xóa skeleton.

### `app.getHostContext()` / `app.onhostcontextchanged = (ctx) => {...}`

Đọc và subscribe vào host context. Gọi `getHostContext()` **sau** `connect()`. Subscribe để nhận cập nhật trực tiếp (người dùng bật dark mode, mở rộng sang fullscreen).

| Trường `ctx.` | Cách dùng |
|---|---|
| `theme` | `"light"` / `"dark"` — toggle class `.dark` |
| `styles.variables` | CSS token của host — truyền vào `applyHostStyleVariables()` để màu sắc/font khớp với chrome của host |
| `displayMode` / `availableDisplayModes` | Mode hiện tại và các target `requestDisplayMode` hợp lệ |
| `containerDimensions.{maxHeight,width}` | Điều chỉnh render theo kích thước này thay vì hard-code px |
| `deviceCapabilities.touch` | Chuyển affordance chỉ dùng hover sang tap (`pointerdown`) |
| `safeAreaInsets` | Padding cho notch / composer overlay |

```js
const applyTheme = (t) =>
  document.documentElement.classList.toggle("dark", t === "dark");

app.onhostcontextchanged = (ctx) => applyTheme(ctx.theme);
await app.connect();
applyTheme(app.getHostContext()?.theme);
```

Giữ màu sắc trong CSS custom props với block override `:root.dark {}` và đặt `color-scheme: light | dark` để các form control native đi theo.

---

## Server → Widget (progress)

Với các thao tác chạy lâu, emit progress notification. Client gửi `progressToken` trong `_meta` của request; server emit dựa vào đó.

```typescript
// Trong tool handler
async ({ query }, extra) => {
  const token = extra._meta?.progressToken;
  for (let i = 0; i < steps.length; i++) {
    if (token !== undefined) {
      await extra.sendNotification({
        method: "notifications/progress",
        params: { progressToken: token, progress: i, total: steps.length, message: steps[i].name },
      });
    }
    await steps[i].run();
  }
  return { content: [{ type: "text", text: "Complete" }] };
}
```

Không destructure `{ notify }` — `extra` là `RequestHandlerExtra`; progress đi qua `sendNotification`.

---

## Lifecycle

1. Claude gọi một tool với `_meta.ui.resourceUri` được khai báo
2. Host fetch resource (HTML của bạn) và mount một **iframe mới** cho lần gọi này
3. Script widget chạy, thiết lập handler, gọi `await app.connect()`
4. Host pipe giá trị trả về của tool → `ontoolresult` bắn
5. Widget render, người dùng tương tác
6. Widget gọi `sendMessage` / `updateModelContext` / `callServerTool` khi cần
7. Iframe tồn tại trong transcript; **lần gọi tiếp theo tới cùng tool sẽ mount thêm một iframe** bên cạnh nó

Không có "submit và đóng" rõ ràng — mỗi instance tồn tại lâu dài, nhưng instance không được tái sử dụng giữa các lần gọi.

### Supersession

Vì các instance trước vẫn được mount, một click vào widget cũ có thể `sendMessage` sau khi một widget mới hơn đã render. Phát hiện điều này bằng `BroadcastChannel` và làm các instance cũ không hoạt động:

```js
let superseded = false;
const seq = Date.now() + Math.random();
const bc = new BroadcastChannel("my-widget");
bc.onmessage = (e) => {
  if (e.data?.seq > seq) {
    superseded = true;
    document.body.classList.add("superseded"); // opacity:.45; pointer-events:none
  }
};
bc.postMessage({ seq });

// Bảo vệ các lần gọi ra ngoài:
function safeSend(msg) {
  if (!superseded) app.sendMessage(msg);
}
```

---

## Các vấn đề Sandbox & CSP

Iframe chạy dưới cả thuộc tính HTML `sandbox` **lẫn** Content-Security-Policy hạn chế. Hệ quả thực tế là hầu như không có gì từ bên ngoài được phép — widget nên tự cung cấp đủ.

| Triệu chứng | Nguyên nhân | Giải pháp |
|---|---|---|
| Widget là hình chữ nhật trắng, không render gì | CDN `import` của ext-apps bị chặn (SDK fetch transitive) | **Inline** bundle `ext-apps/app-with-deps` — xem `iframe-sandbox.md` |
| Widget render nhưng JS không chạy | Inline event handler bị chặn | Dùng `addEventListener` — không bao giờ dùng `onclick="..."` trong HTML |
| Lỗi `eval` / `new Function` | Hạn chế script-src | Không dùng chúng; dùng JSON.parse cho dữ liệu |
| `fetch()` tới API thất bại | Cross-origin bị chặn | Route qua `app.callServerTool()` thay thế |
| CSS bên ngoài không load | Hạn chế `style-src` | Inline style trong tag `<style>` |
| Font không load | Hạn chế `font-src` | Dùng system font (`font: 14px system-ui`) |
| `<img src>` ngoài bị lỗi | CSP `img-src` + chặn hotlink của CDN | Fetch phía server, inline dưới dạng `data:` URL trong payload kết quả tool |
| `window.open()` không làm gì | Sandbox thiếu `allow-popups` | Dùng `app.openLink({url})` |
| `<a target="_blank">` không làm gì | Như trên | Chặn click → `preventDefault()` → `app.openLink` |
| HTML đã sửa không xuất hiện trong Desktop | Desktop cache UI resource | Thoát hoàn toàn (⌘Q) + khởi động lại, không chỉ đóng cửa sổ |

Khi không chắc, mở console devtools **của chính iframe** (không phải của app chính) — vi phạm CSP log ở đó. Xem `iframe-sandbox.md` để biết pattern bundle inlining.
