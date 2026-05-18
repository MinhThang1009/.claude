#!/usr/bin/env python3
# Bash command guard cho Claude Code PreToolUse hook.
# Engine pattern matching tập trung. Chiến lược: PATH-BASED denylist (chặn theo
# path nhạy cảm, không phụ thuộc command name) + behavior-based detection
# (force push, pipe-to-shell, network exfil).

import sys
import json
import re

# Force UTF-8 stderr cho Windows cp1252 (BLOCKED message chứa tiếng Việt).
if hasattr(sys.stderr, "reconfigure"):  # pragma: no cover
    # Module-level — chạy 1 lần lúc import; nhánh False (stream không có
    # reconfigure) không reachable trong test environment.
    sys.stderr.reconfigure(encoding="utf-8")

# ===== Sensitive path patterns =====
# Match path string trong command, bất kể command nào. Dùng regex non-anchored.
# Boundaries: start-of-string, whitespace, ; | & < > = quote → reduce false positive.
SENSITIVE_PATH_PATTERNS = [
    # Dotenv variants — DISABLED: cho phep doc/ghi .env trong project
    # r"\.env(?:\.[\w.-]+)?",
    # r"[\w.-]+\.env",
    # r"\.envrc",
    # Crypto / cert
    r"[\w./~-]*\.pem",
    r"[\w./~-]+[/\\][\w.-]*\.key",
    r"[\w./~-]*\.p12",
    r"[\w./~-]*\.jks",
    r"[\w./~-]*\.pfx",
    # SSH private keys
    r"id_(?:rsa|ed25519|ecdsa|dsa)(?:_[\w-]+)?",
    # Cloud / dev tool credentials
    r"~?/?\.aws/credentials",
    r"~?/?\.aws/config",
    r"~?/?\.netrc",
    r"~?/?\.npmrc",
    r"~?/?\.pypirc",
    r"~?/?\.docker/config\.json",
    r"~?/?\.kube/config",
    r"~?/?\.gitconfig",
    # Common credential filenames
    r"credentials\.json",
    r"service[_-]?account[\w.-]*\.json",
    r"gcp[_-]?key[\w.-]*\.json",
    r"firebase[_-]?adminsdk[\w.-]*\.json",
]

# Build single regex with lookbehind/ahead for boundary.
# Boundary trước có `*` để cover glob expansion (`cat *.env` shell expand → đọc .env).
_SENSITIVE_INNER = "|".join(SENSITIVE_PATH_PATTERNS)
SENSITIVE_RE = re.compile(
    r'(?:^|[\s;|&<>=,()`"\'*])'  # boundary trước (thêm * cho glob)
    r"(?:[\w./~-]*/)?"  # optional path prefix (e.g. ~/.aws/, /etc/)
    r"(?:" + _SENSITIVE_INNER + r")"
    r'(?=[\s;|&<>)`"\']|$)'  # boundary sau (lookahead)
)

# ===== Helper functions =====


SAFE_METADATA_COMMANDS_RE = re.compile(
    r"^\s*(?:ls|stat|file|test|realpath|dirname|basename|which|type|echo|printf|"
    r"find\s+\S+\s+-(?:name|type|maxdepth)|wc\s+[^|;&]*-l\b)\b"
)


def is_sensitive_path_access(cmd: str) -> bool:
    """Block if cmd references sensitive path AND is not safe metadata-only.

    Safe metadata commands (ls/stat/file/test/wc -l/...) chỉ list metadata,
    không reveal nội dung file → cho qua kể cả với sensitive path.
    """
    # Split command into segments by separators (;, &, &&, ||, |, > , >>, <, <<).
    # Redirect operators (>, >>, <, <<) phải tách để 'echo $SECRET > .env' không
    # đi qua check như 1 segment (echo prefix match SAFE_METADATA → bypass).
    segments = re.split(r";|&&|\|\||&|\||>>|>|<<|<", cmd)
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        # Normalize $IFS obfuscation (cat$IFS.env → cat .env) trước khi check.
        # $IFS expand thành whitespace ở runtime; check pattern phải treat as space.
        seg = re.sub(r"\$\{?IFS\}?", " ", seg)
        # Skip if segment is metadata-safe command
        if SAFE_METADATA_COMMANDS_RE.match(seg):
            continue
        # Block if sensitive path appears in this segment
        if SENSITIVE_RE.search(seg):
            return True
    return False


