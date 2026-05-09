#!/usr/bin/env python3
# Bash command guard cho Claude Code PreToolUse hook.
# Engine pattern matching tập trung. Chiến lược: PATH-BASED denylist (chặn theo
# path nhạy cảm, không phụ thuộc command name) + behavior-based detection
# (force push, pipe-to-shell, network exfil).

import sys
import json
import re

# ===== Sensitive path patterns =====
# Match path string trong command, bất kể command nào. Dùng regex non-anchored.
# Boundaries: start-of-string, whitespace, ; | & < > = quote → reduce false positive.
SENSITIVE_PATH_PATTERNS = [
    # Dotenv variants
    r'\.env(?:\.[\w.-]+)?',          # .env, .env.local, .env.production, .env.staging
    r'[\w.-]+\.env',                  # foo.env, app.env
    r'\.envrc',
    # Crypto / cert
    r'[\w./~-]*\.pem',
    r'[\w./~-]*\.key',
    r'[\w./~-]*\.p12',
    r'[\w./~-]*\.jks',
    r'[\w./~-]*\.pfx',
    # SSH private keys
    r'id_(?:rsa|ed25519|ecdsa|dsa)(?:_[\w-]+)?',
    # Cloud / dev tool credentials
    r'~?/?\.aws/credentials',
    r'~?/?\.aws/config',
    r'~?/?\.netrc',
    r'~?/?\.npmrc',
    r'~?/?\.pypirc',
    r'~?/?\.docker/config\.json',
    r'~?/?\.kube/config',
    r'~?/?\.gitconfig',
    # Common credential filenames
    r'credentials\.json',
    r'service[_-]?account[\w.-]*\.json',
    r'gcp[_-]?key[\w.-]*\.json',
    r'firebase[_-]?adminsdk[\w.-]*\.json',
]

# Build single regex with lookbehind/ahead for boundary
_SENSITIVE_INNER = '|'.join(SENSITIVE_PATH_PATTERNS)
SENSITIVE_RE = re.compile(
    r'(?:^|[\s;|&<>=,()`"\'])'    # boundary trước
    r'(?:[\w./~-]*/)?'             # optional path prefix (e.g. ~/.aws/, /etc/)
    r'(?:' + _SENSITIVE_INNER + r')'
    r'(?=[\s;|&<>)`"\']|$)'        # boundary sau (lookahead)
)

# ===== Helper functions =====


SAFE_METADATA_COMMANDS_RE = re.compile(
    r'^\s*(?:ls|stat|file|test|realpath|dirname|basename|which|type|echo|printf|'
    r'find\s+\S+\s+-(?:name|type|maxdepth)|wc\s+[^|;&]*-l\b)\b'
)


def is_sensitive_path_access(cmd: str) -> bool:
    """Block if cmd references sensitive path AND is not safe metadata-only.

    Safe metadata commands (ls/stat/file/test/wc -l/...) chỉ list metadata,
    không reveal nội dung file → cho qua kể cả với sensitive path.
    """
    # Split command into segments by separators (;, &, &&, ||, |)
    segments = re.split(r';|&&|\|\||&|\|', cmd)
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        # Skip if segment is metadata-safe command
        if SAFE_METADATA_COMMANDS_RE.match(seg):
            continue
        # Block if sensitive path appears in this segment
        if SENSITIVE_RE.search(seg):
            return True
    return False


def is_raw_network_tool(cmd: str) -> bool:
    """nc/ncat/socat/telnet — block all uses (rare legitimate use in dev)."""
    return bool(re.search(r'(?:^|[\s;|&])(?:nc|ncat|socat|telnet)\b', cmd))


def is_curl_wget_exfil(cmd: str) -> bool:
    """curl/wget với flag upload data → khả năng exfil secret."""
    return bool(re.search(
        r'(?:^|[\s;|&])(?:curl|wget)\b[^|;&]*?'
        r'(?:--data(?:-binary|-raw|-urlencode)?|--upload-file|--post-file|'
        r'\s-T\b|\s-F\b|\s-d\b)',
        cmd
    ))


def is_pipe_to_shell(cmd: str) -> bool:
    """Download và execute trong cùng command/chain.

    Bao gồm: curl|bash, eval $(curl), source <(curl), bash -c "$(curl)",
    và 2-step download → execute (curl ... -o /tmp/x && bash /tmp/x).
    """
    patterns = [
        # Direct pipe: curl ... | bash
        r'(?:curl|wget)[^|]*\|\s*(?:bash|sh|zsh|ksh|dash|fish)\b',
        # eval $(curl ...)
        r'eval\s*[\'"]?\$\([^)]*(?:curl|wget)\b',
        # source <(curl ...) hoặc . <(curl ...)
        r'(?:source|\.)\s+<\(\s*(?:curl|wget)\b',
        # bash -c "$(curl ...)"
        r'(?:bash|sh|zsh|ksh)\s+-c\s+[\'"]?\$\([^)]*(?:curl|wget)\b',
        # 2-step: curl ... -o /tmp/x && (bash|sh) /tmp/x
        # Match "curl/wget ... -o <path>" sau đó "(bash|sh|source) <path>"
        r'(?:curl|wget)[^|;&]*-[oO]\s+(\S+)[^|;&]*'
        r'(?:&&|;|\|\|)\s*(?:bash|sh|zsh|source|\.)\s+\1',
    ]
    return any(re.search(p, cmd) for p in patterns)


