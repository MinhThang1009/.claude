---
name: commit-push-pr
allowed-tools: Bash(git checkout --branch:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
description: Commit, push, and open a pull request
---

## Context

- Trạng thái git hiện tại: !`git status`
- Git diff hiện tại (thay đổi staged và unstaged): !`git diff HEAD`
- Branch hiện tại: !`git branch --show-current`

## Your task

Dựa trên các thay đổi ở trên:

1. Tạo branch mới nếu đang ở main
2. Tạo một commit duy nhất với message phù hợp
3. Push branch lên origin
4. Tạo pull request bằng `gh pr create`
5. Bạn có khả năng gọi nhiều tool trong một response. Bạn PHẢI thực hiện tất cả các bước trên trong một message duy nhất. Không dùng tool khác hoặc làm bất cứ điều gì khác. Không gửi bất kỳ text hay message nào khác ngoài các tool call này.
