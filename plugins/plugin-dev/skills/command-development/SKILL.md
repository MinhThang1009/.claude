---
name: Command Development
description: This skill should be used when the user asks to "create a slash command", "add a command", "write a custom command", "define command arguments", "use command frontmatter", "organize commands", "create command with file references", "interactive command", "use AskUserQuestion in command", or needs guidance on slash command structure, YAML frontmatter fields, dynamic arguments, bash execution in commands, user interaction patterns, or command development best practices for Claude Code.
---

# Phát triển Command cho Claude Code

> **Lưu ý:** Thư mục `.claude/commands/` là định dạng legacy. Với skills mới, hãy dùng định dạng `.claude/skills/<name>/SKILL.md`. Cả hai đều được load giống nhau — chỉ khác cách tổ chức file. Xem skill `skill-development` để biết định dạng được khuyến nghị.

## Tổng quan

Slash command là các prompt dùng thường xuyên, được định nghĩa dưới dạng file Markdown mà Claude thực thi trong các phiên làm việc tương tác. Hiểu cấu trúc command, các tùy chọn frontmatter và tính năng động giúp tạo ra các workflow mạnh mẽ, tái sử dụng được.

**Các khái niệm cốt lõi:**
- Định dạng file Markdown cho command
- YAML frontmatter để cấu hình
- Argument động và file reference
- Bash execution để lấy context
- Tổ chức command và namespacing

## Cơ bản về Command

### Slash Command là gì?

Slash command là file Markdown chứa một prompt mà Claude thực thi khi được gọi. Command cung cấp:
- **Tái sử dụng**: Định nghĩa một lần, dùng nhiều lần
- **Nhất quán**: Chuẩn hóa các workflow phổ biến
- **Chia sẻ**: Phân phối trong team hoặc dự án
- **Hiệu quả**: Truy cập nhanh vào các prompt phức tạp

### Quan trọng: Command là Chỉ dẫn CHO Claude

**Command được viết để agent tiêu thụ, không phải để con người đọc.**

Khi người dùng gọi `/command-name`, nội dung command trở thành chỉ dẫn của Claude. Viết command như các chỉ thị GỬI ĐẾN Claude về việc cần làm, không phải là thông điệp GỬI ĐẾN người dùng.

**Cách đúng (chỉ dẫn cho Claude):**
```markdown
Review this code for security vulnerabilities including:
- SQL injection
- XSS attacks
- Authentication issues

Provide specific line numbers and severity ratings.
```

**Cách sai (thông điệp gửi đến người dùng):**
```markdown
This command will review your code for security issues.
You'll receive a report with vulnerability details.
```

Ví dụ đầu nói cho Claude biết cần làm gì. Ví dụ sau nói cho người dùng biết điều gì sẽ xảy ra nhưng không hướng dẫn Claude. Luôn dùng cách đầu tiên.

### Vị trí Command

**Project command** (chia sẻ với team):
- Vị trí: `.claude/commands/`
- Phạm vi: Khả dụng trong project cụ thể
- Nhãn: Hiển thị là "(project)" trong `/help`
- Dùng cho: Workflow của team, tác vụ đặc thù của project

**Personal command** (khả dụng ở mọi nơi):
- Vị trí: `~/.claude/commands/`
- Phạm vi: Khả dụng trong tất cả project
- Nhãn: Hiển thị là "(user)" trong `/help`
- Dùng cho: Workflow cá nhân, tiện ích xuyên project

**Plugin command** (đi kèm plugin):
- Vị trí: `plugin-name/commands/`
- Phạm vi: Khả dụng khi plugin được cài đặt
- Nhãn: Hiển thị là "(plugin-name)" trong `/help`
- Dùng cho: Chức năng đặc thù của plugin

## Định dạng File

### Cấu trúc cơ bản

Command là các file Markdown với phần mở rộng `.md`:

```
.claude/commands/
├── review.md           # lệnh /review
├── test.md             # lệnh /test
└── deploy.md           # lệnh /deploy
```

**Command đơn giản:**
```markdown
Review this code for security vulnerabilities including:
- SQL injection
- XSS attacks
- Authentication bypass
- Insecure data handling
```

Không cần frontmatter cho command cơ bản.

### Với YAML Frontmatter

Thêm cấu hình bằng YAML frontmatter:

```markdown
---
description: Review code for security issues
allowed-tools: Read, Grep, Bash(git:*)
model: sonnet
---

Review this code for security vulnerabilities...
```

## Các trường YAML Frontmatter

