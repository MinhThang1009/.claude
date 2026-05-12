# Widget Templates

Các scaffold HTML tối giản cho các dạng widget phổ biến. Copy, điền vào, ship.

Tất cả template đều inline class `App` từ `@modelcontextprotocol/ext-apps` lúc build time — CSP của iframe chặn import script từ CDN. Chúng cố ý không dùng framework; widget đủ nhỏ để chi phí hydration của React/Vue thường không đáng.

---

## Phục vụ widget HTML

Widget là HTML tĩnh với một placeholder: `/*__EXT_APPS_BUNDLE__*/` được thay thế lúc server khởi động bằng bundle `ext-apps/app-with-deps` (được viết lại để expose `globalThis.ExtApps`).

```typescript
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { registerAppResource, RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";

const require = createRequire(import.meta.url);

const bundle = readFileSync(
  require.resolve("@modelcontextprotocol/ext-apps/app-with-deps"), "utf8",
).replace(/export\{([^}]+)\};?\s*$/, (_, body) =>
  "globalThis.ExtApps={" +
  body.split(",").map((p) => {
    const [local, exported] = p.split(" as ").map((s) => s.trim());
    return `${exported ?? local}:${local}`;
  }).join(",") + "};",
);

const pickerHtml = readFileSync("./widgets/picker.html", "utf8")
  .replace("/*__EXT_APPS_BUNDLE__*/", () => bundle);

registerAppResource(server, "Picker", "ui://widgets/picker.html", {},
  async () => ({
    contents: [{ uri: "ui://widgets/picker.html", mimeType: RESOURCE_MIME_TYPE, text: pickerHtml }],
  }),
);
```

Bundle một lần mỗi lần server khởi động (hoặc lúc build time); tái sử dụng chuỗi `bundle` qua tất cả widget template.

---

## Picker (danh sách chọn một)

```html
<!doctype html>
<meta charset="utf-8" />
<style>
  body { font: 14px system-ui; margin: 0; }
  ul { list-style: none; padding: 0; margin: 0; max-height: 280px; overflow-y: auto; }
  li { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #eee; }
  li:hover { background: #f5f5f5; }
  .sub { color: #666; font-size: 12px; }
</style>
<ul id="list"></ul>
<script type="module">
/*__EXT_APPS_BUNDLE__*/
const { App } = globalThis.ExtApps;
(async () => {
  const app = new App({ name: "Picker", version: "1.0.0" }, {});
  const ul = document.getElementById("list");

  app.ontoolresult = ({ content }) => {
    const { items } = JSON.parse(content[0].text);
    ul.innerHTML = "";
    for (const it of items) {
      const li = document.createElement("li");
      li.innerHTML = `<div>${it.label}</div><div class="sub">${it.sub ?? ""}</div>`;
      li.addEventListener("click", () => {
        app.sendMessage({
          role: "user",
          content: [{ type: "text", text: `Đã chọn: ${it.id}` }],
        });
      });
      ul.append(li);
    }
  };

  await app.connect();
})();
</script>
```

**Tool trả về:** `{ content: [{ type: "text", text: JSON.stringify({ items: [{ id, label, sub? }] }) }] }`

---

## Confirm dialog

```html
<!doctype html>
<meta charset="utf-8" />
<style>
  body { font: 14px system-ui; margin: 16px; }
  .actions { display: flex; gap: 8px; margin-top: 16px; }
  button { padding: 8px 16px; cursor: pointer; }
  .danger { background: #d33; color: white; border: none; }
</style>
<p id="msg"></p>
<div class="actions">
  <button id="cancel">Hủy</button>
  <button id="confirm" class="danger">Xác nhận</button>
</div>
<script type="module">
/*__EXT_APPS_BUNDLE__*/
const { App } = globalThis.ExtApps;
(async () => {
  const app = new App({ name: "Confirm", version: "1.0.0" }, {});

  app.ontoolresult = ({ content }) => {
    const { message, confirmLabel } = JSON.parse(content[0].text);
    document.getElementById("msg").textContent = message;
    if (confirmLabel) document.getElementById("confirm").textContent = confirmLabel;
  };

  await app.connect();

  document.getElementById("confirm").addEventListener("click", () => {
    app.sendMessage({ role: "user", content: [{ type: "text", text: "Đã xác nhận." }] });
  });
  document.getElementById("cancel").addEventListener("click", () => {
    app.sendMessage({ role: "user", content: [{ type: "text", text: "Đã hủy." }] });
  });
})();
</script>
```

**Tool trả về:** `{ content: [{ type: "text", text: JSON.stringify({ message, confirmLabel? }) }] }`

**Lưu ý:** Với xác nhận đơn giản, ưu tiên **elicitation** thay vì widget — xem `../build-mcp-server/references/elicitation.md`. Dùng widget này khi cần style tùy chỉnh hoặc context vượt quá những gì native form cung cấp.

---

## Progress (thao tác chạy lâu)

