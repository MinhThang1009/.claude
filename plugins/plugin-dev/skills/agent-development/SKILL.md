---
name: agent-development
description: This skill should be used when the user asks to "create an agent", "add an agent", "write a subagent", "agent frontmatter", "when to use description", "agent examples", "agent tools", "agent colors", "autonomous agent", or needs guidance on agent structure, system prompts, triggering conditions, or agent development best practices for Claude Code plugins.
version: 0.1.0
---

# Phát triển Agent cho Claude Code Plugins

## Tổng quan

Agent là các subprocess tự trị xử lý các nhiệm vụ phức tạp, nhiều bước một cách độc lập. Hiểu cấu trúc agent, điều kiện kích hoạt, và thiết kế system prompt giúp tạo ra khả năng tự trị mạnh mẽ.

**Khái niệm chính:**
- Agent dành cho công việc tự trị, command dành cho hành động do người dùng khởi tạo
- Định dạng file Markdown với frontmatter YAML
- Kích hoạt qua trường description kèm ví dụ
- System prompt định nghĩa hành vi của agent
- Tùy chỉnh model và màu sắc

## Cấu trúc File Agent

### Định dạng Đầy đủ

```markdown
---
name: agent-identifier
description: Use this agent when [triggering conditions]. Typical triggers include [scenario 1 in prose], [scenario 2 in prose], and [scenario 3 in prose]. See "When to invoke" in the agent body for worked scenarios.
model: inherit
color: blue
tools: ["Read", "Write", "Grep"]
---

You are [agent role description]...

## When to invoke

[Two to four representative scenarios written as prose, e.g.:]
- **[Scenario name].** [What the situation looks like and what the agent should do.]
- **[Scenario name].** [Same.]

**Your Core Responsibilities:**
1. [Responsibility 1]
2. [Responsibility 2]

**Analysis Process:**
[Step-by-step workflow]

**Output Format:**
[What to return]
```

## Các Trường Frontmatter

### name (bắt buộc)

Định danh agent dùng để đặt tên namespace và gọi.

**Định dạng:** chữ thường, số, dấu gạch ngang
**Độ dài:** 3-50 ký tự
**Pattern:** Phải bắt đầu và kết thúc bằng ký tự chữ số

**Ví dụ tốt:**
- `code-reviewer`
- `test-generator`
- `api-docs-writer`
- `security-analyzer`

**Ví dụ xấu:**
- `helper` (quá chung chung)
- `-agent-` (bắt đầu/kết thúc bằng dấu gạch ngang)
- `my_agent` (dấu gạch dưới không được phép)
- `ag` (quá ngắn, < 3 ký tự)

### description (bắt buộc)

Định nghĩa khi nào Claude nên kích hoạt agent này. **Đây là trường quan trọng nhất** — được load vào context mỗi khi agent được đăng ký, để harness quyết định khi nào dispatch.

**Phải bao gồm:**
1. Điều kiện kích hoạt ("Use this agent when...")
2. Tóm tắt prose ngắn về các trigger scenario điển hình
3. Con trỏ đến section "When to invoke" trong body agent cho các worked scenario chi tiết

**Định dạng:**
```
Use this agent when [conditions]. Typical triggers include [scenario 1 in prose], [scenario 2 in prose], and [scenario 3 in prose]. See "When to invoke" in the agent body for worked scenarios.
```

**Thực hành tốt nhất:**
- Nêu tên 2-4 trigger scenario trong prose summary
- Bao gồm cả kích hoạt chủ động (assistant tự gọi) và phản ứng (user yêu cầu)
- Bao gồm các cách diễn đạt khác nhau cho cùng ý định
- Nêu rõ khi nào KHÔNG dùng agent
- Đặt các worked scenario chi tiết trong body dưới section "When to invoke" dưới dạng danh sách prose bullet

### model (bắt buộc)

Model nào agent nên sử dụng.

**Tùy chọn:**
- `inherit` - Dùng cùng model với parent (khuyến nghị)
- `sonnet` - Claude Sonnet (cân bằng)
- `opus` - Claude Opus (mạnh nhất, tốn kém)
- `haiku` - Claude Haiku (nhanh, rẻ)

**Khuyến nghị:** Dùng `inherit` trừ khi agent cần khả năng model cụ thể.

### color (bắt buộc)

Định danh trực quan cho agent trong UI.

**Tùy chọn:** `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`

**Hướng dẫn:**
- Chọn màu khác biệt cho các agent khác nhau trong cùng plugin
- Dùng màu nhất quán cho các loại agent tương tự
- Blue/cyan: Phân tích, review
- Green: Nhiệm vụ định hướng thành công
- Yellow: Thận trọng, xác thực
- Red: Quan trọng, bảo mật
- Magenta: Sáng tạo, tạo sinh

### tools (tùy chọn)

