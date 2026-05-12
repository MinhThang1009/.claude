# Gợi Ý Subagent

Subagent là các phiên bản Claude chuyên biệt chạy song song, mỗi cái có context window và quyền truy cập tool riêng. Chúng lý tưởng cho các tác vụ review, phân tích, hoặc tạo nội dung tập trung.

**Lưu ý**: Đây là các pattern phổ biến. Thiết kế subagent tùy chỉnh dựa trên nhu cầu review và phân tích cụ thể của codebase.

## Agent Review Code

### code-reviewer
**Phù hợp nhất cho**: Kiểm tra chất lượng code tự động trên codebase lớn

| Khuyến nghị khi | Phát hiện |
|----------------|-----------|
| Codebase lớn (>500 file) | Số lượng file |
| Thay đổi code thường xuyên | Đang phát triển tích cực |
| Team muốn review nhất quán | Tập trung vào chất lượng |

**Giá trị**: Chạy review code song song trong khi bạn tiếp tục làm việc
**Model**: sonnet (cân bằng chất lượng/tốc độ)
**Tools**: Read, Grep, Glob, Bash

---

### security-reviewer
**Phù hợp nhất cho**: Review code tập trung vào bảo mật

| Khuyến nghị khi | Phát hiện |
|----------------|-----------|
| Có code auth | Pattern `auth/`, `login`, `session` |
| Xử lý thanh toán | Pattern `stripe`, `payment`, `billing` |
| Xử lý dữ liệu người dùng | Pattern `user`, `profile`, `pii` |
| API key trong code | Pattern biến môi trường |

**Giá trị**: Phát hiện lỗ hổng OWASP, vấn đề auth, lộ dữ liệu
**Model**: sonnet
**Tools**: Read, Grep, Glob (chỉ đọc để đảm bảo an toàn)

---

### test-writer
**Phù hợp nhất cho**: Tạo test coverage toàn diện

| Khuyến nghị khi | Phát hiện |
|----------------|-----------|
| Coverage test thấp | Ít file test so với file source |
| Có test suite | Thư mục `tests/`, `__tests__/` tồn tại |
| Đã cấu hình testing framework | jest, pytest, vitest trong deps |

**Giá trị**: Tạo test theo convention của project
**Model**: sonnet
**Tools**: Read, Write, Grep, Glob

---

## Agent Chuyên Biệt

### api-documenter
**Phù hợp nhất cho**: Tạo API documentation

| Khuyến nghị khi | Phát hiện |
|----------------|-----------|
| Có REST endpoint | Express route, FastAPI path |
| GraphQL schema | File `.graphql` |
| OpenAPI đã có | `openapi.yaml`, `swagger.json` |
| API chưa có tài liệu | Route không có docs |

**Giá trị**: Tạo OpenAPI spec, tài liệu endpoint
**Model**: sonnet
**Tools**: Read, Write, Grep, Glob

---

### performance-analyzer
**Phù hợp nhất cho**: Tìm bottleneck hiệu năng

| Khuyến nghị khi | Phát hiện |
|----------------|-----------|
| Có database query | ORM, raw SQL |
| Code có lưu lượng cao | API endpoint, hot path |
| Phàn nàn về hiệu năng | Người dùng báo chậm |
| Thuật toán phức tạp | Nested loop, đệ quy |

**Giá trị**: Tìm N+1 query, thuật toán O(n²), memory leak
**Model**: sonnet
**Tools**: Read, Grep, Glob, Bash

---

### ui-reviewer
**Phù hợp nhất cho**: Review accessibility và UX frontend

| Khuyến nghị khi | Phát hiện |
|----------------|-----------|
| React/Vue/Angular | Phát hiện frontend framework |
| Thư viện component | Thư mục `components/` |
| UI hướng người dùng | Không chỉ là project API |

**Giá trị**: Phát hiện vấn đề accessibility, UX, thiếu responsive design
**Model**: sonnet
**Tools**: Read, Grep, Glob

---

## Agent Tiện Ích

### dependency-updater
**Phù hợp nhất cho**: Cập nhật dependency an toàn

| Khuyến nghị khi | Phát hiện |
|----------------|-----------|
| Dep lỗi thời | `npm outdated` có kết quả |
| Cảnh báo bảo mật | `npm audit` có cảnh báo |
| Chênh lệch major version lớn | Khoảng cách version đáng kể |

**Giá trị**: Cập nhật dependency từng bước kèm kiểm thử
**Model**: sonnet
**Tools**: Read, Write, Bash, Grep

---

### migration-helper
**Phù hợp nhất cho**: Migration framework/version

| Khuyến nghị khi | Phát hiện |
|----------------|-----------|
| Cần nâng cấp major | Version framework quá cũ |
| Sắp có breaking change | Cảnh báo deprecation |
| Lên kế hoạch refactoring | Thay đổi kiến trúc |

**Giá trị**: Lên kế hoạch và thực hiện migration từng bước
**Model**: opus (cần suy luận phức tạp)
**Tools**: Read, Write, Grep, Glob, Bash

---

## Tham Khảo Nhanh: Phát Hiện → Gợi Ý

| Nếu thấy | Khuyến nghị Subagent |
|------------|-------------------|
| Codebase lớn | code-reviewer |
| Code auth/thanh toán | security-reviewer |
| Ít test | test-writer |
| API route | api-documenter |
| Nhiều database | performance-analyzer |
| Component frontend | ui-reviewer |
| Package lỗi thời | dependency-updater |
| Framework cũ | migration-helper |

---

## Vị Trí Đặt Subagent

Subagent đặt trong `.claude/agents/`:

```
.claude/
└── agents/
    ├── code-reviewer.md
    ├── security-reviewer.md
    └── test-writer.md
```

---

## Hướng Dẫn Chọn Model

| Model | Phù hợp nhất cho | Đánh đổi |
|-------|----------|-----------|
| **haiku** | Kiểm tra đơn giản, lặp đi lặp lại | Nhanh, rẻ, kém kỹ lưỡng |
| **sonnet** | Hầu hết tác vụ review/phân tích | Cân bằng (mặc định khuyến nghị) |
| **opus** | Migration phức tạp, kiến trúc | Kỹ lưỡng, chậm hơn, tốn kém hơn |

---

## Hướng Dẫn Quyền Truy Cập Tool

| Mức độ truy cập | Tools | Trường hợp dùng |
|--------------|-------|----------|
| Chỉ đọc | Read, Grep, Glob | Review, phân tích |
| Có ghi | + Write | Tạo code, docs |
| Đầy đủ | + Bash | Migration, kiểm thử |