def is_dangerous_rm(cmd: str) -> bool:
    """rm hoặc find xóa root/home/cwd/parent.

    Cover: short flag (-rf, -fr, -Rf, -r, -R), long flag (--recursive --force),
    find với -delete hoặc -exec rm.
    """
    # Target patterns: root, home, cwd, parent
    targets = r'(?:/|/\*|~|~/|~/\*|\$HOME|\$\{HOME\}|\.|\./|\./\*|\.\.)'
    target_boundary = rf'{targets}(?=[\s;|&]|$)'

    patterns = [
        # rm với short flag chứa r/R
        rf'(?:^|[\s;|&])rm\s+-[a-zA-Z]*[rR][a-zA-Z]*\s+{target_boundary}',
        # rm với long flag --recursive (có thể có --force, --interactive=never xen)
        rf'(?:^|[\s;|&])rm\s+(?:--(?:recursive|force|interactive=never|verbose|preserve-root=no)\s+)*'
        rf'(?:--(?:recursive|force))\s+'
        rf'(?:--(?:recursive|force|interactive=never|verbose|preserve-root=no)\s+)*'
        rf'{target_boundary}',
        # find <target> -delete
        rf'(?:^|[\s;|&])find\s+{targets}[^|;&]*-delete',
        # find <target> -exec rm
        rf'(?:^|[\s;|&])find\s+{targets}[^|;&]*-exec\s+rm',
    ]
    return any(re.search(p, cmd) for p in patterns)


def is_force_push_variant(cmd: str) -> bool:
    """git push với force/force-with-lease/+ref/git -c override."""
    patterns = [
        # --force, --force-with-lease, --force-if-includes, hoặc -f short flag
        r'\bgit\b[^|;&]*\bpush\b[^|;&]*(?:--force(?:-with-lease|-if-includes)?\b|\s-f\b)',
        # +ref refspec (e.g., git push origin +main)
        r'\bgit\b[^|;&]*\bpush\b[^|;&]*\s\+\w[\w/-]*',
        # git -c <key>=<val> push (override config inline)
        r'\bgit\s+-c\s+\S+\s+push\b',
    ]
    return any(re.search(p, cmd) for p in patterns)


def is_fork_bomb(cmd: str) -> bool:
    """Classic fork bomb pattern."""
    return bool(re.search(r':\(\)\s*\{', cmd))


def is_dd_to_disk(cmd: str) -> bool:
    """dd ghi vào disk device → data destruction."""
    return bool(re.search(
        r'(?:^|[\s;|&])dd\b[^|;&]*\bof=/dev/(?:sd|hd|nvme|disk|loop|mmcblk|vd|xvd)',
        cmd
    ))


# ===== Main check =====


def check_command(cmd: str):
    """Return (blocked, reason). blocked=True → exit 2."""
    checks = [
        (is_sensitive_path_access, "đọc/ghi/copy file nhạy cảm (.env, *.pem, "
         "~/.aws/*, ~/.ssh/id_*, ~/.netrc, credentials.json, serviceAccount*.json). "
         "Dùng Read tool nếu thực sự cần (Read deny rule sẽ filter)."),
        (is_raw_network_tool, "raw network tool (nc/ncat/socat/telnet) — "
         "potential exfil channel."),
        (is_curl_wget_exfil, "curl/wget với flag upload data (--data*/--upload-file/-T/-F/-d). "
         "Có thể exfil secret. Confirm intent với user."),
        (is_pipe_to_shell, "tải nội dung từ network và thực thi (curl|bash, "
         "eval $(curl), source <(curl), 2-step download-execute). Tải về file, "
         "kiểm tra, rồi chạy thủ công."),
        (is_dangerous_rm, "xóa đệ quy root/home/cwd/parent (rm -rf /, "
         "rm --recursive --force ~, find / -delete). Để xóa subdir, "
         "dùng path đầy đủ cụ thể (vd: rm -rf ./node_modules)."),
        (is_force_push_variant, "git push với --force/--force-with-lease/+ref/"
         "git -c override. Có thể overwrite branch chia sẻ."),
        (is_fork_bomb, "fork bomb pattern — sẽ làm máy treo."),
        (is_dd_to_disk, "dd ghi vào disk device — risk wipe ổ cứng."),
    ]

    for check_fn, reason in checks:
        if check_fn(cmd):
            return True, reason

    return False, None


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Malformed input → cho qua (không phải lỗi của command)
        sys.exit(0)

    cmd = data.get('tool_input', {}).get('command', '')
    if not cmd:
        sys.exit(0)

    blocked, reason = check_command(cmd)
    if blocked:
        print(f"BLOCKED: {reason}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()
