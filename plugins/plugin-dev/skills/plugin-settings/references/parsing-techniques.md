# Kỹ Thuật Phân Tích File Settings

Hướng dẫn đầy đủ về cách phân tích file `.claude/plugin-name.local.md` trong bash script.

## Cấu Trúc File

File settings dùng markdown với YAML frontmatter:

```markdown
---
field1: value1
field2: "value with spaces"
numeric_field: 42
boolean_field: true
list_field: ["item1", "item2", "item3"]
---

# Nội Dung Markdown

Nội dung body này có thể được trích xuất riêng.
Hữu ích cho prompt, tài liệu, hoặc ngữ cảnh bổ sung.
```

## Phân Tích Frontmatter

### Trích Xuất Khối Frontmatter

```bash
#!/bin/bash
FILE=".claude/my-plugin.local.md"

# Trích xuất tất cả nội dung giữa các marker --- (không bao gồm marker)
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")
```

**Cách hoạt động:**
- `sed -n` — Tắt in tự động
- `/^---$/,/^---$/` — Phạm vi từ `---` đầu đến `---` thứ hai
- `{ /^---$/d; p; }` — Xóa dòng `---`, in tất cả còn lại

### Trích Xuất Từng Trường

**Trường kiểu string:**
```bash
# Giá trị đơn giản
VALUE=$(echo "$FRONTMATTER" | grep '^field_name:' | sed 's/field_name: *//')

# Giá trị có dấu nháy (xóa dấu nháy bao quanh)
VALUE=$(echo "$FRONTMATTER" | grep '^field_name:' | sed 's/field_name: *//' | sed 's/^"\(.*\)"$/\1/')
```

**Trường boolean:**
```bash
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')

# Dùng trong điều kiện
if [[ "$ENABLED" == "true" ]]; then
  # Đã bật
fi
```

**Trường số:**
```bash
MAX=$(echo "$FRONTMATTER" | grep '^max_value:' | sed 's/max_value: *//')

# Validate là số
if [[ "$MAX" =~ ^[0-9]+$ ]]; then
  # Dùng trong so sánh số
  if [[ $MAX -gt 100 ]]; then
    # Quá lớn
  fi
fi
```

**Trường list (đơn giản):**
```bash
# YAML: list: ["item1", "item2", "item3"]
LIST=$(echo "$FRONTMATTER" | grep '^list:' | sed 's/list: *//')
# Kết quả: ["item1", "item2", "item3"]

# Để kiểm tra đơn giản:
if [[ "$LIST" == *"item1"* ]]; then
  # List chứa item1
fi
```

**Trường list (phân tích đúng với jq):**
```bash
# Để xử lý list đúng, dùng yq hoặc chuyển sang JSON
# Yêu cầu yq (brew install yq)

# Trích xuất list dưới dạng JSON array
LIST=$(echo "$FRONTMATTER" | yq -o json '.list' 2>/dev/null)

# Duyệt qua các item
echo "$LIST" | jq -r '.[]' | while read -r item; do
  echo "Đang xử lý: $item"
done
```

## Phân Tích Phần Body Markdown

### Trích Xuất Nội Dung Body

```bash
#!/bin/bash
FILE=".claude/my-plugin.local.md"

# Trích xuất tất cả sau dấu --- đóng
# Đếm marker ---: đầu tiên là mở, thứ hai là đóng, tất cả sau là body
BODY=$(awk '/^---$/{i++; next} i>=2' "$FILE")
```

**Cách hoạt động:**
- `/^---$/` — Khớp dòng `---`
- `{i++; next}` — Tăng counter và bỏ qua dòng `---`
- `i>=2` — In tất cả dòng sau `---` thứ hai

**Xử lý trường hợp biên:** Nếu `---` xuất hiện trong body markdown, cách phân tích vẫn hoạt động vì chúng ta chỉ đếm hai `---` đầu tiên ở đầu file.

### Dùng Body Làm Prompt

```bash
# Trích xuất body
PROMPT=$(awk '/^---$/{i++; next} i>=2' "$RALPH_STATE_FILE")

# Đưa lại cho Claude
echo '{"decision": "block", "reason": "'"$PROMPT"'"}' | jq .
```

