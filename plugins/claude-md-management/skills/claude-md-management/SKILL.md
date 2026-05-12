---
name: claude-md-management
description: Audit and improve CLAUDE.md files in repositories. Use when user asks to check, audit, update, improve, or fix CLAUDE.md files. Scans for all CLAUDE.md files, evaluates quality against templates, outputs quality report, then makes targeted updates. Also use when the user mentions "CLAUDE.md maintenance" or "project memory optimization".
allowed-tools: Read Grep Glob Bash Edit
argument-hint: "[audit | revise | path to CLAUDE.md]"
---

# CLAUDE.md Management — Audit & Improve

Hai chế độ: **audit** (đánh giá + cải thiện) và **revise** (capture session learnings).

## Chế độ 1: Audit (mặc định)

Khi `$ARGUMENTS` trống hoặc chứa `audit`:

### Phase 1: Discovery

Tìm tất cả CLAUDE.md files:

```bash
find . -name "CLAUDE.md" -o -name ".claude.md" -o -name ".claude.local.md" 2>/dev/null | head -50
```

| Loại | Vị trí | Mục đích |
|------|--------|----------|
| Project root | `./CLAUDE.md` | Context chính (git, shared) |
| Local override | `./.claude.local.md` | Cá nhân (gitignored) |
| Global | `~/.claude/CLAUDE.md` | Mặc định cross-project |
| Package-specific | `./packages/*/CLAUDE.md` | Module-level trong monorepo |
| Subdirectory | Bất kỳ nested dir | Feature/domain-specific context |

Claude auto-discovers CLAUDE.md files trong parent directories — monorepo setup tự động work.

### Phase 2: Quality Assessment

Đánh giá từng file theo 6 tiêu chí:

| Tiêu chí | Trọng số | Kiểm tra |
|-----------|----------|----------|
| Commands/workflows | Cao | Build/test/deploy commands có không? |
| Architecture clarity | Cao | Claude hiểu codebase structure không? |
| Non-obvious patterns | TB | Gotchas, quirks đã document? |
| Conciseness | TB | Có verbose hoặc info hiển nhiên? |
| Currency | Cao | Phản ánh đúng codebase hiện tại? |
| Actionability | Cao | Instructions có executable, không mơ hồ? |

Thang điểm: **A** (90-100), **B** (70-89), **C** (50-69), **D** (30-49), **F** (0-29).

Scoring per-level (ví dụ Commands/workflows, max 20):
- **20**: đầy đủ build/test/dev/lint/deploy, copy-paste ready
- **15**: có commands chính nhưng thiếu 1-2 (vd chỉ có build, thiếu test)
- **10**: có nhưng mơ hồ hoặc outdated
- **5**: chỉ mention "run tests" mà không có command cụ thể
- **0**: không có

**Red Flags** — flag ngay khi phát hiện:
- Commands mà khi chạy thực tế sẽ fail
- References tới files/dirs đã bị xóa
- Copy-paste từ template mà chưa customize cho project
- TODO items chưa bao giờ complete
- Duplicate info giữa nhiều CLAUDE.md files trong cùng repo

### Phase 3: Quality Report

**LUÔN output report TRƯỚC khi sửa bất kỳ file nào.**

```markdown
## CLAUDE.md Quality Report

### Tóm tắt
- Files tìm thấy: X
- Điểm trung bình: X/100
- Files cần cập nhật: X

### Đánh giá từng file

#### 1. ./CLAUDE.md (Project Root)
**Điểm: XX/100 (Grade: X)**

| Tiêu chí | Điểm | Ghi chú |
|-----------|-------|---------|
| Commands/workflows | X/20 | ... |
| Architecture clarity | X/20 | ... |
| Non-obvious patterns | X/15 | ... |
| Conciseness | X/15 | ... |
| Currency | X/15 | ... |
| Actionability | X/15 | ... |

**Vấn đề:** [liệt kê]
**Đề xuất bổ sung:** [liệt kê]
```

### Phase 4: Targeted Updates

Sau report, hỏi user xác nhận trước khi sửa.

Nguyên tắc:
- **Chỉ bổ sung thông tin hữu ích**: commands discovered, gotchas, package relationships, testing approaches, config quirks.
- **Tránh**: info hiển nhiên từ code, generic best practices, one-off fixes, verbose explanations.
- **Show diff** cho mỗi thay đổi kèm lý do ngắn.

