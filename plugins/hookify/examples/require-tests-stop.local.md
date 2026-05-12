---
name: require-tests-run
enabled: false
event: stop
action: block
conditions:
  - field: transcript
    operator: not_contains
    pattern: npm test|pytest|cargo test
---

**Chưa phát hiện test command nào trong transcript!**

Trước khi dừng, hãy chạy tests để verify thay đổi hoạt động đúng.

Tìm kiếm lệnh test phù hợp:
- `npm test`
- `pytest`
- `cargo test`

**Lưu ý:** Rule này block việc dừng nếu không có test command nào trong transcript.
Chỉ bật khi cần enforce test nghiêm ngặt.
