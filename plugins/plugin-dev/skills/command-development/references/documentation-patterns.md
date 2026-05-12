# Các Pattern Tài Liệu cho Command

Chiến lược tạo command tự tài liệu hóa, dễ bảo trì và mang lại trải nghiệm người dùng xuất sắc.

## Tổng quan

Command được tài liệu hóa tốt thì dễ sử dụng, dễ bảo trì và dễ phân phối hơn. Tài liệu nên được nhúng trực tiếp vào command, giúp người dùng và người bảo trì truy cập ngay lập tức.

## Cấu Trúc Command Tự Tài Liệu Hóa

### Template Command Hoàn Chỉnh

```markdown
---
description: Clear, actionable description under 60 chars
argument-hint: [arg1] [arg2] [optional-arg]
allowed-tools: Read, Bash(git:*)
model: sonnet
---

<!--
COMMAND: command-name
VERSION: 1.0.0
AUTHOR: Team Name
LAST UPDATED: 2025-01-15

PURPOSE:
Giải thích chi tiết command này làm gì và tại sao nó tồn tại.

USAGE:
  /command-name arg1 arg2

ARGUMENTS:
  arg1: Mô tả argument đầu tiên (bắt buộc)
  arg2: Mô tả argument thứ hai (tùy chọn, mặc định là X)

EXAMPLES:
  /command-name feature-branch main
    → So sánh feature-branch với main

  /command-name my-branch
    → So sánh my-branch với branch hiện tại

REQUIREMENTS:
  - Git repository
  - Branch phải tồn tại
  - Quyền đọc repository

RELATED COMMANDS:
  /other-command - Chức năng liên quan
  /another-command - Cách tiếp cận thay thế

TROUBLESHOOTING:
  - Nếu không tìm thấy branch: Kiểm tra chính tả tên branch
  - Nếu bị từ chối quyền truy cập: Kiểm tra quyền truy cập repository

CHANGELOG:
  v1.0.0 (2025-01-15): Phát hành lần đầu
  v0.9.0 (2025-01-10): Phiên bản beta
-->

# Triển Khai Command

[Nội dung prompt của command...]

[Giải thích điều gì sẽ xảy ra...]

[Hướng dẫn người dùng qua từng bước...]

[Cung cấp output rõ ràng...]
```

### Các Section Comment Tài Liệu

**PURPOSE**: Lý do command tồn tại
- Vấn đề nó giải quyết
- Các trường hợp sử dụng
- Khi nào nên dùng và không nên dùng

**USAGE**: Cú pháp cơ bản
- Pattern gọi command
- Argument bắt buộc vs tùy chọn
- Giá trị mặc định

**ARGUMENTS**: Tài liệu argument chi tiết
- Mô tả từng argument
- Thông tin kiểu dữ liệu
- Giá trị/phạm vi hợp lệ
- Giá trị mặc định

**EXAMPLES**: Ví dụ sử dụng cụ thể
- Các trường hợp sử dụng phổ biến
- Các trường hợp biên
- Output mong đợi

**REQUIREMENTS**: Điều kiện tiên quyết
- Các phụ thuộc
- Quyền hạn
- Cài đặt môi trường

**RELATED COMMANDS**: Các kết nối
- Command tương tự
- Command bổ sung
- Cách tiếp cận thay thế

**TROUBLESHOOTING**: Các vấn đề thường gặp
- Vấn đề đã biết
- Giải pháp
- Cách xử lý tạm thời

**CHANGELOG**: Lịch sử phiên bản
- Thay đổi gì và khi nào
- Breaking change được làm nổi bật
- Hướng dẫn migration

## Các Pattern Tài Liệu Nội Tuyến

### Section Có Comment

```markdown
---
description: Complex multi-step command
---

<!-- SECTION 1: VALIDATION -->
<!-- Section này kiểm tra điều kiện tiên quyết trước khi tiếp tục -->

Đang kiểm tra điều kiện tiên quyết...
- Git repository: !`git rev-parse --git-dir 2>/dev/null`
- Branch tồn tại: [logic validation]

<!-- SECTION 2: ANALYSIS -->
<!-- Phân tích sự khác biệt giữa các branch -->

Đang phân tích sự khác biệt giữa $1 và $2...
[Logic phân tích...]

<!-- SECTION 3: RECOMMENDATIONS -->
<!-- Cung cấp khuyến nghị có thể thực thi -->

Dựa trên phân tích, khuyến nghị:
[Khuyến nghị...]

<!-- END: Các bước tiếp theo cho người dùng -->
```

