# Các Pattern Command Tương Tác

Hướng dẫn toàn diện về cách tạo command thu thập phản hồi từ người dùng và đưa ra quyết định thông qua tool AskUserQuestion.

## Tổng Quan

Một số command cần input từ người dùng không phù hợp với argument đơn giản. Ví dụ:
- Chọn giữa nhiều tùy chọn phức tạp có đánh đổi
- Chọn nhiều item từ danh sách
- Đưa ra quyết định cần giải thích
- Thu thập preferences hoặc cấu hình một cách tương tác

Cho những trường hợp này, hãy dùng **tool AskUserQuestion** trong quá trình thực thi command thay vì dựa vào argument.

## Khi Nào Dùng AskUserQuestion

### Dùng AskUserQuestion Khi:

1. **Quyết định multiple choice** cần giải thích
2. **Tùy chọn phức tạp** cần context để lựa chọn
3. **Tình huống multi-select** (chọn nhiều item)
4. **Thu thập preferences** cho cấu hình
5. **Workflow tương tác** thích ứng dựa trên câu trả lời

### Dùng Argument Command Khi:

1. **Giá trị đơn giản** (đường dẫn file, số, tên)
2. **Input đã biết** mà người dùng đã có sẵn
3. **Workflow có thể script hóa** nên tự động hóa được
4. **Gọi nhanh** mà việc hỏi sẽ làm chậm

## Cơ Bản về AskUserQuestion

### Các Tham Số của Tool

```typescript
{
  questions: [
    {
      question: "Which authentication method should we use?",
      header: "Auth method",  // Nhãn ngắn (tối đa 12 ký tự)
      multiSelect: false,     // true để chọn nhiều
      options: [
        {
          label: "OAuth 2.0",
          description: "Tiêu chuẩn ngành, hỗ trợ nhiều provider"
        },
        {
          label: "JWT",
          description: "Stateless, phù hợp cho API"
        },
        {
          label: "Session",
          description: "Truyền thống, state phía server"
        }
      ]
    }
  ]
}
```

**Các điểm quan trọng:**
- Người dùng luôn có thể chọn "Other" để cung cấp input tùy chỉnh (tự động)
- `multiSelect: true` cho phép chọn nhiều tùy chọn
- Tùy chọn nên là 2–4 lựa chọn (không nhiều hơn)
- Có thể hỏi 1–4 câu hỏi mỗi lần gọi tool

## Pattern Command cho Tương Tác Người Dùng

### Command Tương Tác Cơ Bản

```markdown
---
description: Interactive setup command
allowed-tools: AskUserQuestion, Write
---

# Interactive Plugin Setup

Command này sẽ hướng dẫn bạn cấu hình plugin qua một loạt câu hỏi.

## Bước 1: Thu Thập Cấu Hình

Dùng tool AskUserQuestion để hỏi:

**Câu hỏi 1 — Đích deploy:**
- header: "Deploy to"
- question: "Which deployment platform will you use?"
- options:
  - AWS (Amazon Web Services với ECS/EKS)
  - GCP (Google Cloud với GKE)
  - Azure (Microsoft Azure với AKS)
  - Local (Docker trên máy local)

**Câu hỏi 2 — Chiến lược môi trường:**
- header: "Environments"
- question: "How many environments do you need?"
- options:
  - Single (Chỉ production)
  - Standard (Dev, Staging, Production)
  - Complete (Dev, QA, Staging, Production)

**Câu hỏi 3 — Tính năng cần bật:**
- header: "Features"
- question: "Which features do you want to enable?"
- multiSelect: true
- options:
  - Auto-scaling (Tự động mở rộng tài nguyên)
  - Monitoring (Health check và metrics)
  - CI/CD (Pipeline deployment tự động)
  - Backups (Sao lưu database tự động)

## Bước 2: Xử Lý Câu Trả Lời

Dựa trên câu trả lời nhận được từ AskUserQuestion:

1. Phân tích lựa chọn deployment target
2. Thiết lập cấu hình theo môi trường
3. Bật các tính năng đã chọn
4. Tạo file cấu hình

## Bước 3: Tạo Cấu Hình

Tạo `.claude/plugin-name.local.md` với:

\`\`\`yaml
---
deployment_target: [câu trả lời từ Q1]
environments: [câu trả lời từ Q2]
features:
  auto_scaling: [true nếu được chọn trong Q3]
  monitoring: [true nếu được chọn trong Q3]
  ci_cd: [true nếu được chọn trong Q3]
  backups: [true nếu được chọn trong Q3]
---

# Plugin Configuration

Tạo lúc: [timestamp]
Target: [deployment_target]
Môi trường: [environments]
\`\`\`

## Bước 4: Xác Nhận và Bước Tiếp Theo

Xác nhận cấu hình đã tạo và hướng dẫn người dùng về bước tiếp theo.
```

