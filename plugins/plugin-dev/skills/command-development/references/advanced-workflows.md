# Các Pattern Workflow Nâng Cao

Chuỗi lệnh nhiều bước và các pattern kết hợp dành cho workflow phức tạp.

## Tổng quan

Workflow nâng cao kết hợp nhiều command, điều phối trạng thái qua các lần gọi và tạo ra chuỗi tự động hóa tinh vi. Những pattern này cho phép xây dựng chức năng phức tạp từ các khối lệnh đơn giản.

## Các Pattern Command Nhiều Bước

### Command Workflow Tuần Tự

Command hướng dẫn người dùng qua quy trình nhiều bước:

```markdown
---
description: Complete PR review workflow
argument-hint: [pr-number]
allowed-tools: Bash(gh:*), Read, Grep
---

# PR Review Workflow for #$1

## Bước 1: Lấy thông tin PR
!`gh pr view $1 --json title,body,author,files`

## Bước 2: Review file
Files đã thay đổi: !`gh pr diff $1 --name-only`

Với mỗi file:
- Kiểm tra chất lượng code
- Xác nhận đã có test
- Review tài liệu

## Bước 3: Chạy kiểm tra
Trạng thái test: !`gh pr checks $1`

Xác nhận:
- Tất cả test đều pass
- Không có merge conflict
- CI/CD thành công

## Bước 4: Đưa ra nhận xét

Tóm tắt:
- Vấn đề tìm thấy (critical/minor)
- Đề xuất cải thiện
- Khuyến nghị approve

Bạn muốn:
1. Approve PR
2. Request changes
3. Chỉ để lại comments

Trả lời lựa chọn của bạn và tôi sẽ giúp hoàn tất thao tác.
```

**Tính năng chính:**
- Đánh số bước để rõ ràng
- Thực thi Bash để lấy context
- Điểm quyết định để nhận input từ người dùng
- Gợi ý hành động tiếp theo

### Workflow Lưu Trạng Thái

Command duy trì trạng thái giữa các lần gọi:

```markdown
---
description: Initialize deployment workflow
allowed-tools: Write, Bash(git:*)
---

# Initialize Deployment

Đang tạo file theo dõi deployment...

Branch hiện tại: !`git branch --show-current`
Commit mới nhất: !`git log -1 --format=%H`

Trạng thái deployment đã lưu vào `.claude/deployment-state.local.md`:

\`\`\`markdown
---
initialized: true
branch: $(git branch --show-current)
commit: $(git log -1 --format=%H)
timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
status: initialized
---

# Deployment Tracking

Branch: $(git branch --show-current)
Bắt đầu: $(date)

Các bước tiếp theo:
1. Chạy test: /deploy-test
2. Build: /deploy-build
3. Deploy: /deploy-execute
\`\`\`

Trạng thái đã lưu. Chạy `/deploy-test` để tiếp tục.
```

**Command tiếp theo** (`/deploy-test`):
```markdown
---
description: Run deployment tests
allowed-tools: Read, Bash(npm:*)
---

Đang đọc trạng thái deployment từ `.claude/deployment-state.local.md`...

Chạy test: !`npm test`

Cập nhật trạng thái thành 'tested'...

Test hoàn tất. Chạy `/deploy-build` để tiếp tục.
```

**Lợi ích của pattern:**
- Trạng thái bền vững qua các command
- Tiến trình workflow rõ ràng
- Các checkpoint an toàn
- Khả năng tiếp tục từ giữa chừng

### Phân Nhánh Workflow Có Điều Kiện

Command thích ứng dựa trên điều kiện:

```markdown
---
description: Smart deployment workflow
argument-hint: [environment]
allowed-tools: Bash(git:*), Bash(npm:*), Read
---

# Deploy to $1

## Kiểm tra trước khi bay

Branch: !`git branch --show-current`
Trạng thái: !`git status --short`

**Kiểm tra điều kiện:**

1. Trạng thái branch:
   - Nếu là main/master: Yêu cầu approval
   - Nếu là feature branch: Cảnh báo về target
   - Nếu là hotfix: Quy trình nhanh

2. Test:
   !`npm test`
   - Nếu test thất bại: DỪNG — sửa test trước
   - Nếu test pass: Tiếp tục

3. Môi trường:
   - Nếu $1 = 'production': Xác nhận thêm
   - Nếu $1 = 'staging': Quy trình tiêu chuẩn
   - Nếu $1 = 'dev': Kiểm tra tối thiểu

**Quyết định workflow:**
Dựa trên các điều kiện trên, tiếp tục với: [workflow đã xác định]

[Các bước có điều kiện dựa trên môi trường và trạng thái]

Sẵn sàng deploy? (yes/no)
```

