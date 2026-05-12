# Auth cho MCP Servers

Auth là lý do hầu hết mọi người cuối cùng phải dùng server **remote** ngay cả khi server local đơn giản hơn. OAuth redirect, lưu trữ token, và refresh token đều hoạt động gọn gàng khi có một endpoint được host thực sự để redirect về.

## Xác thực dành riêng cho Claude

MCP client của Claude hỗ trợ một tập auth type cụ thể — không phải mọi flow tuân thủ spec đều hoạt động. Tham chiếu đầy đủ: https://claude.com/docs/connectors/building/authentication

| Type | Ghi chú |
|---|---|
| `oauth_dcr` | Được hỗ trợ. Với các directory entry có lưu lượng lớn, ưu tiên dùng CIMD hoặc Anthropic-held creds — DCR đăng ký một client mới mỗi lần kết nối mới. |
| `oauth_cimd` | Được hỗ trợ, khuyến nghị dùng thay DCR cho directory entry. |
| `oauth_anthropic_creds` | Partner cung cấp `client_id`/`client_secret` cho Anthropic; yêu cầu sự đồng ý của user. Liên hệ `mcp-review@anthropic.com`. |
| `custom_connection` | User cung cấp URL/creds lúc kết nối (theo kiểu Snowflake). Liên hệ `mcp-review@anthropic.com`. |
| `none` | Không xác thực. |

**Không được hỗ trợ:** bearer token do user dán vào (`static_bearer`); grant `client_credentials` thuần machine-to-machine không có sự đồng ý của user.

**Callback URL** (duy nhất, tất cả các bề mặt): `https://claude.ai/api/mcp/auth_callback`

---

## Ba tầng

### Tầng 1: Không auth / static API key

Server đọc key từ env. User cung cấp một lần lúc setup. Xong.

```typescript
const apiKey = process.env.UPSTREAM_API_KEY;
if (!apiKey) throw new Error("UPSTREAM_API_KEY not set");
```

Hoạt động với local stdio, MCPB, và remote server như nhau. Nếu đây là tất cả những gì bạn cần, dừng ở đây.

### Tầng 2: OAuth 2.0 qua CIMD (ưu tiên theo spec 2025-11-25)

**Client ID Metadata Document.** MCP host công bố client metadata của mình tại một HTTPS URL và dùng URL đó *làm* `client_id`. Authorization server của bạn fetch document đó, validate nó, và tiến hành auth-code flow. Không có registration endpoint, không có client record được lưu.

Spec 2025-11-25 đã nâng CIMD lên SHOULD (ưu tiên). Quảng bá hỗ trợ qua `client_id_metadata_document_supported: true` trong OAuth AS metadata của bạn.

**Trách nhiệm của server:**

1. Phục vụ OAuth Authorization Server Metadata (RFC 8414) tại `/.well-known/oauth-authorization-server` với `client_id_metadata_document_supported: true`
2. Phục vụ một MCP protected-resource metadata document trỏ tới (1)
3. Khi authorize: fetch `client_id` như một HTTPS URL, validate client metadata trả về, tiếp tục
4. Validate bearer token trên các request `/mcp` đến

```
┌─────────┐  client_id=https://...  ┌──────────────┐   upstream OAuth   ┌──────────┐
│ MCP host│ ──────────────────────> │ Your MCP srv │ ─────────────────> │ Upstream │
└─────────┘ <─── bearer token ───── └──────────────┘ <── access token ──└──────────┘
```

### Tầng 3: OAuth 2.0 qua Dynamic Client Registration (DCR)

**Fallback tương thích ngược** — spec 2025-11-25 đã hạ DCR xuống MAY. Host tìm `registration_endpoint` của bạn, POST metadata của nó để tự đăng ký làm client, nhận `client_id`, sau đó chạy auth-code flow.

Triển khai DCR nếu bạn cần hỗ trợ các host chưa chuyển sang CIMD. Trách nhiệm server giống như CIMD, nhưng thay vì fetch URL `client_id` bạn chạy một registration endpoint lưu trữ client record.

**Thứ tự ưu tiên của client:** pre-registered → CIMD (nếu AS quảng bá `client_id_metadata_document_supported`) → DCR (nếu AS có `registration_endpoint`) → hỏi user.

---

## Các nhà cung cấp hosting tích hợp sẵn DCR/CIMD

Một số nhà cung cấp hosting tập trung vào MCP xử lý OAuth plumbing cho bạn — bạn chỉ implement logic của tool, họ chạy authorization server. Xem docs của họ để biết khả năng hiện tại. Nếu user không có yêu cầu hosting cụ thể, đây thường là con đường nhanh nhất để có một OAuth-protected server hoạt động.

---

## Server local và OAuth

Server local stdio **có thể** dùng OAuth (mở browser, bắt redirect trên một localhost port, lưu token vào OS keychain). Nhưng cách này hay bị lỗi:

- Bị lỗi trong môi trường headless/remote
- Mỗi user phải lặp lại toàn bộ quy trình
- Không có token refresh hoặc revocation tập trung

Nếu OAuth là bắt buộc, hãy nghiêng mạnh về phía remote HTTP. Nếu bạn *buộc phải* ship local + OAuth, `@modelcontextprotocol/sdk` có sẵn localhost-redirect helper, và MCPB là đúng packaging để ít nhất runtime có thể dự đoán được.

---

## Lưu trữ token

| Deployment | Lưu token ở |
|---|---|
| Remote, stateless | Không lưu — host gửi bearer theo từng request |
| Remote, stateful | Session store theo MCP session ID (Redis, v.v.) |
| MCPB / local | OS keychain (`keytar` trên Node, `keyring` trên Python). **Không bao giờ lưu plaintext trên disk.** |

---

## Validate token audience (MUST theo spec)

Validate "đây có phải bearer token hợp lệ không" là chưa đủ. Spec yêu cầu validate "token này có được phát hành *cho server này* không" — RFC 8707 audience. Token được phát hành cho `api.other-service.com` phải bị từ chối dù chữ ký hợp lệ.

**Token passthrough bị cấm tuyệt đối.** Không nhận token rồi chuyển tiếp nó upstream. Nếu server của bạn cần gọi một service khác, hãy exchange token hoặc dùng credential riêng của nó.

---

## SDK helpers — đừng tự viết lại

`@modelcontextprotocol/sdk/server/auth` cung cấp:
- `mcpAuthRouter()` — Express router cho toàn bộ OAuth AS surface (metadata, authorize, token)
- `bearerAuth` — middleware validate bearer token đối chiếu với verifier của bạn
- `proxyProvider` — chuyển tiếp auth tới upstream IdP

Nếu bạn đang tự nối auth từ đầu, hãy kiểm tra những thứ này trước.