### Workflow Tương Tác Nhiều Giai Đoạn

```markdown
---
description: Multi-stage interactive workflow
allowed-tools: AskUserQuestion, Read, Write, Bash
---

# Multi-Stage Deployment Setup

Command này hướng dẫn thiết lập deployment theo từng giai đoạn, thích ứng dựa trên câu trả lời của bạn.

## Giai Đoạn 1: Cấu Hình Cơ Bản

Dùng AskUserQuestion để hỏi về các cài đặt deployment cơ bản.

Dựa trên câu trả lời, xác định câu hỏi bổ sung cần hỏi.

## Giai Đoạn 2: Tùy Chọn Nâng Cao (Có Điều Kiện)

Nếu người dùng chọn deployment "Advanced" ở Giai đoạn 1:

Dùng AskUserQuestion để hỏi về:
- Chiến lược load balancing
- Cấu hình caching
- Các tùy chọn tăng cường bảo mật

Nếu người dùng chọn deployment "Simple":
- Bỏ qua câu hỏi nâng cao
- Dùng các giá trị mặc định hợp lý

## Giai Đoạn 3: Xác Nhận

Hiển thị tóm tắt tất cả lựa chọn.

Dùng AskUserQuestion để xác nhận cuối:
- header: "Confirm"
- question: "Does this configuration look correct?"
- options:
  - Yes (Tiến hành thiết lập)
  - No (Bắt đầu lại)
  - Modify (Để tôi điều chỉnh cài đặt cụ thể)

Nếu "Modify", hỏi cài đặt cụ thể nào cần thay đổi.

## Giai Đoạn 4: Thực Thi Thiết Lập

Dựa trên cấu hình đã xác nhận, thực thi các bước thiết lập.
```

## Thiết Kế Câu Hỏi Tương Tác

### Cấu Trúc Câu Hỏi

**Câu hỏi tốt:**
```markdown
Question: "Which database should we use for this project?"
Header: "Database"
Options:
  - PostgreSQL (Relational, tuân thủ ACID, tốt nhất cho query phức tạp)
  - MongoDB (Document store, schema linh hoạt, tốt nhất cho phát triển nhanh)
  - Redis (In-memory, nhanh, tốt nhất cho caching và session)
```

**Câu hỏi kém:**
```markdown
Question: "Database?"  // Quá mơ hồ
Header: "DB"  // Viết tắt không rõ
Options:
  - Option 1  // Không mô tả
  - Option 2
```

### Nguyên Tắc Thiết Kế Tùy Chọn Tốt Nhất

**Nhãn rõ ràng:**
- Dùng 1–5 từ
- Cụ thể và mô tả
- Không dùng jargon không có ngữ cảnh

**Mô tả hữu ích:**
- Giải thích tùy chọn có nghĩa gì
- Đề cập lợi ích hoặc đánh đổi chính
- Giúp người dùng đưa ra quyết định có thông tin
- Giữ trong 1–2 câu

**Số lượng phù hợp:**
- 2–4 tùy chọn mỗi câu hỏi
- Không làm người dùng choáng ngợp với quá nhiều lựa chọn
- Nhóm các tùy chọn liên quan
- "Other" được cung cấp tự động

### Câu Hỏi Multi-Select

**Khi nào dùng multiSelect:**

