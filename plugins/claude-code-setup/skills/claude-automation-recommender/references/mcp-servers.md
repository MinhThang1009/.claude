# Gợi Ý MCP Server

MCP (Model Context Protocol) server mở rộng khả năng của Claude bằng cách kết nối với các tool và dịch vụ bên ngoài.

**Lưu ý**: Đây là các MCP server phổ biến. Dùng web search để tìm MCP server phù hợp với các dịch vụ và tích hợp cụ thể của codebase.

## Thiết Lập & Chia Sẻ Trong Team

**Phương thức kết nối:**
1. **Project config** (`.mcp.json`) - Chỉ khả dụng trong thư mục đó
2. **Global config** (`~/.claude.json`) - Khả dụng trên toàn bộ project
3. **`.mcp.json` được commit** - Khả dụng cho toàn bộ team (khuyến nghị!)

**Mẹo**: Commit `.mcp.json` vào git để cả team dùng chung một bộ MCP server.

**Debug**: Dùng `claude --mcp-debug` để xác định các vấn đề cấu hình.

## Documentation & Kiến Thức

### context7
**Phù hợp nhất cho**: Các project dùng thư viện/SDK phổ biến, nơi bạn muốn Claude code với documentation cập nhật

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Dùng React, Vue, Angular | Frontend framework |
| Dùng Express, FastAPI, Django | Backend framework |
| Dùng Prisma, Drizzle | ORM |
| Dùng Stripe, Twilio, SendGrid | Third-party API |
| Dùng AWS SDK, Google Cloud | Cloud SDK |
| Dùng LangChain, OpenAI SDK | Thư viện AI/ML |

**Giá trị**: Claude lấy documentation trực tiếp thay vì dựa vào dữ liệu huấn luyện, giảm thiểu API bịa đặt và pattern lỗi thời.

---

## Browser & Frontend

### Playwright MCP
**Phù hợp nhất cho**: Các project frontend cần tự động hóa browser, testing, hoặc chụp ảnh màn hình

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Ứng dụng React/Vue/Angular | Kiểm thử UI component |
| Cần E2E test | Kiểm tra luồng người dùng |
| Visual regression testing | So sánh ảnh chụp màn hình |
| Debug vấn đề UI | Xem giao diện từ góc nhìn người dùng |
| Kiểm thử form | Workflow nhiều bước |

**Giá trị**: Claude có thể tương tác với ứng dụng đang chạy, chụp ảnh màn hình, điền form, và kiểm tra hành vi UI.

### Puppeteer MCP
**Phù hợp nhất cho**: Tự động hóa browser headless, web scraping

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Tạo PDF từ HTML | Tạo báo cáo |
| Tác vụ web scraping | Trích xuất dữ liệu |
| Kiểm thử headless | Môi trường CI |

---

## Databases

### Supabase MCP
**Phù hợp nhất cho**: Các project dùng Supabase làm backend/database

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Phát hiện project Supabase | `@supabase/supabase-js` trong deps |
| Cần auth + database | Ứng dụng quản lý người dùng |
| Tính năng real-time | Đồng bộ dữ liệu trực tiếp |

**Giá trị**: Claude có thể query table, quản lý auth, và tương tác trực tiếp với Supabase storage.

### PostgreSQL MCP
**Phù hợp nhất cho**: Truy cập trực tiếp database PostgreSQL

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Dùng PostgreSQL thuần | Không có ORM |
| Database migration | Quản lý schema |
| Phân tích dữ liệu | Query phức tạp |
| Debug vấn đề dữ liệu | Kiểm tra dữ liệu thực tế |

### Neon MCP
**Phù hợp nhất cho**: Người dùng Neon serverless Postgres

### Turso MCP
**Phù hợp nhất cho**: Người dùng database edge Turso/libSQL

---

## Version Control & DevOps

### GitHub MCP
**Phù hợp nhất cho**: Các repository trên GitHub cần tích hợp issue/PR

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Repository GitHub | `.git` với GitHub remote |
| Phát triển theo issue | Tham chiếu issue trong commit |
| Workflow PR | Review, thao tác merge |
| GitHub Actions | Truy cập CI/CD pipeline |
| Quản lý release | Tự động hóa tag và release |

**Giá trị**: Claude có thể tạo issue, review PR, kiểm tra workflow run, và quản lý release.

### GitLab MCP
**Phù hợp nhất cho**: Các repository trên GitLab

