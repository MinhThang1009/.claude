# Các Cân Nhắc Marketplace cho Command

Hướng dẫn tạo command được thiết kế để phân phối và thành công trên marketplace.

## Tổng Quan

Command phân phối qua marketplace cần cân nhắc thêm so với command dùng cá nhân. Chúng phải hoạt động trên nhiều môi trường, xử lý các trường hợp sử dụng đa dạng và mang lại trải nghiệm người dùng xuất sắc cho những người dùng chưa biết.

## Thiết Kế Cho Phân Phối

### Tương Thích Đa Nền Tảng

**Cân nhắc cross-platform:**

```markdown
---
description: Cross-platform command
allowed-tools: Bash(*)
---

# Platform-Aware Command

Đang phát hiện nền tảng...

case "$(uname)" in
  Darwin*)  PLATFORM="macOS" ;;
  Linux*)   PLATFORM="Linux" ;;
  MINGW*|MSYS*|CYGWIN*) PLATFORM="Windows" ;;
  *)        PLATFORM="Unknown" ;;
esac

Nền tảng: $PLATFORM

<!-- Điều chỉnh hành vi theo nền tảng -->
if [ "$PLATFORM" = "Windows" ]; then
  # Xử lý Windows
  PATH_SEP="\\"
  NULL_DEVICE="NUL"
else
  # Xử lý Unix-like
  PATH_SEP="/"
  NULL_DEVICE="/dev/null"
fi

[Triển khai phù hợp với nền tảng...]
```

**Tránh lệnh đặc thù nền tảng:**

```markdown
<!-- XẤU: Chỉ chạy trên macOS -->
!`pbcopy < file.txt`

<!-- TỐT: Phát hiện nền tảng -->
if command -v pbcopy > /dev/null; then
  pbcopy < file.txt
elif command -v xclip > /dev/null; then
  xclip -selection clipboard < file.txt
elif command -v clip.exe > /dev/null; then
  cat file.txt | clip.exe
else
  echo "Clipboard không khả dụng trên nền tảng này"
fi
```

### Dependency Tối Thiểu

**Kiểm tra các tool cần thiết:**

```markdown
---
description: Dependency-aware command
allowed-tools: Bash(*)
---

# Check Dependencies

Các tool cần thiết:
- git
- jq
- node

Đang kiểm tra tình trạng...

MISSING_DEPS=""

for tool in git jq node; do
  if ! command -v $tool > /dev/null; then
    MISSING_DEPS="$MISSING_DEPS $tool"
  fi
done

if [ -n "$MISSING_DEPS" ]; then
  ❌ LỖI: Thiếu dependency:$MISSING_DEPS

  HƯỚNG DẪN CÀI ĐẶT:
  - git: https://git-scm.com/downloads
  - jq: https://stedolan.github.io/jq/download/
  - node: https://nodejs.org/

  Cài đặt các tool còn thiếu và thử lại.

  Thoát.
fi

✓ Tất cả dependency đã có

[Tiếp tục với command...]
```

**Ghi lại dependency tùy chọn:**

```markdown
<!--
DEPENDENCIES:
  Bắt buộc:
  - git 2.0+: Version control
  - jq 1.6+: Xử lý JSON

  Tùy chọn:
  - gh: GitHub CLI (cho thao tác PR)
  - docker: Thao tác container (cho test trong container)

  Tính năng có sẵn phụ thuộc vào tool đã cài đặt.
-->
```

### Xuống Cấp Khéo Léo

**Xử lý tính năng thiếu:**

```markdown
---
description: Feature-aware command
---

# Feature Detection

Đang phát hiện tính năng có sẵn...

FEATURES=""

if command -v gh > /dev/null; then
  FEATURES="$FEATURES github"
fi

if command -v docker > /dev/null; then
  FEATURES="$FEATURES docker"
fi

Tính năng có sẵn: $FEATURES

if echo "$FEATURES" | grep -q "github"; then
  # Chức năng đầy đủ với GitHub integration
  echo "✓ GitHub integration có sẵn"
else
  # Chức năng hạn chế khi không có GitHub
  echo "⚠ Chức năng hạn chế: GitHub CLI chưa cài đặt"
  echo "  Cài 'gh' để có đầy đủ tính năng"
fi

[Thích nghi hành vi dựa trên tính năng có sẵn...]
```

## Trải Nghiệm Người Dùng Cho Người Dùng Chưa Biết

### Onboarding Rõ Ràng

**Trải nghiệm lần chạy đầu tiên:**