def is_raw_network_tool(cmd: str) -> bool:
    """nc/ncat/socat/telnet — block all uses (rare legitimate use in dev)."""
    return bool(re.search(r"(?:^|[\s;|&])(?:nc|ncat|socat|telnet)\b", cmd))


def is_curl_wget_exfil(cmd: str) -> bool:
    """curl/wget upload nội dung từ file → khả năng exfil secret.

    Chỉ block khi data source là FILE (`@<path>`, --upload-file, --post-file, -T).
    Không block `-d hello` (literal string) hay `-d '{"a":1}'` (inline JSON) —
    đây là API call thông thường.
    """
    return bool(
        re.search(
            r"(?:^|[\s;|&])(?:curl|wget)\b[^|;&]*?"
            r"(?:"
            r"--upload-file\b|"  # luôn upload file
            r"--post-file\b|"  # wget post file
            r"\s-T\s+\S+|"  # -T file → upload
            r"--data(?:-binary|-raw|-urlencode)?(?:\s+|=)@|"  # --data @file hoặc --data=@file
            r"\s-d\s+@|"  # -d @file
            r"\s-F\s+[\w.-]+=@"  # -F name=@file
            r")",
            cmd,
        )
    )


def is_pipe_to_shell(cmd: str) -> bool:
    """Download và execute trong cùng command/chain.

    Bao gồm: curl|bash, eval $(curl), source <(curl), bash -c "$(curl)",
    và 2-step download → execute (curl ... -o /tmp/x && bash /tmp/x).
    """
    patterns = [
        # Direct pipe: curl ... | bash
        r"(?:curl|wget)[^|]*\|\s*(?:bash|sh|zsh|ksh|dash|fish)\b",
        # eval $(curl ...)
        r'eval\s*[\'"]?\$\([^)]*(?:curl|wget)\b',
        # source <(curl ...) hoặc . <(curl ...)
        r"(?:source|\.)\s+<\(\s*(?:curl|wget)\b",
        # bash -c "$(curl ...)"
        r'(?:bash|sh|zsh|ksh)\s+-c\s+[\'"]?\$\([^)]*(?:curl|wget)\b',
        # 2-step: curl ... -o /tmp/x && (bash|sh) /tmp/x
        # Match "curl/wget ... -o <path>" sau đó "(bash|sh|source) <path>"
        # \1 phải kết thúc bằng word boundary để không match prefix khác
        r"(?:curl|wget)[^|;&]*-[oO]\s+(\S+)[^|;&]*"
        r"(?:&&|;|\|\|)\s*(?:bash|sh|zsh|source|\.)\s+\1(?=\s|$|[;|&])",
    ]
    return any(re.search(p, cmd) for p in patterns)


