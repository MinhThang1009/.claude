---
name: review-pr
description: "Review pull request toàn diện bằng các agent chuyên biệt"
argument-hint: "[review-aspects]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# Comprehensive PR Review

Chạy review pull request toàn diện bằng nhiều agent chuyên biệt, mỗi agent tập trung vào một khía cạnh khác nhau của chất lượng code.

**Review Aspects (tùy chọn):** "$ARGUMENTS"

## Review Workflow

1. **Xác định phạm vi Review**
   - Kiểm tra git status để xác định các file đã thay đổi
   - Parse arguments để xem user yêu cầu các khía cạnh review cụ thể nào
   - Mặc định: Chạy tất cả các review phù hợp

2. **Các Review Aspect có sẵn:**

   - **comments** - Phân tích độ chính xác và tính maintainability của comment trong code
   - **tests** - Review chất lượng và độ đầy đủ của test coverage
   - **errors** - Kiểm tra error handling có silent failure không
   - **types** - Phân tích thiết kế type và invariant (nếu có type mới được thêm)
   - **code** - Review code tổng quát theo project guideline
   - **simplify** - Đơn giản hóa code để tăng sự rõ ràng và maintainability
   - **all** - Chạy tất cả review phù hợp (mặc định)

3. **Xác định các file đã thay đổi**
   - Chạy `git diff --name-only` để xem file đã chỉnh sửa
   - Kiểm tra PR đã tồn tại chưa: `gh pr view`
   - Xác định loại file và review nào phù hợp

4. **Xác định các Review phù hợp**

   Dựa trên thay đổi:
   - **Luôn phù hợp**: code-reviewer (chất lượng tổng quát)
   - **Nếu file test thay đổi**: pr-test-analyzer
   - **Nếu comment/docs được thêm**: comment-analyzer
   - **Nếu error handling thay đổi**: silent-failure-hunter
   - **Nếu type được thêm/chỉnh sửa**: type-design-analyzer
   - **Sau khi vượt review**: code-simplifier (hoàn thiện và tinh chỉnh)

5. **Khởi chạy Review Agent**

   **Cách tiếp cận tuần tự** (từng cái một):
   - Dễ hiểu và dễ hành động hơn
   - Mỗi report hoàn chỉnh trước khi sang cái tiếp theo
   - Tốt cho review tương tác

   **Cách tiếp cận song song** (user có thể yêu cầu):
   - Khởi chạy tất cả agent đồng thời
   - Nhanh hơn cho review toàn diện
   - Kết quả trả về cùng lúc

6. **Tổng hợp kết quả**

   Sau khi agent hoàn thành, tóm tắt:
   - **Critical Issues** (phải sửa trước khi merge)
   - **Important Issues** (nên sửa)
   - **Suggestions** (nên có)
   - **Positive Observations** (điểm tốt)

7. **Cung cấp Action Plan**

   Tổ chức findings:
   ```markdown
   # PR Review Summary

   ## Critical Issues (X found)
   - [agent-name]: Issue description [file:line]

   ## Important Issues (X found)
   - [agent-name]: Issue description [file:line]

   ## Suggestions (X found)
   - [agent-name]: Suggestion [file:line]

   ## Strengths
   - Điểm làm tốt trong PR này

   ## Recommended Action
   1. Sửa critical issue trước
   2. Xử lý important issue
   3. Cân nhắc suggestion
   4. Chạy lại review sau khi sửa
   ```

## Usage Examples

**Full review (mặc định):**
```
/pr-review-toolkit:review-pr
```

**Các khía cạnh cụ thể:**
```
/pr-review-toolkit:review-pr tests errors
# Chỉ review test coverage và error handling

/pr-review-toolkit:review-pr comments
# Chỉ review code comment

/pr-review-toolkit:review-pr simplify
# Đơn giản hóa code sau khi đã vượt review
```

**Review song song:**
```
/pr-review-toolkit:review-pr all parallel
# Khởi chạy tất cả agent song song
```

## Agent Descriptions

**comment-analyzer**:
- Xác minh độ chính xác của comment so với code
- Xác định comment rot
- Kiểm tra độ đầy đủ của documentation

**pr-test-analyzer**:
- Review behavioral test coverage
- Xác định các gap quan trọng
- Đánh giá chất lượng test

**silent-failure-hunter**:
- Tìm silent failure
- Review các catch block
- Kiểm tra error logging

**type-design-analyzer**:
- Phân tích type encapsulation
- Review cách biểu diễn invariant
- Đánh giá chất lượng thiết kế type

**code-reviewer**:
- Kiểm tra tuân thủ CLAUDE.md
- Phát hiện bug và vấn đề
- Review chất lượng code tổng quát

**code-simplifier**:
- Đơn giản hóa code phức tạp
- Cải thiện sự rõ ràng và dễ đọc
- Áp dụng chuẩn project
- Giữ nguyên functionality

## Tips

- **Chạy sớm**: Trước khi tạo PR, không phải sau
- **Tập trung vào thay đổi**: Agent phân tích git diff theo mặc định
- **Xử lý critical trước**: Sửa vấn đề ưu tiên cao trước khi xử lý ưu tiên thấp hơn
- **Chạy lại sau khi sửa**: Xác minh các vấn đề đã được giải quyết
- **Dùng review cụ thể**: Nhắm vào khía cạnh cụ thể khi bạn biết vấn đề nằm ở đâu

## Workflow Integration

**Trước khi commit:**
```
1. Viết code
2. Chạy: /pr-review-toolkit:review-pr code errors
3. Sửa các critical issue
4. Commit
```

**Trước khi tạo PR:**
```
1. Stage tất cả thay đổi
2. Chạy: /pr-review-toolkit:review-pr all
3. Xử lý tất cả critical và important issue
4. Chạy lại review cụ thể để xác minh
5. Tạo PR
```

**Sau khi nhận phản hồi PR:**
```
1. Thực hiện các thay đổi được yêu cầu
2. Chạy review có mục tiêu dựa trên phản hồi
3. Xác minh các vấn đề đã được giải quyết
4. Push update
```

## Notes

- Agent chạy tự động và trả về báo cáo chi tiết
- Mỗi agent tập trung vào chuyên môn của mình để phân tích sâu
- Kết quả có thể hành động được với tham chiếu file:line cụ thể
- Agent dùng model phù hợp với độ phức tạp của chúng
- Tất cả agent có trong danh sách `/agents`
