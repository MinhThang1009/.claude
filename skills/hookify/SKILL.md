---
name: hookify
description: Tạo Claude Code hooks ngăn unwanted behaviors từ phân tích conversation hoặc explicit instructions. Dùng khi user nói "tạo hook", "ngăn behavior X", "hookify", hoặc gọi /hookify.
allowed-tools: Read Grep Glob Bash Write AskUserQuestion TodoWrite
argument-hint: "[tùy chọn — behavior cụ thể cần ngăn, vd: 'đừng dùng rm -rf']"
---

# Hookify — Tạo Hooks từ Unwanted Behaviors

Tạo rule files ngăn Claude thực hiện hành vi không mong muốn — không cần edit `settings.json` thủ công.

## Bước 1: Thu thập behaviors

**Nếu `$ARGUMENTS` có nội dung:**
- Phân tích instruction của user: `$ARGUMENTS`
- Scan thêm 10-15 message gần nhất để tìm context/ví dụ.

**Nếu `$ARGUMENTS` trống:**
- Dispatch subagent phân tích conversation (focus **20-30 message** gần nhất):
  - Tìm corrections ("don't do X", "stop doing Y")
  - Tìm reversions (user sửa lại action của Claude)
  - Tìm frustrated reactions ("tại sao lại...", "không phải thế")
  - Tìm repeated issues (cùng vấn đề nhiều lần)
- Mỗi issue: tool nào, pattern gì, tại sao có vấn đề, severity (high/medium/low).

## Bước 2: Hỏi user xác nhận

Dùng AskUserQuestion:

1. **Chọn behaviors** (multiSelect): liệt kê behaviors phát hiện được (tối đa 4), user chọn cái nào cần hookify.
2. **Action cho mỗi behavior**: `warn` (hiển thị cảnh báo, cho phép tiếp) hay `block` (ngăn thực thi)?
3. **Patterns**: hiển thị patterns phát hiện, cho user chỉnh sửa/thêm.

## Bước 3: Tạo rule files

Mỗi rule = 1 file `.claude/hookify.<rule-name>.local.md` trong **project directory hiện tại** (KHÔNG phải plugin directory).

**Naming convention**: kebab-case, bắt đầu bằng action verb: `block-dangerous-rm`, `warn-console-log`, `require-tests-before-stop`.
Tránh: `hookify.rule1.local.md` (không mô tả), `hookify.md` (thiếu .local), `danger.local.md` (thiếu hookify prefix).

### Format đơn giản (1 pattern)

```markdown
---
name: <rule-name>
enabled: true
event: <bash|file|stop|prompt|all>
pattern: <regex pattern>  # match vào `command` (bash) hoặc `new_text` (file) — Python regex
action: <warn|block>   # optional — mặc định là warn nếu không khai báo
---

<Message hiển thị cho Claude khi rule trigger>
```

### Format phức tạp (nhiều conditions)

```markdown
---
name: <rule-name>
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
  - field: new_text
    operator: contains
    pattern: API_KEY
action: warn
---

<Warning message>
```

### Event types

| Event | Match |
|-------|-------|
| `bash` | Bash tool commands |
| `file` | Edit, Write, MultiEdit tools |
| `stop` | Khi agent muốn dừng. Dùng cho: nhắc nhở steps bắt buộc, completion checklists, process enforcement |
| `prompt` | Khi user submit prompt |
| `all` | Tất cả events |

### Operators cho conditions

| Operator | Mô tả |
|----------|-------|
| `regex_match` | Match regex pattern |
| `contains` | Chứa substring |
| `equals` | Bằng chính xác |
| `not_contains` | Không chứa substring |
| `starts_with` | Bắt đầu bằng |
| `ends_with` | Kết thúc bằng |

### Fields theo event type

| Event | Fields khả dụng |
|-------|-----------------|
| `bash` | `command` |
| `file` | `file_path`, `new_text`, `old_text`, `content` (toàn bộ nội dung file sau edit) |
| `prompt` | `user_prompt` |
| `stop` | _(check transcript hoặc completion criteria)_ |

**YAML escaping**:
- YAML unquoted: `pattern: \s+-rf` — work as-is, không cần escape backslash.
- YAML quoted: `pattern: "\\s+-rf"` — cần double backslash.
- Pattern chứa `:`, `#`, `{`, `}` → bắt buộc quote.
- **Khuyến nghị: dùng unquoted** trừ khi pattern chứa ký tự YAML special.

## Bước 4: Tạo files và confirm