### Giải Thích Nội Tuyến

```markdown
---
description: Deployment command with inline docs
---

# Deploy to $1

## Kiểm Tra Trước Khi Bay

<!-- Kiểm tra trạng thái branch để tránh deploy từ branch sai -->
Branch hiện tại: !`git branch --show-current`

<!-- Deploy lên production phải từ main/master -->
if [ "$1" = "production" ] && [ "$(git branch --show-current)" != "main" ]; then
  ⚠️  CẢNH BÁO: Không ở main branch để deploy lên production
  Điều này bất thường. Xác nhận đây là cố ý.
fi

<!-- Trạng thái test đảm bảo không deploy code lỗi -->
Đang chạy test: !`npm test`

✓ Tất cả kiểm tra đã pass

## Deployment

<!-- Deployment thực sự diễn ra ở đây -->
<!-- Dùng chiến lược blue-green để không downtime -->
Đang deploy lên môi trường $1...
[Các bước deployment...]

<!-- Xác minh sau deployment -->
Đang xác minh tình trạng deployment...
[Health check...]

Deployment hoàn tất!

## Các Bước Tiếp Theo

<!-- Hướng dẫn người dùng làm gì sau khi deploy -->
1. Theo dõi log: /logs $1
2. Chạy smoke test: /smoke-test $1
3. Thông báo team: /notify-deployment $1
```

### Tài Liệu Điểm Quyết Định

```markdown
---
description: Interactive deployment command
---

# Interactive Deployment

## Xem Lại Cấu Hình

Target: $1
Phiên bản hiện tại: !`cat version.txt`
Phiên bản mới: $2

<!-- ĐIỂM QUYẾT ĐỊNH: Người dùng xác nhận cấu hình -->
<!-- Dừng ở đây để người dùng kiểm tra lại mọi thứ -->
<!-- Không thể tự động tiếp tục vì deployment có rủi ro -->

Hãy xem lại cấu hình trên.

**Tiếp tục với deployment?**
- Trả lời "yes" để tiến hành
- Trả lời "no" để hủy
- Trả lời "edit" để chỉnh sửa cấu hình

[Chờ input từ người dùng trước khi tiếp tục...]

<!-- Sau khi người dùng xác nhận, tiến hành deployment -->
<!-- Tất cả các bước tiếp theo được tự động hóa -->

Đang tiến hành deployment...
```

## Các Pattern Help Text

### Command Help Tích Hợp

Tạo subcommand help cho command phức tạp:

```markdown
---
description: Main command with help
argument-hint: [subcommand] [args]
---

# Command Processor

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
  **Trợ Giúp Command**

  CÁCH DÙNG:
    /command [subcommand] [args]

  SUBCOMMANDS:
    init [name]       Khởi tạo cấu hình mới
    deploy [env]      Deploy lên môi trường
    status            Hiển thị trạng thái hiện tại
    rollback          Rollback lần deploy cuối
    help              Hiển thị trợ giúp này

  VÍ DỤ:
    /command init my-project
    /command deploy staging
    /command status
    /command rollback

  Để xem trợ giúp chi tiết về subcommand:
    /command [subcommand] --help

  Thoát.
fi

[Xử lý command thông thường...]
```

### Help Theo Ngữ Cảnh

Cung cấp help dựa trên ngữ cảnh:

```markdown
---
description: Context-aware command
argument-hint: [operation] [target]
---

# Context-Aware Operation

if [ -z "$1" ]; then
  **Chưa chỉ định thao tác**

  Các thao tác có sẵn:
  - analyze: Phân tích target để tìm vấn đề
  - fix: Áp dụng sửa lỗi tự động
  - report: Tạo báo cáo chi tiết

  Cách dùng: /command [operation] [target]

  Ví dụ:
    /command analyze src/
    /command fix src/app.js
    /command report

  Chạy /command help để biết thêm chi tiết.

  Thoát.
fi

[Command tiếp tục nếu operation đã được cung cấp...]
```