```markdown
---
description: Command with onboarding
allowed-tools: Read, Write
---

# First Run Check

if [ ! -f ".claude/command-initialized" ]; then
  **Chào mừng đến với Command Name!**

  Có vẻ đây là lần đầu bạn dùng command này.

  COMMAND NÀY LÀM GÌ:
  [Giải thích ngắn gọn về mục đích và lợi ích]

  BẮTĐẦU NHANH:
  1. Cách dùng cơ bản: /command [arg]
  2. Để xem trợ giúp: /command help
  3. Ví dụ: /command examples

  CÀI ĐẶT:
  Không cần cài đặt thêm. Bạn đã sẵn sàng!

  ✓ Khởi tạo hoàn tất

  [Tạo marker khởi tạo]

  Sẵn sàng xử lý yêu cầu của bạn...
fi

[Thực thi command bình thường...]
```

**Khám phá tính năng dần dần:**

```markdown
---
description: Command with tips
---

# Command Execution

[Chức năng chính...]

---

💡 MẸO: Bạn có biết?

Bạn có thể tăng tốc command này với flag --fast:
  /command --fast [args]

Để xem thêm mẹo: /command tips
```

### Xử Lý Lỗi Toàn Diện

**Dự đoán lỗi của người dùng:**

```markdown
---
description: Forgiving command
---

# User Input Handling

Argument: "$1"

<!-- Kiểm tra lỗi đánh máy phổ biến -->
if [ "$1" = "hlep" ] || [ "$1" = "hepl" ]; then
  Bạn có muốn gõ: help?

  Đang hiển thị help thay...
  [Hiển thị help]

  Thoát.
fi

<!-- Gợi ý lệnh tương tự nếu không tìm thấy -->
if [ "$1" != "valid-option1" ] && [ "$1" != "valid-option2" ]; then
  ❌ Tùy chọn không xác định: $1

  Bạn có muốn nói:
  - valid-option1 (tương tự nhất)
  - valid-option2

  Để xem tất cả tùy chọn: /command help

  Thoát.
fi

[Command tiếp tục...]
```

**Thông tin chẩn đoán hữu ích:**

```markdown
---
description: Diagnostic command
---

# Operation Failed

Thao tác không thể hoàn thành.

**Thông Tin Chẩn Đoán:**

Môi trường:
- Nền tảng: $(uname)
- Shell: $SHELL
- Thư mục làm việc: $(pwd)
- Command: /command $@

Đang kiểm tra các vấn đề phổ biến:
- Git repository: $(git rev-parse --git-dir 2>&1)
- Quyền ghi: $(test -w . && echo "OK" || echo "BỊ TỪ CHỐI")
- File cần thiết: $(test -f config.yml && echo "Tìm thấy" || echo "Thiếu")

Thông tin này giúp debug vấn đề.

Để được hỗ trợ, hãy kèm theo thông tin chẩn đoán trên.
```

## Nguyên Tắc Tốt Nhất Khi Phân Phối

### Ý Thức về Namespace

**Tránh va chạm tên:**

```markdown
---
description: Namespaced command
---

<!--
TÊN COMMAND: plugin-name-command

Command này có namespace theo tên plugin để tránh
conflict với command từ plugin khác.

Các cách đặt tên thay thế:
- Dùng prefix plugin: /plugin-command
- Dùng category: /category-command
- Dùng verb-noun: /verb-noun

Cách chọn: prefix plugin-name
Lý do: Rõ ràng nhất về ownership, ít khả năng conflict nhất
-->

# Plugin Name Command

[Triển khai...]
```

**Ghi lại lý do đặt tên:**

```markdown
<!--
QUYẾT ĐỊNH ĐẶT TÊN:

Tên command: /deploy-app

Các phương án đã cân nhắc:
- /deploy: Quá chung, dễ conflict
- /app-deploy: Thứ tự ít trực quan hơn
- /my-plugin-deploy: Quá dài dòng

Lựa chọn cuối cân bằng:
- Dễ khám phá (mục đích rõ ràng)
- Ngắn gọn (dễ gõ)
- Độc đáo (ít khả năng conflict)
-->
```

### Khả Năng Cấu Hình

**Preferences của người dùng:**

```markdown
---
description: Configurable command
allowed-tools: Read
---

# Load User Configuration

Cấu hình mặc định:
- verbose: false
- color: true
- max_results: 10

Đang kiểm tra cấu hình người dùng: .claude/plugin-name.local.md

if [ -f ".claude/plugin-name.local.md" ]; then
  # Parse YAML frontmatter để lấy cài đặt
  VERBOSE=$(grep "^verbose:" .claude/plugin-name.local.md | cut -d: -f2 | tr -d ' ')
  COLOR=$(grep "^color:" .claude/plugin-name.local.md | cut -d: -f2 | tr -d ' ')
  MAX_RESULTS=$(grep "^max_results:" .claude/plugin-name.local.md | cut -d: -f2 | tr -d ' ')

  echo "✓ Đang dùng cấu hình người dùng"
else
  echo "Đang dùng cấu hình mặc định"
  echo "Tạo .claude/plugin-name.local.md để tùy chỉnh"
fi

[Dùng cấu hình trong command...]
```

