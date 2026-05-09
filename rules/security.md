# Quy tắc Bảo mật

> Áp dụng MỌI session. Bảo mật ưu tiên hơn tính tiện lợi.

## Secrets & credentials

- **KHÔNG** in/log secret, token, API key, password, private key. Phát hiện hardcoded secret → cảnh báo NGAY (không chờ user xác nhận).
- **KHÔNG** commit `.env`, `.env.*` (trừ `.env.example` đã sanitize), `*.key`, `*.pem`, `*.p12`, `*.jks`, `id_rsa*`, `credentials.json`.
- Trước khi commit → kiểm tra `.gitignore`. File chưa có → thêm trước.
- Mask khi hiển thị log/output: chuỗi 32+ hex, JWT (3 phần `.`-separated), AWS key (`AKIA...`), Bearer token, `Basic <base64>`.
- Phát hiện secret rò rỉ trong git history → khuyến cáo dùng `git-filter-repo` + **rotate secret ngay**, KHÔNG chỉ sửa file mới nhất.

## Validate input

- KHÔNG tin input từ user/network/file. Validate kiểu, range, format trước khi dùng.
- KHÔNG dùng input trực tiếp trong: SQL (dùng prepared statement / parameterized query), shell command (escape hoặc dùng `args` array), file path (resolve về absolute, check trong allowed dir), regex (escape special char).
- Output: HTML escape, JSON encode đúng cách. Đừng tự build string concat.

## Injection prevention

| Loại lỗ hổng      | Cách phòng                                                              |
| ----------------- | ----------------------------------------------------------------------- |
| SQL injection     | Prepared statement / ORM với binding                                    |
| Command injection | KHÔNG `eval`, KHÔNG `shell=True` ghép user input                        |
| Path traversal    | Resolve `path.resolve()`, check prefix trong allowed dir                |
| XSS               | Escape output, dùng template engine có auto-escape                      |
| SSRF              | Validate URL host, allowlist domain, deny private IP range              |
| XXE               | Tắt external entity trong XML parser                                    |
| Deserialization   | KHÔNG `pickle.loads`, `unserialize`, `Marshal.load` từ untrusted source |

## Crypto

- KHÔNG bịa thuật toán. Dùng thư viện chuẩn (`crypto`, `cryptography`, `bcrypt`, `argon2`, `libsodium`).
- Hash password: `argon2id` (ưu tiên) hoặc `bcrypt` cost ≥12. KHÔNG MD5/SHA1/SHA256 trần.
- Đối xứng: AES-GCM hoặc ChaCha20-Poly1305 với random nonce. KHÔNG ECB.
- Random: `secrets` (Python), `crypto.randomBytes` (Node), `/dev/urandom`. KHÔNG `Math.random()` cho security.
- TLS: tối thiểu 1.2, ưu tiên 1.3. Cert pinning chỉ khi cần thiết (không phải mặc định).

## Dependency

- Trước thêm dep mới → check: maintained gần đây? license OK? có CVE không? popular hay lone-wolf?
- Lock version (lockfile commit). Update có chủ đích, không auto.
- Tools: `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, Dependabot.

## Logging an toàn

- Log **request id, user id, action, result** — KHÔNG log body có PII/secret.
- Error message hiển thị cho user: tiếng Việt, generic ("Đã xảy ra lỗi, vui lòng thử lại"). Stack trace + chi tiết → log internal, KHÔNG response cho client.
- Đừng log full request/response của payment, auth, file upload.

## Auth/Authz

- Authentication ≠ Authorization. Mỗi endpoint kiểm tra cả hai.
- Session token: random ≥128 bit, HttpOnly + Secure + SameSite cookie hoặc trong header `Authorization`.
- JWT: signed (RS256/EdDSA ưu tiên hơn HS256), verify expiry + audience + issuer.
- Rate limit: login, password reset, OTP, API public.
- Default-deny: nếu không có rule explicit allow → deny.

## Lệnh nguy hiểm — KHÔNG bao giờ chạy

- `rm -rf /`, `rm -rf $VAR` (nếu `$VAR` rỗng → wipe `/`), `rm -rf ~` không có whitelist scope.
- `chmod -R 777`, `chown -R` ngoài project.
- `curl ... | bash`, `wget ... | sh` từ URL không phải vendor chính thức.
- `dd if=... of=/dev/sd*` (overwrite disk).
- `git push --force` lên branch chia sẻ (`main`, `master`, `develop`, `release/*`).
- `DROP DATABASE`, `TRUNCATE` trên DB production.

## Khi audit

Báo cáo theo format:
```text
🔴 CRITICAL — RCE/SQLi/auth bypass/secret leak (CVSS ≥9)
🟠 HIGH      — XSS/SSRF/IDOR/crypto sai (CVSS 7-8.9)
🟡 MEDIUM    — info disclosure/missing rate limit (CVSS 4-6.9)
🟢 LOW       — best practice deviation (CVSS <4)
ℹ️ INFO      — gợi ý hardening
```
Mỗi finding: vị trí (`file:line`), mô tả ngắn, cách fix cụ thể, CWE ID nếu biết.
