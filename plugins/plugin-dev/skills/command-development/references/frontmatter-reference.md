# Tài Liệu Tham Chiếu Frontmatter của Command

Tài liệu tham chiếu đầy đủ về các trường YAML frontmatter trong slash command.

## Tổng Quan về Frontmatter

YAML frontmatter là metadata tùy chọn ở đầu file command:

```markdown
---
description: Brief description
allowed-tools: Read, Write
model: sonnet
argument-hint: [arg1] [arg2]
---

Nội dung prompt command ở đây...
```

Tất cả trường đều tùy chọn. Command hoạt động tốt ngay cả khi không có frontmatter.

## Các Trường Cụ Thể

### description

**Kiểu:** String
**Bắt buộc:** Không
**Mặc định:** Dòng đầu tiên của prompt command
**Độ dài tối đa:** ~60 ký tự được khuyến nghị để hiển thị trong `/help`

**Mục đích:** Mô tả command làm gì, hiển thị trong output của `/help`

**Ví dụ:**
```yaml
description: Review code for security issues
```
```yaml
description: Deploy to staging environment
```
```yaml
description: Generate API documentation
```

**Nguyên tắc tốt nhất:**
- Giữ dưới 60 ký tự để hiển thị gọn
- Bắt đầu bằng động từ (Review, Deploy, Generate)
- Cụ thể về việc command làm gì
- Tránh dùng từ thừa "command" hay "slash command"

**Đúng:**
- ✅ "Review PR for code quality and security"
- ✅ "Deploy application to specified environment"
- ✅ "Generate comprehensive API documentation"

**Sai:**
- ❌ "This command reviews PRs" (thừa "This command")
- ❌ "Review" (quá mơ hồ)
- ❌ "A command that reviews pull requests for code quality, security issues, and best practices" (quá dài)

### allowed-tools

**Kiểu:** String hoặc Array of strings
**Bắt buộc:** Không
**Mặc định:** Kế thừa từ quyền của conversation

**Mục đích:** Giới hạn hoặc chỉ định tool nào command có thể sử dụng

**Các định dạng:**

**Một tool:**
```yaml
allowed-tools: Read
```

**Nhiều tool (phân cách bằng dấu phẩy):**
```yaml
allowed-tools: Read, Write, Edit
```

**Nhiều tool (array):**
```yaml
allowed-tools:
  - Read
  - Write
  - Bash(git:*)
```

**Các Pattern Tool:**

**Tool cụ thể:**
```yaml
allowed-tools: Read, Grep, Edit
```

**Bash với bộ lọc lệnh:**
```yaml
allowed-tools: Bash(git:*)           # Chỉ lệnh git
allowed-tools: Bash(npm:*)           # Chỉ lệnh npm
allowed-tools: Bash(docker:*)        # Chỉ lệnh docker
```

**Tất cả tool (không khuyến nghị):**
```yaml
allowed-tools: "*"
```

**Khi nào dùng:**

1. **Bảo mật:** Giới hạn command chỉ thực hiện thao tác an toàn
   ```yaml
   allowed-tools: Read, Grep  # Command chỉ đọc
   ```

2. **Rõ ràng:** Ghi lại các tool cần thiết
   ```yaml
   allowed-tools: Bash(git:*), Read
   ```

3. **Thực thi Bash:** Cho phép output lệnh bash
   ```yaml
   allowed-tools: Bash(git status:*), Bash(git diff:*)
   ```

**Nguyên tắc tốt nhất:**
- Giới hạn càng chặt càng tốt
- Dùng bộ lọc lệnh cho Bash (ví dụ: `git:*` thay vì `*`)
- Chỉ chỉ định khi khác với quyền của conversation
- Ghi lại lý do cần tool cụ thể

### model

**Kiểu:** String
**Bắt buộc:** Không
**Mặc định:** Kế thừa từ conversation
**Giá trị:** `sonnet`, `opus`, `haiku`

**Mục đích:** Chỉ định model Claude nào thực thi command

