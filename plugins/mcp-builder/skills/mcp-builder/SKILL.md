---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: Complete terms in LICENSE.txt
---

# Hướng dẫn phát triển MCP Server

## Tổng quan

Tạo MCP (Model Context Protocol) server để LLM tương tác với external service qua các tool được thiết kế tốt. Chất lượng của một MCP server được đo bằng việc nó cho phép LLM hoàn thành real-world task tốt đến mức nào.

---

# Quy trình

## High-Level Workflow

Tạo MCP server chất lượng cao gồm bốn phase chính:

### Phase 1: Nghiên cứu sâu và lập plan

#### 1.1 Hiểu thiết kế MCP hiện đại

**API Coverage vs. Workflow Tools:**
Cân bằng giữa comprehensive API endpoint coverage và specialized workflow tool. Workflow tool có thể tiện hơn cho task cụ thể, trong khi comprehensive coverage cho agent flexibility để compose operation. Performance khác nhau theo client — một số client benefit từ code execution kết hợp các basic tool, trong khi client khác work tốt hơn với workflow cấp cao hơn. Khi không chắc, ưu tiên comprehensive API coverage.

**Tool Naming và Discoverability:**
Tên tool rõ ràng, descriptive giúp agent tìm đúng tool nhanh. Dùng prefix nhất quán (vd `github_create_issue`, `github_list_repos`) và action-oriented naming.

**Context Management:**
Agent benefit từ tool description ngắn gọn và khả năng filter/paginate result. Thiết kế tool return data focused, relevant. Một số client support code execution có thể giúp agent filter và process data hiệu quả.

**Actionable Error Messages:**
Error message phải hướng dẫn agent tới solution với suggestion cụ thể và next step.

#### 1.2 Study MCP Protocol Documentation

**Navigate MCP specification:**

Bắt đầu với sitemap để tìm page liên quan: `https://modelcontextprotocol.io/sitemap.xml`

Sau đó fetch page cụ thể với suffix `.md` cho markdown format (vd `https://modelcontextprotocol.io/specification/draft.md`).

Page chính cần review:
- Specification overview và architecture
- Transport mechanism (streamable HTTP, stdio)
- Tool, resource, và prompt definition

#### 1.3 Study Framework Documentation

**Recommended stack:**
- **Language**: TypeScript (SDK support chất lượng cao và compatibility tốt trong nhiều execution environment vd MCPB. Cộng thêm AI model viết TypeScript tốt, benefit từ broad usage, static typing và linting tool tốt)
- **Transport**: Streamable HTTP cho remote server, dùng stateless JSON (đơn giản hơn để scale và maintain, opposite của stateful session và streaming response). stdio cho local server.

**Load framework documentation:**

- **MCP Best Practices**: [View Best Practices](./reference/mcp_best_practices.md) - Core guideline

**Cho TypeScript (recommended):**
- **TypeScript SDK**: Dùng WebFetch để load `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [TypeScript Guide](./reference/node_mcp_server.md) - Pattern và example TypeScript

**Cho Python:**
- **Python SDK**: Dùng WebFetch để load `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [Python Guide](./reference/python_mcp_server.md) - Pattern và example Python

#### 1.4 Plan Implementation

**Hiểu API:**
Review API documentation của service để identify endpoint chính, authentication requirement, và data model. Dùng web search và WebFetch khi cần.

**Tool Selection:**
Ưu tiên comprehensive API coverage. List endpoint sẽ implement, bắt đầu với operation phổ biến nhất.

---

### Phase 2: Implementation

#### 2.1 Set Up Project Structure

Xem language-specific guide để biết project setup:
- [TypeScript Guide](./reference/node_mcp_server.md) - Project structure, package.json, tsconfig.json
- [Python Guide](./reference/python_mcp_server.md) - Module organization, dependency

#### 2.2 Implement Core Infrastructure

Tạo shared utility:
- API client với authentication
- Error handling helper
- Response formatting (JSON/Markdown)
- Pagination support

#### 2.3 Implement Tools

Cho mỗi tool:

**Input Schema:**
- Dùng Zod (TypeScript) hoặc Pydantic (Python)
- Include constraint và description rõ ràng
- Add example trong field description

