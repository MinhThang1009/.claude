---
name: refactor
description: Refactor code không thay đổi behavior. Yêu cầu có test trước, refactor từng bước nhỏ, verify sau mỗi bước. Dùng khi user nói "refactor", "tái cấu trúc", "code này khó đọc quá", hoặc gọi /refactor.
allowed-tools: Read Grep Glob Edit Bash
argument-hint: "[đường dẫn file hoặc mô tả phạm vi]"
---

# Skill: Refactor an toàn

> Refactor = đổi cấu trúc code KHÔNG đổi behavior. Nếu thay đổi behavior → đó là feature/fix, không phải refactor.

## Bước 1: Pre-flight check

KHÔNG bắt đầu refactor nếu một trong các điều sau đúng:
- Working tree không sạch (có thay đổi chưa commit) → đề xuất commit trước.
- Test suite hiện tại đang fail → đề xuất fix test trước.
- Không có test cho code sắp refactor → đề xuất viết test characterization trước (test capture behavior hiện tại, kể cả behavior chưa chắc đúng).

Hỏi user nếu cần:
- Phạm vi refactor: chỉ 1 file, 1 module, hay xuyên codebase?
- Mục tiêu: dễ đọc hơn? Tách responsibility? Loại duplicate? Đổi pattern?
- Có constraint về public API không? (function nào export ra ngoài KHÔNG được đổi signature?)

## Bước 2: Phân tích & lập plan

Đọc code, hiểu nó đang làm gì. Sau đó:

1. **Liệt kê smell** đang có:
   - Long function/class
   - Duplicate code
   - Magic number, magic string
   - Naming khó hiểu
   - Coupling cao giữa module
   - Side effect ngầm
   - Error handling không nhất quán

2. **Đề xuất plan refactor** dạng các bước nhỏ, mỗi bước:
   - Atomic (commit độc lập được)
   - Reversible (rollback dễ)
   - Verify được bằng test sau mỗi bước

   Ví dụ:
   ```text
   Bước 1: Extract function `validateEmail` ra khỏi `signupUser`
   Bước 2: Đổi tên `data` → `userInput` (4 chỗ)
   Bước 3: Tách type `User` thành 2 type: `UserInput` và `UserRecord`
   Bước 4: Thay magic number 86400 bằng const `SECONDS_PER_DAY`
   ```

3. **Trình bày plan cho user**, hỏi: "OK plan như vậy không? Muốn làm hết hay chỉ một số bước?"

## Bước 3: Thực hiện từng bước

Với MỖI bước:

1. **Áp dụng thay đổi** (Edit file).
2. **Chạy test** ngay sau đó. Nếu test fail → revert ngay, không tiếp tục.
3. **Chạy lint/format** nếu project có.
4. **Báo cáo ngắn**: "Bước N xong, test pass" hoặc "Bước N fail vì X, đã revert".
5. Đề xuất commit checkpoint: `refactor: tách hàm validateEmail`.

KHÔNG combine nhiều bước thành một edit lớn. Cảm giác muốn làm hết một thể là cám dỗ — nhưng sai một chỗ trong batch lớn thì khó tìm. Bước nhỏ + commit nhỏ = revert dễ.

## Bước 4: Verify cuối

Sau khi xong tất cả bước:
- Toàn bộ test suite PASS
- Lint/format clean
- Build thành công
- (Nếu có) Manual smoke test: chạy app, click một flow chính, đảm bảo không vỡ.
- Diff cuối có khớp với plan ban đầu không? Có thay đổi behavior nào lọt vào không? Nếu có → tách ra commit riêng.

## Quy tắc đỏ

KHÔNG làm trong refactor:
- ❌ Thêm feature mới
- ❌ Sửa bug (kể cả thấy bug rõ ràng — note ra TODO, làm sau)
- ❌ Đổi public API signature mà chưa thông báo
- ❌ Đổi behavior dù chỉ "một xíu" (ví dụ "chỗ này throw error sớm hơn cho an toàn") — đó là behavior change, làm commit riêng.
- ❌ Format-only change xen kẽ với logic change trong cùng diff
- ❌ Refactor file không liên quan "tiện tay"

## Khi gặp legacy code khó

Nếu code quá rối, không có test, người viết đã nghỉ:
- Đề xuất **strangler pattern**: viết mới song song, dần chuyển caller, xóa cũ sau cùng.
- Hoặc đề xuất **characterization test**: chạy code cũ với nhiều input, capture output, dùng làm test. Test sẽ trông xấu (không assert "đúng đắn", chỉ assert "giống hôm nay") — nhưng đó là an toàn duy nhất khi không hiểu intent gốc.

## Output format

Sau khi xong, báo cáo:

```text
Đã refactor xong: [phạm vi]

Các bước đã thực hiện:
1. ✓ Extract validateEmail (commit abc123)
2. ✓ Rename data → userInput (commit def456)
3. ✗ Bước 3 (split type) — fail test, đã revert. Lý do: ...
4. ✓ Replace magic number (commit ghi789)

Đã chạy:
- Test suite: pass (124 tests)
- Lint: clean
- Build: success

[Nếu có] Note để follow-up:
- Phát hiện bug ở foo.ts:42 trong lúc refactor — chưa fix, mở issue?
```

## Gotchas

- **Refactor = giữ behavior**. Test phải pass TRƯỚC và SAU. Nếu khác → feature/fix, không phải refactor.
- **Không có test → viết characterization test trước**. Refactor blind rất nguy hiểm với code legacy.
- **Đổi tên file/symbol** = đổi nhiều import. Dùng IDE refactor tool nếu có, không grep & replace blind (dễ miss case-sensitive, comment, string literal).
- **Performance thay đổi = optimize, không phải refactor**. Tách 2 loại commit riêng để revert dễ.
