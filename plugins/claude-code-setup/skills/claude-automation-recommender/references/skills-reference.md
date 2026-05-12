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
description: Tạo OpenAPI documentation cho một endpoint. Dùng khi viết tài liệu cho API route.
---

Tạo OpenAPI documentation cho endpoint tại $ARGUMENTS.

Dùng template trong [openapi-template.yaml](openapi-template.yaml) làm cấu trúc.

1. Đọc code endpoint
2. Trích xuất path, method, parameter, schema request/response
3. Điền template với các giá trị thực tế
4. Xuất ra YAML hoàn chỉnh
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
description: Tạo file database migration
disable-model-invocation: true
allowed-tools: Read, Write, Bash
---

Tạo migration cho: $ARGUMENTS

1. Tạo file migration trong `migrations/` với tiền tố timestamp
2. Bao gồm hàm up và down
3. Chạy kiểm tra: `bash ~/.claude/skills/create-migration/scripts/validate-migration.sh`
4. Báo cáo bất kỳ vấn đề nào tìm thấy
```

**scripts/validate-migration.sh:**
```bash
#!/bin/bash
# Kiểm tra cú pháp migration
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
description: Tạo test cho một file theo convention của project
disable-model-invocation: true
---

Tạo test cho: $ARGUMENTS

Tham khảo các ví dụ sau để biết pattern mong đợi:
- Unit test: [examples/unit-test.ts](examples/unit-test.ts)
- Integration test: [examples/integration-test.ts](examples/integration-test.ts)

1. Phân tích file source
2. Xác định các hàm/method cần test
3. Tạo test khớp với convention của project
4. Đặt vào thư mục test phù hợp
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
description: Scaffold React component mới kèm test và story
disable-model-invocation: true
---

Tạo component: $ARGUMENTS

Dùng template trong thư mục [templates/](templates/):
1. Tạo component từ component.tsx.template
2. Tạo test từ component.test.tsx.template
3. Tạo Storybook story từ component.stories.tsx.template

Thay {{ComponentName}} bằng tên PascalCase.
Thay {{component-name}} bằng tên kebab-case.
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
description: Review PR theo checklist của project
disable-model-invocation: true
context: fork
---

## Context PR
- Diff: !`gh pr diff`
- Mô tả: !`gh pr view`

Review theo [checklist.md](checklist.md).

Với mỗi mục, đánh dấu ✅ hoặc ❌ kèm giải thích.
```

**checklist.md:**
```markdown
## Checklist PR

- [ ] Đã thêm test cho tính năng mới
- [ ] Không có lệnh console.log
- [ ] Xử lý lỗi bao gồm message hiển thị cho người dùng
- [ ] Thay đổi API tương thích ngược
- [ ] Database migration có thể rollback
```

---

### Tạo Release Note

Tạo release note từ lịch sử git:

**SKILL.md:**
```yaml
---
name: release-notes
description: Tạo release note từ các commit kể từ tag gần nhất
disable-model-invocation: true
---

## Thay Đổi Gần Đây
- Commit kể từ tag gần nhất: !`git log $(git describe --tags --abbrev=0)..HEAD --oneline`
- Tag gần nhất: !`git describe --tags --abbrev=0`

Tạo release note:
1. Nhóm commit theo loại (feat, fix, docs, v.v.)
2. Viết mô tả thân thiện với người dùng
3. Làm nổi bật breaking change
4. Format dưới dạng markdown
```

---

### Convention Project (Chỉ Claude Gọi)

Kiến thức nền Claude tự động áp dụng:

**SKILL.md:**
```yaml
---
name: project-conventions
description: Quy tắc code style và pattern cho project này. Áp dụng khi viết hoặc review code.
user-invocable: false
---

## Convention Đặt Tên
- React component: PascalCase
- Utility: camelCase
- Hằng số: UPPER_SNAKE_CASE
- File: kebab-case

## Pattern
- Dùng `Result<T, E>` cho các thao tác có thể thất bại, không dùng exception
- Ưu tiên composition hơn inheritance
- Mọi API response dùng shape `{ data, error, meta }`

## Cấm
- Không dùng kiểu `any`
- Không dùng `console.log` trong code production
- Không dùng file I/O đồng bộ
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
description: Cài đặt môi trường phát triển cho contributor mới
disable-model-invocation: true
---

Cài đặt môi trường phát triển:

1. Kiểm tra prerequisites: `bash scripts/check-prerequisites.sh`
2. Cài đặt dependencies: `npm install`
3. Copy template environment: `cp .env.example .env`
4. Cài đặt database: `npm run db:setup`
5. Kiểm tra cài đặt: `npm test`

Báo cáo bất kỳ vấn đề nào gặp phải.
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