```markdown
Dùng AskUserQuestion để bật tính năng:

Question: "Which features do you want to enable?"
Header: "Features"
multiSelect: true  // Cho phép chọn nhiều
Options:
  - Logging (Log thao tác chi tiết)
  - Metrics (Theo dõi hiệu năng)
  - Alerts (Thông báo lỗi)
  - Backups (Sao lưu tự động)
```

Người dùng có thể chọn bất kỳ kết hợp nào: không có, một số, hoặc tất cả.

**Khi KHÔNG dùng multiSelect:**

```markdown
Question: "Which authentication method?"
multiSelect: false  // Chỉ một phương thức auth có ý nghĩa
```

Các lựa chọn loại trừ lẫn nhau không nên dùng multiSelect.

## Các Pattern Command với AskUserQuestion

### Pattern 1: Quyết Định Yes/No Đơn Giản

```markdown
---
description: Command with confirmation
allowed-tools: AskUserQuestion, Bash
---

# Destructive Operation

Thao tác này sẽ xóa tất cả dữ liệu đã cache.

Dùng AskUserQuestion để xác nhận:

Question: "This will delete all cached data. Are you sure?"
Header: "Confirm"
Options:
  - Yes (Tiến hành xóa)
  - No (Hủy thao tác)

Nếu người dùng chọn "Yes":
  Thực thi xóa
  Báo cáo kết quả

Nếu người dùng chọn "No":
  Hủy thao tác
  Thoát không có thay đổi
```

### Pattern 2: Nhiều Câu Hỏi Cấu Hình

```markdown
---
description: Multi-question configuration
allowed-tools: AskUserQuestion, Write
---

# Project Configuration Setup

Thu thập cấu hình qua nhiều câu hỏi.

Dùng AskUserQuestion với nhiều câu hỏi trong một lần gọi:

**Câu hỏi 1:**
- question: "Which programming language?"
- header: "Language"
- options: Python, TypeScript, Go, Rust

**Câu hỏi 2:**
- question: "Which test framework?"
- header: "Testing"
- options: Jest, PyTest, Go Test, Cargo Test
  (Thích nghi dựa trên ngôn ngữ từ Q1)

**Câu hỏi 3:**
- question: "Which CI/CD platform?"
- header: "CI/CD"
- options: GitHub Actions, GitLab CI, CircleCI

**Câu hỏi 4:**
- question: "Which features do you need?"
- header: "Features"
- multiSelect: true
- options: Linting, Type checking, Code coverage, Security scanning

Xử lý tất cả câu trả lời cùng nhau để tạo cấu hình thống nhất.
```

### Pattern 3: Luồng Câu Hỏi Có Điều Kiện

```markdown
---
description: Conditional interactive workflow
allowed-tools: AskUserQuestion, Read, Write
---

# Adaptive Configuration

## Câu Hỏi 1: Độ Phức Tạp Deployment

Dùng AskUserQuestion:

Question: "How complex is your deployment?"
Header: "Complexity"
Options:
  - Simple (Một server, đơn giản)
  - Standard (Nhiều server, load balancing)
  - Complex (Microservice, orchestration)

## Câu Hỏi Có Điều Kiện Dựa Trên Câu Trả Lời

Nếu câu trả lời là "Simple":
  - Không có câu hỏi thêm
  - Dùng cấu hình tối thiểu

Nếu câu trả lời là "Standard":
  - Hỏi về chiến lược load balancing
  - Hỏi về chính sách scaling

Nếu câu trả lời là "Complex":
  - Hỏi về nền tảng orchestration (Kubernetes, Docker Swarm)
  - Hỏi về service mesh (Istio, Linkerd, None)
  - Hỏi về monitoring (Prometheus, Datadog, CloudWatch)
  - Hỏi về log aggregation

## Xử Lý Câu Trả Lời Có Điều Kiện

Tạo cấu hình phù hợp với mức độ phức tạp đã chọn.
```

### Pattern 4: Thu Thập Lặp Đi Lặp Lại