**Output Schema:**
- Define `outputSchema` khi có thể cho structured data
- Dùng `structuredContent` trong tool response (TypeScript SDK feature)
- Giúp client hiểu và process tool output

**Tool Description:**
- Summary ngắn gọn về functionality
- Mô tả parameter
- Return type schema

**Implementation:**
- Async/await cho I/O operation
- Error handling đúng với message actionable
- Support pagination khi applicable
- Return cả text content và structured data khi dùng SDK hiện đại

**Annotations:**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

---

### Phase 3: Review và Test

#### 3.1 Code Quality

Review:
- Không duplicate code (DRY principle)
- Error handling nhất quán
- Full type coverage
- Tool description rõ ràng

#### 3.2 Build và Test

**TypeScript:**
- Chạy `npm run build` để verify compilation
- Test với MCP Inspector: `npx @modelcontextprotocol/inspector`

**Python:**
- Verify syntax: `python -m py_compile your_server.py`
- Test với MCP Inspector

Xem language-specific guide để biết testing approach chi tiết và quality checklist.

---

### Phase 4: Create Evaluations

Sau khi implement MCP server, tạo evaluation comprehensive để test effectiveness.

**Load [Evaluation Guide](./reference/evaluation.md) để có complete evaluation guideline.**

#### 4.1 Hiểu mục đích Evaluation

Dùng evaluation để test xem LLM có thể dùng MCP server của bạn hiệu quả để trả lời câu hỏi realistic, complex hay không.

#### 4.2 Tạo 10 Evaluation Question

Để tạo evaluation hiệu quả, follow process trong evaluation guide:

1. **Tool Inspection**: List tool có sẵn và hiểu capability của chúng
2. **Content Exploration**: Dùng operation READ-ONLY để explore data có sẵn
3. **Question Generation**: Tạo 10 câu hỏi complex, realistic
4. **Answer Verification**: Tự giải mỗi câu hỏi để verify answer

#### 4.3 Evaluation Requirements

Đảm bảo mỗi câu hỏi:
- **Independent**: Không depend vào câu hỏi khác
- **Read-only**: Chỉ cần operation non-destructive
- **Complex**: Cần multiple tool call và deep exploration
- **Realistic**: Dựa trên real use case mà human care
- **Verifiable**: Single, clear answer có thể verify bằng string comparison
- **Stable**: Answer không đổi theo thời gian

#### 4.4 Output Format

Tạo file XML với structure:

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

---

# Reference Files

## Documentation Library

Load các resource này khi cần trong development:

### Core MCP Documentation (Load First)
- **MCP Protocol**: Bắt đầu với sitemap tại `https://modelcontextprotocol.io/sitemap.xml`, sau đó fetch page cụ thể với suffix `.md`
- [MCP Best Practices](./reference/mcp_best_practices.md) - Universal MCP guideline bao gồm:
  - Convention naming server và tool
  - Guideline response format (JSON vs Markdown)
  - Best practice pagination
  - Transport selection (streamable HTTP vs stdio)
  - Standard security và error handling

### SDK Documentation (Load During Phase 1/2)
- **Python SDK**: Fetch từ `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- **TypeScript SDK**: Fetch từ `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`

### Language-Specific Implementation Guides (Load During Phase 2)
- [Python Implementation Guide](./reference/python_mcp_server.md) - Complete Python/FastMCP guide với:
  - Pattern server initialization
  - Example Pydantic model
  - Tool registration với `@mcp.tool`
  - Working example hoàn chỉnh
  - Quality checklist

- [TypeScript Implementation Guide](./reference/node_mcp_server.md) - Complete TypeScript guide với:
  - Project structure
  - Pattern Zod schema
  - Tool registration với `server.registerTool`
  - Working example hoàn chỉnh
  - Quality checklist

### Evaluation Guide (Load During Phase 4)
- [Evaluation Guide](./reference/evaluation.md) - Complete evaluation creation guide với:
  - Guideline tạo question
  - Strategy verify answer
  - XML format specification
  - Example question và answer
  - Chạy evaluation với script được cung cấp