**Giá trị mặc định hợp lý:**

```markdown
---
description: Command with smart defaults
---

# Smart Defaults

Cấu hình:
- Format: ${FORMAT:-json}  # Mặc định là json
- Output: ${OUTPUT:-stdout}  # Mặc định là stdout
- Verbose: ${VERBOSE:-false}  # Mặc định là false

Các giá trị mặc định này phù hợp với 80% trường hợp sử dụng.

Ghi đè bằng argument:
  /command --format yaml --output file.txt --verbose

Hoặc đặt trong .claude/plugin-name.local.md:
\`\`\`yaml
---
format: yaml
output: custom.txt
verbose: true
---
\`\`\`
```

### Tương Thích Phiên Bản

**Kiểm tra phiên bản:**

```markdown
---
description: Version-aware command
---

<!--
COMMAND VERSION: 2.1.0

TƯƠNG THÍCH:
- Yêu cầu phiên bản plugin: >= 2.0.0
- Breaking change từ v1.x được ghi trong MIGRATION.md

LỊCH SỬ PHIÊN BẢN:
- v2.1.0: Thêm flag --new-feature
- v2.0.0: BREAKING: Đổi thứ tự argument
- v1.0.0: Phát hành lần đầu
-->

# Version Check

Phiên bản command: 2.1.0
Phiên bản plugin: [phát hiện từ plugin.json]

if [  "$PLUGIN_VERSION" < "2.0.0" ]; then
  ❌ LỖI: Phiên bản plugin không tương thích

  Command này yêu cầu phiên bản plugin >= 2.0.0
  Phiên bản hiện tại: $PLUGIN_VERSION

  Cập nhật plugin:
    /plugin update plugin-name

  Thoát.
fi

✓ Phiên bản tương thích

[Command tiếp tục...]
```

**Cảnh báo deprecated:**

```markdown
---
description: Command with deprecation warnings
---

# Deprecation Check

if [ "$1" = "--old-flag" ]; then
  ⚠️  CẢNH BÁO DEPRECATED

  Tùy chọn --old-flag đã deprecated từ v2.0.0
  Sẽ bị xóa trong v3.0.0 (ước tính tháng 6 năm 2025)

  Dùng thay thế: --new-flag

  Ví dụ:
    Cũ: /command --old-flag value
    Mới: /command --new-flag value

  Xem hướng dẫn migration: /command migrate

  Đang tiếp tục với hành vi deprecated tạm thời...
fi

[Xử lý cả flag cũ và mới trong thời gian deprecated...]
```

## Thể Hiện Trên Marketplace

### Khám Phá Command

**Đặt tên mô tả:**

```markdown
---
description: Review pull request with security and quality checks
---

<!-- TỐT: Tên và mô tả rõ ràng -->
```

```markdown
---
description: Do the thing
---

<!-- XẤU: Mô tả mơ hồ -->
```

**Từ khóa có thể tìm kiếm:**

```markdown
<!--
KEYWORDS: security, code-review, quality, validation, audit

Các từ khóa này giúp người dùng khám phá command khi tìm kiếm
chức năng liên quan trên marketplace.
-->
```

### Ví Dụ Demo Ấn Tượng

**Minh họa hấp dẫn:**

```markdown
---
description: Advanced code analysis command
---

# Code Analysis Command

Command này thực hiện phân tích code sâu với insight có thể thực thi.

## Demo: Kiểm Tra Bảo Mật Nhanh

Thử ngay:
\`\`\`
/analyze-code src/ --security
\`\`\`

**Những gì bạn nhận được:**
- Phát hiện lỗ hổng bảo mật
- Metrics chất lượng code
- Xác định điểm nghẽn hiệu năng
- Khuyến nghị có thể thực thi

**Output mẫu:**
\`\`\`
Security Analysis Results
=========================

🔴 Critical (2):
  - SQL injection risk in users.js:45
  - XSS vulnerability in display.js:23

🟡 Warnings (5):
  - Unvalidated input in api.js:67
  ...

Recommendations:
1. Sửa vấn đề critical ngay lập tức
2. Review warning trước release tiếp theo
3. Chạy /analyze-code --fix để sửa tự động
\`\`\`

---

Sẵn sàng phân tích code của bạn...

[Triển khai command...]
```