## Các Pattern Kết Hợp Command

### Chuỗi Command

Command được thiết kế để hoạt động cùng nhau:

```markdown
---
description: Prepare for code review
---

# Prepare Code Review

Đang chạy chuỗi chuẩn bị:

1. Format code: /format-code
2. Chạy linter: /lint-code
3. Chạy test: /test-all
4. Tạo coverage: /coverage-report
5. Tạo review summary: /review-summary

Đây là meta-command. Sau khi hoàn thành từng bước trên,
tôi sẽ tổng hợp kết quả và chuẩn bị tài liệu review toàn diện.

Đang bắt đầu chuỗi...
```

**Các command riêng lẻ** đơn giản:
- `/format-code` — Chỉ format
- `/lint-code` — Chỉ lint
- `/test-all` — Chỉ test

**Composition command** điều phối chúng.

### Pattern Pipeline

Command xử lý output từ các command trước:

```markdown
---
description: Analyze test failures
---

# Analyze Test Failures

## Bước 1: Lấy kết quả test
(Chạy /test-all trước nếu chưa làm)

Đang đọc output test...

## Bước 2: Phân loại lỗi
- Flaky test (lỗi ngẫu nhiên)
- Lỗi nhất quán
- Lỗi mới so với lỗi cũ

## Bước 3: Ưu tiên
Xếp hạng theo:
- Impact (critical path vs edge case)
- Tần suất (luôn fail vs đôi khi fail)
- Công sức (sửa nhanh vs việc lớn)

## Bước 4: Tạo kế hoạch sửa
Với mỗi lỗi:
- Giả thuyết về nguyên nhân gốc rễ
- Hướng tiếp cận đề xuất
- Ước tính công sức

Bạn muốn tôi:
1. Sửa lỗi ưu tiên cao nhất
2. Tạo kế hoạch sửa chi tiết cho tất cả
3. Tạo GitHub issue cho từng lỗi
```

### Pattern Thực Thi Song Song

Command điều phối nhiều thao tác đồng thời:

```markdown
---
description: Run comprehensive validation
allowed-tools: Bash(*), Read
---

# Comprehensive Validation

Đang chạy validation song song...

Đang bắt đầu:
- Kiểm tra chất lượng code
- Quét bảo mật
- Kiểm tra dependency
- Profiling hiệu năng

Sẽ mất 2–3 phút. Tôi sẽ theo dõi tất cả tiến trình
và báo cáo khi hoàn tất.

[Poll từng tiến trình và báo cáo tiến độ]

Tất cả validation hoàn tất. Tóm tắt:
- Quality: PASS (0 vấn đề)
- Security: WARN (2 vấn đề nhỏ)
- Dependencies: PASS
- Performance: PASS (đạt baseline)

Chi tiết:
[Kết quả tổng hợp từ tất cả kiểm tra]
```

## Quản Lý Trạng Thái Workflow

### Dùng File .local.md

Lưu trạng thái workflow trong file riêng của plugin:

```markdown
.claude/plugin-name-workflow.local.md:

---
workflow: deployment
stage: testing
started: 2025-01-15T10:30:00Z
environment: staging
branch: feature/new-api
commit: abc123def
tests_passed: false
build_complete: false
---

# Deployment Workflow State

Stage hiện tại: Testing
Bắt đầu: 2025-01-15 10:30 UTC

Các bước đã hoàn thành:
- ✅ Validation
- ✅ Kiểm tra branch
- ⏳ Testing (đang thực hiện)

Các bước còn lại:
- Build
- Deploy
- Smoke test
```

**Đọc trạng thái trong command:**

```markdown
---
description: Continue deployment workflow
allowed-tools: Read, Write
---

Đang đọc trạng thái workflow từ .claude/plugin-name-workflow.local.md...

Stage hiện tại: @.claude/plugin-name-workflow.local.md

[Parse YAML frontmatter để xác định bước tiếp theo]

Hành động tiếp theo dựa trên trạng thái: [hành động đã xác định]
```

### Phục Hồi Workflow

Xử lý workflow bị gián đoạn:

```markdown
---
description: Resume deployment workflow
allowed-tools: Read
---

# Resume Deployment

Đang kiểm tra workflow bị gián đoạn...

State file: @.claude/plugin-name-workflow.local.md

**Workflow tìm thấy:**
- Bắt đầu: [timestamp]
- Môi trường: [env]
- Hoàn thành gần nhất: [step]

**Tùy chọn phục hồi:**
1. Tiếp tục từ bước cuối cùng
2. Khởi động lại từ đầu
3. Hủy bỏ và dọn dẹp

Bạn chọn tùy chọn nào? (1/2/3)
```

## Các Pattern Điều Phối Workflow

### Giao Tiếp Giữa Các Command

Command phát tín hiệu cho nhau:

```markdown
---
description: Mark feature complete
allowed-tools: Write
---

# Mark Feature Complete

Đang ghi marker hoàn thành...

Tạo: .claude/feature-complete.flag

Điều này báo hiệu cho các command khác rằng feature đã sẵn sàng:
- Integration testing (/integration-test sẽ tự phát hiện)
- Tạo tài liệu (/docs-generate sẽ bao gồm)
- Release notes (/release-notes sẽ thêm vào)

Feature đã được đánh dấu hoàn thành.
```

**Các command khác kiểm tra flag:**

```markdown
---
description: Generate release notes
allowed-tools: Read, Bash(git:*)
---

Đang kiểm tra feature đã hoàn thành...

if [ -f .claude/feature-complete.flag ]; then
  Feature sẵn sàng cho release notes
fi

[Bao gồm vào release notes]
```

### Khóa Workflow

Ngăn chạy workflow đồng thời:

```markdown
---
description: Start deployment
allowed-tools: Read, Write, Bash
---

# Start Deployment

Đang kiểm tra deployment đang hoạt động...

if [ -f .claude/deployment.lock ]; then
  LỖI: Đang có deployment đang chạy
  Bắt đầu: [timestamp từ lock file]

  Không thể bắt đầu deployment đồng thời.
  Chờ hoàn tất hoặc chạy /deployment-abort

  Thoát.
fi

Đang tạo deployment lock...

Deployment đã bắt đầu. Lock đã tạo.
[Tiếp tục với deployment]
```

**Dọn dẹp lock:**

```markdown
---
description: Complete deployment
allowed-tools: Write, Bash
---

Deployment hoàn tất.

Đang xóa deployment lock...
rm .claude/deployment.lock

Sẵn sàng cho deployment tiếp theo.
```

## Xử Lý Argument Nâng Cao

### Argument Tùy Chọn với Giá Trị Mặc Định

```markdown
---
description: Deploy with optional version
argument-hint: [environment] [version]
---

Environment: ${1:-staging}
Version: ${2:-latest}

Đang deploy ${2:-latest} lên ${1:-staging}...

Lưu ý: Dùng giá trị mặc định cho argument thiếu:
- Environment mặc định là 'staging'
- Version mặc định là 'latest'
```

### Validation Argument

```markdown
---
description: Deploy to validated environment
argument-hint: [environment]
---

Environment: $1

Đang validate environment...

valid_envs="dev staging production"
if ! echo "$valid_envs" | grep -w "$1" > /dev/null; then
  LỖI: Environment không hợp lệ '$1'
  Các tùy chọn hợp lệ: dev, staging, production
  Thoát.
fi

Environment hợp lệ. Đang tiếp tục...
```

### Biến Đổi Argument

```markdown
---
description: Deploy with shorthand
argument-hint: [env-shorthand]
---

Input: $1

Mở rộng shorthand:
- d/dev → development
- s/stg → staging
- p/prod → production

case "$1" in
  d|dev) ENV="development";;
  s|stg) ENV="staging";;
  p|prod) ENV="production";;
  *) ENV="$1";;
esac

Đang deploy lên: $ENV
```

## Xử Lý Lỗi trong Workflow

### Thất Bại Khéo Léo

```markdown
---
description: Resilient deployment workflow
---

# Deployment Workflow

Đang chạy các bước với xử lý lỗi...

## Bước 1: Test
!`npm test`

if [ $? -ne 0 ]; then
  LỖI: Test thất bại

  Tùy chọn:
  1. Sửa test và thử lại
  2. Bỏ qua test (KHÔNG khuyến nghị)
  3. Hủy deployment

  Bạn muốn làm gì?

  [Chờ input từ người dùng trước khi tiếp tục]
fi

## Bước 2: Build
[Chỉ tiếp tục nếu Bước 1 thành công]
```

### Rollback Khi Thất Bại

