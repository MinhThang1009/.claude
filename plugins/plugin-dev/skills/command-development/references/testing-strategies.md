# Các Chiến Lược Kiểm Thử Command

Các chiến lược toàn diện để kiểm thử slash command trước khi triển khai và phân phối.

## Tổng Quan

Kiểm thử command đảm bảo chúng hoạt động đúng, xử lý trường hợp biên và mang lại trải nghiệm người dùng tốt. Một cách tiếp cận kiểm thử có hệ thống phát hiện vấn đề sớm và xây dựng sự tin tưởng vào độ tin cậy của command.

## Các Cấp Kiểm Thử

### Cấp 1: Validation Cú Pháp và Cấu Trúc

**Những gì cần kiểm thử:**
- Cú pháp YAML frontmatter
- Định dạng Markdown
- Vị trí và tên file

**Cách kiểm thử:**

```bash
# Validate YAML frontmatter
head -n 20 .claude/commands/my-command.md | grep -A 10 "^---"

# Kiểm tra marker đóng frontmatter
head -n 20 .claude/commands/my-command.md | grep -c "^---" # Phải là 2

# Xác minh file có phần mở rộng .md
ls .claude/commands/*.md

# Kiểm tra file ở đúng vị trí
test -f .claude/commands/my-command.md && echo "Found" || echo "Missing"
```

**Script validation tự động:**

```bash
#!/bin/bash
# validate-command.sh

COMMAND_FILE="$1"

if [ ! -f "$COMMAND_FILE" ]; then
  echo "LỖI: Không tìm thấy file: $COMMAND_FILE"
  exit 1
fi

# Kiểm tra phần mở rộng .md
if [[ ! "$COMMAND_FILE" =~ \.md$ ]]; then
  echo "LỖI: File phải có phần mở rộng .md"
  exit 1
fi

# Validate YAML frontmatter nếu có
if head -n 1 "$COMMAND_FILE" | grep -q "^---"; then
  # Đếm marker frontmatter
  MARKERS=$(head -n 50 "$COMMAND_FILE" | grep -c "^---")
  if [ "$MARKERS" -ne 2 ]; then
    echo "LỖI: YAML frontmatter không hợp lệ (cần đúng 2 marker '---')"
    exit 1
  fi
  echo "✓ Cú pháp YAML frontmatter hợp lệ"
fi

# Kiểm tra file trống
if [ ! -s "$COMMAND_FILE" ]; then
  echo "LỖI: File trống"
  exit 1
fi

echo "✓ Cấu trúc file command hợp lệ"
```

### Cấp 2: Validation Trường Frontmatter

**Những gì cần kiểm thử:**
- Kiểu trường đúng
- Giá trị trong phạm vi hợp lệ
- Các trường bắt buộc có mặt (nếu có)

**Script validation:**

```bash
#!/bin/bash
# validate-frontmatter.sh

COMMAND_FILE="$1"

# Trích xuất YAML frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$COMMAND_FILE" | sed '1d;$d')

if [ -z "$FRONTMATTER" ]; then
  echo "Không có frontmatter để validate"
  exit 0
fi

# Kiểm tra trường 'model' nếu có
if echo "$FRONTMATTER" | grep -q "^model:"; then
  MODEL=$(echo "$FRONTMATTER" | grep "^model:" | cut -d: -f2 | tr -d ' ')
  if ! echo "sonnet opus haiku" | grep -qw "$MODEL"; then
    echo "LỖI: Model không hợp lệ '$MODEL' (phải là sonnet, opus, hoặc haiku)"
    exit 1
  fi
  echo "✓ Trường model hợp lệ: $MODEL"
fi

# Kiểm tra định dạng trường 'allowed-tools'
if echo "$FRONTMATTER" | grep -q "^allowed-tools:"; then
  echo "✓ Trường allowed-tools có mặt"
  # Có thể thêm validation phức tạp hơn ở đây
fi

# Kiểm tra độ dài 'description'
if echo "$FRONTMATTER" | grep -q "^description:"; then
  DESC=$(echo "$FRONTMATTER" | grep "^description:" | cut -d: -f2-)
  LENGTH=${#DESC}
  if [ "$LENGTH" -gt 80 ]; then
    echo "CẢNH BÁO: Độ dài description $LENGTH (khuyến nghị < 60 ký tự)"
  else
    echo "✓ Độ dài description chấp nhận được: $LENGTH ký tự"
  fi
fi

echo "✓ Các trường frontmatter hợp lệ"
```

