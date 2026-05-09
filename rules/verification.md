# Quy tắc Verification

> Bổ sung "Phong cách làm việc" trong [`CLAUDE.md`](../CLAUDE.md). Tránh lặp lại lỗi từ session trước.

## Subagent

- Kết quả từ subagent → **verify bằng tool trực tiếp** (grep, đọc file, WebFetch) trước khi báo user. Subagent không thấy parent context (WebFetch results, file reads trước đó) → dễ báo sai.
- Nếu delegate cross-check → **paste data cần thiết** vào prompt subagent, không assume agent tự tìm.
- Không báo findings cho user mà chưa tự confirm ít nhất 1 lần.

## Git state

- Đầu session → **verify branch** bằng `git branch --show-current`. Startup hook có thể báo sai.
- Kiểm tra file trên branch khác → dùng `git ls-tree`/`git show branch:path`, **KHÔNG** dùng `ls`/`find` (working tree ≠ git tracking).

## External dependencies

- Dùng GitHub Action / package bên ngoài → **verify tồn tại** (WebFetch check repo/tag) trước khi commit. Không bịa tag version.
- Sửa file bằng Python script `open(file, 'w')` → **dùng Edit tool** thay vì viết script — tránh vô tình xóa/truncate file.
