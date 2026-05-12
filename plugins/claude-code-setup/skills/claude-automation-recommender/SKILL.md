---
name: claude-automation-recommender
description: Analyze a codebase and recommend Claude Code automations (hooks, subagents, skills, plugins, MCP servers). Use when user asks for automation recommendations, wants to optimize their Claude Code setup, mentions improving Claude Code workflows, asks how to first set up Claude Code for a project, or wants to know what Claude Code features they should use.
tools: Read, Glob, Grep, Bash
---

# Claude Automation Recommender

Phân tích các pattern trong codebase để đề xuất các automation phù hợp trong Claude Code — bao gồm tất cả các tùy chọn mở rộng.

**Skill này chỉ đọc, không ghi.** Skill phân tích codebase và xuất ra các đề xuất. Skill KHÔNG tạo hoặc sửa đổi file nào. Người dùng tự implement theo đề xuất hoặc nhờ Claude giúp xây dựng riêng.

## Hướng dẫn Output

- **Đề xuất 1-2 loại mỗi category**: Không làm người dùng choáng ngợp — chỉ nêu 1-2 automation có giá trị nhất mỗi loại
- **Nếu user hỏi loại cụ thể**: Tập trung vào loại đó và đưa ra nhiều tùy chọn hơn (3-5 đề xuất)
- **Đi xa hơn danh sách tham chiếu**: Các reference file chứa các pattern phổ biến, nhưng hãy dùng web search để tìm đề xuất cụ thể cho tools, framework, và thư viện của codebase
- **Báo user rằng có thể hỏi thêm**: Kết thúc bằng lưu ý rằng họ có thể yêu cầu thêm đề xuất cho bất kỳ category cụ thể nào

## Tổng quan các loại Automation

| Loại | Phù hợp nhất cho |
|------|----------|
| **Hooks** | Hành động tự động theo tool events (format khi save, lint, block edits) |
| **Subagents** | Reviewer/analyzer chuyên biệt chạy song song |
| **Skills** | Đóng gói expertise, workflows, và các task lặp lại (gọi bởi Claude hoặc user qua `/skill-name`) |
| **Plugins** | Tập hợp các skill có thể cài đặt |
| **MCP Servers** | Tích hợp tool ngoài (database, API, browser, docs) |

## Workflow

### Phase 1: Phân tích Codebase

Thu thập thông tin context về project:

```bash
# Xác định loại project và tools
ls -la package.json pyproject.toml Cargo.toml go.mod pom.xml 2>/dev/null
cat package.json 2>/dev/null | head -50

# Kiểm tra dependencies để đề xuất MCP server
cat package.json 2>/dev/null | grep -E '"(react|vue|angular|next|express|fastapi|django|prisma|supabase|stripe)"'

# Kiểm tra config Claude Code hiện có
ls -la .claude/ CLAUDE.md 2>/dev/null

# Phân tích cấu trúc project
ls -la src/ app/ lib/ tests/ components/ pages/ api/ 2>/dev/null
```

**Các chỉ số quan trọng cần ghi lại:**

| Category | Tìm gì | Thông tin cho |
|----------|------------------|----------------------------|
| Language/Framework | package.json, pyproject.toml, import patterns | Hooks, MCP servers |
| Frontend stack | React, Vue, Angular, Next.js | Playwright MCP, frontend skills |
| Backend stack | Express, FastAPI, Django | API documentation tools |
| Database | Prisma, Supabase, raw SQL | Database MCP servers |
| External APIs | Stripe, OpenAI, AWS SDKs | context7 MCP for docs |
| Testing | Jest, pytest, Playwright configs | Testing hooks, subagents |
| CI/CD | GitHub Actions, CircleCI | GitHub MCP server |
| Issue tracking | Linear, Jira references | Issue tracker MCP |
| Docs patterns | OpenAPI, JSDoc, docstrings | Documentation skills |

### Phase 2: Tạo Đề xuất

Dựa trên phân tích, tạo đề xuất theo tất cả các category:

#### A. Đề xuất MCP Server

Xem [references/mcp-servers.md](references/mcp-servers.md) để biết các pattern chi tiết.