**Quan trọng:** Dùng `jq -n --arg` để xây dựng JSON an toàn hơn với nội dung của người dùng:

```bash
PROMPT=$(awk '/^---$/{i++; next} i>=2' "$FILE")

# Xây dựng JSON an toàn
jq -n --arg prompt "$PROMPT" '{
  "decision": "block",
  "reason": $prompt
}'
```

## Các Pattern Phân Tích Phổ Biến

### Pattern: Trường với Giá Trị Mặc Định

```bash
VALUE=$(echo "$FRONTMATTER" | grep '^field:' | sed 's/field: *//' | sed 's/^"\(.*\)"$/\1/')

# Dùng giá trị mặc định nếu trống
if [[ -z "$VALUE" ]]; then
  VALUE="default_value"
fi
```

### Pattern: Trường Tùy Chọn

```bash
OPTIONAL=$(echo "$FRONTMATTER" | grep '^optional_field:' | sed 's/optional_field: *//' | sed 's/^"\(.*\)"$/\1/')

# Chỉ dùng nếu có
if [[ -n "$OPTIONAL" ]] && [[ "$OPTIONAL" != "null" ]]; then
  # Trường đã được đặt, dùng nó
  echo "Optional field: $OPTIONAL"
fi
```

### Pattern: Nhiều Trường Cùng Lúc

```bash
# Phân tích tất cả trường trong một lần duyệt
while IFS=': ' read -r key value; do
  # Xóa dấu nháy nếu có
  value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/')

  case "$key" in
    enabled)
      ENABLED="$value"
      ;;
    mode)
      MODE="$value"
      ;;
    max_size)
      MAX_SIZE="$value"
      ;;
  esac
done <<< "$FRONTMATTER"
```

## Cập Nhật File Settings

### Cập Nhật Atomic

Luôn dùng temp file + atomic move để ngăn file bị hỏng:

```bash
#!/bin/bash
FILE=".claude/my-plugin.local.md"
NEW_VALUE="updated_value"

# Tạo temp file
TEMP_FILE="${FILE}.tmp.$$"

# Cập nhật trường dùng sed
sed "s/^field_name: .*/field_name: $NEW_VALUE/" "$FILE" > "$TEMP_FILE"

# Thay thế atomic
mv "$TEMP_FILE" "$FILE"
```

### Cập Nhật Một Trường

```bash
# Tăng iteration counter
CURRENT=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
NEXT=$((CURRENT + 1))

# Cập nhật file
TEMP_FILE="${FILE}.tmp.$$"
sed "s/^iteration: .*/iteration: $NEXT/" "$FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$FILE"
```

### Cập Nhật Nhiều Trường

```bash
# Cập nhật nhiều trường cùng lúc
TEMP_FILE="${FILE}.tmp.$$"

sed -e "s/^iteration: .*/iteration: $NEXT_ITERATION/" \
    -e "s/^pr_number: .*/pr_number: $PR_NUMBER/" \
    -e "s/^status: .*/status: $NEW_STATUS/" \
    "$FILE" > "$TEMP_FILE"

mv "$TEMP_FILE" "$FILE"
```

## Kỹ Thuật Validation

### Validate File Tồn Tại và Có Thể Đọc

```bash
FILE=".claude/my-plugin.local.md"

if [[ ! -f "$FILE" ]]; then
  echo "Không tìm thấy file settings" >&2
  exit 1
fi

if [[ ! -r "$FILE" ]]; then
  echo "Không thể đọc file settings" >&2
  exit 1
fi
```

### Validate Cấu Trúc Frontmatter

```bash
# Đếm marker --- (phải đúng 2 ở đầu)
MARKER_COUNT=$(grep -c '^---$' "$FILE" 2>/dev/null || echo "0")

if [[ $MARKER_COUNT -lt 2 ]]; then
  echo "File settings không hợp lệ: thiếu marker frontmatter" >&2
  exit 1
fi
```

### Validate Giá Trị Trường

