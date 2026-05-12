---
name: skill-development
description: This skill should be used when the user wants to "create a skill", "add a skill to plugin", "write a new skill", "improve skill description", "organize skill content", or needs guidance on skill structure, progressive disclosure, or skill development best practices for Claude Code plugins.
version: 0.1.0
---

# Phát triển Skill cho Claude Code Plugins

Skill này cung cấp hướng dẫn để tạo các skill hiệu quả cho Claude Code plugins.

## Về Skills

Skills là các gói module hóa, độc lập, mở rộng khả năng của Claude bằng cách cung cấp
kiến thức chuyên biệt, workflow và tool. Hãy coi chúng như "hướng dẫn onboarding" cho các
lĩnh vực hoặc tác vụ cụ thể — chúng biến Claude từ một agent đa năng thành một agent chuyên biệt
được trang bị kiến thức thủ tục mà không model nào có thể sở hữu đầy đủ.

### Skills cung cấp những gì

1. Workflow chuyên biệt - Các quy trình nhiều bước cho các lĩnh vực cụ thể
2. Tích hợp tool - Hướng dẫn làm việc với các định dạng file hoặc API cụ thể
3. Chuyên môn lĩnh vực - Kiến thức đặc thù của công ty, schema, business logic
4. Tài nguyên bundled - Script, tài liệu tham chiếu và asset cho các tác vụ phức tạp và lặp lại

### Cấu tạo của một Skill

Mỗi skill bao gồm file SKILL.md bắt buộc và các tài nguyên bundled tùy chọn:

```
skill-name/
├── SKILL.md (bắt buộc)
│   ├── Metadata YAML frontmatter (bắt buộc)
│   │   ├── name: (bắt buộc)
│   │   └── description: (bắt buộc)
│   └── Hướng dẫn Markdown (bắt buộc)
└── Tài nguyên Bundled (tùy chọn)
    ├── scripts/          - Code thực thi được (Python/Bash/v.v.)
    ├── references/       - Tài liệu dùng để load vào context khi cần
    └── assets/           - File dùng trong output (template, icon, font, v.v.)
```

#### SKILL.md (bắt buộc)

**Chất lượng Metadata:** `name` và `description` trong YAML frontmatter xác định khi nào Claude sẽ dùng skill. Mô tả cụ thể skill làm gì và khi nào nên dùng. Dùng ngôi thứ ba (ví dụ: "This skill should be used when..." thay vì "Use this skill when...").

#### Tài nguyên Bundled (tùy chọn)

##### Scripts (`scripts/`)

Code thực thi được (Python/Bash/v.v.) cho các tác vụ cần độ tin cậy tất định hoặc bị viết lại nhiều lần.

- **Khi nào nên có**: Khi cùng một đoạn code bị viết lại nhiều lần hoặc cần độ tin cậy tất định
- **Ví dụ**: `scripts/rotate_pdf.py` cho tác vụ xoay PDF
- **Lợi ích**: Tiết kiệm token, tất định, có thể thực thi mà không cần load vào context
- **Lưu ý**: Script vẫn có thể cần Claude đọc để vá lỗi hoặc điều chỉnh theo môi trường cụ thể

##### References (`references/`)

Tài liệu và tài liệu tham chiếu dùng để load vào context khi cần để thông tin cho quá trình xử lý và suy luận của Claude.

- **Khi nào nên có**: Khi có tài liệu mà Claude nên tham chiếu trong lúc làm việc
- **Ví dụ**: `references/finance.md` cho schema tài chính, `references/mnda.md` cho template NDA của công ty, `references/policies.md` cho chính sách công ty, `references/api_docs.md` cho đặc tả API
- **Trường hợp sử dụng**: Database schema, tài liệu API, kiến thức lĩnh vực, chính sách công ty, hướng dẫn workflow chi tiết
- **Lợi ích**: Giữ SKILL.md gọn, chỉ load khi Claude xác định cần thiết
- **Best practice**: Nếu file lớn (>10k từ), thêm các pattern tìm kiếm grep vào SKILL.md
- **Tránh trùng lặp**: Thông tin nên tồn tại ở SKILL.md hoặc references, không phải cả hai. Ưu tiên references cho thông tin chi tiết trừ khi thực sự là cốt lõi của skill — điều này giữ SKILL.md gọn trong khi vẫn có thể khám phá thông tin mà không chiếm dụng context window. Chỉ giữ hướng dẫn thủ tục thiết yếu và workflow trong SKILL.md; chuyển tài liệu tham chiếu chi tiết, schema và ví dụ sang references.

