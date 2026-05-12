---
name: warn-console-log
enabled: true
event: file
pattern: console\.log\(
action: warn
---

**Phát hiện console.log**

Đang thêm `console.log`. Cân nhắc:
- Đây là debug tạm thời hay cần dùng logging library đúng cách?
- Code này có ship lên production không?
- Có nên dùng logging library thay vì console.log?
