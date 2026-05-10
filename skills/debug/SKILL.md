---
name: debug
description: Hỗ trợ debug bug có hệ thống. Yêu cầu reproduce trước, viết failing test, rồi mới fix. Dùng khi user nói "debug", "fix bug", "lỗi này không hiểu", "sao chạy không được", hoặc gọi /debug.
allowed-tools: Read Grep Glob Bash Edit
argument-hint: "[tùy chọn — mô tả bug]"
---

# Skill: Debug có hệ thống

Bạn được gọi để debug. **KHÔNG** sửa ngẫu nhiên cho đến khi hiểu vấn đề.

## Nguyên tắc

> "A bug you can reproduce reliably is half-fixed."

## Bước 1: Thu thập triệu chứng

Hỏi user (nếu chưa rõ):
- Triệu chứng cụ thể là gì? (lỗi gì, output sai gì, crash chỗ nào)
- Khi nào xảy ra? (luôn, ngẫu nhiên, chỉ trong môi trường nào)
- Trước đây có hoạt động không? Nếu có, thay đổi gần nhất là gì?
- Có error message / stack trace không? Paste vào.

## Bước 2: Reproduce

Trước khi đoán nguyên nhân, **reproduce trong môi trường local**:
- Chạy lệnh user mô tả
- Mở file, gọi hàm, gửi request — tái tạo điều kiện gây lỗi
- Capture output đầy đủ

Nếu **KHÔNG reproduce được**:
- Nói rõ với user
- Đề xuất bước thu thập thêm thông tin (log thêm, env khác, version khác)
- KHÔNG đoán mò sửa khi chưa reproduce.

## Bước 3: Khoanh vùng nguyên nhân

Áp dụng phương pháp khoa học:

1. **Quan sát**: chính xác output sai là gì so với output đúng kỳ vọng?
2. **Giả thuyết**: liệt kê 2-4 nguyên nhân khả dĩ, theo độ tin cậy.
3. **Verify**: với mỗi giả thuyết, xác định **thí nghiệm** kiểm chứng (đọc file nào, chạy lệnh nào, log gì). Bắt đầu từ giả thuyết có chi phí kiểm chứng thấp nhất.
4. **Khoanh vùng**: bisect — chia đôi không gian khả nghi (commit, file, hàm, input range) cho đến khi tìm được phần nhỏ nhất gây lỗi.

Công cụ:
- `git bisect` cho regression
- Binary search trong code: comment/uncomment chia đôi
- Log thêm tại các điểm quan trọng (nhớ xóa sau khi fix)
- Reproduce với input nhỏ nhất gây lỗi (minimal reproducer)

## Bước 4: Hiểu nguyên nhân (root cause, KHÔNG phải triệu chứng)

Khi tìm thấy chỗ lỗi:
- Tại sao code này gây lỗi? (cơ chế cụ thể, không phải "nó sai")
- Tại sao nó được viết như vậy? (đọc git blame, đọc PR cũ)
- Có nơi nào khác trong codebase có pattern tương tự không? (dùng Grep — fix một chỗ thường không đủ)

## Bước 5: Viết failing test

Trước khi fix:
- Viết test reproduce bug. Test này phải **FAIL** trên code hiện tại.
- Test phải minimal, chỉ test cái bug, không test thứ khác.
- Đặt tên test mô tả bug: `it('không crash khi input là array rỗng', ...)`.

Nếu project không có test framework hoặc bug khó test (UI bug, race condition) → tạo **manual reproduction script** thay thế.

## Bước 6: Fix

- Fix root cause, KHÔNG patch triệu chứng.
- Nếu fix có nhiều cách → chọn cách ít xâm lấn nhất, có ít side effect nhất.
- Sửa CẢ các nơi khác có pattern tương tự (đã tìm ở bước 4).

## Bước 7: Verify

- Chạy lại failing test → giờ phải PASS.
- Chạy toàn bộ test suite → không break test khác.
- Reproduce lại bug ban đầu manually → không còn xảy ra.

## Bước 8: Báo cáo

```markdown
## Bug: <mô tả ngắn>

**Nguyên nhân**: <root cause cụ thể, 1-3 câu>

**Fix**: <cách sửa, 1-3 câu>

**File thay đổi**:
- src/foo.ts (line 42-45) — sửa logic check empty
- tests/foo.test.ts — thêm test reproduce

**Verify**:
- ✓ failing test giờ pass
- ✓ test suite full pass
- ✓ reproduce thủ công không còn lỗi
```

## Khi bug không reproduce được

Trường hợp khó (race condition, env khác, "works-on-my-machine"):
- KHÔNG đoán fix rồi báo "chắc xong rồi". Nói thẳng: "Không reproduce được, fix sau đây dựa trên giả thuyết X. Cần verify bằng [cách Y]."
- Đề xuất thêm log/telemetry để bắt được lần xảy ra tiếp theo.

## Khi đã sửa 2 lần vẫn không đúng

DỪNG. Đề xuất: "Đã thử 2 cách không thành. Đề xuất `/clear` rồi mô tả lại bug với context tốt hơn — có thể đang miss điểm gì đó."

## Gotchas

- **Bug bay biến** = chưa thực sự reproduce. Chạy lại 5-10 lần xác nhận reproducibility trước khi đoán nguyên nhân.
- **Failing test PHẢI fail bằng test runner của project** (pytest, jest, go test, cargo test, v.v.) — không chỉ manual. Test không reproducible = chưa nắm được bug.
- **Race condition / async**: bug hiện không đều = nghi race. Đừng fix bằng retry loop — tìm shared state thực sự.
- **Fix symptom ≠ fix root cause**: in/log nguyên nhân ra trước khi sửa. Nếu không giải thích được "tại sao", chưa fix xong.