##### Assets (`assets/`)

Các file không dùng để load vào context, mà dùng trong output mà Claude tạo ra.

- **Khi nào nên có**: Khi skill cần file sẽ được dùng trong output cuối cùng
- **Ví dụ**: `assets/logo.png` cho brand asset, `assets/slides.pptx` cho template PowerPoint, `assets/frontend-template/` cho boilerplate HTML/React, `assets/font.ttf` cho typography
- **Trường hợp sử dụng**: Template, hình ảnh, icon, boilerplate code, font, tài liệu mẫu được copy hoặc chỉnh sửa
- **Lợi ích**: Tách biệt tài nguyên output khỏi tài liệu, cho phép Claude dùng file mà không cần load vào context

### Nguyên tắc thiết kế Progressive Disclosure

Skills dùng hệ thống tải ba cấp để quản lý context hiệu quả:

1. **Metadata (name + description)** - Luôn có trong context (~100 từ)
2. **SKILL.md body** - Khi skill được kích hoạt (<5k từ)
3. **Tài nguyên bundled** - Khi Claude cần (Không giới hạn*)

*Không giới hạn vì script có thể thực thi mà không cần đọc vào context window.

## Quy trình tạo Skill

Để tạo skill, thực hiện "Quy trình tạo Skill" theo thứ tự, bỏ qua bước chỉ khi có lý do rõ ràng tại sao nó không áp dụng.

### Bước 1: Hiểu Skill qua các Ví dụ cụ thể

Bỏ qua bước này chỉ khi các pattern sử dụng của skill đã được hiểu rõ. Bước này vẫn có giá trị kể cả khi làm việc với skill đã có sẵn.

Để tạo skill hiệu quả, cần hiểu rõ các ví dụ cụ thể về cách skill sẽ được sử dụng. Sự hiểu biết này có thể đến từ ví dụ trực tiếp của người dùng hoặc các ví dụ được tạo ra rồi xác nhận với phản hồi của người dùng.

Ví dụ, khi xây dựng skill image-editor, các câu hỏi liên quan bao gồm:

- "Skill image-editor nên hỗ trợ những chức năng gì? Chỉnh sửa, xoay, hay gì khác?"
- "Bạn có thể cho ví dụ về cách skill này sẽ được dùng không?"
- "Tôi hình dung người dùng có thể hỏi những câu như 'Xóa mắt đỏ khỏi ảnh này' hoặc 'Xoay ảnh này'. Bạn có nghĩ đến cách dùng nào khác không?"
- "Người dùng sẽ nói gì để kích hoạt skill này?"

Để tránh làm người dùng choáng ngợp, tránh hỏi quá nhiều câu trong một lần. Bắt đầu với câu hỏi quan trọng nhất và hỏi thêm khi cần để tăng hiệu quả.

Kết thúc bước này khi đã có cảm nhận rõ về chức năng mà skill cần hỗ trợ.

### Bước 2: Lên kế hoạch Nội dung Skill tái sử dụng

Để biến các ví dụ cụ thể thành skill hiệu quả, phân tích từng ví dụ bằng cách:

1. Cân nhắc cách thực hiện ví dụ đó từ đầu
2. Xác định những script, references và assets nào sẽ hữu ích khi thực hiện các workflow này nhiều lần

Ví dụ: Khi xây dựng skill `pdf-editor` để xử lý câu hỏi "Giúp tôi xoay PDF này," phân tích cho thấy:

1. Xoay PDF đòi hỏi viết lại cùng đoạn code mỗi lần
2. Script `scripts/rotate_pdf.py` sẽ hữu ích để lưu trong skill

Ví dụ: Khi thiết kế skill `frontend-webapp-builder` cho câu hỏi "Tạo cho tôi một todo app" hoặc "Tạo cho tôi một dashboard để theo dõi số bước đi," phân tích cho thấy:

1. Viết frontend webapp đòi hỏi cùng boilerplate HTML/React mỗi lần
2. Template `assets/hello-world/` chứa các file project HTML/React boilerplate sẽ hữu ích để lưu trong skill

Ví dụ: Khi xây dựng skill `big-query` để xử lý câu hỏi "Hôm nay có bao nhiêu người dùng đăng nhập?" phân tích cho thấy:

1. Query BigQuery đòi hỏi tái khám phá table schema và mối quan hệ mỗi lần
2. File `references/schema.md` ghi lại table schema sẽ hữu ích để lưu trong skill

**Cho Claude Code plugins:** Khi xây dựng skill hooks, phân tích cho thấy:
1. Developers thường xuyên cần validate hooks.json và kiểm thử hook script
2. Tiện ích `scripts/validate-hook-schema.sh` và `scripts/test-hook.sh` sẽ hữu ích
3. `references/patterns.md` cho các pattern hook chi tiết để tránh làm SKILL.md phình to

Để xác lập nội dung của skill, phân tích từng ví dụ cụ thể để tạo danh sách tài nguyên tái sử dụng cần có: scripts, references và assets.

### Bước 3: Tạo cấu trúc Skill

Cho Claude Code plugins, tạo cấu trúc thư mục skill:

```bash
mkdir -p plugin-name/skills/skill-name/{references,examples,scripts}
touch plugin-name/skills/skill-name/SKILL.md
```

**Lưu ý:** Khác với skill-creator tổng quát dùng `init_skill.py`, plugin skill được tạo trực tiếp trong thư mục `skills/` của plugin với cấu trúc thủ công đơn giản hơn.

### Bước 4: Chỉnh sửa Skill

Khi chỉnh sửa skill (mới tạo hoặc đã có), nhớ rằng skill đang được tạo cho một instance Claude khác sử dụng. Tập trung vào việc đưa vào những thông tin có lợi và không hiển nhiên với Claude. Cân nhắc kiến thức thủ tục, chi tiết chuyên ngành hoặc asset tái sử dụng nào sẽ giúp một instance Claude khác thực hiện các tác vụ này hiệu quả hơn.

#### Bắt đầu với Nội dung Skill tái sử dụng

Để bắt đầu triển khai, bắt đầu với các tài nguyên tái sử dụng đã xác định ở trên: các file `scripts/`, `references/` và `assets/`. Lưu ý bước này có thể cần input của người dùng. Ví dụ, khi triển khai skill `brand-guidelines`, người dùng có thể cần cung cấp brand asset hoặc template để lưu trong `assets/`, hoặc tài liệu để lưu trong `references/`.

Ngoài ra, xóa các file và thư mục ví dụ không cần cho skill. Chỉ tạo các thư mục thực sự cần (references/, examples/, scripts/).

#### Cập nhật SKILL.md

**Phong cách viết:** Viết toàn bộ skill theo **dạng mệnh lệnh/nguyên thể** (câu bắt đầu bằng động từ), không dùng ngôi thứ hai. Dùng ngôn ngữ khách quan, mang tính chỉ dẫn (ví dụ: "To accomplish X, do Y" thay vì "You should do X" hoặc "If you need to do X"). Điều này duy trì sự nhất quán và rõ ràng cho AI xử lý.

**Description (Frontmatter):** Dùng định dạng ngôi thứ ba với các cụm từ kích hoạt cụ thể:

```yaml
---
name: Skill Name
description: This skill should be used when the user asks to "specific phrase 1", "specific phrase 2", "specific phrase 3". Include exact phrases users would say that should trigger this skill. Be concrete and specific.
---
```

