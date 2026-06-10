---
name: quick-audit
description: "This skill should be used when the user asks for a quick security audit of 1-5 files or one module ('quick audit', 'audit nhanh file nay', 'check security of this folder') without running the full pipeline. Spawns a single read-only audit agent with an injection/crypto/auth checklist and severity-rated findings."
argument-hint: "[path] [focus:<concern>]"
---

Run a focused security audit on a specific path or module.

**Input:** `$ARGUMENTS` = path to audit + optional focus area.
Examples:
- `/quick-audit src/auth/`
- `/quick-audit src/payment/webhook.js focus:race-condition`
- `/quick-audit frontend/src/features/auth/ focus:token-storage`

**Steps:**

1. **Parse arguments:**
   - Extract PATH (required)
   - Extract FOCUS (optional — specific concern to prioritize)

2. **List files in scope:**
```bash
Bash("find [PATH] \( -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.py' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.rb' -o -name '*.php' \) 2>/dev/null | grep -v node_modules | head -10")
```
If >5 files: warn "Scope has [N] files — quick-audit targets 1–5 files; for more, use /plan-tasks for the full pipeline. Proceeding with the first 5."

3. **Spawn a single audit agent.** Replace `[SECURITY CHECKLIST]` in the template with the full content of §Security checklist at the bottom of this file.

Agent type: `claude`
Agent prompt template:
```
THIS IS A READ-ONLY AUDIT — do NOT edit any project files.

Scope: [PATH]
Focus: [FOCUS or "general security audit"]

Files to audit:
[list from step 2]

Read each file. Apply this security checklist:

[SECURITY CHECKLIST]

Report findings with:
- severity: 🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW
- file:line
- description
- specific fix

COMPLETION_CHECKLIST:
Mark each item [x] when done, [o] if skipped (with reason).
[ ] [file 1]
[ ] [file 2]
...
[ ] Summarize findings by severity
```

4. **After agent completes:**
   - Run completion-checker on agent output
   - If STATUS = SUSPICIOUS: note incomplete coverage
   - Output findings directly to conversation

5. **No checkpoint written** — quick-audit is ephemeral. For persistent results, follow up with `/plan-tasks` for a full pipeline.

**When to use quick-audit vs full pipeline:**

| Scenario | Use |
|----------|-----|
| 1-5 files, quick check | `/quick-audit` |
| Single module, pre-PR | `/quick-audit` |
| Full codebase audit | `/plan-tasks` → full pipeline |
| Post-fix verification | `/quick-audit path/to/fixed/file` |

## Security checklist

> Moved from `rules/security.md` (2026-06) so it loads on demand instead of every session. Paste into the audit agent prompt (step 3).

**Injection prevention:**

| Vulnerability     | Prevention                                                              |
| ----------------- | ----------------------------------------------------------------------- |
| SQL injection     | Prepared statements / ORM with binding                                  |
| Command injection | No `eval`, no `shell=True` with user input                              |
| Path traversal    | Resolve with `path.resolve()`, check prefix is within allowed dir       |
| XSS               | Escape output, use template engines with auto-escaping                  |
| SSRF              | Validate URL host, allowlist domains, deny private IP ranges            |
| XXE               | Disable external entities in XML parser                                 |
| Deserialization   | No `pickle.loads`, `yaml.load` (use `safe_load`), `unserialize`, `Marshal.load` from untrusted sources |

**Cryptography:**

- Do NOT invent algorithms. Use standard libraries (`crypto`, `cryptography`, `bcrypt`, `argon2`, `libsodium`).
- Password hashing: `argon2id` (preferred) or `scrypt`. `bcrypt` with cost ≥10 only for **legacy systems** where Argon2/scrypt isn't available. Never bare MD5/SHA1/SHA256. Source: [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
- Symmetric encryption: AES-GCM or ChaCha20-Poly1305 with a random nonce. Never ECB.
- Randomness: `secrets` (Python), `crypto.randomBytes` (Node), `/dev/urandom`. Never `Math.random()` for security-sensitive purposes.
- TLS: minimum 1.2, prefer 1.3. Certificate pinning only when required (not by default).

**Authentication & Authorization:**

- Authentication ≠ Authorization. Verify both at every endpoint.
- Session tokens: random ≥128 bits, `HttpOnly` + `Secure` + `SameSite` cookie or `Authorization` header.
- JWT: signed (RS256/EdDSA preferred over HS256), verify expiry + audience + issuer.
- Rate limit: login, password reset, OTP, and public API endpoints.
- Default-deny: if no explicit allow rule → deny.