### Cấp 3: Gọi Command Thủ Công

**Những gì cần kiểm thử:**
- Command xuất hiện trong `/help`
- Command thực thi không có lỗi
- Output như mong đợi

**Quy trình kiểm thử:**

```bash
# 1. Khởi động Claude Code
claude --debug

# 2. Kiểm tra command xuất hiện trong help
> /help
# Tìm command của bạn trong danh sách

# 3. Gọi command không có argument
> /my-command
# Kiểm tra xử lý hợp lý hoặc hành vi phù hợp

# 4. Gọi với argument hợp lệ
> /my-command arg1 arg2
# Xác minh hành vi mong đợi

# 5. Kiểm tra debug log
tail -f ~/.claude/debug-logs/latest
# Tìm lỗi hoặc cảnh báo
```

### Cấp 4: Kiểm Thử Argument

**Những gì cần kiểm thử:**
- Argument vị trí hoạt động ($1, $2, v.v.)
- $ARGUMENTS bắt được tất cả argument
- Thiếu argument được xử lý khéo léo
- Argument không hợp lệ được phát hiện

**Ma trận kiểm thử:**

| Test Case | Command | Kết Quả Mong Đợi |
|-----------|---------|------------------|
| Không có arg | `/cmd` | Xử lý khéo léo hoặc thông báo hữu ích |
| Một arg | `/cmd arg1` | $1 được thay thế đúng |
| Hai arg | `/cmd arg1 arg2` | $1 và $2 được thay thế |
| Arg thừa | `/cmd a b c d` | Tất cả được bắt hoặc phần thừa được xử lý phù hợp |
| Ký tự đặc biệt | `/cmd "arg with spaces"` | Dấu nháy được xử lý đúng |
| Arg trống | `/cmd ""` | Chuỗi rỗng được xử lý |

**Script kiểm thử:**

```bash
#!/bin/bash
# test-command-arguments.sh

COMMAND="$1"

echo "Kiểm thử xử lý argument cho /$COMMAND"
echo

echo "Test 1: Không có argument"
echo "  Command: /$COMMAND"
echo "  Mong đợi: [mô tả hành vi mong đợi]"
echo "  Cần kiểm thử thủ công"
echo

echo "Test 2: Một argument"
echo "  Command: /$COMMAND test-value"
echo "  Mong đợi: 'test-value' xuất hiện trong output"
echo "  Cần kiểm thử thủ công"
echo

echo "Test 3: Nhiều argument"
echo "  Command: /$COMMAND arg1 arg2 arg3"
echo "  Mong đợi: Tất cả argument được dùng phù hợp"
echo "  Cần kiểm thử thủ công"
echo

echo "Test 4: Ký tự đặc biệt"
echo "  Command: /$COMMAND \"value with spaces\""
echo "  Mong đợi: Toàn bộ cụm từ được bắt"
echo "  Cần kiểm thử thủ công"
```

### Cấp 5: Kiểm Thử Tham Chiếu File

**Những gì cần kiểm thử:**
- Cú pháp @ tải nội dung file
- File không tồn tại được xử lý
- File lớn được xử lý phù hợp
- Nhiều tham chiếu file hoạt động

**Quy trình kiểm thử:**

```bash
# Tạo file kiểm thử
echo "Test content" > /tmp/test-file.txt
echo "Second file" > /tmp/test-file-2.txt

# Kiểm thử tham chiếu một file
> /my-command /tmp/test-file.txt
# Xác minh nội dung file được đọc

# Kiểm thử file không tồn tại
> /my-command /tmp/nonexistent.txt
# Xác minh xử lý lỗi khéo léo

# Kiểm thử nhiều file
> /my-command /tmp/test-file.txt /tmp/test-file-2.txt
# Xác minh cả hai file được xử lý

# Kiểm thử file lớn
dd if=/dev/zero of=/tmp/large-file.bin bs=1M count=100
> /my-command /tmp/large-file.bin
# Xác minh hành vi hợp lý (có thể truncate hoặc cảnh báo)

# Dọn dẹp
rm /tmp/test-file*.txt /tmp/large-file.bin
```