**Ví dụ description tốt:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", "implement prompt-based hooks", or mentions hook events (PreToolUse, PostToolUse, Stop).
```

**Ví dụ description kém:**
```yaml
description: Use this skill when working with hooks.  # Sai ngôi, mơ hồ
description: Load when user needs hook help.  # Không phải ngôi thứ ba
description: Provides hook guidance.  # Không có cụm từ kích hoạt
```

Để hoàn thiện phần body của SKILL.md, trả lời các câu hỏi sau:

1. Mục đích của skill là gì, trong vài câu?
2. Khi nào nên dùng skill? (Thêm vào mô tả frontmatter với các trigger cụ thể)
3. Trong thực tế, Claude nên dùng skill như thế nào? Tất cả nội dung skill tái sử dụng đã phát triển ở trên phải được tham chiếu để Claude biết cách dùng.

**Giữ SKILL.md gọn:** Target 1,500-2,000 từ cho phần body. Chuyển nội dung chi tiết sang references/:
- Pattern chi tiết → `references/patterns.md`
- Kỹ thuật nâng cao → `references/advanced.md`
- Hướng dẫn migration → `references/migration.md`
- Tham chiếu API → `references/api-reference.md`

**Tham chiếu tài nguyên trong SKILL.md:**
```markdown
## Tài nguyên bổ sung

### Các file tham chiếu

Để biết pattern và kỹ thuật chi tiết, tham khảo:
- **`references/patterns.md`** - Các pattern phổ biến
- **`references/advanced.md`** - Trường hợp sử dụng nâng cao

### Các file ví dụ

Ví dụ hoạt động trong `examples/`:
- **`example-script.sh`** - Ví dụ hoạt động
```

### Bước 5: Xác thực và Kiểm thử

**Đối với plugin skill, xác thực khác với skill tổng quát:**

1. **Kiểm tra cấu trúc**: Thư mục skill trong `plugin-name/skills/skill-name/`
2. **Xác thực SKILL.md**: Có frontmatter với name và description
3. **Kiểm tra cụm từ kích hoạt**: Description có query người dùng cụ thể
4. **Xác minh phong cách viết**: Body dùng dạng mệnh lệnh/nguyên thể, không dùng ngôi thứ hai
5. **Kiểm tra progressive disclosure**: SKILL.md gọn (~1,500-2,000 từ), nội dung chi tiết trong references/
6. **Kiểm tra references**: Tất cả file được tham chiếu đều tồn tại
7. **Xác thực examples**: Ví dụ đầy đủ và đúng
8. **Kiểm thử scripts**: Script có thể thực thi và hoạt động đúng

**Dùng skill-reviewer agent:**
```
Hỏi: "Review my skill and check if it follows best practices"
```

Skill-reviewer agent sẽ kiểm tra chất lượng description, tổ chức nội dung và progressive disclosure.

### Bước 6: Lặp cải tiến

Sau khi kiểm thử skill, người dùng có thể yêu cầu cải tiến. Thường xảy ra ngay sau khi dùng skill, khi context về hiệu suất của skill còn tươi.

**Workflow lặp cải tiến:**
1. Dùng skill trên các tác vụ thực tế
2. Chú ý những điểm vướng mắc hoặc kém hiệu quả
3. Xác định SKILL.md hoặc tài nguyên bundled nên cập nhật như thế nào
4. Triển khai thay đổi và kiểm thử lại

**Các cải tiến phổ biến:**
- Tăng cường cụm từ kích hoạt trong description
- Chuyển các section dài từ SKILL.md sang references/
- Thêm ví dụ hoặc script còn thiếu
- Làm rõ hướng dẫn mơ hồ
- Thêm xử lý các trường hợp edge case

## Cân nhắc dành riêng cho Plugin

### Vị trí Skill trong Plugins

Plugin skill nằm trong thư mục `skills/` của plugin:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── agents/
└── skills/
    └── my-skill/
        ├── SKILL.md
        ├── references/
        ├── examples/
        └── scripts/
```

