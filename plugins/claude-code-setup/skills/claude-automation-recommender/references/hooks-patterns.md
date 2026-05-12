# Gợi ý Hooks

Hooks tự động chạy lệnh khi Claude Code nhận sự kiện. Phù hợp nhất cho việc thực thi quy tắc và tự động hóa cần diễn ra nhất quán.

**Lưu ý**: Đây là các pattern phổ biến. Dùng web search để tìm hooks cho tools/frameworks chưa có trong danh sách nhằm đề xuất hooks phù hợp nhất cho người dùng.

## Hooks Tự Động Format Code

### Prettier (JavaScript/TypeScript)
| Phát hiện | File tồn tại |
|-----------|-------------|
| `.prettierrc`, `.prettierrc.json`, `prettier.config.js` | ✓ |

**Đề xuất**: PostToolUse hook trên Edit/Write để auto-format
**Giá trị**: Code luôn được format mà không cần nghĩ đến

### ESLint (JavaScript/TypeScript)
| Phát hiện | File tồn tại |
|-----------|-------------|
| `.eslintrc`, `.eslintrc.json`, `eslint.config.js` | ✓ |

**Đề xuất**: PostToolUse hook trên Edit/Write để auto-fix
**Giá trị**: Lỗi lint được sửa tự động

### Black/isort (Python)
| Phát hiện | File tồn tại |
|-----------|-------------|
| `pyproject.toml` với black/isort, `.black`, `setup.cfg` | ✓ |

**Đề xuất**: PostToolUse hook để format file Python
**Giá trị**: Format Python nhất quán

### Ruff (Python - Hiện đại)
| Phát hiện | File tồn tại |
|-----------|-------------|
| `ruff.toml`, `pyproject.toml` với `[tool.ruff]` | ✓ |

**Đề xuất**: PostToolUse hook cho lint + format
**Giá trị**: Python linting nhanh, toàn diện

### gofmt (Go)
| Phát hiện | File tồn tại |
|-----------|-------------|
| `go.mod` | ✓ |

**Đề xuất**: PostToolUse hook để chạy gofmt
**Giá trị**: Format Go chuẩn

### rustfmt (Rust)
| Phát hiện | File tồn tại |
|-----------|-------------|
| `Cargo.toml` | ✓ |

**Đề xuất**: PostToolUse hook để chạy rustfmt
**Giá trị**: Format Rust chuẩn

---

## Hooks Kiểm Tra Kiểu

### TypeScript
| Phát hiện | File tồn tại |
|-----------|-------------|
| `tsconfig.json` | ✓ |

**Đề xuất**: PostToolUse hook để chạy tsc --noEmit
**Giá trị**: Phát hiện lỗi kiểu ngay lập tức

### mypy/pyright (Python)
| Phát hiện | File tồn tại |
|-----------|-------------|
| `mypy.ini`, `pyrightconfig.json`, pyproject.toml với mypy | ✓ |

**Đề xuất**: PostToolUse hook để kiểm tra kiểu
**Giá trị**: Phát hiện lỗi kiểu trong Python

---

## Hooks Bảo Vệ

### Chặn Sửa File Nhạy Cảm
| Phát hiện | Sự hiện diện của |
|-----------|-------------|
| `.env`, `.env.local`, `.env.production` | File environment |
| `credentials.json`, `secrets.yaml` | File secret |
| Thư mục `.git/` | Git internals |

**Đề xuất**: PreToolUse hook chặn Edit/Write vào các path này
**Giá trị**: Ngăn vô tình lộ secret hoặc làm hỏng git

### Chặn Sửa Lock File
| Phát hiện | Sự hiện diện của |
|-----------|-------------|
| `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` | Lock file JS |
| `Cargo.lock`, `poetry.lock`, `Pipfile.lock` | Lock file khác |

**Đề xuất**: PreToolUse hook chặn sửa trực tiếp
**Giá trị**: Lock file chỉ nên thay đổi qua package manager