### Đánh Giá và Phản Hồi Người Dùng

**Cơ chế phản hồi:**

```markdown
---
description: Command with feedback
---

# Command Complete

[Kết quả command...]

---

**Trải nghiệm của bạn thế nào?**

Điều này giúp cải thiện command cho mọi người.

Đánh giá command này:
- 👍 Hữu ích
- 👎 Không hữu ích
- 🐛 Tìm thấy bug
- 💡 Có đề xuất

Trả lời bằng emoji hoặc:
- /command feedback

Phản hồi của bạn rất quan trọng!
```

**Chuẩn bị cho analytics:**

```markdown
<!--
GHI CHÚ ANALYTICS:

Theo dõi để cải thiện:
- Argument phổ biến nhất
- Tỷ lệ thất bại
- Thời gian thực thi trung bình
- Điểm hài lòng người dùng

Bảo vệ privacy:
- Không có thông tin nhận dạng cá nhân
- Chỉ thống kê tổng hợp
- Tôn trọng opt-out của người dùng
-->
```

## Tiêu Chuẩn Chất Lượng

### Đánh Bóng Chuyên Nghiệp

**Branding nhất quán:**

```markdown
---
description: Branded command
---

# ✨ Command Name

Một phần của bộ [Plugin Name]

[Chức năng command...]

---

**Cần Trợ Giúp?**
- Tài liệu: https://docs.example.com
- Hỗ trợ: support@example.com
- Cộng đồng: https://community.example.com

Powered by Plugin Name v2.1.0
```

**Chú ý đến chi tiết:**

```markdown
<!-- Những chi tiết quan trọng -->

✓ Dùng emoji/symbol nhất quán
✓ Căn chỉnh cột output gọn gàng
✓ Định dạng số với dấu phân cách hàng nghìn
✓ Dùng màu sắc/định dạng đúng cách
✓ Cung cấp progress indicator
✓ Hiển thị thời gian còn lại ước tính
✓ Xác nhận thao tác thành công
```

### Độ Tin Cậy

**Idempotency:**

```markdown
---
description: Idempotent command
---

# Safe Repeated Execution

Đang kiểm tra xem thao tác đã hoàn thành chưa...

if [ -f ".claude/operation-completed.flag" ]; then
  ℹ️  Thao tác đã hoàn thành

  Hoàn thành lúc: $(cat .claude/operation-completed.flag)

  Để chạy lại:
  1. Xóa flag: rm .claude/operation-completed.flag
  2. Chạy lại command

  Nếu không, không cần hành động gì.

  Thoát.
fi

Đang thực hiện thao tác...

[Thao tác an toàn, có thể lặp lại...]

Đang đánh dấu hoàn thành...
echo "$(date)" > .claude/operation-completed.flag
```

**Thao tác atomic:**

```markdown
---
description: Atomic command
---

# Atomic Operation

Thao tác này là atomic — hoặc thành công hoàn toàn hoặc thất bại hoàn toàn.

Đang tạo workspace tạm thời...
TEMP_DIR=$(mktemp -d)

Thực hiện thay đổi trong môi trường cách ly...
[Thực hiện thay đổi trong $TEMP_DIR]

if [ $? -eq 0 ]; then
  ✓ Thay đổi đã được validate

  Đang áp dụng thay đổi theo kiểu atomic...
  mv $TEMP_DIR/* ./target/

  ✓ Thao tác hoàn tất
else
  ❌ Thay đổi không qua validation

  Đang rollback...
  rm -rf $TEMP_DIR

  Không có thay đổi nào được áp dụng. An toàn để thử lại.
fi
```

## Kiểm Thử Để Phân Phối

### Checklist Trước Khi Phát Hành

```markdown
<!--
CHECKLIST TRƯỚC KHI PHÁT HÀNH:

Chức năng:
- [ ] Hoạt động trên macOS
- [ ] Hoạt động trên Linux
- [ ] Hoạt động trên Windows (WSL)
- [ ] Tất cả argument đã test
- [ ] Các trường hợp lỗi đã xử lý
- [ ] Các trường hợp biên đã cover

Trải nghiệm người dùng:
- [ ] Mô tả rõ ràng
- [ ] Thông báo lỗi hữu ích
- [ ] Ví dụ đã được cung cấp
- [ ] Trải nghiệm lần đầu tốt
- [ ] Tài liệu đầy đủ

Phân phối:
- [ ] Không có đường dẫn hardcoded
- [ ] Dependency đã ghi lại
- [ ] Tùy chọn cấu hình rõ ràng
- [ ] Số phiên bản đã đặt
- [ ] Changelog đã cập nhật

Chất lượng:
- [ ] Không có TODO comment
- [ ] Không có debug code
- [ ] Hiệu năng chấp nhận được
- [ ] Đã review bảo mật
- [ ] Đã cân nhắc privacy

Hỗ trợ:
- [ ] README đầy đủ
- [ ] Hướng dẫn troubleshooting
- [ ] Thông tin liên hệ hỗ trợ đã cung cấp
- [ ] Cơ chế phản hồi đã có
- [ ] License đã chỉ định
-->
```

