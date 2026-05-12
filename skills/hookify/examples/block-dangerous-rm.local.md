---
name: block-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
action: block
---

**Phát hiện lệnh rm -rf nguy hiểm!**

Lệnh này có thể xóa dữ liệu quan trọng. Cần:
- Xác nhận đường dẫn chính xác
- Cân nhắc dùng cách an toàn hơn (move to trash)
- Đảm bảo đã có backup
