# Gợi Ý Skills

Skill là kiến thức chuyên biệt được đóng gói, bao gồm workflow, tài liệu tham khảo, và best practice. Tạo chúng trong `.claude/skills/<name>/SKILL.md`. Skill có thể được Claude tự động gọi khi phù hợp, hoặc người dùng gọi trực tiếp qua `/skill-name`.

Một số skill dựng sẵn có thể cài qua plugin chính thức (cài qua `/plugin install`).

**Lưu ý**: Đây là các pattern phổ biến. Dùng web search để tìm ý tưởng skill phù hợp với tool và framework cụ thể của codebase.

---

## Có Sẵn Từ Plugin Chính Thức

### Phát Triển Plugin (plugin-dev)

| Skill | Phù hợp nhất cho |
|-------|----------|
| **skill-development** | Tạo skill mới đúng cấu trúc |
| **hook-development** | Xây dựng hook để tự động hóa |
| **command-development** | Tạo slash command |
| **agent-development** | Xây dựng subagent chuyên biệt |
| **mcp-integration** | Tích hợp MCP server vào plugin |
| **plugin-structure** | Hiểu kiến trúc plugin |

### Workflow Git (commit-commands)

| Skill | Phù hợp nhất cho |
|-------|----------|
| **commit** | Tạo git commit với message chuẩn |
| **commit-push-pr** | Toàn bộ workflow commit, push, và PR |

### Frontend (frontend-design)

| Skill | Phù hợp nhất cho |
|-------|----------|
| **frontend-design** | Tạo UI component hoàn thiện |

**Giá trị**: Tạo UI đặc sắc, chất lượng cao thay vì thiết kế AI chung chung.

### Quy Tắc Tự Động Hóa (hookify)

| Skill | Phù hợp nhất cho |
|-------|----------|
| **writing-rules** | Tạo quy tắc hookify để tự động hóa |

### Phát Triển Tính Năng (feature-dev)

| Skill | Phù hợp nhất cho |
|-------|----------|
| **feature-dev** | Workflow phát triển tính năng end-to-end |

---

## Tham Khảo Nhanh: Skill Từ Plugin Chính Thức

| Dấu hiệu Codebase | Skill | Plugin |
|-----------------|-------|--------|
| Đang xây dựng plugin | skill-development | plugin-dev |
| Commit git | commit | commit-commands |
| React/Vue/Angular | frontend-design | frontend-design |
| Quy tắc tự động hóa | writing-rules | hookify |
| Lập kế hoạch tính năng | feature-dev | feature-dev |

---

## Skill Tùy Chỉnh Cho Project

Tạo skill riêng cho project trong `.claude/skills/<name>/SKILL.md`.

### Cấu Trúc Skill

```
.claude/skills/
└── my-skill/
    ├── SKILL.md           # Hướng dẫn chính (bắt buộc)
    ├── template.yaml      # Template để áp dụng
    ├── scripts/
    │   └── validate.sh    # Script để chạy
    └── examples/          # Ví dụ tham khảo
```

### Tham Khảo Frontmatter

```yaml
---
name: skill-name
description: Skill này làm gì và khi nào dùng
disable-model-invocation: true  # Chỉ người dùng mới gọi được (dành cho side effect)
user-invocable: false           # Chỉ Claude gọi được (dành cho kiến thức nền)
allowed-tools: Read, Grep, Glob # Giới hạn quyền truy cập tool
context: fork                   # Chạy trong subagent độc lập
agent: Explore                  # Loại agent khi fork
---
```

### Kiểm Soát Gọi Skill

| Cài đặt | Người dùng | Claude | Dùng cho |
|---------|------|--------|---------|
| (mặc định) | ✓ | ✓ | Skill đa năng |
| `disable-model-invocation: true` | ✓ | ✗ | Side effect (deploy, gửi) |
| `user-invocable: false` | ✗ | ✓ | Kiến thức nền |

---

## Ví Dụ Skill Tùy Chỉnh

### Tạo API Documentation Với OpenAPI Template

Áp dụng YAML template để tạo API doc nhất quán:

```
.claude/skills/api-doc/
├── SKILL.md
└── openapi-template.yaml
```

**SKILL.md:**
```yaml
---
name: api-doc
description: Generate OpenAPI documentation for an endpoint. Use when documenting API routes.
---

Generate OpenAPI documentation for the endpoint at $ARGUMENTS.

Use the template in [openapi-template.yaml](openapi-template.yaml) as the structure.

1. Read the endpoint code
2. Extract path, method, parameters, request/response schemas
3. Fill in the template with actual values
4. Output the completed YAML
```

**openapi-template.yaml:**
```yaml
paths:
  /{path}:
    {method}:
      summary: ""
      description: ""
      parameters: []
      requestBody:
        content:
          application/json:
            schema: {}
      responses:
        "200":
          description: ""
          content:
            application/json:
              schema: {}
```

---

### Tạo Database Migration Với Script

Tạo và kiểm tra migration dùng script đi kèm:

```
.claude/skills/create-migration/
├── SKILL.md
└── scripts/
    └── validate-migration.sh
```