### description

**Mục đích:** Mô tả ngắn hiển thị trong `/help`
**Kiểu:** String
**Mặc định:** Dòng đầu tiên của prompt command

```yaml
---
description: Review pull request for code quality
---
```

**Thực hành tốt:** Mô tả rõ ràng, có tính hành động (dưới 60 ký tự)

### allowed-tools

**Mục đích:** Chỉ định tool nào command có thể dùng
**Kiểu:** String hoặc Array
**Mặc định:** Kế thừa từ conversation

```yaml
---
allowed-tools: Read, Write, Edit, Bash(git:*)
---
```

**Các pattern:**
- `Read, Write, Edit` - Tool cụ thể
- `Bash(git:*)` - Bash chỉ với git command
- `*` - Tất cả tool (hiếm khi cần)

**Dùng khi:** Command yêu cầu quyền truy cập tool cụ thể

### model

**Mục đích:** Chỉ định model để thực thi command
**Kiểu:** String (sonnet, opus, haiku)
**Mặc định:** Kế thừa từ conversation

```yaml
---
model: haiku
---
```

**Các trường hợp dùng:**
- `haiku` - Command nhanh, đơn giản
- `sonnet` - Workflow tiêu chuẩn
- `opus` - Phân tích phức tạp

### argument-hint

**Mục đích:** Tài liệu hóa các argument mong đợi cho autocomplete
**Kiểu:** String
**Mặc định:** Không có

```yaml
---
argument-hint: [pr-number] [priority] [assignee]
---
```

**Lợi ích:**
- Giúp người dùng hiểu các argument của command
- Cải thiện khả năng tìm kiếm command
- Tài liệu hóa interface của command

### disable-model-invocation

**Mục đích:** Ngăn SlashCommand tool gọi command theo chương trình
**Kiểu:** Boolean
**Mặc định:** false

```yaml
---
disable-model-invocation: true
---
```

**Dùng khi:** Command chỉ nên được gọi thủ công

## Argument Động

### Dùng $ARGUMENTS

Bắt tất cả argument dưới dạng một string:

```markdown
---
description: Fix issue by number
argument-hint: [issue-number]
---

Fix issue #$ARGUMENTS following our coding standards and best practices.
```

**Cách dùng:**
```
> /fix-issue 123
> /fix-issue 456
```

**Kết quả mở rộng:**
```
Fix issue #123 following our coding standards...
Fix issue #456 following our coding standards...
```

### Dùng Positional Argument

Bắt từng argument riêng lẻ với `$1`, `$2`, `$3`, v.v.:

```markdown
---
description: Review PR with priority and assignee
argument-hint: [pr-number] [priority] [assignee]
---

Review pull request #$1 with priority level $2.
After review, assign to $3 for follow-up.
```

**Cách dùng:**
```
> /review-pr 123 high alice
```

**Kết quả mở rộng:**
```
Review pull request #123 with priority level high.
After review, assign to alice for follow-up.
```

### Kết hợp Argument

Trộn positional và argument còn lại:

```markdown
Deploy $1 to $2 environment with options: $3
```

**Cách dùng:**
```
> /deploy api staging --force --skip-tests
```

**Kết quả mở rộng:**
```
Deploy api to staging environment with options: --force --skip-tests
```

## File Reference

### Dùng cú pháp @

Đưa nội dung file vào command:

```markdown
---
description: Review specific file
argument-hint: [file-path]
---

Review @$1 for:
- Code quality
- Best practices
- Potential bugs
```

**Cách dùng:**
```
> /review-file src/api/users.ts
```

**Hiệu ứng:** Claude đọc `src/api/users.ts` trước khi xử lý command

### Nhiều File Reference

Tham chiếu nhiều file:

```markdown
Compare @src/old-version.js with @src/new-version.js

Identify:
- Breaking changes
- New features
- Bug fixes
```

### File Reference Tĩnh

Tham chiếu file đã biết mà không cần argument:

```markdown
Review @package.json and @tsconfig.json for consistency

Ensure:
- TypeScript version matches
- Dependencies are aligned
- Build configuration is correct
```

## Bash Execution trong Command

Command có thể thực thi bash command nội tuyến để thu thập context động trước khi Claude xử lý command. Điều này hữu ích khi cần đưa vào trạng thái repository, thông tin môi trường, hoặc context đặc thù của project.

**Khi nào dùng:**
- Đưa vào context động (git status, biến môi trường, v.v.)
- Thu thập trạng thái project/repository
- Xây dựng workflow nhận biết context

