# Security Policy

## Phạm vi áp dụng

Repo `dotclaude` cung cấp cấu hình `~/.claude/` cho Claude Code, bao gồm `hooks/bash-guard.py` (defense layer chặn lệnh nguy hiểm) và permission rules trong `settings.json`. Vấn đề bảo mật trong các thành phần này được xử lý ưu tiên.

## Phiên bản được hỗ trợ

| Phiên bản | Hỗ trợ bảo mật |
|---|---|
| `main` (latest commit) | Có |
| Tag releases | Không |
| Branch khác (`plugin-experiment/*`) | Không |

Mọi fix bảo mật được apply trên `main`. Người dùng pin commit cũ tự chịu trách nhiệm rebase.

## Báo cáo lỗ hổng

### Lỗ hổng nghiêm trọng (CRITICAL / HIGH)

Các vấn đề có khả năng gây RCE, command injection bypass, secret exfiltration, hoặc bypass `bash-guard.py`:

1. **KHÔNG mở public issue** — tránh exposing chi tiết trước khi fix.
2. Sử dụng [GitHub Private Vulnerability Reporting](https://github.com/MinhThang1009/dotclaude/security/advisories/new) — báo cáo riêng tư qua GitHub Security tab.
3. Hoặc liên hệ qua email maintainer (xem profile GitHub).

### Lỗ hổng mức trung bình hoặc thấp (MEDIUM / LOW)

Các vấn đề như missing edge case trong pattern matching, false positive/negative không gây bypass nghiêm trọng: mở public issue với label `security`.

## Nội dung báo cáo

Báo cáo nên bao gồm:

- **Mô tả lỗ hổng**: Pattern bypass / config flaw / etc.
- **Reproduction steps**: Câu lệnh hoặc input cụ thể trigger vấn đề.
- **Impact**: Phạm vi ảnh hưởng (đọc/ghi file gì, exfil channel nào).
- **Suggested fix** (nếu có): Pattern regex hoặc config thay đổi.
- **Phiên bản**: Commit SHA tested.

## Quy trình xử lý

1. **Acknowledgement**: Trong vòng 7 ngày.
2. **Assessment + fix development**: 7-30 ngày tùy mức nghiêm trọng.
3. **Coordinated disclosure**: Patch được merge và push trước khi disclose chi tiết.
4. **Credit**: Reporter được ghi nhận trong commit message và `CHANGELOG` (nếu reporter đồng ý).

## Phạm vi giới hạn

Repo này KHÔNG xử lý vấn đề bảo mật của:

- Claude Code core (báo về [anthropics/claude-code](https://github.com/anthropics/claude-code/security)).
- Anthropic API (báo qua <https://www.anthropic.com/responsible-disclosure-policy>).
- Third-party MCP servers, plugins, hoặc tools.
- User-side misconfiguration sau khi clone repo (vd: commit `.env` vào project).

## Defense layer hiện có

Để cộng đồng tham khảo và đánh giá:

- **`hooks/bash-guard.py`**: Pattern matching engine, chặn 8 vector — sensitive path access, raw network exfil, curl/wget data upload, pipe-to-shell, dangerous rm, force push, fork bomb, dd-to-disk.
- **`hooks/format-on-edit.sh`**: Skip prettier khi config có thể chứa executable code (`.prettierrc.js`, `package.json` plugins).
- **`settings.json` permission rules**: Read deny cho `.env`, `*.pem`, `*.key`, SSH keys, AWS credentials, etc.
- **Test suite**: 119 regression test trong `hooks/test-bash-guard.sh`.

Vector đã biết bypass (documented, không phải zero-day):

- Variable substitution động: `FILE=.env cat $FILE` — pattern matching tĩnh không expand variable.
- Custom shell built-in (rất hiếm trong context Claude Code generated).

Nếu phát hiện vector bypass mới, báo cáo theo quy trình trên.
