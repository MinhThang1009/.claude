# Quy tắc Verification

> Bổ sung "Phong cách làm việc" trong [`CLAUDE.md`](../CLAUDE.md). Tránh lặp lại lỗi từ session trước.

## Subagent

- Kết quả từ subagent có **impact** (security finding, action user sẽ thực thi, claim về số liệu/version) → **verify bằng tool trực tiếp** (grep, đọc file, WebFetch) trước khi báo user. Subagent không thấy parent context → dễ báo sai. Summary trivial (vd "đã đọc 5 file, không tìm thấy X") thì có thể skip verify.
- Data trong parent context (WebFetch, tool output trước, conversation) → **paste subset relevant** vào prompt subagent. Data trên disk + subagent có `Read`/`Grep` → để subagent tự tìm.
- Không báo findings cho user mà chưa tự confirm ít nhất 1 lần.

## Git state

- Đầu session → **verify branch** bằng `git branch --show-current`. Startup hook có thể báo sai.
- Kiểm tra file trên branch khác → dùng `git ls-tree`/`git show branch:path`, **KHÔNG** dùng `ls`/`find` (working tree ≠ git tracking).

## External dependencies

- Dùng GitHub Action / package bên ngoài → **verify tồn tại** (WebFetch check repo/tag) trước khi commit. Không bịa tag version.
- Sửa **1 file** bằng Python script `open(file, 'w')` → **dùng Edit tool** thay vì viết script (tránh vô tình truncate). Batch op (rename N file, mass refactor) → script OK nhưng PHẢI: (1) preview list file affected, (2) backup hoặc git stash trước, (3) chạy với dry-run flag nếu có.