### Linear MCP
**Phù hợp nhất cho**: Các team dùng Linear để theo dõi issue

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Workspace Linear | Tham chiếu issue dạng `ABC-123` |
| Lập kế hoạch sprint | Quản lý backlog |
| Tạo issue từ code | Tự động tạo issue cho TODO |

---

## Cloud Infrastructure

### AWS MCP
**Phù hợp nhất cho**: Quản lý hạ tầng AWS

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| AWS SDK trong dependencies | Các package `@aws-sdk/*` |
| Infrastructure as code | Terraform, CDK, SAM |
| Phát triển Lambda | Serverless function |
| Dùng S3, DynamoDB | Dịch vụ dữ liệu cloud |

### Cloudflare MCP
**Phù hợp nhất cho**: Cloudflare Workers, Pages, R2, D1

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Cloudflare Workers | Edge function |
| Pages deployment | Hosting static site |
| R2 storage | Object storage |
| D1 database | Edge SQL database |

### Vercel MCP
**Phù hợp nhất cho**: Deployment và cấu hình Vercel

---

## Monitoring & Observability

### Sentry MCP
**Phù hợp nhất cho**: Theo dõi lỗi và debug

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Đã cấu hình Sentry | `@sentry/*` trong deps |
| Debug production | Điều tra lỗi |
| Pattern lỗi | Nhóm các vấn đề tương tự |
| Theo dõi release | Liên kết deploy với lỗi |

**Giá trị**: Claude có thể điều tra issue trên Sentry, tìm nguyên nhân gốc rễ, và gợi ý hướng sửa.

### Datadog MCP
**Phù hợp nhất cho**: APM, log, và metrics

---

## Giao Tiếp

### Slack MCP
**Phù hợp nhất cho**: Tích hợp với workspace Slack

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Team dùng Slack | Gửi thông báo |
| Thông báo deployment | Cảnh báo channel |
| Xử lý sự cố | Đăng cập nhật |

### Notion MCP
**Phù hợp nhất cho**: Workspace Notion dùng để viết documentation

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Dùng Notion cho docs | Đọc/cập nhật trang |
| Knowledge base | Tìm kiếm documentation |
| Ghi chú họp | Tạo tóm tắt |

---

## File & Dữ Liệu

### Filesystem MCP
**Phù hợp nhất cho**: Các thao tác file nâng cao hơn tool tích hợp sẵn

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Thao tác file phức tạp | Xử lý hàng loạt |
| Theo dõi file | Giám sát thay đổi |
| Tìm kiếm nâng cao | Pattern tùy chỉnh |

### Memory MCP
**Phù hợp nhất cho**: Bộ nhớ bền vững xuyên suốt các session

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Project dài hạn | Ghi nhớ context |
| Tùy chọn người dùng | Lưu cài đặt |
| Học pattern | Xây dựng kiến thức |

**Giá trị**: Claude ghi nhớ context, quyết định, và pattern của project xuyên suốt các cuộc hội thoại.

---

## Container & DevOps

### Docker MCP
**Phù hợp nhất cho**: Quản lý container

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Có file Docker Compose | Điều phối container |
| Có Dockerfile | Build image |
| Debug container | Kiểm tra log, exec |

### Kubernetes MCP
**Phù hợp nhất cho**: Quản lý Kubernetes cluster

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Có K8s manifest | Deploy, scale pod |
| Có Helm chart | Quản lý package |
| Debug cluster | Log pod, trạng thái |

---

## AI & ML

### Exa MCP
**Phù hợp nhất cho**: Tìm kiếm web và nghiên cứu

| Khuyến nghị khi | Ví dụ |
|----------------|----------|
| Tác vụ nghiên cứu | Tìm thông tin mới nhất |
| Phân tích cạnh tranh | Nghiên cứu thị trường |
| Thiếu documentation | Tìm ví dụ |

---

## Tham Khảo Nhanh: Pattern Phát Hiện

| Phát hiện | Gợi ý MCP Server |
|----------|-------------------|
| Các npm package phổ biến | context7 |
| React/Vue/Next.js | Playwright MCP |
| `@supabase/supabase-js` | Supabase MCP |
| `pg` hoặc `postgres` | PostgreSQL MCP |
| GitHub remote | GitHub MCP |
| `.linear` hoặc tham chiếu Linear | Linear MCP |
| `@aws-sdk/*` | AWS MCP |
| `@sentry/*` | Sentry MCP |
| `docker-compose.yml` | Docker MCP |
| Slack webhook URL | Slack MCP |
| `@anthropic-ai/sdk` | context7 cho Anthropic docs |