```markdown
---
description: Collect multiple items iteratively
allowed-tools: AskUserQuestion, Write
---

# Collect Team Members

Chúng ta sẽ thu thập thông tin thành viên nhóm cho project.

## Câu Hỏi: Bao Nhiêu Thành Viên?

Dùng AskUserQuestion:

Question: "How many team members should we set up?"
Header: "Team size"
Options:
  - 2 người
  - 3 người
  - 4 người
  - 6 người

## Lặp Qua Từng Thành Viên

Với mỗi thành viên (1 đến N dựa trên câu trả lời):

Dùng AskUserQuestion để hỏi chi tiết thành viên:

Question: "What role for team member [number]?"
Header: "Role"
Options:
  - Frontend Developer
  - Backend Developer
  - DevOps Engineer
  - QA Engineer
  - Designer

Lưu thông tin từng thành viên.

## Tạo Cấu Hình Nhóm

Sau khi thu thập đủ N thành viên, tạo file cấu hình nhóm với tất cả thành viên và vai trò của họ.
```

### Pattern 5: Chọn Dependency

```markdown
---
description: Select dependencies with multi-select
allowed-tools: AskUserQuestion
---

# Configure Project Dependencies

## Câu Hỏi: Thư Viện Cần Thiết

Dùng AskUserQuestion với multiSelect:

Question: "Which libraries does your project need?"
Header: "Dependencies"
multiSelect: true
Options:
  - React (UI framework)
  - Express (Web server)
  - TypeORM (Database ORM)
  - Jest (Testing framework)
  - Axios (HTTP client)

Người dùng có thể chọn bất kỳ kết hợp nào.

## Xử Lý Lựa Chọn

Với mỗi thư viện được chọn:
- Thêm vào package.json dependencies
- Tạo cấu hình mẫu
- Tạo ví dụ sử dụng
- Cập nhật tài liệu
```

## Nguyên Tắc Tốt Nhất cho Command Tương Tác

### Thiết Kế Câu Hỏi

1. **Rõ ràng và cụ thể**: Câu hỏi phải không mơ hồ
2. **Header ngắn gọn**: Tối đa 12 ký tự để hiển thị gọn
3. **Tùy chọn hữu ích**: Nhãn rõ ràng, mô tả giải thích đánh đổi
4. **Số lượng phù hợp**: 2–4 tùy chọn mỗi câu hỏi, 1–4 câu hỏi mỗi lần gọi
5. **Thứ tự logic**: Câu hỏi chảy tự nhiên

### Xử Lý Lỗi

```markdown
# Xử Lý Phản Hồi AskUserQuestion

Sau khi gọi AskUserQuestion, xác minh câu trả lời nhận được:

Nếu câu trả lời trống hoặc không hợp lệ:
  Có gì đó đã sai khi thu thập phản hồi.

  Hãy thử lại hoặc cung cấp cấu hình thủ công:
  [Hiển thị cách tiếp cận thay thế]

  Thoát.

Nếu câu trả lời có vẻ đúng:
  Xử lý như mong đợi
```

### Tiết Lộ Dần Dần

```markdown
# Bắt Đầu Đơn Giản, Đi Sâu Khi Cần

## Câu Hỏi 1: Loại Thiết Lập

Dùng AskUserQuestion:

Question: "How would you like to set up?"
Header: "Setup type"
Options:
  - Quick (Dùng các giá trị mặc định được khuyến nghị)
  - Custom (Cấu hình tất cả tùy chọn)
  - Guided (Từng bước với giải thích)

Nếu "Quick":
  Áp dụng mặc định, câu hỏi tối thiểu

Nếu "Custom":
  Hỏi tất cả câu hỏi cấu hình có sẵn

Nếu "Guided":
  Hỏi câu hỏi với giải thích thêm
  Cung cấp khuyến nghị theo từng bước
```

### Hướng Dẫn Multi-Select

**Dùng multi-select đúng cách:**
```markdown
Question: "Which features do you want to enable?"
multiSelect: true
Options:
  - Logging
  - Metrics
  - Alerts
  - Backups

Lý do: Người dùng có thể muốn bất kỳ kết hợp nào
```