```html
<!doctype html>
<meta charset="utf-8" />
<style>
  body { font: 14px system-ui; margin: 16px; }
  .bar { height: 8px; background: #eee; border-radius: 4px; overflow: hidden; }
  .fill { height: 100%; background: #2a7; transition: width 200ms; }
</style>
<p id="label">Đang bắt đầu…</p>
<div class="bar"><div id="fill" class="fill" style="width:0%"></div></div>
<script type="module">
/*__EXT_APPS_BUNDLE__*/
const { App } = globalThis.ExtApps;
(async () => {
  const app = new App({ name: "Progress", version: "1.0.0" }, {});
  const label = document.getElementById("label");
  const fill = document.getElementById("fill");

  // Kết quả tool bắn khi công việc hoàn thành — cập nhật trung gian
  // đến qua cùng handler nếu server stream chúng
  app.ontoolresult = ({ content }) => {
    const state = JSON.parse(content[0].text);
    if (state.progress !== undefined) {
      label.textContent = state.message ?? `${state.progress}/${state.total}`;
      fill.style.width = `${(state.progress / state.total) * 100}%`;
    }
    if (state.done) {
      label.textContent = "Hoàn thành";
      fill.style.width = "100%";
    }
  };

  await app.connect();
})();
</script>
```

Phía server, emit progress qua `extra.sendNotification({ method: "notifications/progress", ... })` — xem `apps-sdk-messages.md`.

---

## Display-only (chart / preview)

Widget display không gọi `sendMessage` — chúng render và ở đó. Tool nên trả về một text summary **kèm** widget để Claude tiếp tục reasoning trong khi người dùng thấy phần visual:

```typescript
registerAppTool(server, "show_chart", {
  description: "Render biểu đồ doanh thu",
  inputSchema: { range: z.enum(["week", "month", "year"]) },
  _meta: { ui: { resourceUri: "ui://widgets/chart.html" } },
}, async ({ range }) => {
  const data = await fetchRevenue(range);
  return {
    content: [{
      type: "text",
      text: `Doanh thu tăng ${data.change}% trong ${range}. Đã render biểu đồ.\n\n` +
            JSON.stringify(data.points),
    }],
  };
});
```

```html
<!doctype html>
<meta charset="utf-8" />
<style>body { font: 14px system-ui; margin: 12px; }</style>
<canvas id="chart" width="400" height="200"></canvas>
<script type="module">
/*__EXT_APPS_BUNDLE__*/
const { App } = globalThis.ExtApps;
(async () => {
  const app = new App({ name: "Chart", version: "1.0.0" }, {});

  app.ontoolresult = ({ content }) => {
    // Parse các điểm JSON từ text content (sau dòng summary)
    const text = content[0].text;
    const jsonStart = text.indexOf("\n\n") + 2;
    const points = JSON.parse(text.slice(jsonStart));
    drawChart(document.getElementById("chart"), points);
  };

  await app.connect();

  function drawChart(canvas, points) { /* ... */ }
})();
</script>
```

---

## Carousel (hiển thị nhiều item với action)

Dùng để trình bày nhiều item (gợi ý sản phẩm, kết quả tìm kiếm) trong một horizontal scroll rail. Các pattern thử nghiệm tốt:

- **Bỏ chevron điều hướng** — người dùng biết cách scroll. `scroll-snap-type` có thể gây render lệch vài px ban đầu; bỏ đi và `scrollLeft = 0` sau khi render.
- **Fork layout theo số lượng item** — `items.length === 1` → layout detail/PDP, `> 1` → carousel. Xử lý trong widget JS, giữ tool schema phẳng.
- **Đặt reasoning của Claude vào mỗi item** — một trường `note` render thành callout nhỏ trên card cho người dùng thấy "tại sao" ngay trong card.
- **Trạng thái im lặng qua `updateModelContext`** — thay đổi cart/selection nên thông báo cho Claude mà không spam chat. Chỉ dùng `sendMessage` cho action kết thúc ("checkout", "done").
- **Link ra ngoài qua `app.openLink`** — `window.open` và `<a target="_blank">` bị sandbox chặn.

```html
<style>
  .rail { display: flex; gap: 10px; overflow-x: auto; padding: 12px; scrollbar-width: none; }
  .rail::-webkit-scrollbar { display: none; }
  .card { flex: 0 0 220px; border: 1px solid #ddd; border-radius: 6px; padding: 10px; }
  .thumb-box { aspect-ratio: 1 / 1; display: grid; place-items: center; background: #f7f8f8; }
  .thumb { max-width: 100%; max-height: 100%; object-fit: contain; }
  .note { font-size: 12px; color: #666; border-left: 3px solid orange; padding: 2px 8px; margin: 8px 0; }
</style>
<div class="rail" id="rail"></div>
```

**Ảnh:** CSP của iframe chặn remote `img-src`. Fetch thumbnail phía server trong tool handler, nhúng dưới dạng `data:` URL trong JSON payload, và render từ đó. Thêm `referrerpolicy="no-referrer"` như fallback.
