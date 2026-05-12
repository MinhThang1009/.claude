# Agent Triggering: Best Practices

Hướng dẫn đầy đủ về cách viết mô tả trigger để agent được dispatch một cách đáng tin cậy.

## Trigger description nằm ở đâu

Một file agent có hai nơi nói về triggering:

1. **Trường `description:` trong YAML frontmatter.** Được load vào context bất cứ khi nào agent được đăng ký, dùng bởi harness để quyết định khi nào dispatch. Giữ dạng flat prose.
2. **Section "When to invoke" trong body agent.** Chỉ được load khi agent thực sự được gọi. Đây là nơi chứa các kịch bản cụ thể, dưới dạng danh sách bullet prose.

## Format

### Trường `description:`

```
description: Use this agent when [conditions]. Typical triggers include [scenario 1 phrased as a prose noun phrase], [scenario 2], and [scenario 3]. See "When to invoke" in the agent body for worked scenarios.
```

Quy tắc:
- Một dòng flat prose trong YAML scalar.
- Nêu 2–4 kịch bản trigger dưới dạng noun phrase.
- Kết thúc bằng con trỏ tới section "When to invoke" trong body.

### Section "When to invoke" trong body

```markdown
## When to invoke

[Hai đến bốn kịch bản đại diện dưới dạng bullet prose. Mỗi kịch bản mô tả tình huống
theo ngôi thứ ba và agent nên làm gì.]

- **[Tên kịch bản ngắn].** [Tình huống trông như thế nào — điều gì vừa xảy ra hoặc
  người dùng đang yêu cầu gì — và agent nên làm gì để phản hồi.]
- **[Tên kịch bản ngắn].** [Như trên.]
```

## Giải phẫu một kịch bản tốt

### Tên kịch bản (phần in đậm đầu tiên)

**Mục đích:** Một noun phrase ngắn xác định loại tình huống.

**Tên tốt:**
- *User-requested review after a feature lands.*
- *Proactive review of newly-written code.*
- *Pre-PR sanity check.*
- *PR updated with new logic.*

**Tên tệ:**
- *Normal usage.* (không cụ thể)
- *User needs help.* (mơ hồ)

### Body kịch bản (sau phần dẫn)

**Mục đích:** Mô tả điều gì xảy ra và agent nên làm gì — bằng prose, ngôi thứ ba, không có câu trích dẫn.

**Tốt:**
> The user has just implemented a feature (often spanning several files) and asks whether everything looks good. Run a review of the recent diff and report findings.

**Tệ (dạng transcript — không dùng):**
> ```
> user: "Can you check if everything looks good?"
> assistant: "I'll use the reviewer agent..."
> ```

Phiên bản tệ trộn lẫn dạng turn-marker vào file agent. Giữ kịch bản là mô tả tình huống bằng prose.

## Các loại trigger cần bao phủ

Nhắm tới 2–4 kịch bản bao gồm các trục sau:

### Yêu cầu rõ ràng
Người dùng yêu cầu trực tiếp những gì agent làm.
- *User-requested security check.* Người dùng yêu cầu rõ ràng một security review cho code gần đây.

### Trigger chủ động
Assistant gọi agent mà không có yêu cầu rõ ràng, sau công việc liên quan.
- *Proactive review after writing database code.* Assistant vừa viết code truy cập database và nên kiểm tra SQL injection và các rủi ro tầng database khác trước khi khai báo task hoàn thành.

### Yêu cầu ngầm định
Người dùng gợi ý nhu cầu mà không nêu tên agent.
- *Code-clarity complaint.* Người dùng mô tả code hiện tại là khó hiểu hoặc khó theo dõi. Coi như yêu cầu refactor để dễ đọc hơn.

### Pattern sử dụng tool
Agent nên tuân theo một pattern sử dụng tool cụ thể.
- *Post-test-edit verification.* Assistant vừa thực hiện nhiều edit vào file test. Xác minh các test đã edit vẫn đáp ứng tiêu chuẩn chất lượng và coverage trước khi tiếp tục.

## Biến thể cách diễn đạt

Nếu cùng một intent thường được diễn đạt nhiều cách, đề cập điều đó bằng prose:

> **Pre-PR sanity check.** The user signals (in any phrasing — "ready to open a PR", "I think we're done here", "let's ship this") that they're about to open a pull request.

Không viết ba kịch bản gần giống nhau chỉ khác nhau ở cụm từ nguyên văn — gộp chúng thành một kịch bản prose đề cập biến thể.

## Bao nhiêu kịch bản là đủ?

