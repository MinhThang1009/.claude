---
name: clean-gone
description: "Cleans up all local git branches marked as [gone] (deleted on remote but still exist locally), including removing associated worktrees."
---

## Your Task

Bạn cần thực thi các lệnh bash sau để dọn dẹp các local branch cũ đã bị xóa khỏi remote repository.

## Commands to Execute

1. **Đầu tiên, liệt kê các branch để xác định những branch có trạng thái [gone]**
   Thực thi lệnh sau:
   ```bash
   git branch -v
   ```

   Lưu ý: Branch có tiền tố '+' có worktree liên kết và phải được xóa worktree trước khi xóa branch.

2. **Tiếp theo, xác định các worktree cần xóa cho các branch [gone]**
   Thực thi lệnh sau:
   ```bash
   git worktree list
   ```

3. **Cuối cùng, xóa worktree và xóa các branch [gone] (xử lý cả branch thường và branch có worktree)**
   Thực thi lệnh sau:
   ```bash
   # Xử lý tất cả branch [gone], loại bỏ tiền tố '+' nếu có
   git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
     echo "Processing branch: $branch"
     # Tìm và xóa worktree nếu tồn tại
     worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
     if [ ! -z "$worktree" ] && [ "$worktree" != "$(git rev-parse --show-toplevel)" ]; then
       echo "  Removing worktree: $worktree"
       git worktree remove --force "$worktree"
     fi
     # Xóa branch
     echo "  Deleting branch: $branch"
     git branch -D "$branch"
   done
   ```

## Expected Behavior

Sau khi thực thi các lệnh này, bạn sẽ:

- Thấy danh sách tất cả local branch với trạng thái của chúng
- Xác định và xóa các worktree liên kết với branch [gone]
- Xóa tất cả branch được đánh dấu [gone]
- Cung cấp phản hồi về các worktree và branch đã được xóa

Nếu không có branch nào được đánh dấu [gone], báo cáo rằng không cần dọn dẹp.
