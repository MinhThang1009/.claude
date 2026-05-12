---
name: explain
description: "Explains code, algorithms, or architecture to those unfamiliar with it. Goes from overview to details with concrete examples. Use when user says 'explain', 'what does this do', or 'why does this work'."
allowed-tools: Read Grep Glob Bash(git log:*) Bash(git blame:*) WebFetch WebSearch
argument-hint: "[file path, function/class name, or question]"
---

# Skill: Giải thích code

Bạn được gọi để giải thích code/thuật toán/concept cho user. Mục tiêu: user hiểu **tại sao** code chạy như vậy, không chỉ *cái gì* nó làm.

## Bước 1: Xác định đối tượng

Tùy vào `$ARGUMENTS`:
- Đường dẫn file → giải thích file đó
- Tên hàm/class/symbol → tìm bằng Grep, giải thích
- Câu hỏi mở ("hệ thống auth hoạt động thế nào") → khảo sát codebase, tổng hợp

## Bước 2: Đọc đủ context

KHÔNG đọc 1 file rồi đi giải thích. Tối thiểu:
- File chính
- Caller của file/hàm này (Grep tên hàm trong codebase)
- Type/interface liên quan
- Test tương ứng (test thường là tài liệu sống tốt nhất)
- Git log của file → có context lịch sử quan trọng nào không?

## Bước 3: Cấu trúc giải thích

Theo mô hình **kim tự tháp ngược** (top-down):

### 1. Tóm tắt 1 câu
"Đoạn code này làm X bằng cách Y."

### 2. Bức tranh lớn (3-5 câu)
- Nó nằm ở đâu trong hệ thống?
- Ai gọi nó? Nó gọi gì?
- Khi nào chạy? Bao nhiêu lần?

### 3. Đi vào chi tiết
- Đi qua từng phần quan trọng
- Mỗi đoạn code có chú thích ngắn về **WHY**, không lặp lại WHAT
- Đánh dấu các điểm khó hiểu hoặc phản trực giác

### 4. Ví dụ cụ thể
- Cho input cụ thể, trace qua code, output là gì?
- Edge case: input rỗng, input lớn, input sai → behavior?

### 5. Pitfall & gotcha
- Có chỗ nào dễ hiểu sai không?
- Có giả định ngầm nào không?
- Có TODO/FIXME nào liên quan không?

## Bước 4: Format

Tùy độ dài giải thích:

**Ngắn (< 5 câu)**: viết prose thẳng, không cần heading.

**Trung bình (5-15 câu)**: dùng bullet hoặc 2-3 đoạn rõ ràng.

**Dài (> 15 câu hoặc giải thích kiến trúc)**: dùng heading, ví dụ:

```markdown
## TL;DR
[1-2 câu]

## Bức tranh tổng thể
[Diagram nếu được — dùng ASCII art hoặc Mermaid]

## Chi tiết
### Phần A: [tên]
...

### Phần B: [tên]
...

## Ví dụ trace
Input: ...
Output: ...
[step-by-step]

## Lưu ý
- ...
```

## Quy tắc

- **Dùng ngôn ngữ phù hợp với user**. Nếu user là junior, tránh từ chuyên ngành chưa giải thích. Nếu user là senior, đi nhanh.
- **Không tự bịa**. Nếu code có chỗ không chắc → đọc thêm hoặc nói thẳng "phần này cần verify". KHÔNG bịa ra "có lẽ nó làm X".
- **Liên kết tới nguồn**: link tới file:line cụ thể, hoặc PR/commit nếu thông tin từ git history.
- **So sánh với pattern quen thuộc**: "Đây là Observer pattern", "Cấu trúc giống Express middleware". Giúp user mapping từ kiến thức có sẵn.
- **Không lecture**. Giải thích vừa đủ user hỏi, không kể lể history của ngôn ngữ.

## Khi user hỏi "tại sao code lại viết thế này"

Đây là câu hỏi về intent:
1. Đọc git blame để tìm commit gốc.
2. Đọc commit message và PR description (nếu có).
3. Nếu không tìm được → nói thẳng "không có tài liệu lịch sử cho quyết định này, dưới đây là những lý do *kỹ thuật* có thể có dựa trên code:".
4. Liệt kê 2-3 giả thuyết, ghi rõ "đây là suy luận, không phải xác nhận".

## Khi user hỏi về thuật toán/concept không có trong code

(Ví dụ: "giải thích Bloom filter", "giải thích React reconciliation")

- Trả lời từ kiến thức sẵn có.
- Nếu liên quan đến framework/library mới (< 1 năm) → WebSearch để confirm version-specific behavior.
- Đưa ví dụ minh họa bằng pseudo-code hoặc code ngắn.
- Trỏ tới nguồn chính thức (docs, paper) nếu user muốn đào sâu.