| Tín hiệu trong codebase | MCP Server đề xuất |
|-----------------|------------------------|
| Dùng thư viện phổ biến (React, Express, ...) | **context7** - Tra cứu tài liệu trực tiếp |
| Frontend cần test UI | **Playwright** - Browser automation/testing |
| Dùng Supabase | **Supabase MCP** - Thao tác database trực tiếp |
| Database PostgreSQL/MySQL | **Database MCP** - Query và schema tools |
| GitHub repository | **GitHub MCP** - Issues, PRs, actions |
| Dùng Linear để quản lý issues | **Linear MCP** - Issue management |
| Hạ tầng AWS | **AWS MCP** - Cloud resource management |
| Slack workspace | **Slack MCP** - Team notifications |
| Cần lưu context xuyên session | **Memory MCP** - Cross-session memory |
| Theo dõi lỗi bằng Sentry | **Sentry MCP** - Error investigation |
| Container Docker | **Docker MCP** - Container management |

#### B. Đề xuất Skills

Xem [references/skills-reference.md](references/skills-reference.md) để biết chi tiết.

Tạo skills trong `.claude/skills/<name>/SKILL.md`. Một số cũng có sẵn qua plugins:

| Tín hiệu trong codebase | Skill | Plugin |
|-----------------|-------|--------|
| Đang xây dựng plugins | skill-development | plugin-dev |
| Git commits | commit | commit-commands |
| React/Vue/Angular | frontend-design | frontend-design |
| Automation rules | writing-rules | hookify |
| Feature planning | feature-dev | feature-dev |

**Skills tùy chỉnh cần tạo** (kèm templates, scripts, examples):

| Tín hiệu trong codebase | Skill cần tạo | Cách gọi |
|-----------------|-----------------|------------|
| API routes | **api-doc** (với OpenAPI template) | Cả hai |
| Database project | **create-migration** (với validation script) | Chỉ user |
| Test suite | **gen-test** (với example tests) | Chỉ user |
| Component library | **new-component** (với templates) | Chỉ user |
| PR workflow | **pr-check** (với checklist) | Chỉ user |
| Releases | **release-notes** (với git context) | Chỉ user |
| Code style | **project-conventions** | Chỉ Claude |
| Onboarding | **setup-dev** (với prereq script) | Chỉ user |

#### C. Đề xuất Hooks

Xem [references/hooks-patterns.md](references/hooks-patterns.md) để biết cấu hình.

| Tín hiệu trong codebase | Hook đề xuất |
|-----------------|------------------|
| Cấu hình Prettier | PostToolUse: tự động format khi edit |
| Cấu hình ESLint/Ruff | PostToolUse: tự động lint khi edit |
| Project TypeScript | PostToolUse: type-check khi edit |
| Có thư mục tests | PostToolUse: chạy test liên quan |
| Có file `.env` | PreToolUse: block edit `.env` |
| Có lock files | PreToolUse: block edit lock files |
| Code nhạy cảm với security | PreToolUse: yêu cầu xác nhận |

#### D. Đề xuất Subagents

Xem [references/subagent-templates.md](references/subagent-templates.md) để biết templates.

| Tín hiệu trong codebase | Subagent đề xuất |
|-----------------|---------------------|
| Codebase lớn (>500 files) | **code-reviewer** - Code review song song |
| Code auth/payments | **security-reviewer** - Security audits |
| Project API | **api-documenter** - Tạo OpenAPI |
| Performance critical | **performance-analyzer** - Phát hiện bottleneck |
| Frontend nặng | **ui-reviewer** - Accessibility review |
| Cần thêm tests | **test-writer** - Tạo tests |

#### E. Đề xuất Plugins

Xem [references/plugins-reference.md](references/plugins-reference.md) để biết các plugin có sẵn.

| Tín hiệu trong codebase | Plugin đề xuất |
|-----------------|-------------------|
| Năng suất chung | **anthropic-agent-skills** - Gói skills cốt lõi |
| Workflow với tài liệu | Cài skills docx, xlsx, pdf |
| Phát triển frontend | Plugin **frontend-design** |
| Xây dựng AI tools | **mcp-builder** cho phát triển MCP |

### Phase 3: Xuất Báo cáo Đề xuất

Format đề xuất rõ ràng. **Chỉ bao gồm 1-2 đề xuất mỗi category** — những cái có giá trị nhất cho codebase cụ thể này. Bỏ qua các category không liên quan.

