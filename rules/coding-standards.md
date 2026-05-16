# Quy tắc Code

> Auto-import mọi session qua `rules/`.

## Nguyên tắc cốt lõi

- **Đọc trước khi viết**: ưu tiên đọc cả function chứa change; function >100 dòng thì 30 dòng xung quanh + signature/return là đủ. Fix nhỏ (1-2 dòng) thì context narrow hơn OK. File mới → scan file tương tự để theo pattern.
- **Convention codebase trước, "best practice" sau**. Snake_case nếu codebase snake_case. Tab nếu codebase tab.
- **Đúng > đẹp > nhanh**. Code chạy đúng quan trọng hơn pattern fancy.
- **Không over-engineer**. YAGNI. Generic abstraction sinh trong nhu cầu thật, không "phòng xa". Viết 200 dòng mà 50 dòng giải quyết được → viết lại.
- **Function < 50 dòng** lý tưởng. >100 dòng → xem xét tách (trừ khi logic có kết dính trên toàn bộ). Nesting >3 level → có thể flatten.
- **Đặt tên rõ ràng**. `getUserById` thay `getUser`. `isEmailVerified` thay `verified`. Tránh `data`, `info`, `obj` trừ khi context rõ.

## Surgical Changes

- **Chỉ sửa đúng thứ được yêu cầu**. Mọi dòng thay đổi phải trace trực tiếp về request của user.
- KHÔNG "cải thiện" code, comment, formatting xung quanh khi đang sửa thứ khác. KHÔNG refactor thứ chưa hỏng.
- Orphan do chính mình tạo ra (import, biến, function không còn dùng SAU khi sửa) → **xóa luôn**. Dead code có sẵn từ trước → **đề cập, không xóa** trừ khi user yêu cầu.
- Self-check: "Senior engineer có thấy diff này phức tạp quá không?" Nếu có → đơn giản lại.

## Verification khi refactor

- Refactor → **chạy test TRƯỚC khi sửa** (xác nhận baseline pass), sửa, **chạy test SAU** (xác nhận không regression).
- Nếu task mơ hồ ("make it work", "clean up") → transform thành tiêu chí verify cụ thể trước khi bắt đầu. Tiêu chí yếu → hỏi user thay vì đoán.

## Comment

- **Comment WHY, không WHAT** (code tự nói WHAT).
- **Tiếng Việt** cho comment giải thích logic/lý do (project tiếng Anh hoàn toàn → tiếng Anh).
- **Tiếng Anh** cho TODO/FIXME tag (để tool grep được): `// TODO(tên): Mô tả ngắn bằng tiếng Việt`.
- Docstring/JSDoc: tiếng Việt cho mô tả, nhưng giữ format chuẩn (`@param`, `@returns`, `@throws`).

Ví dụ tốt:
```python
# Cache theo IP để tránh user attack rate-limit qua nhiều account
limiter = RateLimiter(key_func=get_remote_ip)
```

Ví dụ kém (comment WHAT thay vì WHY):
```python
# Tạo rate limiter
limiter = RateLimiter(...)
```

## Error handling

- KHÔNG `catch` rỗng/swallow exception. Lỗi cần được handle có chủ đích.
- KHÔNG `catch (Exception e)` blanket — bắt cụ thể loại lỗi mong đợi.
- KHÔNG thêm error handling cho scenario không thể xảy ra. Chỉ validate ở system boundary (user input, external API, I/O).
- Ưu tiên **early return / guard clause / Result types** hơn try-catch khi có thể. Try-catch chỉ dùng khi thực sự cần catch exception (I/O, network, parsing).
- Fallback behavior phải **explicit và justified** — không silently fallback mà user không biết. Optional chaining (`?.`) có thể hide errors — chỉ dùng khi `undefined` là kết quả hợp lệ.
- Re-throw kèm context: `throw new ServiceError("Không lấy được user", { cause: e })`.
- Error message hiển thị cho user: **tiếng Việt**, generic, không lộ stack/internal info.
- Log internal: tiếng Việt OK, kèm context (user id, request id).

## Test

- Project có test framework → mọi feature mới có test, mọi bug fix có failing-test-then-fix.
- Test đặt tên mô tả: `test_login_fails_when_password_wrong` thay `test_login_2`.
- Arrange-Act-Assert. Mỗi test 1 assertion logic.
- KHÔNG mock thừa: chỉ mock external dependency (DB, HTTP, time, random). Không mock code đang test.
- Test description bằng tiếng Việt: `it('trả về 401 khi token hết hạn', ...)`.

## Performance

- **Đo trước khi optimize**. Profile (`cProfile`, `py-spy`, Chrome DevTools, `perf`) — không đoán.
- **Big-O quan trọng > vi-optimize**. O(n²) trên 10k item = 100 triệu phép tính — rất chậm; vi-optimize không cứu được.
- DB: index theo column hay query, không index loạn. N+1 query → batch hoặc join.
- Network: batch request, cache hợp lý, set timeout.

## Type safety

- Project có type system (TypeScript, mypy, Pydantic, Rust...) → dùng triệt để.
- KHÔNG `any`/`Any`/`unknown` trừ khi thực sự cần và có comment giải thích.
- Type chặt cho boundary (input từ user/network/file): validate runtime, không tin TypeScript compiler.

## Style

- Format theo formatter project (`prettier`, `black`, `gofmt`, `rustfmt`...). Không tự ý đổi style.
- Lint pass trước khi báo "xong". `eslint`, `ruff`, `clippy`, `golangci-lint`...
- Import order: theo formatter quy định, không thủ công.

## Tool usage

- Sửa **1 file** → **dùng Edit tool**, không viết Python script `open(file, 'w')` (tránh truncate). Batch op (rename N file, mass refactor) → script OK nhưng PHẢI: (1) preview list file affected, (2) backup hoặc git stash trước, (3) dry-run flag nếu có.

## Cờ đỏ DỪNG-HỎI

Cần hỏi xác nhận trước khi thực hiện:
- Thêm dependency mới (kể cả "phổ biến").
- Đổi schema DB / migration.
- Thay đổi config production / deployment.
- Sửa file shared (>3 module dùng) làm thay đổi behavior.
- Refactor cross-cutting (>5 file).
- Đổi public API signature.
- Xóa file/code không chắc 100% là dead.