### Cấp 6: Kiểm Thử Thực Thi Bash

**Những gì cần kiểm thử:**
- Lệnh !` thực thi đúng
- Output lệnh được đưa vào prompt
- Thất bại lệnh được xử lý
- Bảo mật: chỉ các lệnh được phép chạy

**Quy trình kiểm thử:**

```bash
# Tạo command kiểm thử với thực thi bash
cat > .claude/commands/test-bash.md << 'EOF'
---
description: Test bash execution
allowed-tools: Bash(echo:*), Bash(date:*)
---

Ngày hiện tại: !`date`
Output kiểm thử: !`echo "Hello from bash"`

Phân tích output trên...
EOF

# Kiểm thử trong Claude Code
> /test-bash
# Xác minh:
# 1. Ngày xuất hiện đúng
# 2. Output echo xuất hiện
# 3. Không có lỗi trong debug log

# Kiểm thử với lệnh không được phép (nên thất bại hoặc bị chặn)
cat > .claude/commands/test-forbidden.md << 'EOF'
---
description: Test forbidden command
allowed-tools: Bash(echo:*)
---

Thử lệnh bị cấm: !`ls -la /`
EOF

> /test-forbidden
# Xác minh: Bị từ chối quyền hoặc lỗi phù hợp
```

### Cấp 7: Kiểm Thử Tích Hợp

**Những gì cần kiểm thử:**
- Command hoạt động với các thành phần plugin khác
- Command tương tác đúng với nhau
- Quản lý trạng thái hoạt động qua các lần gọi
- Command workflow thực thi theo thứ tự

**Các kịch bản kiểm thử:**

**Kịch bản 1: Tích Hợp Command + Hook**

```bash
# Thiết lập: Command kích hoạt một hook
# Test: Gọi command, xác minh hook thực thi

# Command: .claude/commands/risky-operation.md
# Hook: PreToolUse validate thao tác

> /risky-operation
# Xác minh: Hook thực thi và validate trước khi command hoàn tất
```

**Kịch bản 2: Chuỗi Command**

```bash
# Thiết lập: Workflow nhiều command
> /workflow-init
# Xác minh: State file được tạo

> /workflow-step2
# Xác minh: State file được đọc, bước 2 thực thi

> /workflow-complete
# Xác minh: State file được dọn dẹp
```

**Kịch bản 3: Tích Hợp Command + MCP**

```bash
# Thiết lập: Command dùng tool MCP
# Test: Xác minh MCP server có thể truy cập

> /mcp-command
# Xác minh:
# 1. MCP server khởi động (nếu là stdio)
# 2. Gọi tool thành công
# 3. Kết quả được đưa vào output
```

## Các Cách Tiếp Cận Kiểm Thử Tự Động

### Bộ Kiểm Thử Command

Tạo script bộ kiểm thử:

```bash
#!/bin/bash
# test-commands.sh - Bộ kiểm thử command

TEST_DIR=".claude/commands"
FAILED_TESTS=0

echo "Bộ Kiểm Thử Command"
echo "=================="
echo