```markdown
---
description: Deployment with rollback
---

# Deploy with Rollback

Đang lưu trạng thái hiện tại để rollback...
Phiên bản trước: !`current-version.sh`

Đang deploy phiên bản mới...

!`deploy.sh`

if [ $? -ne 0 ]; then
  DEPLOYMENT THẤT BẠI

  Đang bắt đầu rollback tự động...
  !`rollback.sh`

  Đã rollback về phiên bản trước.
  Kiểm tra log để biết chi tiết lỗi.
fi

Deployment hoàn tất.
```

### Phục Hồi từ Checkpoint

```markdown
---
description: Workflow with checkpoints
---

# Multi-Stage Deployment

## Checkpoint 1: Validation
!`validate.sh`
echo "checkpoint:validation" >> .claude/deployment-checkpoints.log

## Checkpoint 2: Build
!`build.sh`
echo "checkpoint:build" >> .claude/deployment-checkpoints.log

## Checkpoint 3: Deploy
!`deploy.sh`
echo "checkpoint:deploy" >> .claude/deployment-checkpoints.log

Nếu bất kỳ bước nào thất bại, tiếp tục với:
/deployment-resume [last-successful-checkpoint]
```

## Các Nguyên Tắc Tốt Nhất

### Thiết Kế Workflow

1. **Tiến trình rõ ràng**: Đánh số bước, hiển thị vị trí hiện tại
2. **Trạng thái tường minh**: Không dựa vào trạng thái ngầm định
3. **Kiểm soát của người dùng**: Cung cấp điểm quyết định
4. **Phục hồi lỗi**: Xử lý thất bại khéo léo
5. **Chỉ báo tiến độ**: Hiển thị những gì đã xong, những gì còn lại

### Kết Hợp Command

1. **Single responsibility**: Mỗi command làm tốt một việc
2. **Thiết kế có thể kết hợp**: Các command dễ làm việc cùng nhau
3. **Interface tiêu chuẩn**: Format input/output nhất quán
4. **Loose coupling**: Các command không phụ thuộc vào internal của nhau

### Quản Lý Trạng Thái

1. **Trạng thái bền vững**: Dùng file .local.md
2. **Cập nhật atomic**: Ghi file trạng thái hoàn chỉnh theo kiểu atomic
3. **Validation trạng thái**: Kiểm tra format/tính đầy đủ của state file
4. **Dọn dẹp**: Xóa state file cũ
5. **Tài liệu**: Ghi lại format của state file

### Xử Lý Lỗi

1. **Fail fast**: Phát hiện lỗi sớm
2. **Thông báo rõ ràng**: Giải thích điều gì đã sai
3. **Tùy chọn phục hồi**: Cung cấp bước tiếp theo rõ ràng
4. **Bảo toàn trạng thái**: Giữ trạng thái để phục hồi
5. **Khả năng rollback**: Hỗ trợ hoàn tác thay đổi

## Ví dụ: Workflow Deployment Hoàn Chỉnh

### Command Initialize

```markdown
---
description: Initialize deployment
argument-hint: [environment]
allowed-tools: Write, Bash(git:*)
---

# Initialize Deployment to $1

Đang tạo trạng thái workflow...

\`\`\`yaml
---
workflow: deployment
environment: $1
branch: !`git branch --show-current`
commit: !`git rev-parse HEAD`
stage: initialized
timestamp: !`date -u +%Y-%m-%dT%H:%M:%SZ`
---
\`\`\`

Đã ghi vào .claude/deployment-state.local.md

Tiếp theo: Chạy /deployment-validate
```

### Command Validation

```markdown
---
description: Validate deployment
allowed-tools: Read, Bash
---

Đang đọc trạng thái: @.claude/deployment-state.local.md

Đang chạy validation...
- Kiểm tra branch: PASS
- Test: PASS
- Build: PASS

Đang cập nhật trạng thái thành 'validated'...

Tiếp theo: Chạy /deployment-execute
```

### Command Thực Thi

```markdown
---
description: Execute deployment
allowed-tools: Read, Bash, Write
---

Đang đọc trạng thái: @.claude/deployment-state.local.md

Đang thực thi deployment lên [environment]...

!`deploy.sh [environment]`

Deployment hoàn tất.
Đang cập nhật trạng thái thành 'completed'...

Dọn dẹp: /deployment-cleanup
```

### Command Dọn Dẹp

```markdown
---
description: Clean up deployment
allowed-tools: Bash
---

Đang xóa trạng thái deployment...
rm .claude/deployment-state.local.md

Workflow deployment hoàn tất.
```

Workflow hoàn chỉnh này minh họa quản lý trạng thái, thực thi tuần tự, xử lý lỗi và phân tách rõ ràng các mối quan tâm trên nhiều command.