def is_dangerous_rm(cmd: str) -> bool:
    """rm hoặc find xóa root/home/cwd/parent.

    Cover: short flag (-rf, -fr, -Rf, -r, -R), long flag (--recursive --force),
    --no-preserve-root, target có/không trailing slash, find với -delete hoặc -exec rm.
    """
    # Target patterns: root, home, cwd, parent (cover trailing / và /*)
    targets = (
        r"(?:"
        r"/(?:\*)?|"  # /, /*
        r"~(?:/(?:\*)?)?|"  # ~, ~/, ~/*
        r"\$\{?HOME\}?(?:/(?:\*)?)?|"  # $HOME, ${HOME}, $HOME/, ${HOME}/, $HOME/*, ${HOME}/*
        r"\.{1,2}(?:/(?:\*)?)?|"  # ., .., ./, ../, ./*, ../*
        r"\$\{?PWD\}?(?:/(?:\*)?)?|"  # $PWD, ${PWD}, $PWD/, $PWD/*
        r"\$\(pwd\)(?:/(?:\*)?)?"  # $(pwd), $(pwd)/, $(pwd)/*
        r")"
    )
    target_boundary = rf"{targets}(?=[\s;|&]|$)"

    # rm với recursive flag (-r/-R/--recursive/--no-preserve-root) ở bất kỳ vị trí
    # nào trước target nguy hiểm. Match flag thông qua word boundary để cover
    # `rm --no-preserve-root -rf /` (--no-preserve-root xen giữa rm và -rf).
    rm_dangerous = (
        rf"(?:^|[\s;|&])rm\b[^|;&]*?"
        rf"(?:--recursive|--no-preserve-root|-[a-zA-Z]*[rR][a-zA-Z]*)\b"
        rf"[^|;&]*?{target_boundary}"
    )

    patterns = [
        rm_dangerous,
        # find <target> -delete
        rf"(?:^|[\s;|&])find\s+{targets}[^|;&]*-delete",
        # find <target> -exec rm
        rf"(?:^|[\s;|&])find\s+{targets}[^|;&]*-exec\s+rm",
    ]
    return any(re.search(p, cmd) for p in patterns)


def is_force_push_variant(cmd: str) -> bool:
    """git push với force/force-with-lease/+ref/git -c override."""
    patterns = [
        # --force, --force-with-lease, --force-if-includes, hoặc -f short flag
        r"\bgit\b[^|;&]*\bpush\b[^|;&]*(?:--force(?:-with-lease|-if-includes)?\b|\s-f\b)",
        # +ref refspec (e.g., git push origin +main)
        r"\bgit\b[^|;&]*\bpush\b[^|;&]*\s\+\w[\w/-]*",
        # git -c <key>=<val> push (override config inline)
        r"\bgit\s+-c\s+\S+\s+push\b",
    ]
    return any(re.search(p, cmd) for p in patterns)


def is_fork_bomb(cmd: str) -> bool:
    """Classic fork bomb pattern."""
    return bool(re.search(r":\(\)\s*\{", cmd))


def is_dd_to_disk(cmd: str) -> bool:
    """dd ghi vào disk device → data destruction."""
    return bool(
        re.search(
            r"(?:^|[\s;|&])dd\b[^|;&]*\bof=/dev/(?:sd|hd|nvme|disk|loop|mmcblk|vd|xvd)",
            cmd,
        )
    )


# ===== Main check =====


def check_command(cmd: str):
    """Return (blocked, reason). blocked=True → exit 2."""
    checks = [
        (
            is_sensitive_path_access,
            "đọc/ghi/copy file nhạy cảm (.env, *.pem, "
            "~/.aws/*, ~/.ssh/id_*, ~/.netrc, credentials.json, serviceAccount*.json). "
            "Dùng Read tool nếu thực sự cần (Read deny rule sẽ filter).",
        ),
        (
            is_raw_network_tool,
            "raw network tool (nc/ncat/socat/telnet) — potential exfil channel.",
        ),
        (
            is_curl_wget_exfil,
            "curl/wget với flag upload data (--data*/--upload-file/-T/-F/-d). "
            "Có thể exfil secret. Confirm intent với user.",
        ),
        (
            is_pipe_to_shell,
            "tải nội dung từ network và thực thi (curl|bash, "
            "eval $(curl), source <(curl), 2-step download-execute). Tải về file, "
            "kiểm tra, rồi chạy thủ công.",
        ),
        (
            is_dangerous_rm,
            "xóa đệ quy root/home/cwd/parent (rm -rf /, "
            "rm --recursive --force ~, find / -delete). Để xóa subdir, "
            "dùng path đầy đủ cụ thể (vd: rm -rf ./node_modules).",
        ),
        (
            is_force_push_variant,
            "git push với --force/--force-with-lease/+ref/"
            "git -c override. Có thể overwrite branch chia sẻ.",
        ),
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

    cmd = data.get("tool_input", {}).get("command", "")
    if not cmd:
        sys.exit(0)

    blocked, reason = check_command(cmd)
    if blocked:
        print(f"BLOCKED: {reason}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
