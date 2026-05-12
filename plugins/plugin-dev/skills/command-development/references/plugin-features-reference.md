# Tài Liệu Tham Chiếu Tính Năng Command Dành Riêng cho Plugin

Tài liệu này bao gồm các tính năng và pattern dành riêng cho command được đóng gói trong Claude Code plugin.

## Mục Lục

- [Khám Phá Command của Plugin](#khám-phá-command-của-plugin)
- [Biến Môi Trường CLAUDE_PLUGIN_ROOT](#biến-môi-trường-claude_plugin_root)
- [Các Pattern Command của Plugin](#các-pattern-command-của-plugin)
- [Tích Hợp với Các Thành Phần Plugin](#tích-hợp-với-các-thành-phần-plugin)
- [Các Pattern Validation](#các-pattern-validation)

## Khám Phá Command của Plugin

### Auto-Discovery

Claude Code tự động khám phá command trong plugin ở các vị trí sau:

```
plugin-name/
├── commands/              # Command được tự động khám phá
│   ├── foo.md            # /foo (plugin:plugin-name)
│   └── bar.md            # /bar (plugin:plugin-name)
└── plugin.json           # Plugin manifest
```

**Các điểm quan trọng:**
- Command được khám phá khi plugin được tải
- Không cần đăng ký thủ công
- Command xuất hiện trong `/help` với nhãn "(plugin:plugin-name)"
- Thư mục con tạo namespace

### Command Plugin có Namespace

Tổ chức command trong thư mục con để nhóm logic:

```
plugin-name/
└── commands/
    ├── review/
    │   ├── security.md    # /security (plugin:plugin-name:review)
    │   └── style.md       # /style (plugin:plugin-name:review)
    └── deploy/
        ├── staging.md     # /staging (plugin:plugin-name:deploy)
        └── prod.md        # /prod (plugin:plugin-name:deploy)
```

**Hành vi namespace:**
- Tên thư mục con trở thành namespace
- Hiển thị là "(plugin:plugin-name:namespace)" trong `/help`
- Giúp tổ chức các command liên quan
- Dùng khi plugin có 5+ command

### Quy Ước Đặt Tên Command

**Tên command của plugin nên:**
1. Mô tả rõ và định hướng hành động
2. Tránh conflict với tên command phổ biến
3. Dùng dấu gạch ngang cho tên nhiều từ
4. Cân nhắc thêm prefix tên plugin để đảm bảo độc đáo

**Ví dụ:**
```
Tốt:
- /mylyn-sync          (prefix đặc thù plugin)
- /analyze-performance (hành động mô tả)
- /docker-compose-up   (mục đích rõ ràng)

Tránh:
- /test               (conflict với tên phổ biến)
- /run                (quá chung)
- /do-stuff           (không mô tả)
```

## Biến Môi Trường CLAUDE_PLUGIN_ROOT

### Mục Đích

`${CLAUDE_PLUGIN_ROOT}` là biến môi trường đặc biệt có sẵn trong command của plugin, trỏ tới đường dẫn tuyệt đối của thư mục plugin.

**Tại sao quan trọng:**
- Cho phép đường dẫn portable trong plugin
- Cho phép tham chiếu đến file và script của plugin
- Hoạt động qua các cài đặt khác nhau
- Cần thiết cho thao tác plugin nhiều file

### Cách Dùng Cơ Bản

Tham chiếu file trong plugin của bạn:

```markdown
---
description: Analyze using plugin script
allowed-tools: Bash(node:*), Read
---

Chạy phân tích: !`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js`

Đọc template: @${CLAUDE_PLUGIN_ROOT}/templates/report.md
```

**Mở rộng thành:**
```
Chạy phân tích: !`node /path/to/plugins/plugin-name/scripts/analyze.js`

Đọc template: @/path/to/plugins/plugin-name/templates/report.md
```

### Các Pattern Phổ Biến

#### 1. Thực Thi Script của Plugin

```markdown
---
description: Run custom linter from plugin
allowed-tools: Bash(node:*)
---

Kết quả lint: !`node ${CLAUDE_PLUGIN_ROOT}/bin/lint.js $1`

Review output lint và đề xuất sửa.
```

#### 2. Tải File Cấu Hình

```markdown
---
description: Deploy using plugin configuration
allowed-tools: Read, Bash(*)
---

Cấu hình: @${CLAUDE_PLUGIN_ROOT}/config/deploy-config.json

Deploy ứng dụng dùng cấu hình trên cho môi trường $1.
```

#### 3. Truy Cập Tài Nguyên Plugin

```markdown
---
description: Generate report from template
---

Dùng template này: @${CLAUDE_PLUGIN_ROOT}/templates/api-report.md

Tạo báo cáo cho @$1 theo định dạng template.
```

#### 4. Workflow Plugin Nhiều Bước

```markdown
---
description: Complete plugin workflow
allowed-tools: Bash(*), Read
---

Bước 1 — Chuẩn bị: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/prepare.sh $1`
Bước 2 — Config: @${CLAUDE_PLUGIN_ROOT}/config/$1.json
Bước 3 — Thực thi: !`${CLAUDE_PLUGIN_ROOT}/bin/execute $1`

Review kết quả và báo cáo trạng thái.
```

### Nguyên Tắc Tốt Nhất

1. **Luôn dùng cho đường dẫn nội bộ plugin:**
   ```markdown
   # Tốt
   @${CLAUDE_PLUGIN_ROOT}/templates/foo.md

   # Xấu
   @./templates/foo.md  # Tương đối so với thư mục hiện tại, không phải plugin
   ```

2. **Validate sự tồn tại của file:**
   ```markdown
   ---
   description: Use plugin config if exists
   allowed-tools: Bash(test:*), Read
   ---

   !`test -f ${CLAUDE_PLUGIN_ROOT}/config.json && echo "exists" || echo "missing"`

   Nếu config tồn tại, tải nó: @${CLAUDE_PLUGIN_ROOT}/config.json
   Nếu không, dùng giá trị mặc định...
   ```

3. **Ghi lại cấu trúc file plugin:**
   ```markdown
   <!--
   Cấu trúc plugin:
   ${CLAUDE_PLUGIN_ROOT}/
   ├── scripts/analyze.js  (script phân tích)
   ├── templates/          (template báo cáo)
   └── config/             (file cấu hình)
   -->
   ```

4. **Kết hợp với argument:**
   ```markdown
   Chạy: !`${CLAUDE_PLUGIN_ROOT}/bin/process.sh $1 $2`
   ```

### Troubleshooting

**Biến không mở rộng:**
- Đảm bảo command được tải từ plugin
- Kiểm tra thực thi bash được phép
- Xác minh cú pháp chính xác: `${CLAUDE_PLUGIN_ROOT}`

**Lỗi không tìm thấy file:**
- Xác minh file tồn tại trong thư mục plugin
- Kiểm tra đường dẫn file đúng so với plugin root
- Đảm bảo quyền file cho phép đọc/thực thi

**Đường dẫn có khoảng trắng:**
- Lệnh Bash tự động xử lý khoảng trắng
- Tham chiếu file hoạt động với khoảng trắng trong đường dẫn
- Không cần quote đặc biệt

## Các Pattern Command của Plugin

### Pattern 1: Command Dựa Trên Cấu Hình

Command tải cấu hình đặc thù plugin:

```markdown
---
description: Deploy using plugin settings
allowed-tools: Read, Bash(*)
---

Tải cấu hình: @${CLAUDE_PLUGIN_ROOT}/deploy-config.json

Deploy lên môi trường $1 dùng:
1. Các cài đặt cấu hình trên
2. Git branch hiện tại: !`git branch --show-current`
3. Phiên bản ứng dụng: !`cat package.json | grep version`

Thực thi deployment và theo dõi tiến độ.
```

**Khi nào dùng:** Command cần cài đặt nhất quán qua các lần gọi

### Pattern 2: Tạo Dựa Trên Template

Command dùng template của plugin:

```markdown
---
description: Generate documentation from template
argument-hint: [component-name]
---

Template: @${CLAUDE_PLUGIN_ROOT}/templates/component-docs.md

Tạo tài liệu cho component $1 theo cấu trúc template.
Bao gồm:
- Mục đích và cách dùng component
- Tài liệu tham chiếu API
- Ví dụ
- Hướng dẫn kiểm thử
```

**Khi nào dùng:** Tạo output theo chuẩn

### Pattern 3: Workflow Nhiều Script

Command điều phối nhiều script của plugin:

```markdown
---
description: Complete build and test workflow
allowed-tools: Bash(*)
---

Build: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh`
Validate: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh`
Test: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/test.sh`

Review tất cả output và báo cáo:
1. Trạng thái build
2. Kết quả validation
3. Kết quả test
4. Bước tiếp theo được khuyến nghị
```

**Khi nào dùng:** Workflow plugin phức tạp với nhiều bước

### Pattern 4: Command Thích Ứng Theo Môi Trường

Command thích ứng theo môi trường:

```markdown
---
description: Deploy based on environment
argument-hint: [dev|staging|prod]
---

Config môi trường: @${CLAUDE_PLUGIN_ROOT}/config/$1.json

Kiểm tra môi trường: !`echo "Đang deploy lên: $1"`

Deploy ứng dụng dùng cấu hình môi trường $1.
Xác minh deployment và chạy smoke test.
```

**Khi nào dùng:** Command có hành vi khác nhau theo môi trường

### Pattern 5: Quản Lý Dữ Liệu Plugin

Command quản lý dữ liệu đặc thù plugin:

```markdown
---
description: Save analysis results to plugin cache
allowed-tools: Bash(*), Read, Write
---

Thư mục cache: ${CLAUDE_PLUGIN_ROOT}/cache/

Phân tích @$1 và lưu kết quả vào cache:
!`mkdir -p ${CLAUDE_PLUGIN_ROOT}/cache && date > ${CLAUDE_PLUGIN_ROOT}/cache/last-run.txt`

Lưu trữ phân tích để tham khảo và so sánh sau này.
```

**Khi nào dùng:** Command cần lưu trữ dữ liệu bền vững

## Tích Hợp với Các Thành Phần Plugin

### Gọi Agent của Plugin

Command có thể kích hoạt agent của plugin dùng tool Task:

```markdown
---
description: Deep analysis using plugin agent
argument-hint: [file-path]
---

Khởi tạo phân tích code sâu cho @$1 dùng agent code-analyzer.

Agent sẽ:
1. Phân tích cấu trúc code
2. Xác định các pattern
3. Đề xuất cải thiện
4. Tạo báo cáo chi tiết

Lưu ý: Dùng tool Task để khởi chạy agent code-analyzer của plugin.
```

**Các điểm quan trọng:**
- Agent phải được định nghĩa trong thư mục `agents/` của plugin
- Claude sẽ tự động dùng tool Task để khởi chạy agent
- Agent có quyền truy cập tài nguyên plugin tương tự

### Gọi Skill của Plugin

Command có thể tham chiếu skill của plugin để có kiến thức chuyên sâu:

```markdown
---
description: API documentation with best practices
argument-hint: [api-file]
---

Viết tài liệu cho API trong @$1 theo tiêu chuẩn tài liệu API của chúng ta.

Dùng skill api-docs-standards để đảm bảo tài liệu bao gồm:
- Mô tả endpoint
- Đặc tả tham số
- Định dạng response
- Mã lỗi
- Ví dụ sử dụng

Lưu ý: Điều này tận dụng skill api-docs-standards của plugin để nhất quán.
```

**Các điểm quan trọng:**
- Skill phải được định nghĩa trong thư mục `skills/` của plugin
- Đề cập skill theo tên để gợi ý Claude nên gọi nó
- Skill cung cấp kiến thức domain chuyên sâu

### Phối Hợp với Hook của Plugin

Command có thể được thiết kế để làm việc với hook của plugin:

```markdown
---
description: Commit with pre-commit validation
allowed-tools: Bash(git:*)
---

Stage thay đổi: !\`git add $1\`

Commit thay đổi: !\`git commit -m "$2"\`

Lưu ý: Commit này sẽ kích hoạt pre-commit hook của plugin để validation.
Review output của hook để tìm vấn đề.
```

**Các điểm quan trọng:**
- Hook thực thi tự động khi có sự kiện
- Command có thể chuẩn bị trạng thái cho hook
- Ghi lại sự tương tác với hook trong command

### Command Plugin Nhiều Thành Phần

Command điều phối nhiều thành phần plugin:

```markdown
---
description: Comprehensive code review workflow
argument-hint: [file-path]
---

File cần review: @$1

Thực thi review toàn diện:

1. **Phân Tích Tĩnh** (qua script plugin)
   !`node ${CLAUDE_PLUGIN_ROOT}/scripts/lint.js $1`

2. **Review Sâu** (qua agent plugin)
   Khởi chạy agent code-reviewer để phân tích chi tiết.

3. **Nguyên Tắc Tốt Nhất** (qua skill plugin)
   Dùng skill code-standards để đảm bảo tuân thủ.

4. **Tài Liệu** (qua template plugin)
   Template: @${CLAUDE_PLUGIN_ROOT}/templates/review-report.md

Tạo báo cáo cuối kết hợp tất cả output.
```

**Khi nào dùng:** Workflow phức tạp tận dụng nhiều khả năng của plugin

## Các Pattern Validation

### Validation Input

Command nên validate input trước khi xử lý:

```markdown
---
description: Deploy to environment with validation
argument-hint: [environment]
---

Validate môi trường: !`echo "$1" | grep -E "^(dev|staging|prod)$" || echo "INVALID"`

$IF($1 in [dev, staging, prod],
  Deploy lên môi trường $1 dùng cấu hình đã validate,
  LỖI: Môi trường không hợp lệ '$1'. Phải là một trong: dev, staging, prod
)
```

**Các cách tiếp cận validation:**
1. Validation Bash dùng grep/test
2. Validation inline trong prompt
3. Validation dùng script

### Kiểm Tra File Tồn Tại

Xác minh file cần thiết tồn tại:

```markdown
---
description: Process configuration file
argument-hint: [config-file]
---

Kiểm tra file: !`test -f $1 && echo "EXISTS" || echo "MISSING"`

Xử lý cấu hình nếu file tồn tại: @$1

Nếu file không tồn tại, giải thích:
- Vị trí mong đợi
- Định dạng bắt buộc
- Cách tạo file
```

### Argument Bắt Buộc

Validate argument bắt buộc đã được cung cấp:

```markdown
---
description: Create deployment with version
argument-hint: [environment] [version]
---

Validate input: !`test -n "$1" -a -n "$2" && echo "OK" || echo "MISSING"`

$IF($1 AND $2,
  Deploy phiên bản $2 lên môi trường $1,
  LỖI: Cần cả environment và version. Cách dùng: /deploy [env] [version]
)
```

### Validation Tài Nguyên Plugin

Xác minh tài nguyên plugin có sẵn:

```markdown
---
description: Run analysis with plugin tools
allowed-tools: Bash(test:*)
---

Validate thiết lập plugin:
- Config tồn tại: !`test -f ${CLAUDE_PLUGIN_ROOT}/config.json && echo "✓" || echo "✗"`
- Script tồn tại: !`test -d ${CLAUDE_PLUGIN_ROOT}/scripts && echo "✓" || echo "✗"`
- Tool có sẵn: !`test -x ${CLAUDE_PLUGIN_ROOT}/bin/analyze && echo "✓" || echo "✗"`

Nếu tất cả kiểm tra pass, tiến hành phân tích.
Nếu không, báo cáo thành phần còn thiếu và các bước cài đặt.
```

### Validation Output

Validate kết quả thực thi command:

```markdown
---
description: Build and validate output
allowed-tools: Bash(*)
---

Build: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh`

Validate output:
- Exit code: !`echo $?`
- Output tồn tại: !`test -d dist && echo "✓" || echo "✗"`
- Số file: !`find dist -type f | wc -l`

Báo cáo trạng thái build và các lỗi validation.
```

### Xử Lý Lỗi Khéo Léo

Xử lý lỗi khéo léo với thông báo hữu ích:

```markdown
---
description: Process file with error handling
argument-hint: [file-path]
---

Thử xử lý: !`node ${CLAUDE_PLUGIN_ROOT}/scripts/process.js $1 2>&1 || echo "ERROR: $?"`

Nếu xử lý thành công:
- Báo cáo kết quả
- Gợi ý bước tiếp theo

Nếu xử lý thất bại:
- Giải thích nguyên nhân có thể
- Cung cấp bước troubleshooting
- Đề xuất cách tiếp cận thay thế
```

## Tóm Tắt Nguyên Tắc Tốt Nhất

### Command Plugin Nên:

1. **Dùng ${CLAUDE_PLUGIN_ROOT} cho tất cả đường dẫn nội bộ plugin**
   - Script, template, cấu hình, tài nguyên

2. **Validate input sớm**
   - Kiểm tra argument bắt buộc
   - Xác minh file tồn tại
   - Validate định dạng argument

3. **Ghi lại cấu trúc plugin**
   - Giải thích các file cần thiết
   - Ghi lại mục đích script
   - Làm rõ các dependency

4. **Tích hợp với các thành phần plugin**
   - Tham chiếu agent cho tác vụ phức tạp
   - Dùng skill cho kiến thức chuyên sâu
   - Phối hợp với hook khi liên quan

5. **Cung cấp thông báo lỗi hữu ích**
   - Giải thích điều gì đã sai
   - Đề xuất cách sửa
   - Đưa ra phương án thay thế

6. **Xử lý trường hợp biên**
   - File thiếu
   - Argument không hợp lệ
   - Thực thi script thất bại
   - Dependency còn thiếu

7. **Giữ command tập trung**
   - Một mục đích rõ ràng mỗi command
   - Ủy thác logic phức tạp cho script
   - Dùng agent cho workflow nhiều bước

8. **Test trên nhiều cài đặt**
   - Xác minh đường dẫn hoạt động ở mọi nơi
   - Test với các argument khác nhau
   - Validate các trường hợp lỗi

---

Để phát triển command chung, xem SKILL.md chính.
Để xem ví dụ command, xem thư mục examples/.