## Tài Liệu Thông Báo Lỗi

### Thông Báo Lỗi Hữu Ích

```markdown
---
description: Command with good error messages
---

# Validation Command

if [ -z "$1" ]; then
  ❌ LỖI: Thiếu argument bắt buộc

  Argument 'file-path' là bắt buộc.

  CÁCH DÙNG:
    /validate [file-path]

  VÍ DỤ:
    /validate src/app.js

  Hãy thử lại với đường dẫn file.

  Thoát.
fi

if [ ! -f "$1" ]; then
  ❌ LỖI: Không tìm thấy file: $1

  File được chỉ định không tồn tại hoặc không thể truy cập.

  NGUYÊN NHÂN THƯỜNG GẶP:
  1. Lỗi đánh máy trong đường dẫn file
  2. File đã bị xóa hoặc di chuyển
  3. Không đủ quyền truy cập

  GỢI Ý:
  - Kiểm tra chính tả: $1
  - Xác nhận file tồn tại: ls -la $(dirname "$1")
  - Kiểm tra quyền: ls -l "$1"

  Thoát.
fi

[Command tiếp tục nếu validation pass...]
```

### Hướng Dẫn Phục Hồi Lỗi

```markdown
---
description: Command with recovery guidance
---

# Operation Command

Đang chạy thao tác...

!`risky-operation.sh`

if [ $? -ne 0 ]; then
  ❌ THAO TÁC THẤT BẠI

  Thao tác gặp lỗi và không thể hoàn thành.

  ĐIỀU GÌ ĐÃ XẢY RA:
  Script risky-operation.sh trả về exit code khác không.

  ĐIỀU NÀY CÓ NGHĨA:
  - Thay đổi có thể đã được áp dụng một phần
  - Hệ thống có thể đang ở trạng thái không nhất quán
  - Có thể cần can thiệp thủ công

  CÁC BƯỚC PHỤC HỒI:
  1. Kiểm tra log thao tác: cat /tmp/operation.log
  2. Xác minh trạng thái hệ thống: /check-state
  3. Nếu cần, rollback: /rollback-operation
  4. Sửa vấn đề gốc rễ
  5. Thử lại thao tác: /retry-operation

  CẦN TRỢ GIÚP?
  - Xem hướng dẫn troubleshooting: /help troubleshooting
  - Liên hệ hỗ trợ với mã lỗi: ERR_OP_FAILED_001

  Thoát.
fi
```

## Tài Liệu Ví Dụ Sử Dụng

### Ví Dụ Nhúng Trực Tiếp

```markdown
---
description: Command with embedded examples
---

# Feature Command

Command này thực hiện phân tích feature với nhiều tùy chọn.

## Sử Dụng Cơ Bản

\`\`\`
/feature analyze src/
\`\`\`

Phân tích tất cả file trong thư mục src/ để tìm feature đang dùng.

## Sử Dụng Nâng Cao

\`\`\`
/feature analyze src/ --detailed
\`\`\`

Cung cấp phân tích chi tiết bao gồm:
- Phân tích feature theo file
- Các pattern sử dụng
- Đề xuất tối ưu hóa

## Các Trường Hợp Sử Dụng

**Trường hợp 1: Tổng quan nhanh**
\`\`\`
/feature analyze .
\`\`\`
Lấy tóm tắt feature cấp cao của toàn bộ project.

**Trường hợp 2: Thư mục cụ thể**
\`\`\`
/feature analyze src/components
\`\`\`
Tập trung phân tích vào thư mục components.

**Trường hợp 3: So sánh**
\`\`\`
/feature analyze src/ --compare baseline.json
\`\`\`
So sánh feature hiện tại với baseline.

---

Đang xử lý yêu cầu của bạn...

[Triển khai command...]
```

### Tài Liệu Lấy Ví Dụ Làm Trung Tâm

