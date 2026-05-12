# Quản lý ngân sách payload

Host giới hạn text của kết quả tool. claude.ai và Claude Desktop truncate ở khoảng **150.000 ký tự**; Claude Code ở ~25k token. Khi kết quả tool vượt giới hạn, host thay thế bằng một chuỗi file-pointer thay cho JSON của bạn. Widget sau đó nhận non-JSON trong `ontoolresult`, `JSON.parse` throw, và người dùng thấy thứ gì đó như *"Bad payload: SyntaxError: Unexpected token 'E'"* — không có gợi ý nào cho thấy kích thước là nguyên nhân.

## Triệu chứng → nguyên nhân

| Triệu chứng | Nguyên nhân có thể |
|---|---|
| Widget hiện lỗi JSON parse trên `content[0].text` | Kết quả vượt giới hạn host; host đã thay bằng chuỗi file-pointer |
| Hoạt động với một query, lỗi với "tất cả X" | Số hàng × số cột đã vượt giới hạn |
| Hoạt động trong MCP Inspector, lỗi trong Desktop | Inspector không có giới hạn; Desktop thì có |

## Chiến lược

Giới hạn payload của bạn ở ~130KB và degrade theo thứ tự:

1. **Gửi đầy đủ hàng** khi `JSON.stringify(rows).length` dưới giới hạn.
2. **Cắt bỏ cột** chỉ giữ những cột mà rendering spec thực sự tham chiếu. Duyệt spec cho cả key `field: "..."` *và* `datum.X` / `datum['X']` bên trong chuỗi expression — nếu spec alias một cột qua transform `calculate`, alias xuất hiện dưới dạng `field:` nhưng cột nguồn chỉ xuất hiện dưới dạng `datum.X`, và việc bỏ nó đi sẽ để widget với NaN.
3. **Truncate hàng** như biện pháp cuối cùng và thêm `{ truncated: N }` vào payload để widget có thể ghi nhãn.

```ts
const MAX = 130_000;
let out = rows;
if (JSON.stringify(out).length > MAX) {
  const keep = referencedFields(spec); // field: + datum.X refs
  out = rows.map((r) => pick(r, keep));
  if (JSON.stringify(out).length > MAX) {
    const per = JSON.stringify(out[0] ?? {}).length || 1;
    out = out.slice(0, Math.floor(MAX / per));
  }
}
```

## Asset nặng đi qua `callServerTool`, không phải trong kết quả

Geometry, image byte, hoặc bất kỳ blob nào widget cần nhưng Claude không cần nên được phục vụ bởi một tool riêng mà widget gọi sau khi mount:

```js
const topo = await app.callServerTool({ name: "get-topojson", arguments: { level } });
```

Đánh dấu tool helper đó với `_meta.ui.visibility: ["app"]` để nó không xuất hiện trong danh sách tool của Claude.