1. Kiểm tra `.claude/` directory tồn tại → tạo nếu chưa có (`mkdir -p .claude`).
   - Kiểm tra `.gitignore` — thêm `.claude/*.local.md` nếu chưa có, để tránh commit rule files cá nhân vào repo.
2. Dùng Write tool tạo từng file.
3. Hiển thị danh sách đã tạo:
   ```
   Đã tạo 2 hookify rules:
   - .claude/hookify.dangerous-rm.local.md → bash: rm -rf (warn)
   - .claude/hookify.sensitive-files.local.md → file: .env edits (block)

   Rules active ngay — không cần restart! Hook sẽ đọc rules mới vào lần dùng tool tiếp theo.
   ```
4. Verify files bằng Glob/Read.

## Pattern Tips

**Bash patterns:**
- Dangerous commands: `rm\s+-rf|chmod\s+777|dd\s+if=`
- Package installs: `npm\s+install\s+|pip\s+install`

**File patterns:**
- Code smells: `console\.log\(|eval\(|innerHTML\s*=`
- Sensitive files: `\.env$|\.git/|credentials`

## Sub-commands

### `/hookify list`
Liệt kê tất cả rules hiện có dạng table:

| Rule | Event | Pattern | Action | Enabled |
|------|-------|---------|--------|---------|
| warn-dangerous-rm | bash | `rm\s+-rf` | warn | ✅ |

Kèm preview message mỗi rule.

### `/hookify configure`
Interactive enable/disable rules bằng AskUserQuestion (multiSelect). Hiển thị danh sách rules → user chọn toggle → update `enabled` field.

### `/hookify help`
Hiển thị tóm tắt cách dùng, event types, operators, ví dụ.

## Quản lý rules thủ công

- **Liệt kê**: `ls .claude/hookify.*.local.md` hoặc Glob.
- **Bật/tắt**: đổi `enabled: true/false` trong frontmatter.
- **Xóa**: delete file.
- Thay đổi apply ngay lần dùng tool tiếp theo.

## Ví dụ workflow

**User**: `/hookify Đừng dùng rm -rf mà không hỏi tôi trước`

1. Phân tích: user muốn ngăn `rm -rf`.
2. Hỏi: "Block luôn hay chỉ cảnh báo?" → User chọn "Cảnh báo".
3. Tạo `.claude/hookify.warn-dangerous-rm.local.md`:
   ```markdown
   ---
   name: warn-dangerous-rm
   enabled: true
   event: bash
   pattern: rm\s+-rf
   action: warn
   ---

   ⚠️ **Phát hiện lệnh rm -rf**
   User yêu cầu được cảnh báo trước khi dùng rm -rf.
   Hãy xác nhận đường dẫn chính xác trước khi thực thi.
   ```
4. Confirm: "Rule active ngay — thử trigger để test!"

Dùng TodoWrite để track progress qua các bước.

## Ví dụ mẫu

Xem thư mục `examples/` để tham khảo 4 rules hoàn chỉnh:
- `warn-console-log.local.md` — cảnh báo khi thêm `console.log`
- `block-dangerous-rm.local.md` — chặn lệnh `rm -rf`
- `require-tests-stop.local.md` — yêu cầu chạy test trước khi dừng
- `warn-sensitive-files.local.md` — cảnh báo khi edit file nhạy cảm (multi-condition)

## Testing Patterns

Test regex pattern trước khi dùng: `python3 -c "import re; print(re.search(r'<pattern>', '<test-string>'))"`
Hoặc dùng [regex101.com](https://regex101.com) (chọn Python flavor) để visualize.

## Pitfalls thường gặp

- **Pattern quá rộng**: `rm` match mọi lệnh chứa "rm" (ví dụ `npm run format`). Dùng `\brm\s+-rf` cụ thể hơn.
- **Pattern quá hẹp**: `rm -rf /` chỉ match exact string, miss `rm -rf ./src`.
- **Escaping issues**: YAML quoted strings (`"pattern"`) cần double backslash (`\\s`); YAML unquoted (`pattern: \s`) work as-is. Khuyến nghị: dùng unquoted.
- **Nhiều conditions = AND logic**: tất cả conditions phải match để rule trigger.

## Troubleshooting

- Rule không trigger → kiểm tra file nằm đúng `.claude/` của project (không phải plugin). Đọc lại file bằng Read tool để verify pattern đúng.
- Pattern không match → test: `python3 -c "import re; print(re.search(r'pattern', 'test'))"`
- Block quá strict → đổi `action: block` thành `action: warn`.