### Beta Testing

**Cách tiếp cận phát hành beta:**

```markdown
---
description: Beta command (v0.9.0)
---

# 🧪 Beta Command

**Đây là phiên bản beta**

Tính năng có thể thay đổi dựa trên phản hồi.

TRẠNG THÁI BETA:
- Phiên bản: 0.9.0
- Độ ổn định: Thực nghiệm
- Hỗ trợ: Hạn chế
- Phản hồi: Được khuyến khích

Hạn chế đã biết:
- Hiệu năng chưa tối ưu
- Một số trường hợp biên chưa xử lý
- Tài liệu chưa đầy đủ

Giúp cải thiện command này:
- Báo cáo vấn đề: /command report-issue
- Đề xuất tính năng: /command suggest
- Tham gia beta tester: /command join-beta

---

[Triển khai command...]

---

**Cảm ơn bạn đã beta testing!**

Phản hồi của bạn giúp command này tốt hơn.
```

## Bảo Trì và Cập Nhật

### Chiến Lược Cập Nhật

**Command có phiên bản:**

```markdown
<!--
CHIẾN LƯỢC PHIÊN BẢN:

Major (X.0.0): Breaking change
- Ghi lại tất cả breaking change
- Cung cấp hướng dẫn migration
- Hỗ trợ phiên bản cũ ngắn hạn

Minor (x.Y.0): Tính năng mới
- Backward compatible
- Thông báo tính năng mới
- Cập nhật ví dụ

Patch (x.y.Z): Sửa bug
- Không thay đổi UI
- Cập nhật changelog
- Ưu tiên sửa bảo mật

Lịch trình phát hành:
- Patch: Khi cần
- Minor: Hàng tháng
- Major: Hàng năm hoặc khi cần
-->
```

**Thông báo cập nhật:**

```markdown
---
description: Update-aware command
---

# Check for Updates

Phiên bản hiện tại: 2.1.0
Phiên bản mới nhất: [kiểm tra nếu có sẵn]

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
  📢 CÓ CẬP NHẬT

  Phiên bản mới: $LATEST_VERSION
  Hiện tại: $CURRENT_VERSION

  Có gì mới:
  - Cải thiện tính năng
  - Sửa bug
  - Cải thiện hiệu năng

  Cập nhật với:
    /plugin update plugin-name

  Release notes: https://releases.example.com/v$LATEST_VERSION
fi

[Command tiếp tục...]
```

## Tóm Tắt Nguyên Tắc Tốt Nhất

### Thiết Kế Phân Phối

1. **Universal**: Hoạt động trên các nền tảng và môi trường khác nhau
2. **Self-contained**: Dependency tối thiểu, yêu cầu rõ ràng
3. **Graceful**: Xuống cấp khéo léo khi thiếu tính năng
4. **Forgiving**: Dự đoán và xử lý lỗi của người dùng
5. **Helpful**: Lỗi rõ ràng, mặc định tốt, tài liệu xuất sắc

### Thành Công Trên Marketplace

1. **Discoverable**: Tên rõ ràng, mô tả tốt, từ khóa có thể tìm kiếm
2. **Professional**: Thể hiện chuyên nghiệp, branding nhất quán
3. **Reliable**: Test kỹ lưỡng, xử lý trường hợp biên
4. **Maintainable**: Có phiên bản, cập nhật thường xuyên, có hỗ trợ
5. **User-focused**: UX tốt, phản hồi nhanh với feedback

### Tiêu Chuẩn Chất Lượng

1. **Complete**: Tài liệu đầy đủ, tất cả tính năng hoạt động
2. **Tested**: Hoạt động trong môi trường thực, xử lý trường hợp biên
3. **Secure**: Không có lỗ hổng, thao tác an toàn
4. **Performant**: Tốc độ hợp lý, tiết kiệm tài nguyên
5. **Ethical**: Tôn trọng privacy, có sự đồng ý của người dùng

Với những cân nhắc này, command trở nên sẵn sàng cho marketplace và làm hài lòng người dùng trên nhiều môi trường và trường hợp sử dụng đa dạng.