- **Tối thiểu: 2.** Thường là một explicit + một proactive.
- **Khuyến nghị: 3–4.** Explicit, proactive, và một implicit hoặc edge case.
- **Tối đa: 5.** Nhiều hơn thế làm phình body mà không thêm tín hiệu routing.

## Ví dụ cụ thể

### Trigger dạng prose trong `description:`

```yaml
description: Use this agent when you need to review code. Typical triggers include user-requested review after a feature lands, proactive review of freshly-written code, and a pre-PR sanity check. See "When to invoke" in the agent body for worked scenarios.
```

### Kịch bản là mô tả tình huống trong body

```markdown
## When to invoke

- **User-requested review.** The user asks for a review of recent changes (any phrasing). Run a review of the unstaged diff.
```

### Chỉ điều kiện trigger — format output để ở nơi khác

```markdown
- **Review.** The user asks for a review. Run the review and report findings as specified in the Output Format section.
```

## Thư viện template

### Agent review code

```yaml
description: Use this agent when you need to review code for adherence to project guidelines and best practices. Typical triggers include the user asking for a review of a feature they just implemented, proactive review of newly-written code before declaring a task done, and a pre-PR sanity check. See "When to invoke" in the agent body.
```

```markdown
## When to invoke

- **User-requested review after a feature lands.** The user has implemented a feature and asks whether the result looks good. Review the recent diff and report findings.
- **Proactive review of newly-written code.** The assistant has just authored new code in response to a user request. Run a self-review before declaring the task done.
- **Pre-PR sanity check.** The user signals readiness to open a pull request. Review the full diff first.
```

### Agent tạo test

```yaml
description: Use this agent when you need to generate tests for code that lacks them. Typical triggers include the user explicitly asking for tests for a function or module, and the assistant proactively generating tests after writing new code that has no test coverage. See "When to invoke" in the agent body.
```

```markdown
## When to invoke

- **Explicit test request.** The user asks for tests covering a specific function, module, or feature. Generate a comprehensive test suite.
- **Proactive coverage after new code.** The assistant has just written new code with no accompanying tests. Generate tests before declaring the task done.
```

### Agent tài liệu

```yaml
description: Use this agent when you need to write or improve documentation for code, especially APIs. Typical triggers include the user asking for docs on a specific function or endpoint, and proactive documentation generation after the assistant adds new API surface. See "When to invoke" in the agent body.
```

```markdown
## When to invoke

- **Explicit doc request.** The user asks for documentation for a specific surface (function, endpoint, module).
- **Proactive docs for new API surface.** The assistant has just added new API endpoints or public functions without docstrings.
```

### Agent validation

```yaml
description: Use this agent when you need to validate code before commit or merge. Typical triggers include the user signaling readiness to commit, and an explicit validation request. See "When to invoke" in the agent body.
```

```markdown
## When to invoke

- **Pre-commit validation.** The user signals readiness to commit. Run validation first and surface any issues.
- **Explicit validation request.** The user asks for the code to be validated.
```

## Debug các vấn đề triggering

### Agent không trigger

Kiểm tra:
1. Prose trong `description:` có nêu đúng kịch bản trigger không.
2. Các kịch bản trong body có bao phủ cách diễn đạt người dùng thực sự dùng không.
3. Có agent cạnh tranh cụ thể hơn đang thắng quyết định routing không.

Giải pháp: thêm hoặc mở rộng kịch bản trong body, và thắt chặt tóm tắt prose trong `description:`.

### Agent trigger quá thường xuyên

Kiểm tra:
1. Các kịch bản trigger có quá chung chung hoặc chồng chéo với agent khác không.
2. `description:` có nói khi nào KHÔNG dùng agent không.

Giải pháp: thu hẹp kịch bản; thêm dòng "Do not invoke when..." vào `description:` nếu cần.

### Agent trigger sai kịch bản

Kiểm tra:
1. Liệu các kịch bản trong body có khớp với khả năng thực tế của agent không.

Giải pháp: viết lại kịch bản để khớp với những gì agent thực sự làm.

## Tóm tắt best practices

- Giữ `description:` dạng flat prose với tóm tắt ngắn về kịch bản trigger
- Đặt kịch bản chi tiết trong section "When to invoke" trong body, dưới dạng bullet prose
- Bao phủ cả triggering explicit và proactive
- Mô tả tình huống agent nên phản hồi
- Đề cập biến thể cách diễn đạt bằng prose ("any phrasing — 'ready to ship', 'looks done'") thay vì qua nhiều kịch bản gần giống nhau
- Giữ kịch bản trigger tách biệt với format output

## Kết luận

Triggering đáng tin cậy đến từ mô tả prose về các tình huống mà agent nên phản hồi.