```markdown
---
description: Example-heavy command
---

# Transformation Command

## Command Này Làm Gì

Chuyển đổi dữ liệu từ định dạng này sang định dạng khác.

## Ví Dụ Trước

### Ví dụ 1: JSON sang YAML
**Input:** `data.json`
\`\`\`json
{"name": "test", "value": 42}
\`\`\`

**Command:** `/transform data.json yaml`

**Output:** `data.yaml`
\`\`\`yaml
name: test
value: 42
\`\`\`

### Ví dụ 2: CSV sang JSON
**Input:** `data.csv`
\`\`\`csv
name,value
test,42
\`\`\`

**Command:** `/transform data.csv json`

**Output:** `data.json`
\`\`\`json
[{"name": "test", "value": "42"}]
\`\`\`

### Ví dụ 3: Với Tùy Chọn
**Command:** `/transform data.json yaml --pretty --sort-keys`

**Kết quả:** YAML được định dạng với key đã sắp xếp

---

## Chuyển Đổi Của Bạn

File: $1
Format: $2

[Thực hiện chuyển đổi...]
```

## Tài Liệu Bảo Trì

### Phiên Bản và Changelog

```markdown
<!--
VERSION: 2.1.0
LAST UPDATED: 2025-01-15
AUTHOR: DevOps Team

CHANGELOG:
  v2.1.0 (2025-01-15):
    - Thêm hỗ trợ cấu hình YAML
    - Cải thiện thông báo lỗi
    - Sửa bug với ký tự đặc biệt trong argument

  v2.0.0 (2025-01-01):
    - BREAKING: Đổi thứ tự argument
    - BREAKING: Bỏ --old-flag đã deprecated
    - Thêm kiểm tra validation mới
    - Hướng dẫn migration: /migration-v2

  v1.5.0 (2024-12-15):
    - Thêm flag --verbose
    - Cải thiện hiệu năng 50%

  v1.0.0 (2024-12-01):
    - Phát hành ổn định đầu tiên

MIGRATION NOTES:
  Từ v1.x lên v2.0:
    Cũ: /command arg1 arg2 --old-flag
    Mới: /command arg2 arg1

  --old-flag đã bị xóa. Dùng --new-flag thay thế.

DEPRECATION WARNINGS:
  - Flag --legacy-mode đã deprecated từ v2.1.0
  - Sẽ bị xóa trong v3.0.0 (ước tính 2025-06-01)
  - Dùng --modern-mode thay thế

KNOWN ISSUES:
  - #123: Hiệu năng chậm với file lớn (cách xử lý tạm: dùng flag --stream)
  - #456: Ký tự đặc biệt trên Windows (dự kiến sửa trong v2.2.0)
-->
```

### Ghi Chú Bảo Trì

```markdown
<!--
MAINTENANCE NOTES:

CẤU TRÚC CODE:
  - Dòng 1–50: Phân tích và validation argument
  - Dòng 51–100: Logic xử lý chính
  - Dòng 101–150: Định dạng output
  - Dòng 151–200: Xử lý lỗi

DEPENDENCIES:
  - Yêu cầu git 2.x trở lên
  - Dùng jq để xử lý JSON
  - Cần bash 4.0+ cho associative array

PERFORMANCE:
  - Fast path cho input nhỏ (< 1MB)
  - Stream file lớn để tránh vấn đề bộ nhớ
  - Cache kết quả trong /tmp trong 1 giờ

SECURITY CONSIDERATIONS:
  - Validate tất cả input để ngăn injection
  - Dùng allowed-tools để giới hạn quyền Bash
  - Không có credentials trong file command

TESTING:
  - Unit test: tests/command-test.sh
  - Integration test: tests/integration/
  - Checklist test thủ công: tests/manual-checklist.md

FUTURE IMPROVEMENTS:
  - TODO: Thêm hỗ trợ định dạng TOML
  - TODO: Triển khai xử lý song song
  - TODO: Thêm progress bar cho file lớn

RELATED FILES:
  - lib/parser.sh: Logic phân tích dùng chung
  - lib/formatter.sh: Định dạng output
  - config/defaults.yml: Cấu hình mặc định
-->
```

## Tài Liệu README

Command nên có file README đi kèm:

