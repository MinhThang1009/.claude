---
name: warn-sensitive-files
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$|\.env\.|credentials|secrets
---

**Phát hiện file nhạy cảm**

Đang edit file có thể chứa dữ liệu nhạy cảm:
- Đảm bảo credentials không hardcoded
- Dùng environment variables cho secrets
- Kiểm tra file có trong .gitignore chưa
- Cân nhắc dùng secrets manager