**Chi tiết triển khai:**
Để biết cú pháp đầy đủ, ví dụ và thực hành tốt, xem `references/plugin-features-reference.md` phần về bash execution. Tài liệu tham chiếu bao gồm cú pháp chính xác và nhiều ví dụ hoạt động để tránh các vấn đề khi thực thi.

## Tổ chức Command

### Cấu trúc phẳng

Tổ chức đơn giản cho bộ command nhỏ:

```
.claude/commands/
├── build.md
├── test.md
├── deploy.md
├── review.md
└── docs.md
```

**Dùng khi:** 5-15 command, không có danh mục rõ ràng

### Cấu trúc có Namespace

Tổ chức command trong thư mục con:

```
.claude/commands/
├── ci/
│   ├── build.md        # /build (project:ci)
│   ├── test.md         # /test (project:ci)
│   └── lint.md         # /lint (project:ci)
├── git/
│   ├── commit.md       # /commit (project:git)
│   └── pr.md           # /pr (project:git)
└── docs/
    ├── generate.md     # /generate (project:docs)
    └── publish.md      # /publish (project:docs)
```

**Lợi ích:**
- Nhóm hợp lý theo danh mục
- Namespace hiển thị trong `/help`
- Dễ tìm các command liên quan

**Dùng khi:** 15+ command, có danh mục rõ ràng

## Thực hành Tốt

### Thiết kế Command

1. **Trách nhiệm đơn:** Một command, một tác vụ
2. **Mô tả rõ ràng:** Tự giải thích được trong `/help`
3. **Dependency tường minh:** Dùng `allowed-tools` khi cần
4. **Tài liệu hóa argument:** Luôn cung cấp `argument-hint`
5. **Đặt tên nhất quán:** Dùng pattern động từ-danh từ (review-pr, fix-issue)

### Xử lý Argument

1. **Validate argument:** Kiểm tra argument bắt buộc trong prompt
2. **Cung cấp giá trị mặc định:** Gợi ý mặc định khi thiếu argument
3. **Tài liệu hóa định dạng:** Giải thích định dạng argument mong đợi
4. **Xử lý edge case:** Xét trường hợp thiếu hoặc argument không hợp lệ

```markdown
---
argument-hint: [pr-number]
---

$IF($1,
  Review PR #$1,
  Please provide a PR number. Usage: /review-pr [number]
)
```

### File Reference

1. **Path tường minh:** Dùng path file rõ ràng
2. **Kiểm tra sự tồn tại:** Xử lý file thiếu một cách graceful
3. **Path tương đối:** Dùng path tương đối với project
4. **Hỗ trợ Glob:** Cân nhắc dùng Glob tool cho các pattern

### Bash Command

1. **Giới hạn phạm vi:** Dùng `Bash(git:*)` không phải `Bash(*)`
2. **Command an toàn:** Tránh các thao tác phá hủy dữ liệu
3. **Xử lý lỗi:** Xét trường hợp command thất bại
4. **Giữ nhanh:** Command chạy lâu làm chậm thời gian gọi

### Tài liệu hóa

1. **Thêm comment:** Giải thích logic phức tạp
2. **Cung cấp ví dụ:** Hiển thị cách dùng trong comment
3. **Liệt kê yêu cầu:** Tài liệu hóa dependency
4. **Phiên bản command:** Ghi chú breaking change

```markdown
---
description: Deploy application to environment
argument-hint: [environment] [version]
---

<!--
Usage: /deploy [staging|production] [version]
Requires: AWS credentials configured
Example: /deploy staging v1.2.3
-->

Deploy application to $1 environment using version $2...
```

## Pattern Phổ Biến

### Pattern Review

```markdown
---
description: Review code changes
allowed-tools: Read, Bash(git:*)
---

Files changed: !`git diff --name-only`

Review each file for:
1. Code quality and style
2. Potential bugs or issues
3. Test coverage
4. Documentation needs

Provide specific feedback for each file.
```

### Pattern Testing

```markdown
---
description: Run tests for specific file
argument-hint: [test-file]
allowed-tools: Bash(npm:*)
---

Run tests: !`npm test $1`

Analyze results and suggest fixes for failures.
```

### Pattern Tài liệu hóa

```markdown
---
description: Generate documentation for file
argument-hint: [source-file]
---

Generate comprehensive documentation for @$1 including:
- Function/class descriptions
- Parameter documentation
- Return value descriptions
- Usage examples
- Edge cases and errors
```