**Dùng multi-select sai cách:**
```markdown
Question: "Which database engine?"
multiSelect: true  # ❌ Nên là single-select

Lý do: Chỉ có thể dùng một database engine
```

## Các Pattern Nâng Cao

### Vòng Lặp Validation

```markdown
---
description: Interactive with validation
allowed-tools: AskUserQuestion, Bash
---

# Setup with Validation

## Thu Thập Cấu Hình

Dùng AskUserQuestion để thu thập các cài đặt.

## Validate Cấu Hình

Kiểm tra cấu hình có hợp lệ không:
- Các dependency bắt buộc có sẵn không?
- Các cài đặt có tương thích với nhau không?
- Không phát hiện conflict?

Nếu validation thất bại:
  Hiển thị lỗi validation

  Dùng AskUserQuestion để hỏi:

  Question: "Configuration has issues. What would you like to do?"
  Header: "Next step"
  Options:
    - Fix (Điều chỉnh cài đặt để giải quyết vấn đề)
    - Override (Tiếp tục bất chấp cảnh báo)
    - Cancel (Hủy bỏ thiết lập)

  Dựa trên câu trả lời, thử lại hoặc tiếp tục hoặc thoát.
```

### Xây Dựng Cấu Hình Dần Dần

```markdown
---
description: Incremental configuration builder
allowed-tools: AskUserQuestion, Write, Read
---

# Incremental Setup

## Giai Đoạn 1: Cài Đặt Cốt Lõi

Dùng AskUserQuestion cho các cài đặt cốt lõi.

Lưu vào `.claude/config-partial.yml`

## Giai Đoạn 2: Xem Lại Cài Đặt Cốt Lõi

Hiển thị cho người dùng các cài đặt cốt lõi:

Dựa trên các cài đặt cốt lõi này, bạn cần cấu hình:
- [Cài đặt A] (vì bạn đã chọn [X])
- [Cài đặt B] (vì bạn đã chọn [Y])

Sẵn sàng tiếp tục?

## Giai Đoạn 3: Cài Đặt Chi Tiết

Dùng AskUserQuestion cho cài đặt dựa trên câu trả lời Giai đoạn 1.

Hợp nhất với cài đặt cốt lõi.

## Giai Đoạn 4: Xem Lại Cuối Cùng

Trình bày cấu hình hoàn chỉnh.

Dùng AskUserQuestion để xác nhận:

Question: "Is this configuration correct?"
Options:
  - Yes (Lưu và áp dụng)
  - No (Bắt đầu lại)
  - Modify (Chỉnh sửa cài đặt cụ thể)
```

### Tùy Chọn Động Dựa Trên Ngữ Cảnh

```markdown
---
description: Context-aware questions
allowed-tools: AskUserQuestion, Bash, Read
---

# Context-Aware Setup

## Phát Hiện Trạng Thái Hiện Tại

Kiểm tra cấu hình hiện có:
- Ngôn ngữ hiện tại: !`detect-language.sh`
- Framework hiện có: !`detect-frameworks.sh`
- Tool có sẵn: !`check-tools.sh`

## Hỏi Câu Hỏi Phù Hợp Với Ngữ Cảnh

Dựa trên ngôn ngữ được phát hiện, hỏi câu hỏi liên quan.

Nếu ngôn ngữ là TypeScript:

  Dùng AskUserQuestion:

  Question: "Which TypeScript features should we enable?"
  Options:
    - Strict Mode (Type safety tối đa)
    - Decorators (Hỗ trợ decorator thực nghiệm)
    - Path Mapping (Alias đường dẫn module)

Nếu ngôn ngữ là Python:

  Dùng AskUserQuestion:

  Question: "Which Python tools should we configure?"
  Options:
    - Type Hints (mypy để kiểm tra kiểu)
    - Black (Định dạng code)
    - Pylint (Lint và style)

Câu hỏi thích nghi với ngữ cảnh project.
```

## Ví Dụ Thực Tế: Khởi Chạy Multi-Agent Swarm

**Từ plugin multi-agent-swarm:**