### Tự động phát hiện

Claude Code tự động phát hiện skill:
- Quét thư mục `skills/`
- Tìm các thư mục con chứa `SKILL.md`
- Luôn load metadata skill (name + description)
- Load SKILL.md body khi skill được kích hoạt
- Load references/examples khi cần

### Không cần đóng gói

Plugin skill được phân phối như một phần của plugin, không phải file ZIP riêng lẻ. Người dùng nhận skill khi cài đặt plugin.

### Kiểm thử trong Plugins

Kiểm thử skill bằng cách cài đặt plugin cục bộ:

```bash
# Kiểm thử với --plugin-dir
cc --plugin-dir /path/to/plugin

# Đặt câu hỏi để kích hoạt skill
# Xác minh skill load đúng
```

## Ví dụ từ Plugin-Dev

Nghiên cứu các skill trong plugin này như ví dụ về best practices:

**skill hook-development:**
- Cụm từ kích hoạt xuất sắc: "create a hook", "add a PreToolUse hook", v.v.
- SKILL.md gọn (1.651 từ)
- 3 file references/ cho nội dung chi tiết
- 3 examples/ về hook hoạt động
- 3 script/ tiện ích

**skill agent-development:**
- Trigger mạnh: "create an agent", "agent frontmatter", v.v.
- SKILL.md tập trung (1.438 từ)
- References có prompt tạo AI từ Claude Code
- Ví dụ agent đầy đủ

**skill plugin-settings:**
- Trigger cụ thể: "plugin settings", ".local.md files", "YAML frontmatter"
- References cho thấy triển khai thực tế (multi-agent-swarm, ralph-loop)
- Script phân tích hoạt động

Mỗi skill thể hiện progressive disclosure và triggering mạnh.

## Progressive Disclosure trong thực tế

### Nội dung vào SKILL.md

**Đưa vào (luôn load khi skill kích hoạt):**
- Khái niệm cốt lõi và tổng quan
- Quy trình thiết yếu và workflow
- Bảng tham chiếu nhanh
- Con trỏ đến references/examples/scripts
- Các trường hợp sử dụng phổ biến nhất

**Giữ dưới 3.000 từ, lý tưởng là 1.500-2.000 từ**

### Nội dung vào references/

**Chuyển sang references/ (load khi cần):**
- Pattern chi tiết và kỹ thuật nâng cao
- Tài liệu API toàn diện
- Hướng dẫn migration
- Edge case và troubleshooting
- Ví dụ và walkthrough đầy đủ

**Mỗi file tham chiếu có thể lớn (2.000-5.000+ từ)**

### Nội dung vào examples/

**Ví dụ code hoạt động:**
- Script đầy đủ, chạy được
- File cấu hình
- File template
- Ví dụ sử dụng thực tế

**Người dùng có thể copy và adapt trực tiếp**

### Nội dung vào scripts/

**Script tiện ích:**
- Tool xác thực
- Helper kiểm thử
- Tiện ích phân tích
- Script tự động hóa

**Nên có thể thực thi và được ghi lại**

## Yêu cầu phong cách viết

### Dạng mệnh lệnh/Nguyên thể

Viết theo câu bắt đầu bằng động từ, không dùng ngôi thứ hai:

**Đúng (mệnh lệnh):**
```
To create a hook, define the event type.
Configure the MCP server with authentication.
Validate settings before use.
```

**Sai (ngôi thứ hai):**
```
You should create a hook by defining the event type.
You need to configure the MCP server.
You must validate settings before use.
```

### Ngôi thứ ba trong Description

Description trong frontmatter phải dùng ngôi thứ ba:

**Đúng:**
```yaml
description: This skill should be used when the user asks to "create X", "configure Y"...
```

**Sai:**
```yaml
description: Use this skill when you want to create X...
description: Load this skill when user asks...
```

### Ngôn ngữ khách quan, mang tính chỉ dẫn

Tập trung vào việc phải làm gì, không phải ai làm:

**Đúng:**
```
Parse the frontmatter using sed.
Extract fields with grep.
Validate values before use.
```

**Sai:**
```
You can parse the frontmatter...
Claude should extract fields...
The user might validate values...
```

## Checklist xác thực

Trước khi hoàn thiện một skill:

**Cấu trúc:**
- [ ] File SKILL.md tồn tại với YAML frontmatter hợp lệ
- [ ] Frontmatter có trường `name` và `description`
- [ ] Phần body Markdown có mặt và đầy đủ
- [ ] Các file được tham chiếu thực sự tồn tại

**Chất lượng Description:**
- [ ] Dùng ngôi thứ ba ("This skill should be used when...")
- [ ] Có cụm từ kích hoạt cụ thể mà người dùng sẽ nói
- [ ] Liệt kê các tình huống cụ thể ("create X", "configure Y")
- [ ] Không mơ hồ hoặc chung chung

**Chất lượng Nội dung:**
- [ ] SKILL.md body dùng dạng mệnh lệnh/nguyên thể
- [ ] Body tập trung và gọn (lý tưởng 1.500-2.000 từ, tối đa <5k)
- [ ] Nội dung chi tiết đã chuyển sang references/
- [ ] Ví dụ đầy đủ và hoạt động
- [ ] Script có thể thực thi và được ghi lại

**Progressive Disclosure:**
- [ ] Khái niệm cốt lõi trong SKILL.md
- [ ] Tài liệu chi tiết trong references/
- [ ] Code hoạt động trong examples/
- [ ] Tiện ích trong scripts/
- [ ] SKILL.md tham chiếu đến các tài nguyên này

**Kiểm thử:**
- [ ] Skill kích hoạt theo query người dùng mong đợi
- [ ] Nội dung hữu ích cho các tác vụ đích
- [ ] Không có thông tin trùng lặp giữa các file
- [ ] References load khi cần

## Các lỗi thường gặp cần tránh

### Lỗi 1: Description kích hoạt yếu

❌ **Kém:**
```yaml
description: Provides guidance for working with hooks.
```

**Lý do kém:** Mơ hồ, không có cụm từ kích hoạt cụ thể, không dùng ngôi thứ ba

✅ **Tốt:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events. Provides comprehensive hooks API guidance.
```

**Lý do tốt:** Ngôi thứ ba, cụm từ cụ thể, tình huống rõ ràng

### Lỗi 2: Quá nhiều nội dung trong SKILL.md

❌ **Kém:**
```
skill-name/
└── SKILL.md  (8.000 từ - tất cả trong một file)
```

**Lý do kém:** Làm phình context khi skill load, nội dung chi tiết luôn được load

✅ **Tốt:**
```
skill-name/
├── SKILL.md  (1.800 từ - những điều cốt lõi thiết yếu)
└── references/
    ├── patterns.md (2.500 từ)
    └── advanced.md (3.700 từ)
```

**Lý do tốt:** Progressive disclosure, nội dung chi tiết chỉ load khi cần

### Lỗi 3: Viết theo ngôi thứ hai

❌ **Kém:**
```markdown
You should start by reading the configuration file.
You need to validate the input.
You can use the grep tool to search.
```

**Lý do kém:** Ngôi thứ hai, không phải dạng mệnh lệnh

✅ **Tốt:**
```markdown
Start by reading the configuration file.
Validate the input before processing.
Use the grep tool to search for patterns.
```

**Lý do tốt:** Dạng mệnh lệnh, hướng dẫn trực tiếp

### Lỗi 4: Thiếu tham chiếu đến tài nguyên

❌ **Kém:**
```markdown
# SKILL.md

[Nội dung cốt lõi]

[Không đề cập references/ hoặc examples/]
```

**Lý do kém:** Claude không biết references tồn tại

✅ **Tốt:**
```markdown
# SKILL.md

[Nội dung cốt lõi]

## Tài nguyên bổ sung