**SKILL.md:**
```yaml
---
name: create-migration
description: Create a database migration file
disable-model-invocation: true
allowed-tools: Read, Write, Bash
---

Create a migration for: $ARGUMENTS

1. Generate migration file in `migrations/` with timestamp prefix
2. Include up and down functions
3. Run validation: `bash ~/.claude/skills/create-migration/scripts/validate-migration.sh`
4. Report any issues found
```

**scripts/validate-migration.sh:**
```bash
#!/bin/bash
# Validate migration syntax
npx prisma validate 2>&1 || echo "Validation failed"
```

---

### Tạo Test Với Ví Dụ

Tạo test theo pattern của project:

```
.claude/skills/gen-test/
├── SKILL.md
└── examples/
    ├── unit-test.ts
    └── integration-test.ts
```

**SKILL.md:**
```yaml
---
name: gen-test
description: Generate tests for a file following project conventions
disable-model-invocation: true
---

Generate tests for: $ARGUMENTS

Reference these examples for the expected patterns:
- Unit tests: [examples/unit-test.ts](examples/unit-test.ts)
- Integration tests: [examples/integration-test.ts](examples/integration-test.ts)

1. Analyze the source file
2. Identify functions/methods to test
3. Generate tests matching project conventions
4. Place in appropriate test directory
```

---

### Tạo Component Với Template

Scaffold component mới từ template:

```
.claude/skills/new-component/
├── SKILL.md
└── templates/
    ├── component.tsx.template
    ├── component.test.tsx.template
    └── component.stories.tsx.template
```

**SKILL.md:**
```yaml
---
name: new-component
description: Scaffold a new React component with tests and stories
disable-model-invocation: true
---

Create component: $ARGUMENTS

Use templates in [templates/](templates/) directory:
1. Generate component from component.tsx.template
2. Generate tests from component.test.tsx.template
3. Generate Storybook story from component.stories.tsx.template

Replace {{ComponentName}} with the PascalCase name.
Replace {{component-name}} with the kebab-case name.
```

---

### Review PR Với Checklist

Review PR theo checklist riêng của project:

```
.claude/skills/pr-check/
├── SKILL.md
└── checklist.md
```

**SKILL.md:**
```yaml
---
name: pr-check
description: Review PR against project checklist
disable-model-invocation: true
context: fork
---

## PR Context
- Diff: !`gh pr diff`
- Description: !`gh pr view`

Review against [checklist.md](checklist.md).

For each item, mark ✅ or ❌ with explanation.
```

**checklist.md:**
```markdown
## PR Checklist

- [ ] Tests added for new functionality
- [ ] No console.log statements
- [ ] Error handling includes user-facing messages
- [ ] API changes are backwards compatible
- [ ] Database migrations are reversible
```

---

### Tạo Release Note

Tạo release note từ lịch sử git:

**SKILL.md:**
```yaml
---
name: release-notes
description: Generate release notes from commits since last tag
disable-model-invocation: true
---

## Recent Changes
- Commits since last tag: !`git log $(git describe --tags --abbrev=0)..HEAD --oneline`
- Last tag: !`git describe --tags --abbrev=0`

Generate release notes:
1. Group commits by type (feat, fix, docs, etc.)
2. Write user-friendly descriptions
3. Highlight breaking changes
4. Format as markdown
```

---

### Convention Project (Chỉ Claude Gọi)

Kiến thức nền Claude tự động áp dụng:

**SKILL.md:**
```yaml
---
name: project-conventions
description: Code style and patterns for this project. Apply when writing or reviewing code.
user-invocable: false
---

## Naming Conventions
- React components: PascalCase
- Utilities: camelCase
- Constants: UPPER_SNAKE_CASE
- Files: kebab-case

## Patterns
- Use `Result<T, E>` for fallible operations, not exceptions
- Prefer composition over inheritance
- All API responses use `{ data, error, meta }` shape

## Forbidden
- No `any` types
- No `console.log` in production code
- No synchronous file I/O
```

---

### Cài Đặt Môi Trường

Hướng dẫn developer mới với script cài đặt:

```
.claude/skills/setup-dev/
├── SKILL.md
└── scripts/
    └── check-prerequisites.sh
```

**SKILL.md:**
```yaml
---
name: setup-dev
description: Set up development environment for new contributors
disable-model-invocation: true
---

Set up development environment:

1. Check prerequisites: `bash scripts/check-prerequisites.sh`
2. Install dependencies: `npm install`
3. Copy environment template: `cp .env.example .env`
4. Set up database: `npm run db:setup`
5. Verify setup: `npm test`

Report any issues encountered.
```

---

## Pattern Argument

| Pattern | Ý nghĩa | Ví dụ |
|---------|---------|---------|
| `$ARGUMENTS` | Toàn bộ argument dưới dạng chuỗi | `/deploy staging` → "staging" |

Argument được nối thêm dưới dạng `ARGUMENTS: <value>` nếu `$ARGUMENTS` không có trong skill.

## Inject Context Động

Dùng `` !`command` `` để inject dữ liệu trực tiếp trước khi skill chạy:

```yaml
## Trạng Thái Hiện Tại
- Branch: !`git branch --show-current`
- Status: !`git status --short`
```

Output của command thay thế placeholder trước khi Claude nhận nội dung skill.
