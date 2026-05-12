# Quy tắc Verification

> Bổ sung "Phong cách làm việc" trong [`CLAUDE.md`](../CLAUDE.md). Tránh lặp lại lỗi từ session trước.

## Subagent

- Kết quả từ subagent có **impact** (security finding, action user sẽ thực thi, claim về số liệu/version) → **verify bằng tool trực tiếp** (Grep, Read, WebFetch) trước khi báo user. Subagent không thấy parent context ([docs](https://code.claude.com/docs/en/sub-agents)) → dễ báo sai. Summary trivial (vd "đã đọc 5 file, không tìm thấy X") thì có thể skip verify.
- Data trong parent context (WebFetch, tool output trước, conversation) → **paste subset relevant** vào prompt subagent. Data trên disk + subagent có `Read`/`Grep` → để subagent tự tìm.
- Không báo findings cho user mà chưa tự confirm ít nhất 1 lần.
- Subagent KHÔNG nhận full Claude Code system prompt — chỉ nhận system prompt riêng (markdown body của agent definition). **CLAUDE.md vẫn load** qua message flow bình thường ([docs](https://code.claude.com/docs/en/sub-agents)). rules/*.md KHÔNG load (suy luận — docs chỉ confirm CLAUDE.md load, không mention rules). Nếu cần convention cụ thể → inject vào prompt hoặc dùng `skills` field. Hai cơ chế fork khác nhau: (1) `CLAUDE_CODE_FORK_SUBAGENT=1` (env var) = fork kế thừa toàn bộ history + system prompt + tools. (2) `context: fork` (skill frontmatter) = chạy isolation, KHÔNG kế thừa history — skill content thành prompt cho subagent mới.
- **Background** subagent auto-deny permissions chưa pre-approve. Kết quả bất thường (ít findings, empty output) → có thể do bị deny silently. Retry bằng foreground nếu nghi ngờ.
- Consolidate output từ nhiều subagent → **đếm findings mỗi subagent** trước (tự đếm, không tin self-count), ghi tổng expected. Nếu consolidated report ít hơn → liệt kê rõ finding nào bị drop + lý do. KHÔNG drop ngầm. Hai subagent report cùng finding nhưng severity khác → lấy severity **cao hơn**. Finding partially valid → giữ phần đúng, ghi rõ phần sai.
- Audit/review spec thay đổi giữa chừng → **re-dispatch** subagent với spec mới. KHÔNG re-evaluate findings cũ từ memory — findings cũ chạy theo spec cũ, không đại diện cho spec mới.
- Subagent có thể **miss content** khi file dài hoặc task quá nhiều (fetch URLs + đọc files + evaluate + report cùng lúc). Không tin coverage rating tuyệt đối — subagent báo "not covered" → **grep verify trước khi chấp nhận**. Giới hạn scope: mỗi subagent ≤10 files hoặc ≤3 complex tasks đồng thời.
- **Session cache** (system-reminder loaded đầu session) ≠ disk state hiện tại. Ảnh hưởng **cả subagent lẫn lead agent**: content đã thêm/sửa/xóa trong session không reflect trong system-reminder. Khi consolidate findings hoặc so sánh file → luôn dùng Read/Grep từ disk, KHÔNG dựa vào nội dung đã load trong context.

## Self-review bias

- Sau batch fixes (>5 edits) → dispatch **fresh subagent** review changes thay vì tự verify. Tự fix → tự review = bias (session này đã chứng minh: tự verify bằng grep miss 5 regressions, fresh subagent bắt được).
- Fresh subagent KHÔNG nhận context về intent sửa — chỉ nhận file paths + instruction "review for correctness". Đây là feature, không phải bug: independent review cần independent context.

## Batch edits

- Sau khi edit → verify **nội dung thay thế** đúng, không chỉ confirm nội dung cũ đã biến mất. Grep "pattern cũ removed" ≠ "pattern mới correct". Đặc biệt với factual claims (version, threshold, URL) → WebFetch verify source trước khi apply.
- Sửa claim xuất hiện ở **nhiều file** → grep claim đó across toàn repo sau khi edit. Sửa file A mà file B vẫn giữ giá trị cũ = tạo inconsistency mới.
- File có thể bị **edit bởi process khác** (user edit tay, hook, formatter, linter) giữa lúc edit và verify → read lại file trước khi kết luận edit thành công.
- Trước batch edit (>3 files) → đảm bảo **git clean** (commit hoặc stash WIP). Nếu edit fail giữa chừng → dùng `/rewind` hoặc `git checkout` để revert. KHÔNG để codebase ở trạng thái nửa-edit.

## Tool output reliability

- Output bị **truncate** (Read `limit`, Bash timeout, WebFetch summary) → không đủ để kết luận. Expand/retry trước khi confirm. Đặc biệt: Read file lớn mà không thấy pattern → chưa chắc không có, có thể nằm ngoài range đã đọc.
- WebFetch **fail** (404, timeout, redirect loop, auth-required) → KHÔNG coi là "đã verify". Thử URL khác hoặc ghi rõ "không verify được, cần user confirm".
- WebFetch summary được tạo bởi **small model trong context riêng** → có thể sai factual. Data dùng để ra quyết định quan trọng (version, threshold, security advisory) → cross-check bằng URL thứ hai hoặc `Bash(curl)` nếu cần raw content.
- Verify qua **MCP tools** (GitHub MCP, database MCP...) → cùng nguyên tắc với subagent: output có impact → cross-check bằng tool khác. MCP server do user cấu hình, có thể trả data stale.

## Git state

- Đầu session → **verify branch** bằng `git branch --show-current`. Output của SessionStart hook (user tự cấu hình) có thể outdated hoặc sai.
- Kiểm tra file trên branch khác → dùng `git ls-tree`/`git show branch:path`, **KHÔNG** dùng `ls`/`find` (working tree chỉ phản ánh branch hiện tại).
- Section này chỉ áp dụng khi project có **git repo**. Project không có git → skip, dùng file system trực tiếp.

## External dependencies

- Dùng GitHub Action / package bên ngoài → **verify tồn tại** (WebFetch check repo/tag) trước khi commit. WebFetch fail khi verify → áp dụng "Tool output reliability": thử URL khác hoặc ghi cần user confirm.
- Dep tồn tại nhưng **version mismatch** → cảnh báo user, không tự downgrade/upgrade.
- Sửa **1 file** bằng Python script `open(file, 'w')` → **dùng Edit tool** thay vì viết script (tránh vô tình truncate). Batch op (rename N file, mass refactor) → script OK nhưng PHẢI: (1) preview list file affected, (2) backup hoặc git stash trước, (3) chạy với dry-run flag nếu có.