Giới hạn agent chỉ dùng các tool cụ thể.

**Định dạng:** Mảng tên tool

```yaml
tools: ["Read", "Write", "Grep", "Bash"]
```

**Mặc định:** Nếu bỏ qua, agent có quyền truy cập tất cả tool

**Thực hành tốt nhất:** Giới hạn tool ở mức tối thiểu cần thiết (nguyên tắc đặc quyền tối thiểu)

**Bộ tool phổ biến:**
- Phân tích chỉ đọc: `["Read", "Grep", "Glob"]`
- Tạo code: `["Read", "Write", "Grep"]`
- Kiểm tra: `["Read", "Bash", "Grep"]`
- Toàn quyền: Bỏ qua trường hoặc dùng `["*"]`

## Thiết kế System Prompt

Phần markdown body trở thành system prompt của agent. Viết ở ngôi thứ hai, xưng hô trực tiếp với agent.

### Cấu trúc

**Template chuẩn:**
```markdown
You are [role] specializing in [domain].

**Your Core Responsibilities:**
1. [Primary responsibility]
2. [Secondary responsibility]
3. [Additional responsibilities...]

**Analysis Process:**
1. [Step one]
2. [Step two]
3. [Step three]
[...]

**Quality Standards:**
- [Standard 1]
- [Standard 2]

**Output Format:**
Provide results in this format:
- [What to include]
- [How to structure]

**Edge Cases:**
Handle these situations:
- [Edge case 1]: [How to handle]
- [Edge case 2]: [How to handle]
```

### Thực hành Tốt nhất

✅ **NÊN:**
- Viết ở ngôi thứ hai ("You are...", "You will...")
- Nêu rõ trách nhiệm
- Cung cấp quy trình từng bước
- Định nghĩa định dạng output
- Bao gồm tiêu chuẩn chất lượng
- Xử lý các edge case
- Giữ dưới 10.000 ký tự

❌ **KHÔNG NÊN:**
- Viết ở ngôi thứ nhất ("I am...", "I will...")
- Mơ hồ hoặc chung chung
- Bỏ qua các bước quy trình
- Để định dạng output không xác định
- Bỏ qua hướng dẫn chất lượng
- Bỏ qua các trường hợp lỗi

## Tạo Agent

### Phương pháp 1: Tạo có Hỗ trợ AI

Dùng pattern prompt này (trích xuất từ Claude Code):

```
Create an agent configuration based on this request: "[YOUR DESCRIPTION]"

Requirements:
1. Extract core intent and responsibilities
2. Design expert persona for the domain
3. Create comprehensive system prompt with:
   - Clear behavioral boundaries
   - Specific methodologies
   - Edge case handling
   - Output format
   - A "When to invoke" section listing 2-4 trigger scenarios as prose bullets
4. Create identifier (lowercase, hyphens, 3-50 chars)
5. Write description with triggering conditions and a short prose summary of trigger scenarios

Return JSON with:
{
  "identifier": "agent-name",
  "whenToUse": "Use this agent when... Typical triggers include [...]. See \"When to invoke\" in the agent body.",
  "systemPrompt": "You are..."
}
```

Sau đó chuyển sang định dạng file agent với frontmatter.

Xem `examples/agent-creation-prompt.md` để biết template đầy đủ.

### Phương pháp 2: Tạo Thủ công

1. Chọn định danh agent (3-50 ký tự, chữ thường, dấu gạch ngang)
2. Viết description kèm ví dụ
3. Chọn model (thường là `inherit`)
4. Chọn màu để nhận dạng trực quan
5. Định nghĩa tool (nếu giới hạn quyền truy cập)
6. Viết system prompt theo cấu trúc trên
7. Lưu thành `agents/agent-name.md`

## Quy tắc Xác thực

### Xác thực Định danh

```
✅ Hợp lệ: code-reviewer, test-gen, api-analyzer-v2
❌ Không hợp lệ: ag (quá ngắn), -start (bắt đầu bằng dấu gạch ngang), my_agent (dấu gạch dưới)
```

**Quy tắc:**
- 3-50 ký tự
- Chỉ chữ thường, số, dấu gạch ngang
- Phải bắt đầu và kết thúc bằng ký tự chữ số
- Không có dấu gạch dưới, khoảng trắng, hoặc ký tự đặc biệt

### Xác thực Description

**Độ dài:** 10-5.000 ký tự
**Phải bao gồm:** Điều kiện kích hoạt và ví dụ
**Tốt nhất:** 200-1.000 ký tự với 2-4 ví dụ

### Xác thực System Prompt

**Độ dài:** 20-10.000 ký tự
**Tốt nhất:** 500-3.000 ký tự
**Cấu trúc:** Trách nhiệm rõ ràng, quy trình, định dạng output

## Tổ chức Agent