**Ví dụ:**
```yaml
model: haiku    # Nhanh, hiệu quả cho tác vụ đơn giản
```
```yaml
model: sonnet   # Hiệu năng cân bằng (mặc định)
```
```yaml
model: opus     # Khả năng tối đa cho tác vụ phức tạp
```

**Khi nào dùng:**

**Dùng `haiku` khi:**
- Command đơn giản, có công thức
- Cần thực thi nhanh
- Tác vụ ít phức tạp
- Gọi thường xuyên

```yaml
---
description: Format code file
model: haiku
---
```

**Dùng `sonnet` khi:**
- Command tiêu chuẩn (mặc định)
- Cân bằng tốc độ/chất lượng
- Hầu hết các trường hợp sử dụng

```yaml
---
description: Review code changes
model: sonnet
---
```

**Dùng `opus` khi:**
- Phân tích phức tạp
- Quyết định kiến trúc
- Hiểu code sâu
- Tác vụ quan trọng

```yaml
---
description: Analyze system architecture
model: opus
---
```

**Nguyên tắc tốt nhất:**
- Bỏ qua nếu không có nhu cầu cụ thể
- Dùng `haiku` để tăng tốc khi có thể
- Dành `opus` cho tác vụ thực sự phức tạp
- Thử nghiệm với các model khác nhau để tìm sự cân bằng phù hợp

### argument-hint

**Kiểu:** String
**Bắt buộc:** Không
**Mặc định:** Không có

**Mục đích:** Ghi lại argument mong đợi cho người dùng và autocomplete

**Định dạng:**
```yaml
argument-hint: [arg1] [arg2] [optional-arg]
```

**Ví dụ:**

**Một argument:**
```yaml
argument-hint: [pr-number]
```

**Nhiều argument bắt buộc:**
```yaml
argument-hint: [environment] [version]
```

**Argument tùy chọn:**
```yaml
argument-hint: [file-path] [options]
```

**Tên mô tả:**
```yaml
argument-hint: [source-branch] [target-branch] [commit-message]
```

**Nguyên tắc tốt nhất:**
- Dùng dấu ngoặc vuông `[]` cho mỗi argument
- Dùng tên mô tả (không phải `arg1`, `arg2`)
- Chỉ rõ tùy chọn vs bắt buộc trong phần mô tả
- Thứ tự khớp với argument vị trí trong command
- Ngắn gọn nhưng rõ ràng

**Ví dụ theo pattern:**

**Command đơn giản:**
```yaml
---
description: Fix issue by number
argument-hint: [issue-number]
---

Fix issue #$1...
```

**Nhiều argument:**
```yaml
---
description: Deploy to environment
argument-hint: [app-name] [environment] [version]
---

Deploy $1 lên $2 dùng phiên bản $3...
```

**Với tùy chọn:**
```yaml
---
description: Run tests with options
argument-hint: [test-pattern] [options]
---

Chạy test khớp $1 với tùy chọn: $2
```

### disable-model-invocation

**Kiểu:** Boolean
**Bắt buộc:** Không
**Mặc định:** false

**Mục đích:** Ngăn tool SlashCommand gọi command theo chương trình

**Ví dụ:**
```yaml
disable-model-invocation: true
```

**Khi nào dùng:**

1. **Command chỉ thủ công:** Command yêu cầu phán đoán của người dùng
   ```yaml
   ---
   description: Approve deployment to production
   disable-model-invocation: true
   ---
   ```

2. **Thao tác destructive:** Command có hiệu quả không thể hoàn tác
   ```yaml
   ---
   description: Delete all test data
   disable-model-invocation: true
   ---
   ```

3. **Workflow tương tác:** Command cần input từ người dùng
   ```yaml
   ---
   description: Walk through setup wizard
   disable-model-invocation: true
   ---
   ```

**Hành vi mặc định (false):**
- Command có sẵn cho tool SlashCommand
- Claude có thể gọi theo chương trình
- Vẫn có thể gọi thủ công

**Khi true:**
- Command chỉ có thể gọi bởi người dùng gõ `/command`
- Không có sẵn cho tool SlashCommand
- An toàn hơn cho thao tác nhạy cảm