```markdown
# Tên Command

Mô tả ngắn về command làm gì.

## Cài Đặt

Command này là một phần của plugin [plugin-name].

Cài đặt với:
\`\`\`
/plugin install plugin-name
\`\`\`

## Cách Dùng

Cách dùng cơ bản:
\`\`\`
/command-name [arg1] [arg2]
\`\`\`

## Argument

- `arg1`: Mô tả (bắt buộc)
- `arg2`: Mô tả (tùy chọn, mặc định là X)

## Ví Dụ

### Ví dụ 1: Cơ Bản
\`\`\`
/command-name value1 value2
\`\`\`

Mô tả điều gì xảy ra.

### Ví dụ 2: Nâng Cao
\`\`\`
/command-name value1 --option
\`\`\`

Mô tả tính năng nâng cao.

## Cấu Hình

File cấu hình tùy chọn: `.claude/command-name.local.md`

\`\`\`markdown
---
default_arg: value
enable_feature: true
---
\`\`\`

## Yêu Cầu

- Git 2.x trở lên
- jq (để xử lý JSON)
- Node.js 14+ (tùy chọn, cho tính năng nâng cao)

## Troubleshooting

### Vấn đề: Command không tìm thấy

**Giải pháp:** Đảm bảo plugin đã được cài đặt và kích hoạt.

### Vấn đề: Bị từ chối quyền truy cập

**Giải pháp:** Kiểm tra quyền file và cài đặt allowed-tools.

## Đóng Góp

Hoan nghênh đóng góp! Xem [CONTRIBUTING.md](CONTRIBUTING.md).

## Giấy Phép

MIT License — Xem [LICENSE](LICENSE).

## Hỗ Trợ

- Issues: https://github.com/user/plugin/issues
- Docs: https://docs.example.com
- Email: support@example.com
```

## Các Nguyên Tắc Tốt Nhất

### Nguyên Tắc Tài Liệu

1. **Viết cho bản thân tương lai**: Giả sử bạn sẽ quên mọi chi tiết
2. **Ví dụ trước rồi mới giải thích**: Cho thấy, sau đó kể
3. **Tiết lộ dần dần**: Thông tin cơ bản trước, chi tiết có sẵn khi cần
4. **Giữ cập nhật**: Cập nhật docs khi code thay đổi
5. **Kiểm tra docs của bạn**: Xác nhận ví dụ thực sự chạy được

### Vị Trí Tài Liệu

1. **Trong file command**: Cách dùng cốt lõi, ví dụ, giải thích nội tuyến
2. **README**: Cài đặt, cấu hình, troubleshooting
3. **Docs riêng**: Hướng dẫn chi tiết, tutorial, tài liệu API
4. **Comment**: Chi tiết triển khai dành cho người bảo trì

### Phong Cách Tài Liệu

1. **Rõ ràng và ngắn gọn**: Không dùng từ thừa
2. **Giọng chủ động**: "Chạy command" thay vì "Command có thể được chạy"
3. **Thuật ngữ nhất quán**: Dùng cùng thuật ngữ xuyên suốt
4. **Định dạng tốt**: Dùng heading, list, code block
5. **Dễ tiếp cận**: Giả sử người đọc là người mới

### Bảo Trì Tài Liệu

1. **Đánh phiên bản mọi thứ**: Theo dõi thay đổi gì khi nào
2. **Deprecated khéo léo**: Cảnh báo trước khi xóa tính năng
3. **Hướng dẫn migration**: Giúp người dùng nâng cấp
4. **Lưu trữ docs cũ**: Giữ cho phiên bản cũ có thể truy cập
5. **Xem xét định kỳ**: Đảm bảo docs khớp với thực tế

## Checklist Tài Liệu

Trước khi phát hành command:

- [ ] Description trong frontmatter rõ ràng
- [ ] argument-hint ghi lại tất cả argument
- [ ] Ví dụ sử dụng có trong comment
- [ ] Các trường hợp sử dụng phổ biến được hiển thị
- [ ] Thông báo lỗi hữu ích
- [ ] Yêu cầu đã được ghi lại
- [ ] Các command liên quan đã được liệt kê
- [ ] Changelog được duy trì
- [ ] Số phiên bản đã cập nhật
- [ ] README đã tạo/cập nhật
- [ ] Ví dụ thực sự chạy được
- [ ] Section troubleshooting hoàn chỉnh

Với tài liệu tốt, command trở thành self-service, giảm gánh nặng hỗ trợ và cải thiện trải nghiệm người dùng.