### Pattern Workflow

```markdown
---
description: Complete PR workflow
argument-hint: [pr-number]
allowed-tools: Bash(gh:*), Read
---

PR #$1 Workflow:

1. Fetch PR: !`gh pr view $1`
2. Review changes
3. Run checks
4. Approve or request changes
```

## Xử lý Sự cố

**Command không hiển thị:**
- Kiểm tra file ở đúng thư mục
- Xác nhận có phần mở rộng `.md`
- Đảm bảo định dạng Markdown hợp lệ
- Khởi động lại Claude Code

**Argument không hoạt động:**
- Xác nhận cú pháp `$1`, `$2` đúng
- Kiểm tra `argument-hint` khớp với cách dùng
- Đảm bảo không có khoảng trắng thừa

**Bash execution thất bại:**
- Kiểm tra `allowed-tools` bao gồm Bash
- Xác nhận cú pháp command trong backtick
- Thử command trong terminal trước
- Kiểm tra quyền truy cập cần thiết

**File reference không hoạt động:**
- Xác nhận cú pháp `@` đúng
- Kiểm tra path file hợp lệ
- Đảm bảo Read tool được cho phép
- Dùng path tuyệt đối hoặc tương đối với project

## Tính năng Đặc thù của Plugin

### Biến CLAUDE_PLUGIN_ROOT

Plugin command có quyền truy cập vào `${CLAUDE_PLUGIN_ROOT}`, biến môi trường phân giải thành đường dẫn tuyệt đối của plugin.

**Mục đích:**
- Tham chiếu file plugin di động
- Thực thi script plugin
- Tải cấu hình plugin
- Truy cập template plugin

**Cách dùng cơ bản:**

```markdown
---
description: Analyze using plugin script
allowed-tools: Bash(node:*)
---

Run analysis: !`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js $1`

Review results and report findings.
```

**Các pattern phổ biến:**

```markdown
# Thực thi script plugin
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/script.sh`

# Tải cấu hình plugin
@${CLAUDE_PLUGIN_ROOT}/config/settings.json

# Dùng template plugin
@${CLAUDE_PLUGIN_ROOT}/templates/report.md

# Truy cập tài nguyên plugin
@${CLAUDE_PLUGIN_ROOT}/docs/reference.md
```

**Tại sao dùng:**
- Hoạt động trên tất cả môi trường cài đặt
- Di động giữa các hệ thống
- Không cần hardcode path
- Thiết yếu cho plugin đa file

### Tổ chức Plugin Command

Plugin command được tự động tìm thấy từ thư mục `commands/`:

```
plugin-name/
├── commands/
│   ├── foo.md              # /foo (plugin:plugin-name)
│   ├── bar.md              # /bar (plugin:plugin-name)
│   └── utils/
│       └── helper.md       # /helper (plugin:plugin-name:utils)
└── plugin.json
```

**Lợi ích của namespace:**
- Nhóm command hợp lý
- Hiển thị trong output `/help`
- Tránh xung đột tên
- Tổ chức command liên quan

**Quy ước đặt tên:**
- Dùng tên hành động mô tả
- Tránh tên chung chung (test, run)
- Cân nhắc prefix đặc thù của plugin
- Dùng dấu gạch ngang cho tên nhiều từ

### Pattern Plugin Command

**Pattern dựa trên cấu hình:**

```markdown
---
description: Deploy using plugin configuration
argument-hint: [environment]
allowed-tools: Read, Bash(*)
---

Load configuration: @${CLAUDE_PLUGIN_ROOT}/config/$1-deploy.json

Deploy to $1 using configuration settings.
Monitor deployment and report status.
```

**Pattern dựa trên template:**

```markdown
---
description: Generate docs from template
argument-hint: [component]
---

Template: @${CLAUDE_PLUGIN_ROOT}/templates/docs.md

Generate documentation for $1 following template structure.
```

**Pattern đa script:**

```markdown
---
description: Complete build workflow
allowed-tools: Bash(*)
---

Build: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh`
Test: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/test.sh`
Package: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/package.sh`

Review outputs and report workflow status.
```

**Xem `references/plugin-features-reference.md` để biết các pattern chi tiết.**

## Tích hợp với Các Thành phần Plugin

Command có thể tích hợp với các thành phần plugin khác để tạo workflow mạnh mẽ.

### Tích hợp Agent

Khởi chạy plugin agent cho các tác vụ phức tạp:

