---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

Để test các web application local, viết script Playwright Python native.

**Helper Scripts có sẵn**:
- `scripts/with_server.py` - Quản lý vòng đời server (hỗ trợ nhiều server)

**Luôn chạy script với `--help` đầu tiên** để xem cách dùng. KHÔNG đọc source trước khi đã thử chạy script và phát hiện ra rằng cần giải pháp tùy chỉnh thực sự. Các script này có thể rất lớn và làm ô nhiễm context window. Chúng tồn tại để được gọi trực tiếp như black-box scripts thay vì nạp vào context window.

## Cây quyết định: Chọn cách tiếp cận

```
User task → Có phải static HTML không?
    ├─ Có → Đọc file HTML trực tiếp để xác định selector
    │         ├─ Thành công → Viết script Playwright dùng selector đó
    │         └─ Fail/Không đủ → Xử lý như dynamic (bên dưới)
    │
    └─ Không (dynamic webapp) → Server đã chạy chưa?
        ├─ Chưa → Chạy: python scripts/with_server.py --help
        │         Rồi dùng helper + viết script Playwright đơn giản
        │
        └─ Rồi → Reconnaissance-then-action:
            1. Navigate và đợi networkidle
            2. Chụp screenshot hoặc inspect DOM
            3. Xác định selector từ rendered state
            4. Thực thi action với selector đã tìm được
```

## Ví dụ: Dùng with_server.py

Để khởi động server, chạy `--help` đầu tiên, rồi dùng helper:

**Một server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Nhiều server (vd: backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

Để tạo automation script, chỉ include logic Playwright (server được quản lý tự động):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Pattern Reconnaissance-Then-Action

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Xác định selector** từ kết quả inspect

3. **Thực thi action** dùng selector đã tìm được

## Pitfall thường gặp

❌ **Đừng** inspect DOM trước khi đợi `networkidle` trên dynamic app
✅ **Hãy** đợi `page.wait_for_load_state('networkidle')` trước khi inspect

## Best Practices

- **Dùng script bundled như black box** - Để hoàn thành task, cân nhắc xem có script nào sẵn trong `scripts/` giúp được không. Các script này xử lý workflow phức tạp thường gặp một cách tin cậy mà không làm rối context window. Dùng `--help` để xem usage, rồi gọi trực tiếp.
- Dùng `sync_playwright()` cho synchronous script
- Luôn đóng browser khi xong
- Dùng selector mô tả rõ: `text=`, `role=`, CSS selector, hoặc ID
- Thêm wait phù hợp: `page.wait_for_selector()` hoặc `page.wait_for_timeout()`

## Reference Files

- **examples/** - Ví dụ các pattern thường gặp:
  - `element_discovery.py` - Phát hiện button, link, và input trên page
  - `static_html_automation.py` - Dùng file:// URL cho HTML local
  - `console_logging.py` - Capture console log trong quá trình automation