**Nguyên tắc tốt nhất:**
- Dùng tiết kiệm (hạn chế quyền tự chủ của Claude)
- Ghi lại lý do trong comment command
- Cân nhắc xem command có nên tồn tại không nếu luôn là thủ công

## Ví Dụ Hoàn Chỉnh

### Command Tối Giản

Không cần frontmatter:

```markdown
Review đoạn code này để tìm các vấn đề phổ biến và đề xuất cải thiện.
```

### Command Đơn Giản

Chỉ description:

```markdown
---
description: Review code for issues
---

Review đoạn code này để tìm các vấn đề phổ biến và đề xuất cải thiện.
```

### Command Tiêu Chuẩn

Description và tool:

```markdown
---
description: Review Git changes
allowed-tools: Bash(git:*), Read
---

Các thay đổi hiện tại: !`git diff --name-only`

Review từng file đã thay đổi về:
- Chất lượng code
- Bug tiềm ẩn
- Các nguyên tắc tốt nhất
```

### Command Phức Tạp

Tất cả trường phổ biến:

```markdown
---
description: Deploy application to environment
argument-hint: [app-name] [environment] [version]
allowed-tools: Bash(kubectl:*), Bash(helm:*), Read
model: sonnet
---

Deploy $1 lên môi trường $2 dùng phiên bản $3

Kiểm tra trước khi deploy:
- Xác minh cấu hình $2
- Kiểm tra trạng thái cluster: !`kubectl cluster-info`
- Xác nhận phiên bản $3 tồn tại

Tiến hành deployment theo runbook.
```

### Command Chỉ Thủ Công

Giới hạn cách gọi:

```markdown
---
description: Approve production deployment
argument-hint: [deployment-id]
disable-model-invocation: true
allowed-tools: Bash(gh:*)
---

<!--
YÊU CẦU APPROVAL THỦ CÔNG
Command này yêu cầu phán đoán của con người và không thể tự động hóa.
-->

Review deployment $1 để approve lên production:

Chi tiết deployment: !`gh api /deployments/$1`

Xác minh:
- Tất cả test đã pass
- Quét bảo mật sạch
- Có approval của stakeholder
- Kế hoạch rollback đã sẵn sàng

Gõ "APPROVED" để xác nhận deployment.
```

## Validation

### Lỗi Thường Gặp

**Cú pháp YAML không hợp lệ:**
```yaml
---
description: Missing quote
allowed-tools: Read, Write
model: sonnet
---  # ❌ Thiếu dấu ngoặc đóng ở trên
```

**Sửa:** Validate cú pháp YAML

**Chỉ định tool không đúng:**
```yaml
allowed-tools: Bash  # ❌ Thiếu bộ lọc lệnh
```

**Sửa:** Dùng định dạng `Bash(git:*)`

**Tên model không hợp lệ:**
```yaml
model: gpt4  # ❌ Không phải model Claude hợp lệ
```

**Sửa:** Dùng `sonnet`, `opus`, hoặc `haiku`

### Checklist Validation

Trước khi commit command:
- [ ] Cú pháp YAML hợp lệ (không có lỗi)
- [ ] Description dưới 60 ký tự
- [ ] allowed-tools dùng đúng định dạng
- [ ] model là giá trị hợp lệ nếu được chỉ định
- [ ] argument-hint khớp với argument vị trí
- [ ] disable-model-invocation được dùng đúng chỗ

## Tóm Tắt Nguyên Tắc Tốt Nhất

1. **Bắt đầu tối giản:** Chỉ thêm frontmatter khi cần thiết
2. **Ghi lại argument:** Luôn dùng argument-hint khi có argument
3. **Giới hạn tool:** Dùng allowed-tools ít quyền nhất mà vẫn hoạt động
4. **Chọn model phù hợp:** Dùng haiku để tăng tốc, opus cho phức tạp
5. **Dùng chỉ thủ công tiết kiệm:** Chỉ dùng disable-model-invocation khi cần thiết
6. **Description rõ ràng:** Giúp command dễ khám phá trong `/help`
7. **Test kỹ lưỡng:** Xác nhận frontmatter hoạt động đúng như mong đợi