for cmd_file in "$TEST_DIR"/*.md; do
  cmd_name=$(basename "$cmd_file" .md)
  echo "Kiểm thử: $cmd_name"

  # Validate cấu trúc
  if ./validate-command.sh "$cmd_file"; then
    echo "  ✓ Cấu trúc hợp lệ"
  else
    echo "  ✗ Cấu trúc không hợp lệ"
    ((FAILED_TESTS++))
  fi

  # Validate frontmatter
  if ./validate-frontmatter.sh "$cmd_file"; then
    echo "  ✓ Frontmatter hợp lệ"
  else
    echo "  ✗ Frontmatter không hợp lệ"
    ((FAILED_TESTS++))
  fi

  echo
done

echo "=================="
echo "Kiểm thử hoàn tất"
echo "Thất bại: $FAILED_TESTS"

exit $FAILED_TESTS
```

### Pre-Commit Hook

Validate command trước khi commit:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Đang validate command..."

COMMANDS_CHANGED=$(git diff --cached --name-only | grep "\.claude/commands/.*\.md")

if [ -z "$COMMANDS_CHANGED" ]; then
  echo "Không có command nào thay đổi"
  exit 0
fi

for cmd in $COMMANDS_CHANGED; do
  echo "Đang kiểm tra: $cmd"

  if ! ./scripts/validate-command.sh "$cmd"; then
    echo "LỖI: Validation command thất bại: $cmd"
    exit 1
  fi
done

echo "✓ Tất cả command hợp lệ"
```

### Kiểm Thử Liên Tục

Kiểm thử command trong CI/CD:

```yaml
# .github/workflows/test-commands.yml
name: Test Commands

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Validate cấu trúc command
        run: |
          for cmd in .claude/commands/*.md; do
            echo "Kiểm thử: $cmd"
            ./scripts/validate-command.sh "$cmd"
          done

      - name: Validate frontmatter
        run: |
          for cmd in .claude/commands/*.md; do
            ./scripts/validate-frontmatter.sh "$cmd"
          done

      - name: Kiểm tra TODO
        run: |
          if grep -r "TODO" .claude/commands/; then
            echo "LỖI: Tìm thấy TODO trong command"
            exit 1
          fi
```

## Kiểm Thử Trường Hợp Biên

### Kiểm Thử Trường Hợp Biên

**Argument trống:**
```bash
> /cmd ""
> /cmd '' ''
```

**Ký tự đặc biệt:**
```bash
> /cmd "arg with spaces"
> /cmd arg-with-dashes
> /cmd arg_with_underscores
> /cmd arg/with/slashes
> /cmd 'arg with "quotes"'
```

**Argument dài:**
```bash
> /cmd $(python -c "print('a' * 10000)")
```

**Đường dẫn file bất thường:**
```bash
> /cmd ./file
> /cmd ../file
> /cmd ~/file
> /cmd "/path with spaces/file"
```

**Trường hợp biên lệnh Bash:**
```markdown
# Lệnh có thể thất bại
!`exit 1`
!`false`
!`command-that-does-not-exist`

# Lệnh với output đặc biệt
!`echo ""`
!`cat /dev/null`
!`yes | head -n 1000000`
```

## Kiểm Thử Hiệu Năng

### Kiểm Thử Thời Gian Phản Hồi

```bash
#!/bin/bash
# test-command-performance.sh

COMMAND="$1"

echo "Kiểm thử hiệu năng của /$COMMAND"
echo

for i in {1..5}; do
  echo "Lần chạy $i:"
  START=$(date +%s%N)

  # Gọi command (bước thủ công — ghi lại thời gian)
  echo "  Gọi: /$COMMAND"
  echo "  Thời gian bắt đầu: $START"
  echo "  (Ghi lại thời gian kết thúc thủ công)"
  echo
done

echo "Phân tích kết quả:"
echo "  - Thời gian phản hồi trung bình"
echo "  - Độ lệch"
echo "  - Ngưỡng chấp nhận được: < 3 giây cho command nhanh"
```

### Kiểm Thử Sử Dụng Tài Nguyên

```bash
# Theo dõi Claude Code trong khi thực thi command
# Trong terminal 1:
claude --debug

# Trong terminal 2:
watch -n 1 'ps aux | grep claude'

# Thực thi command và quan sát:
# - Sử dụng bộ nhớ
# - Sử dụng CPU
# - Số lượng process
```

## Kiểm Thử Trải Nghiệm Người Dùng

### Checklist Khả Dụng

- [ ] Tên command trực quan
- [ ] Mô tả rõ ràng trong `/help`
- [ ] Argument được ghi lại tốt
- [ ] Thông báo lỗi hữu ích
- [ ] Output định dạng dễ đọc
- [ ] Command chạy lâu hiển thị tiến độ
- [ ] Kết quả có thể thực thi được
- [ ] Trường hợp biên có UX tốt

### User Acceptance Testing

Tuyển người dùng kiểm thử:

```markdown
# Hướng Dẫn Kiểm Thử cho Beta Tester

## Command: /my-new-command

### Các Kịch Bản Kiểm Thử

1. **Cách dùng cơ bản:**
   - Chạy: `/my-new-command`
   - Mong đợi: [mô tả]
   - Đánh giá độ rõ ràng: 1–5

2. **Với argument:**
   - Chạy: `/my-new-command arg1 arg2`
   - Mong đợi: [mô tả]
   - Đánh giá tính hữu dụng: 1–5

3. **Trường hợp lỗi:**
   - Chạy: `/my-new-command invalid-input`
   - Mong đợi: Thông báo lỗi hữu ích
   - Đánh giá thông báo lỗi: 1–5

### Câu Hỏi Phản Hồi

1. Command có dễ hiểu không?
2. Output có đáp ứng kỳ vọng không?
3. Bạn sẽ thay đổi gì?
4. Bạn có dùng command này thường xuyên không?
```

## Checklist Kiểm Thử

Trước khi phát hành command:

### Cấu Trúc
- [ ] File ở đúng vị trí
- [ ] Phần mở rộng .md đúng
- [ ] YAML frontmatter hợp lệ (nếu có)
- [ ] Cú pháp Markdown đúng

### Chức Năng
- [ ] Command xuất hiện trong `/help`
- [ ] Mô tả rõ ràng
- [ ] Command thực thi không có lỗi
- [ ] Argument hoạt động như mong đợi
- [ ] Tham chiếu file hoạt động
- [ ] Thực thi Bash hoạt động (nếu dùng)

### Trường Hợp Biên
- [ ] Thiếu argument được xử lý
- [ ] Argument không hợp lệ được phát hiện
- [ ] File không tồn tại được xử lý
- [ ] Ký tự đặc biệt hoạt động
- [ ] Input dài được xử lý

### Tích Hợp
- [ ] Hoạt động với các command khác
- [ ] Hoạt động với hook (nếu có)
- [ ] Hoạt động với MCP (nếu có)
- [ ] Quản lý trạng thái hoạt động

### Chất Lượng
- [ ] Hiệu năng chấp nhận được
- [ ] Không có vấn đề bảo mật
- [ ] Thông báo lỗi hữu ích
- [ ] Output định dạng tốt
- [ ] Tài liệu đầy đủ

### Phân Phối
- [ ] Đã được người khác kiểm thử
- [ ] Phản hồi đã được tích hợp
- [ ] README đã cập nhật
- [ ] Ví dụ đã được cung cấp

## Debug Kiểm Thử Thất Bại

### Vấn Đề Phổ Biến và Giải Pháp

**Vấn đề: Command không xuất hiện trong /help**

```bash
# Kiểm tra vị trí file
ls -la .claude/commands/my-command.md

# Kiểm tra quyền
chmod 644 .claude/commands/my-command.md

# Kiểm tra cú pháp
head -n 20 .claude/commands/my-command.md

# Khởi động lại Claude Code
claude --debug
```

**Vấn đề: Argument không được thay thế**

```bash
# Xác minh cú pháp
grep '\$1' .claude/commands/my-command.md
grep '\$ARGUMENTS' .claude/commands/my-command.md

# Kiểm thử với command đơn giản trước
echo "Test: \$1 and \$2" > .claude/commands/test-args.md
```

**Vấn đề: Lệnh Bash không thực thi**

```bash
# Kiểm tra allowed-tools
grep "allowed-tools" .claude/commands/my-command.md

# Xác minh cú pháp lệnh
grep '!\`' .claude/commands/my-command.md

# Kiểm thử lệnh thủ công
date
echo "test"
```

**Vấn đề: Tham chiếu file không hoạt động**

```bash
# Kiểm tra cú pháp @
grep '@' .claude/commands/my-command.md

# Xác minh file tồn tại
ls -la /path/to/referenced/file

# Kiểm tra quyền
chmod 644 /path/to/referenced/file
```

## Nguyên Tắc Tốt Nhất

1. **Kiểm thử sớm, kiểm thử thường xuyên**: Validate khi đang phát triển
2. **Tự động hóa validation**: Dùng script cho các kiểm tra có thể lặp lại
3. **Kiểm thử trường hợp biên**: Đừng chỉ kiểm thử happy path
4. **Lấy phản hồi**: Để người khác kiểm thử trước khi phát hành rộng
5. **Ghi lại kiểm thử**: Giữ lại kịch bản kiểm thử để regression testing
6. **Theo dõi trên production**: Theo dõi vấn đề sau khi phát hành
7. **Lặp lại**: Cải thiện dựa trên dữ liệu sử dụng thực tế