### Các file tham chiếu
- **`references/patterns.md`** - Pattern chi tiết
- **`references/advanced.md`** - Kỹ thuật nâng cao

### Các file ví dụ
- **`examples/script.sh`** - Ví dụ hoạt động
```

**Lý do tốt:** Claude biết tìm thêm thông tin ở đâu

## Tham chiếu nhanh

### Skill tối giản

```
skill-name/
└── SKILL.md
```

Phù hợp cho: Kiến thức đơn giản, không cần tài nguyên phức tạp

### Skill tiêu chuẩn (Khuyến nghị)

```
skill-name/
├── SKILL.md
├── references/
│   └── detailed-guide.md
└── examples/
    └── working-example.sh
```

Phù hợp cho: Hầu hết plugin skill có tài liệu chi tiết

### Skill đầy đủ

```
skill-name/
├── SKILL.md
├── references/
│   ├── patterns.md
│   └── advanced.md
├── examples/
│   ├── example1.sh
│   └── example2.json
└── scripts/
    └── validate.sh
```

Phù hợp cho: Lĩnh vực phức tạp có tiện ích xác thực

## Tóm tắt Best Practices

✅ **NÊN:**
- Dùng ngôi thứ ba trong description ("This skill should be used when...")
- Có cụm từ kích hoạt cụ thể ("create X", "configure Y")
- Giữ SKILL.md gọn (1.500-2.000 từ)
- Dùng progressive disclosure (chuyển chi tiết sang references/)
- Viết theo dạng mệnh lệnh/nguyên thể
- Tham chiếu các file hỗ trợ rõ ràng
- Cung cấp ví dụ hoạt động
- Tạo script tiện ích cho các thao tác phổ biến
- Nghiên cứu skill của plugin-dev như template

❌ **KHÔNG NÊN:**
- Dùng ngôi thứ hai ở bất kỳ đâu
- Để điều kiện kích hoạt mơ hồ
- Nhồi tất cả vào SKILL.md (>3.000 từ mà không có references/)
- Viết theo ngôi thứ hai ("You should...")
- Để tài nguyên không được tham chiếu
- Thêm ví dụ không đầy đủ hoặc bị lỗi
- Bỏ qua xác thực

## Tài nguyên bổ sung

### Nghiên cứu các Skill này

Skill của plugin-dev thể hiện best practices:
- `../hook-development/` - Progressive disclosure, tiện ích
- `../agent-development/` - Tạo có sự hỗ trợ của AI, references
- `../mcp-integration/` - References toàn diện
- `../plugin-settings/` - Ví dụ thực tế
- `../command-development/` - Khái niệm quan trọng rõ ràng
- `../plugin-structure/` - Tổ chức tốt

### Các file tham chiếu

Để xem phương pháp skill-creator đầy đủ:
- **`references/skill-creator-original.md`** - Nội dung skill-creator gốc đầy đủ

## Quy trình triển khai

Để tạo skill cho plugin của bạn:

1. **Hiểu use case**: Xác định các ví dụ cụ thể về cách dùng skill
2. **Lên kế hoạch tài nguyên**: Xác định scripts/references/examples nào cần có
3. **Tạo cấu trúc**: `mkdir -p skills/skill-name/{references,examples,scripts}`
4. **Viết SKILL.md**:
   - Frontmatter với description ngôi thứ ba và cụm từ kích hoạt
   - Body gọn (1.500-2.000 từ) theo dạng mệnh lệnh
   - Tham chiếu các file hỗ trợ
5. **Thêm tài nguyên**: Tạo references/, examples/, scripts/ khi cần
6. **Xác thực**: Kiểm tra description, phong cách viết, tổ chức
7. **Kiểm thử**: Xác minh skill load theo trigger mong đợi
8. **Lặp cải tiến**: Cải thiện dựa trên sử dụng thực tế

Tập trung vào description kích hoạt mạnh, progressive disclosure và phong cách viết mệnh lệnh để có skill hiệu quả, load đúng lúc và cung cấp hướng dẫn đúng trọng tâm.
