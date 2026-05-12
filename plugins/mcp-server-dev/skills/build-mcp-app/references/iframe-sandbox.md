# Các ràng buộc của iframe sandbox

Widget MCP app chạy bên trong `<iframe>` có sandbox trong host (Claude Desktop, claude.ai). Các thuộc tính sandbox và CSP khóa chặt những gì widget có thể làm. Mỗi mục dưới đây được quan sát thấy thất bại với một iframe trắng im lặng cho đến khi áp dụng bản sửa — lỗi chỉ xuất hiện trong console devtools của chính iframe, không phải của host.

---

## Bảng triệu chứng → giải pháp

| Triệu chứng | Nguyên nhân gốc | Giải pháp |
|---|---|---|
| Widget render thành hình chữ nhật trắng, không có lỗi | CSP `script-src` chặn esm.sh fetch transitive deps `@modelcontextprotocol/sdk` | Inline bundle `ext-apps/app-with-deps` vào HTML |
| `window.open()` không làm gì | Sandbox thiếu `allow-popups` | Dùng `app.openLink({ url })` |
| `<a target="_blank">` không làm gì | Như trên | `e.preventDefault()` + `app.openLink({ url })` khi click |
| `<img src>` ngoài bị lỗi | CSP `img-src` + chặn hotlink của CDN | Fetch phía server, gửi dưới dạng `data:` URL trong payload kết quả tool |
| Sửa widget không xuất hiện sau khi restart server | Host cache UI resource | Thoát hoàn toàn host (⌘Q / Alt+F4) và khởi động lại |
| Top-level `await` throw | Các iframe context cũ hơn | Bọc body module trong một async IIFE |

---

## Inline bundle ext-apps

`@modelcontextprotocol/ext-apps` ship một browser build tự cung cấp đủ tại export `app-with-deps` (~300KB). Đây là ESM đã minify kết thúc bằng `export{…}`; để dùng từ một block `<script type="module">` inline, viết lại câu lệnh export thành một phép gán global lúc build:

```ts
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);

const bundle = readFileSync(
  require.resolve("@modelcontextprotocol/ext-apps/app-with-deps"),
  "utf8",
).replace(/export\{([^}]+)\};?\s*$/, (_, body) =>
  "globalThis.ExtApps={" +
  body.split(",").map((pair) => {
    const [local, exported] = pair.split(" as ").map((s) => s.trim());
    return `${exported ?? local}:${local}`;
  }).join(",") + "};",
);

const widgetHtml = readFileSync("./widgets/widget.html", "utf8")
  .replace("/*__EXT_APPS_BUNDLE__*/", () => bundle);
```

Phía widget:

```html
<script type="module">
/*__EXT_APPS_BUNDLE__*/
const { App } = globalThis.ExtApps;
(async () => {
  const app = new App({ name: "…", version: "…" }, {});
  // …
})();
</script>
```

Dạng replacer `() => bundle` (thay vì chuỗi thuần) quan trọng — `String.replace` diễn giải các chuỗi `$…` trong string replacement, và bundle đã minify đầy rẫy chúng.

---

## Link ra ngoài

```js
// ✗ bị chặn
window.open(url, "_blank");
// ✗ bị chặn
<a href="…" target="_blank">…</a>

// ✓ thông qua host
await app.openLink({ url });
```

Chặn click anchor:

```js
el.addEventListener("click", (e) => {
  e.preventDefault();
  app.openLink({ url: el.href });
});
```

---

## Ảnh từ bên ngoài

CSP `img-src` mặc định (cộng với nhiều referrer policy của CDN) chặn `<img src="https://external-cdn/…">` không load được. Inline chúng phía server trong tool handler:

```ts
async function toDataUrl(url: string): Promise<string | undefined> {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return undefined;
    const buf = Buffer.from(await res.arrayBuffer());
    const mime = res.headers.get("content-type") ?? "image/jpeg";
    return `data:${mime};base64,${buf.toString("base64")}`;
  } catch {
    return undefined;
  }
}

// trong tool handler
const inlined = await Promise.all(
  items.map(async (it) =>
    it.thumb ? { ...it, thumb: await toDataUrl(it.thumb) ?? it.thumb } : it,
  ),
);
```

Thêm `referrerpolicy="no-referrer"` trên `<img>` như một fallback cho URL nào vẫn còn un-inlined.

---

## Theme & host styles

Host render iframe bên trong card chrome của riêng nó — paint nền **transparent** và áp dụng CSS token của host để widget hòa vào trong cả light/dark và qua các host khác nhau.

```html
<meta name="color-scheme" content="light dark" />
```

```css
:root {
  --ink:  var(--color-text-primary,   #0f1111);
  --sub:  var(--color-text-secondary, #5a6270);
  --line: var(--color-border-default, #e3e6ea);
}
html, body { background: transparent; color: var(--ink); }
:root.dark .thumb { mix-blend-mode: normal; } /* multiply → images vanish in dark */
```

```js
const { App, applyHostStyleVariables } = globalThis.ExtApps;

function applyHostContext(ctx) {
  document.documentElement.classList.toggle("dark", ctx?.theme === "dark");
  if (ctx?.styles?.variables) applyHostStyleVariables(ctx.styles.variables);
}
app.onhostcontextchanged = applyHostContext;
await app.connect();
applyHostContext(app.getHostContext());
```

`applyHostStyleVariables` ghi các token `--color-*` / `--font-*` / `--border-radius-*` của host lên `:root`; các giá trị hex ở trên là fallback cho host không cung cấp chúng.

---

## Debug

Iframe có console riêng. Trong Claude Desktop, mở DevTools (View → Toggle Developer Tools), rồi chuyển dropdown context (góc trên trái của tab Console) từ "top" sang iframe của widget. Vi phạm CSP, exception chưa bắt, và lỗi import đều hiển thị ở đó — console chính của host im lặng.