```markdown
---
description: Deep code review
argument-hint: [file-path]
---

Initiate comprehensive review of @$1 using the code-reviewer agent.

The agent will analyze:
- Code structure
- Security issues
- Performance
- Best practices

Agent uses plugin resources:
- ${CLAUDE_PLUGIN_ROOT}/config/rules.json
- ${CLAUDE_PLUGIN_ROOT}/checklists/review.md
```

**Điểm quan trọng:**
- Agent phải tồn tại trong thư mục `plugin/agents/`
- Claude dùng Task tool để khởi chạy agent
- Tài liệu hóa khả năng của agent
- Tham chiếu tài nguyên plugin mà agent dùng

### Tích hợp Skill

Tận dụng plugin skill để có kiến thức chuyên biệt:

```markdown
---
description: Document API with standards
argument-hint: [api-file]
---

Document API in @$1 following plugin standards.

Use the api-docs-standards skill to ensure:
- Complete endpoint documentation
- Consistent formatting
- Example quality
- Error documentation

Generate production-ready API docs.
```

**Điểm quan trọng:**
- Skill phải tồn tại trong thư mục `plugin/skills/`
- Đề cập tên skill để kích hoạt gọi
- Tài liệu hóa mục đích của skill
- Giải thích skill cung cấp gì

### Phối hợp Hook

Thiết kế command hoạt động cùng plugin hook:
- Command có thể chuẩn bị state để hook xử lý
- Hook thực thi tự động theo tool event
- Command nên tài liệu hóa hành vi hook mong đợi
- Hướng dẫn Claude cách diễn giải output của hook

Xem `references/plugin-features-reference.md` để biết ví dụ về command phối hợp với hook

### Workflow Đa Thành phần

Kết hợp agent, skill và script:

```markdown
---
description: Comprehensive review workflow
argument-hint: [file]
allowed-tools: Bash(node:*), Read
---

Target: @$1

Phase 1 - Static Analysis:
!`node ${CLAUDE_PLUGIN_ROOT}/scripts/lint.js $1`

Phase 2 - Deep Review:
Launch code-reviewer agent for detailed analysis.

Phase 3 - Standards Check:
Use coding-standards skill for validation.

Phase 4 - Report:
Template: @${CLAUDE_PLUGIN_ROOT}/templates/review.md

Compile findings into report following template.
```

**Khi nào dùng:**
- Workflow đa bước phức tạp
- Tận dụng nhiều khả năng plugin
- Yêu cầu phân tích chuyên biệt
- Cần output có cấu trúc

## Pattern Validation

Command nên validate input và tài nguyên trước khi xử lý.

### Validation Argument

```markdown
---
description: Deploy with validation
argument-hint: [environment]
---

Validate environment: !`echo "$1" | grep -E "^(dev|staging|prod)$" || echo "INVALID"`

If $1 is valid environment:
  Deploy to $1
Otherwise:
  Explain valid environments: dev, staging, prod
  Show usage: /deploy [environment]
```

### Kiểm tra Sự tồn tại File

```markdown
---
description: Process configuration
argument-hint: [config-file]
---

Check file exists: !`test -f $1 && echo "EXISTS" || echo "MISSING"`

If file exists:
  Process configuration: @$1
Otherwise:
  Explain where to place config file
  Show expected format
  Provide example configuration
```

### Validation Tài nguyên Plugin

```markdown
---
description: Run plugin analyzer
allowed-tools: Bash(test:*)
---

Validate plugin setup:
- Script: !`test -x ${CLAUDE_PLUGIN_ROOT}/bin/analyze && echo "✓" || echo "✗"`
- Config: !`test -f ${CLAUDE_PLUGIN_ROOT}/config.json && echo "✓" || echo "✗"`

If all checks pass, run analysis.
Otherwise, report missing components.
```

### Xử lý Lỗi

```markdown
---
description: Build with error handling
allowed-tools: Bash(*)
---

Execute build: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh 2>&1 || echo "BUILD_FAILED"`

If build succeeded:
  Report success and output location
If build failed:
  Analyze error output
  Suggest likely causes
  Provide troubleshooting steps
```

**Thực hành tốt:**
- Validate sớm trong command
- Cung cấp thông báo lỗi hữu ích
- Gợi ý hành động khắc phục
- Xử lý edge case một cách graceful

---

Để biết đặc tả chi tiết các trường frontmatter, xem `references/frontmatter-reference.md`.
Để biết tính năng và pattern đặc thù của plugin, xem `references/plugin-features-reference.md`.
Để biết ví dụ pattern command, xem thư mục `examples/`.
