# Bảo vệ khỏi lạm dụng cho server không có xác thực

Một StreamableHTTP server không có xác thực có thể bị truy cập bởi bất kỳ ai trên internet.
Có ba tài nguyên cần bảo vệ: tài nguyên tính toán của bạn, hạn mức API upstream mà
các tool của bạn sử dụng, và băng thông egress cho các payload `callServerTool` lớn.

## Bạn không có danh tính per-user

Trong chế độ không xác thực, không có token và transport không trạng thái nên không có
session ID. Traffic từ claude.ai được proxy qua egress của Anthropic — mọi người dùng web
đều đến từ cùng một tập IP nhỏ:

```
160.79.104.0/21
2607:6bc0::/48
```

(Xem https://platform.claude.com/docs/en/api/ip-addresses.)

Claude Desktop, Claude Code, và các host khác kết nối **trực tiếp từ máy của
người dùng**, nên những client đó *có* IP riêng biệt per-user. Do đó, giới hạn per-IP
hoạt động với direct-connect clients; với claude.ai bạn chỉ có thể giới hạn
pool Anthropic chung. Nếu cần giới hạn thực sự per-user, đó là lý do để thêm OAuth.

## Token-bucket theo tầng (backstop per-replica)

```ts
const ANTHROPIC_CIDRS = ["160.79.104.0/21", "2607:6bc0::/48"];
const TIERS = {
  anthropic: { capacity: 600, refillPerSec: 100 }, // shared pool
  other:     { capacity: 30,  refillPerSec: 2   }, // per-IP
};
```

So khớp `req.ip` với các CIDR, chọn bucket (`"anthropic"` hoặc
`"ip:<addr>"`), trả 429 + `Retry-After` khi cạn kiệt. Đây là backstop per-replica —
enforcement xuyên replica thuộc về edge (Cloudflare, Cloud
Armor), giúp các container giữ trạng thái stateless.

## `trust proxy` phải khớp với topology của bạn

`req.ip` chỉ tuân theo `X-Forwarded-For` nếu `app.set('trust proxy', N)` được
thiết lập. `true` tin tưởng mọi hop, điều này cho phép client trực tiếp gửi
`X-Forwarded-For: 160.79.108.42` và giả mạo tầng Anthropic. Đặt giá trị chính xác bằng số hop
đáng tin cậy (ví dụ: `1` sau một LB duy nhất, `2` sau Cloudflare → origin LB) và **không bao giờ dùng `true` trong production**.

## Hard-allowlist IP Anthropic là quyết định sản phẩm

Chặn tất cả ngoài `160.79.104.0/21` sẽ loại Desktop, Claude Code,
và mọi MCP host khác. Dùng các CIDR để **phân tầng** rate limit, không phải để chặn
truy cập, trừ khi chỉ phục vụ claude.ai là mục tiêu rõ ràng.

## Cache response upstream

Với các tool bọc API bên thứ ba, một LRU in-process keyed trên query đã chuẩn hóa (TTL tính theo giờ,
không có secret trong key) là biện pháp kiểm soát chi phí chính — các query lặp lại trở nên
miễn phí và hấp thụ thundering-herd. Rate limit là lưới an toàn, không phải tuyến đầu.