```bash
MODE=$(echo "$FRONTMATTER" | grep '^mode:' | sed 's/mode: *//')

case "$MODE" in
  strict|standard|lenient)
    # Mode hợp lệ
    ;;
  *)
    echo "Mode không hợp lệ: $MODE (phải là strict, standard, hoặc lenient)" >&2
    exit 1
    ;;
esac
```

### Validate Phạm Vi Số

```bash
MAX_SIZE=$(echo "$FRONTMATTER" | grep '^max_size:' | sed 's/max_size: *//')

if ! [[ "$MAX_SIZE" =~ ^[0-9]+$ ]]; then
  echo "max_size phải là một số" >&2
  exit 1
fi

if [[ $MAX_SIZE -lt 1 ]] || [[ $MAX_SIZE -gt 10000000 ]]; then
  echo "max_size ngoài phạm vi (1–10000000)" >&2
  exit 1
fi
```

## Trường Hợp Biên và Lưu Ý

### Dấu Nháy trong Giá Trị

YAML cho phép cả chuỗi có dấu nháy và không có dấu nháy:

```yaml
# Các giá trị này tương đương:
field1: value
field2: "value"
field3: 'value'
```

**Xử lý cả hai:**
```bash
# Xóa dấu nháy bao quanh nếu có
VALUE=$(echo "$FRONTMATTER" | grep '^field:' | sed 's/field: *//' | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\\(.*\\)'$/\\1/")
```

### --- trong Body Markdown

Nếu body markdown chứa `---`, cách phân tích vẫn hoạt động vì chúng ta chỉ khớp hai dấu đầu tiên:

```markdown
---
field: value
---

# Body

Đây là dấu phân cách:
---

Nội dung thêm sau dấu phân cách.
```

Pattern `awk '/^---$/{i++; next} i>=2'` xử lý trường hợp này đúng.

### Giá Trị Trống

Xử lý trường thiếu hoặc trống:

```yaml
field1:
field2: ""
field3: null
```

**Phân tích:**
```bash
VALUE=$(echo "$FRONTMATTER" | grep '^field1:' | sed 's/field1: *//')
# VALUE sẽ là chuỗi rỗng

# Kiểm tra trống/null
if [[ -z "$VALUE" ]] || [[ "$VALUE" == "null" ]]; then
  VALUE="default"
fi
```

### Ký Tự Đặc Biệt

Giá trị với ký tự đặc biệt cần xử lý cẩn thận:

```yaml
message: "Error: Something went wrong!"
path: "/path/with spaces/file.txt"
regex: "^[a-zA-Z0-9_]+$"
```

**Phân tích an toàn:**
```bash
# Luôn đặt biến trong dấu nháy khi dùng
MESSAGE=$(echo "$FRONTMATTER" | grep '^message:' | sed 's/message: *//' | sed 's/^"\(.*\)"$/\1/')

echo "Message: $MESSAGE"  # Đặt trong dấu nháy!
```

## Tối Ưu Hiệu Năng

### Cache Giá Trị Đã Phân Tích

Nếu đọc settings nhiều lần:

```bash
# Phân tích một lần
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")

# Trích xuất nhiều trường từ frontmatter đã cache
FIELD1=$(echo "$FRONTMATTER" | grep '^field1:' | sed 's/field1: *//')
FIELD2=$(echo "$FRONTMATTER" | grep '^field2:' | sed 's/field2: *//')
FIELD3=$(echo "$FRONTMATTER" | grep '^field3:' | sed 's/field3: *//')
```

**Không nên:** Phân tích lại file cho mỗi trường.

### Lazy Loading

Chỉ phân tích settings khi cần:

```bash
#!/bin/bash
input=$(cat)

# Kiểm tra nhanh trước (không có I/O file)
tool_name=$(echo "$input" | jq -r '.tool_name')
if [[ "$tool_name" != "Write" ]]; then
  exit 0  # Không phải thao tác ghi, bỏ qua
fi

# Chỉ lúc này mới kiểm tra file settings
if [[ -f ".claude/my-plugin.local.md" ]]; then
  # Phân tích settings
  # ...
fi
```

## Debug