---

## Hooks Chạy Test

### Jest (JavaScript/TypeScript)
| Phát hiện | Sự hiện diện của |
|-----------|-------------|
| `jest.config.js`, `jest` trong package.json | Jest đã cấu hình |
| `__tests__/`, `*.test.ts`, `*.spec.ts` | File test tồn tại |

**Đề xuất**: PostToolUse hook chạy test liên quan sau khi sửa
**Giá trị**: Phản hồi test ngay lập tức khi có thay đổi

### pytest (Python)
| Phát hiện | Sự hiện diện của |
|-----------|-------------|
| `pytest.ini`, `pyproject.toml` với pytest | pytest đã cấu hình |
| `tests/`, `test_*.py` | File test tồn tại |

**Đề xuất**: PostToolUse hook chạy pytest trên file đã thay đổi
**Giá trị**: Phản hồi test ngay lập tức

---

## Tham Khảo Nhanh: Phát Hiện → Đề Xuất

| Nếu thấy | Đề xuất hook này |
|------------|-------------------|
| Prettier config | Auto-format khi Edit/Write |
| ESLint config | Auto-lint khi Edit/Write |
| Ruff/Black config | Auto-format Python |
| tsconfig.json | Kiểm tra kiểu khi Edit |
| Thư mục test | Chạy test liên quan khi Edit |
| File .env | Chặn sửa .env |
| Lock file | Chặn sửa lock file |
| Dự án Go | gofmt khi Edit |
| Dự án Rust | rustfmt khi Edit |

---

## Hooks Thông Báo

Hooks thông báo chạy khi Claude Code gửi notification. Dùng matcher để lọc theo loại notification.

### Cảnh Báo Permission
| Matcher | Trường hợp dùng |
|---------|----------|
| `permission_prompt` | Cảnh báo khi Claude yêu cầu permission |

**Đề xuất**: Phát âm thanh, gửi desktop notification, hoặc ghi log các yêu cầu permission
**Giá trị**: Không bao giờ bỏ lỡ permission prompt khi đang multitask

### Thông Báo Idle
| Matcher | Trường hợp dùng |
|---------|----------|
| `idle_prompt` | Cảnh báo khi Claude đang chờ input (idle 60+ giây) |

**Đề xuất**: Phát âm thanh hoặc gửi notification khi Claude cần chú ý
**Giá trị**: Biết khi nào Claude sẵn sàng nhận input

### Ví Dụ Cấu Hình

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Ping.aiff"
          }
        ]
      },
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude is waiting\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

### Các Matcher Có Sẵn

| Matcher | Kích hoạt khi |
|---------|---------------|
| `permission_prompt` | Claude cần permission cho một tool |
| `idle_prompt` | Claude đang chờ input (60+ giây) |
| `auth_success` | Xác thực thành công |
| `elicitation_dialog` | MCP tool cần input |

---

## Tham Khảo Nhanh: Phát Hiện → Đề Xuất

| Nếu thấy | Đề xuất hook này |
|------------|-------------------|
| Prettier config | Auto-format khi Edit/Write |
| ESLint config | Auto-lint khi Edit/Write |
| Ruff/Black config | Auto-format Python |
| tsconfig.json | Kiểm tra kiểu khi Edit |
| Thư mục test | Chạy test liên quan khi Edit |
| File .env | Chặn sửa .env |
| Lock file | Chặn sửa lock file |
| Dự án Go | gofmt khi Edit |
| Dự án Rust | rustfmt khi Edit |
| Workflow multitask | Hooks thông báo để nhận cảnh báo |

---

## Vị Trí Đặt Hook

Hooks được đặt trong `.claude/settings.json`:

```
.claude/
└── settings.json  ← Cấu hình hooks ở đây
```

Đề xuất tạo thư mục `.claude/` nếu chưa tồn tại.