### Thư mục Agent của Plugin

```
plugin-name/
└── agents/
    ├── analyzer.md
    ├── reviewer.md
    └── generator.md
```

Tất cả file `.md` trong `agents/` được tự động phát hiện.

### Đặt tên Namespace

Agent được đặt tên namespace tự động:
- Một plugin: `agent-name`
- Với thư mục con: `plugin:subdir:agent-name`

## Kiểm tra Agent

### Kiểm tra Kích hoạt

Tạo kịch bản kiểm tra để xác minh agent kích hoạt đúng:

1. Viết agent với ví dụ kích hoạt cụ thể
2. Dùng cách diễn đạt tương tự ví dụ trong kiểm tra
3. Kiểm tra Claude tải agent
4. Xác minh agent cung cấp chức năng mong đợi

### Kiểm tra System Prompt

Đảm bảo system prompt hoàn chỉnh:

1. Giao cho agent nhiệm vụ điển hình
2. Kiểm tra nó tuân theo các bước quy trình
3. Xác minh định dạng output đúng
4. Kiểm tra các edge case được đề cập trong prompt
5. Xác nhận tiêu chuẩn chất lượng được đáp ứng

## Tham chiếu Nhanh

### Agent Tối giản

```markdown
---
name: simple-agent
description: Use this agent when [condition]. Typical triggers include [trigger 1] and [trigger 2]. See "When to invoke" in the agent body.
model: inherit
color: blue
---

You are an agent that [does X].

## When to invoke

- **[Scenario A].** [Description.]
- **[Scenario B].** [Description.]

Process:
1. [Step 1]
2. [Step 2]

Output: [What to provide]
```

### Tóm tắt Các Trường Frontmatter

| Trường | Bắt buộc | Định dạng | Ví dụ |
|--------|----------|-----------|-------|
| name | Có | lowercase-hyphens | code-reviewer |
| description | Có | Prose triggers | Use when... Typical triggers include... |
| model | Có | inherit/sonnet/opus/haiku | inherit |
| color | Có | Tên màu | blue |
| tools | Không | Mảng tên tool | ["Read", "Grep"] |

### Thực hành Tốt nhất

**NÊN:**
- ✅ Nêu tên 2-4 trigger scenario trong description (dạng prose)
- ✅ Đặt worked scenario chi tiết trong section "When to invoke" ở body, dạng prose bullet
- ✅ Viết điều kiện kích hoạt cụ thể
- ✅ Dùng `inherit` cho model trừ khi có nhu cầu cụ thể
- ✅ Chọn tool phù hợp (đặc quyền tối thiểu)
- ✅ Viết system prompt rõ ràng, có cấu trúc
- ✅ Kiểm tra kích hoạt agent kỹ lưỡng

**KHÔNG NÊN:**
- ❌ Dùng description chung chung không có trigger scenario
- ❌ Bỏ qua điều kiện kích hoạt
- ❌ Cho tất cả agent cùng màu
- ❌ Cấp quyền truy cập tool không cần thiết
- ❌ Viết system prompt mơ hồ
- ❌ Bỏ qua kiểm tra

## Tài nguyên Bổ sung

### File Tham chiếu

Để biết hướng dẫn chi tiết, tham khảo:

- **`references/system-prompt-design.md`** - Pattern system prompt đầy đủ
- **`references/triggering-examples.md`** - Định dạng ví dụ và thực hành tốt nhất
- **`references/agent-creation-system-prompt.md`** - Prompt chính xác từ Claude Code

### File Ví dụ

Ví dụ hoạt động trong `examples/`:

- **`agent-creation-prompt.md`** - Template tạo agent có hỗ trợ AI
- **`complete-agent-examples.md`** - Ví dụ agent đầy đủ cho các trường hợp dùng khác nhau

### Script Tiện ích

Công cụ phát triển trong `scripts/`:

- **`validate-agent.sh`** - Xác thực cấu trúc file agent
- **`test-agent-trigger.sh`** - Kiểm tra xem agent có kích hoạt đúng không

## Quy trình Triển khai

Để tạo agent cho một plugin:

1. Xác định mục đích agent và điều kiện kích hoạt
2. Chọn phương pháp tạo (có hỗ trợ AI hoặc thủ công)
3. Tạo file `agents/agent-name.md`
4. Viết frontmatter với tất cả trường bắt buộc
5. Viết system prompt theo thực hành tốt nhất
6. Nêu tên 2-4 trigger scenario trong description (prose) và chi tiết hóa chúng trong section "When to invoke" ở body
7. Xác thực với `scripts/validate-agent.sh`
8. Kiểm tra kích hoạt với các kịch bản thực tế
9. Ghi lại agent trong README của plugin

Tập trung vào điều kiện kích hoạt rõ ràng và system prompt toàn diện để vận hành tự trị.