### In Giá Trị Đã Phân Tích

```bash
#!/bin/bash
set -x  # Bật debug tracing

FILE=".claude/my-plugin.local.md"

if [[ -f "$FILE" ]]; then
  echo "Tìm thấy file settings" >&2

  FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")
  echo "Frontmatter:" >&2
  echo "$FRONTMATTER" >&2

  ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')
  echo "Enabled: $ENABLED" >&2
fi
```

### Validate Kết Quả Phân Tích

```bash
# Hiển thị những gì đã được phân tích
echo "Các giá trị đã phân tích:" >&2
echo "  enabled: $ENABLED" >&2
echo "  mode: $MODE" >&2
echo "  max_size: $MAX_SIZE" >&2

# Xác minh giá trị mong đợi
if [[ "$ENABLED" != "true" ]] && [[ "$ENABLED" != "false" ]]; then
  echo "⚠️  Giá trị enabled bất thường: $ENABLED" >&2
fi
```

## Thay Thế: Dùng yq

Đối với YAML phức tạp, cân nhắc dùng `yq`:

```bash
# Cài đặt: brew install yq

# Phân tích YAML đúng chuẩn
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")

# Trích xuất trường với yq
ENABLED=$(echo "$FRONTMATTER" | yq '.enabled')
MODE=$(echo "$FRONTMATTER" | yq '.mode')
LIST=$(echo "$FRONTMATTER" | yq -o json '.list_field')

# Duyệt list đúng chuẩn
echo "$LIST" | jq -r '.[]' | while read -r item; do
  echo "Item: $item"
done
```

**Ưu điểm:**
- Phân tích YAML đúng chuẩn
- Xử lý cấu trúc phức tạp
- Hỗ trợ list/object tốt hơn

**Nhược điểm:**
- Yêu cầu cài đặt yq
- Dependency bổ sung
- Có thể không có sẵn trên mọi hệ thống

**Khuyến nghị:** Dùng sed/grep cho trường đơn giản, yq cho cấu trúc phức tạp.

## Ví Dụ Hoàn Chỉnh

```bash
#!/bin/bash
set -euo pipefail

# Cấu hình
SETTINGS_FILE=".claude/my-plugin.local.md"

# Thoát nhanh nếu chưa cấu hình
if [[ ! -f "$SETTINGS_FILE" ]]; then
  # Dùng giá trị mặc định
  ENABLED=true
  MODE=standard
  MAX_SIZE=1000000
else
  # Phân tích frontmatter
  FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SETTINGS_FILE")

  # Trích xuất trường với giá trị mặc định
  ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')
  ENABLED=${ENABLED:-true}

  MODE=$(echo "$FRONTMATTER" | grep '^mode:' | sed 's/mode: *//' | sed 's/^"\(.*\)"$/\1/')
  MODE=${MODE:-standard}

  MAX_SIZE=$(echo "$FRONTMATTER" | grep '^max_size:' | sed 's/max_size: *//')
  MAX_SIZE=${MAX_SIZE:-1000000}

  # Validate giá trị
  if [[ "$ENABLED" != "true" ]] && [[ "$ENABLED" != "false" ]]; then
    echo "⚠️  Giá trị enabled không hợp lệ, dùng mặc định" >&2
    ENABLED=true
  fi

  if ! [[ "$MAX_SIZE" =~ ^[0-9]+$ ]]; then
    echo "⚠️  max_size không hợp lệ, dùng mặc định" >&2
    MAX_SIZE=1000000
  fi
fi

# Thoát nhanh nếu bị tắt
if [[ "$ENABLED" != "true" ]]; then
  exit 0
fi

# Dùng cấu hình
echo "Cấu hình đã tải: mode=$MODE, max_size=$MAX_SIZE" >&2

# Áp dụng logic dựa trên settings
case "$MODE" in
  strict)
    # Validation chặt
    ;;
  standard)
    # Validation tiêu chuẩn
    ;;
  lenient)
    # Validation lỏng
    ;;
esac
```

Ví dụ này cung cấp xử lý settings mạnh mẽ với giá trị mặc định, validation và phục hồi lỗi.