```markdown
---
description: Launch multi-agent swarm
allowed-tools: AskUserQuestion, Read, Write, Bash
---

# Launch Multi-Agent Swarm

## Chế Độ Tương Tác (Chưa Cung Cấp Task List)

Nếu người dùng chưa cung cấp file task list, giúp tạo một cách tương tác.

### Câu Hỏi 1: Số Lượng Agent

Dùng AskUserQuestion:

Question: "How many agents should we launch?"
Header: "Agent count"
Options:
  - 2 agents (Tốt nhất cho project đơn giản)
  - 3 agents (Phù hợp cho project vừa)
  - 4 agents (Quy mô nhóm tiêu chuẩn)
  - 6 agents (Project lớn)
  - 8 agents (Project phức tạp nhiều thành phần)

### Câu Hỏi 2: Cách Định Nghĩa Task

Dùng AskUserQuestion:

Question: "How would you like to define tasks?"
Header: "Task setup"
Options:
  - File (Tôi đã có file task list sẵn)
  - Guided (Giúp tôi tạo task tương tác)
  - Custom (Cách tiếp cận khác)

Nếu "File":
  Hỏi đường dẫn file
  Validate file tồn tại và đúng định dạng

Nếu "Guided":
  Vào chế độ tạo task lặp đi lặp lại (xem bên dưới)

### Câu Hỏi 3: Chế Độ Điều Phối

Dùng AskUserQuestion:

Question: "How should agents coordinate?"
Header: "Coordination"
Options:
  - Team Leader (Một agent điều phối các agent khác)
  - Collaborative (Các agent điều phối như đồng nghiệp)
  - Autonomous (Làm việc độc lập, điều phối tối thiểu)

### Tạo Task Lặp Đi Lặp Lại (Nếu Chọn "Guided")

Với mỗi agent (1 đến N từ Câu hỏi 1):

**Câu hỏi A: Tên Agent**
Question: "What should we call agent [number]?"
Header: "Agent name"
Options:
  - auth-agent
  - api-agent
  - ui-agent
  - db-agent
  (Cung cấp gợi ý liên quan dựa trên các pattern phổ biến)

**Câu hỏi B: Loại Task**
Question: "What task for [agent-name]?"
Header: "Task type"
Options:
  - Authentication (Auth người dùng, JWT, OAuth)
  - API Endpoints (REST/GraphQL API)
  - UI Components (Component frontend)
  - Database (Schema, migration, query)
  - Testing (Bộ test và coverage)
  - Documentation (Docs, README, guide)

**Câu hỏi C: Dependency**
Question: "What does [agent-name] depend on?"
Header: "Dependencies"
multiSelect: true
Options:
  - [Danh sách các agent đã định nghĩa trước đó]
  - No dependencies

**Câu hỏi D: Branch Cơ Sở**
Question: "Which base branch for PR?"
Header: "PR base"
Options:
  - main
  - staging
  - develop

Lưu tất cả thông tin task cho mỗi agent.

### Tạo File Task List

Sau khi thu thập đủ chi tiết task cho mọi agent:

1. Hỏi tên project
2. Tạo task list theo đúng định dạng
3. Lưu vào `.daisy/swarm/tasks.md`
4. Hiển thị đường dẫn file cho người dùng
5. Tiến hành khởi chạy dùng task list đã tạo
```

## Nguyên Tắc Tốt Nhất

### Viết Câu Hỏi

1. **Cụ thể**: "Which database?" thay vì "Choose option?"
2. **Giải thích đánh đổi**: Mô tả ưu/nhược của từng tùy chọn
3. **Cung cấp ngữ cảnh**: Câu hỏi phải đứng được một mình
4. **Hướng dẫn quyết định**: Giúp người dùng đưa ra lựa chọn có thông tin
5. **Giữ ngắn gọn**: Header tối đa 12 ký tự, mô tả 1–2 câu

### Thiết Kế Tùy Chọn

1. **Nhãn có ý nghĩa**: Tên cụ thể, rõ ràng
2. **Mô tả nhiều thông tin**: Giải thích từng tùy chọn làm gì
3. **Hiển thị đánh đổi**: Giúp người dùng hiểu hệ quả
4. **Chi tiết nhất quán**: Tất cả tùy chọn được giải thích đều nhau
5. **2–4 tùy chọn**: Không quá ít, không quá nhiều