```markdown
## Đề xuất Automation cho Claude Code

Tôi đã phân tích codebase của bạn và xác định các automation hàng đầu cho mỗi category. Dưới đây là 1-2 đề xuất tốt nhất mỗi loại:

### Codebase Profile
- **Loại**: [ngôn ngữ/runtime phát hiện được]
- **Framework**: [framework phát hiện được]
- **Thư viện chính**: [thư viện liên quan phát hiện được]

---

### 🔌 MCP Servers

#### context7
**Tại sao**: [lý do cụ thể dựa trên thư viện phát hiện được]
**Cài đặt**: `claude mcp add context7`

---

### 🎯 Skills

#### [tên skill]
**Tại sao**: [lý do cụ thể]
**Tạo tại**: `.claude/skills/[name]/SKILL.md`
**Cách gọi**: Chỉ user / Cả hai / Chỉ Claude
**Cũng có trong**: plugin [plugin-name] (nếu có)
```yaml
---
name: [skill-name]
description: [mô tả skill làm gì]
disable-model-invocation: true  # cho user-only
---
```

---

### ⚡ Hooks

#### [tên hook]
**Tại sao**: [lý do cụ thể dựa trên config phát hiện được]
**Tạo tại**: `.claude/settings.json`

---

### 🤖 Subagents

#### [tên agent]
**Tại sao**: [lý do cụ thể dựa trên patterns trong codebase]
**Tạo tại**: `.claude/agents/[name].md`

---

**Muốn thêm?** Hỏi thêm đề xuất cho bất kỳ category cụ thể nào (ví dụ: "cho tôi thêm tùy chọn MCP server" hoặc "còn hook nào khác hữu ích không?").

**Muốn được giúp triển khai?** Chỉ cần hỏi và tôi có thể giúp bạn thiết lập bất kỳ đề xuất nào ở trên.
```

## Khung quyết định

### Khi nào nên đề xuất MCP Servers
- Cần tích hợp external service (database, API)
- Tra cứu tài liệu cho thư viện/SDK
- Browser automation hoặc testing
- Tích hợp team tools (GitHub, Linear, Slack)
- Quản lý cloud infrastructure

### Khi nào nên đề xuất Skills

- Tạo tài liệu (docx, xlsx, pptx, pdf — cũng có trong plugins)
- Các prompt hoặc workflow lặp lại thường xuyên
- Task đặc thù của project có đối số
- Áp dụng templates hoặc scripts cho tasks (skills có thể bundle các supporting files)
- Quick actions gọi bằng `/skill-name`
- Workflows nên chạy trong isolation (`context: fork`)

**Kiểm soát cách gọi:**
- `disable-model-invocation: true` — Chỉ user (cho side effects: deploy, commit, gửi)
- `user-invocable: false` — Chỉ Claude (cho background knowledge)
- Mặc định (bỏ qua cả hai) — Cả hai đều có thể gọi

### Khi nào nên đề xuất Hooks
- Hành động post-edit lặp lại (formatting, linting)
- Quy tắc bảo vệ (block edit file nhạy cảm)
- Kiểm tra validation (tests, type checks)

### Khi nào nên đề xuất Subagents
- Cần expertise chuyên biệt (security, performance)
- Workflow review song song
- Background quality checks

### Khi nào nên đề xuất Plugins
- Cần nhiều skills liên quan
- Muốn bundle automation được đóng gói sẵn
- Chuẩn hóa trong toàn team

---

## Mẹo Cấu hình

### Thiết lập MCP Server

**Chia sẻ trong team**: Commit `.mcp.json` vào repo để toàn team dùng chung MCP servers

**Debug**: Dùng flag `--mcp-debug` để xác định vấn đề cấu hình

**Prerequisites nên đề xuất:**
- GitHub CLI (`gh`) - kích hoạt các thao tác GitHub native
- Puppeteer/Playwright CLI - cho browser MCP servers

### Headless Mode (cho CI/Automation)

Đề xuất headless Claude cho automated pipelines:

```bash
# Ví dụ pre-commit hook
claude -p "fix lint errors in src/" --allowedTools Edit,Write

# CI pipeline với structured output
claude -p "<prompt>" --output-format stream-json | your_command
```

### Permissions cho Hooks

Cấu hình allowed tools trong `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["Edit", "Write", "Bash(npm test:*)", "Bash(git commit:*)"]
  }
}
```