### Phase 5: Apply

Sau user approve → dùng Edit tool. Giữ nguyên structure hiện có.

## Chế độ 2: Revise (capture session learnings)

Khi `$ARGUMENTS` chứa `revise`:

### Bước 1: Reflect

Context nào thiếu mà lẽ ra giúp Claude hiệu quả hơn?
- Bash commands đã dùng/phát hiện
- Code style patterns đã follow
- Testing approaches work
- Environment/config quirks
- Gotchas gặp phải

### Bước 2: Draft

**Ngắn gọn** — 1 dòng/concept. CLAUDE.md là phần của prompt, brevity quan trọng.

Phân biệt:
- `CLAUDE.md` → team-shared (git)
- `.claude.local.md` → cá nhân (gitignored)

### Bước 3: Show + Apply

Hiển thị diff + lý do cho mỗi addition. Chỉ apply sau khi user approve.

## CLAUDE.md tốt gồm những gì

**Nguyên tắc**: ngắn gọn, actionable, project-specific.

**Sections khuyến nghị** (chỉ dùng cái relevant):
- **Commands**: build, test, dev, lint — copy-paste ready
- **Architecture**: directory structure, key modules
- **Key Files**: entry points, config files
- **Code Style**: project conventions (không generic best practices)
- **Environment**: required env vars, setup steps
- **Testing**: commands, patterns, frameworks
- **Gotchas**: quirks, common mistakes, non-obvious behaviors
- **Workflow**: khi nào làm gì (deploy process, PR flow)

## Templates theo project type

Khi tạo CLAUDE.md mới từ đầu, dùng template phù hợp:

### Minimal (project nhỏ, script, tool)
```markdown
# Project Name
[1 câu mô tả]
## Commands
\`\`\`bash
npm run dev    # Development server
npm test       # Run tests
\`\`\`
## Gotchas
- [Non-obvious behavior]
```

### Comprehensive (web app, API service)
```markdown
# Project Name
[1-2 câu mô tả]
## Commands
[build, test, dev, lint, deploy]
## Architecture
[Directory structure, key modules]
## Key Files
[Entry points, config, shared types]
## Code Style
[Project-specific conventions]
## Environment
[Required env vars, setup steps]
## Testing
[Commands, patterns, test DB setup]
## Gotchas
[Quirks, common mistakes]
```

### Monorepo Root
```markdown
# Monorepo Name
## Structure
[packages/apps listing with 1-line descriptions]
## Shared Commands
[Root-level scripts]
## Cross-package Patterns
[Shared types, build order, dependency rules]
## Per-package CLAUDE.md
[packages/api/CLAUDE.md, packages/web/CLAUDE.md — mỗi package có file riêng]
```

### Package/Module (trong monorepo)
```markdown
# Package Name
[Relationship to other packages]
## Commands
[Package-specific commands]
## Key Patterns
[Module-specific conventions]
```

## Verify currency

Khi đánh giá "Currency": chạy (mentally hoặc thực tế) các commands được document — nếu fail thì flag là stale.

## Diff format cho updates

Mỗi thay đổi trình bày:

```markdown
### Update: ./CLAUDE.md

**Lý do:** [1 dòng giải thích tại sao bổ sung này giúp ích]

\`\`\`diff
+ [nội dung bổ sung — giữ ngắn]
\`\`\`
```

## Common Issues to Flag

1. **Stale commands**: build commands không còn work
2. **Missing deps**: tools cần thiết chưa mention
3. **Outdated architecture**: file structure đã đổi
4. **Missing env setup**: env vars hoặc config cần thiết
5. **Broken test commands**: test scripts đã thay đổi
6. **Undocumented gotchas**: non-obvious patterns chưa capture

## Tips cho user

- **Phím `#`**: trong session, nhấn `#` để Claude auto-incorporate learnings vào CLAUDE.md.
- **Giữ ngắn**: dense tốt hơn verbose.
- **Actionable commands**: tất cả commands phải copy-paste ready.
- **`.claude.local.md`**: dùng cho preferences cá nhân (thêm vào `.gitignore`).
- **Global defaults**: đặt user-wide preferences vào `~/.claude/CLAUDE.md`.