### Thiết Kế Luồng

1. **Thứ tự logic**: Câu hỏi chảy tự nhiên
2. **Xây dựng từ trước**: Câu hỏi sau dùng câu trả lời trước
3. **Tối thiểu hóa câu hỏi**: Chỉ hỏi những gì cần thiết
4. **Nhóm câu hỏi liên quan**: Hỏi câu hỏi liên quan cùng nhau
5. **Hiển thị tiến độ**: Chỉ rõ đang ở đâu trong luồng

### Trải Nghiệm Người Dùng

1. **Đặt kỳ vọng**: Cho người dùng biết điều gì sẽ xảy ra
2. **Giải thích lý do**: Giúp người dùng hiểu mục đích
3. **Cung cấp mặc định**: Gợi ý tùy chọn được khuyến nghị
4. **Cho phép thoát**: Để người dùng hủy hoặc bắt đầu lại
5. **Xác nhận hành động**: Tóm tắt trước khi thực thi

## Các Pattern Phổ Biến

### Pattern: Chọn Tính Năng

```markdown
Dùng AskUserQuestion:

Question: "Which features do you need?"
Header: "Features"
multiSelect: true
Options:
  - Authentication
  - Authorization
  - Rate Limiting
  - Caching
```

### Pattern: Cấu Hình Môi Trường

```markdown
Dùng AskUserQuestion:

Question: "Which environment is this?"
Header: "Environment"
Options:
  - Development (Phát triển local)
  - Staging (Kiểm thử trước production)
  - Production (Môi trường live)
```

### Pattern: Chọn Độ Ưu Tiên

```markdown
Dùng AskUserQuestion:

Question: "What's the priority for this task?"
Header: "Priority"
Options:
  - Critical (Phải làm ngay)
  - High (Quan trọng, làm sớm)
  - Medium (Ưu tiên bình thường)
  - Low (Tốt nếu có)
```

### Pattern: Chọn Phạm Vi

```markdown
Dùng AskUserQuestion:

Question: "What scope should we analyze?"
Header: "Scope"
Options:
  - Current file (Chỉ file này)
  - Current directory (Tất cả file trong thư mục)
  - Entire project (Quét toàn bộ codebase)
```

## Kết Hợp Argument và Câu Hỏi

### Dùng Cả Hai Phù Hợp

**Argument cho giá trị đã biết:**
```markdown
---
argument-hint: [project-name]
allowed-tools: AskUserQuestion, Write
---

Thiết lập cho project: $1

Bây giờ thu thập cấu hình bổ sung...

Dùng AskUserQuestion cho các tùy chọn cần giải thích.
```

**Câu hỏi cho lựa chọn phức tạp:**
```markdown
Tên project từ argument: $1

Bây giờ dùng AskUserQuestion để chọn:
- Pattern kiến trúc
- Technology stack
- Chiến lược deployment

Những thứ này cần giải thích, nên câu hỏi phù hợp hơn argument.
```

## Troubleshooting

**Câu hỏi không hiển thị:**
- Xác minh AskUserQuestion có trong allowed-tools
- Kiểm tra định dạng câu hỏi đúng
- Đảm bảo mảng options có 2–4 item

**Người dùng không thể chọn:**
- Kiểm tra nhãn tùy chọn rõ ràng
- Xác minh mô tả hữu ích
- Cân nhắc xem có quá nhiều tùy chọn không
- Đảm bảo cài đặt multiSelect đúng

**Luồng gây nhầm lẫn:**
- Giảm số câu hỏi
- Nhóm câu hỏi liên quan
- Thêm giải thích giữa các giai đoạn
- Hiển thị tiến độ qua workflow

Với AskUserQuestion, command trở thành các wizard tương tác hướng dẫn người dùng qua các quyết định phức tạp trong khi vẫn giữ sự rõ ràng mà argument đơn giản mang lại cho các input thẳng thắn.
