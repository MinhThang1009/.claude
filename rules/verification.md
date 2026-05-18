# Quy tắc Verification

> Bổ sung "Phong cách làm việc" trong CLAUDE.md. Tránh lặp lại lỗi từ session trước.

## Subagent

- Kết quả từ subagent có **impact** (security finding, action user sẽ thực thi, claim về số liệu/version) → **verify bằng tool trực tiếp** (Grep, Read, WebFetch) trước khi báo user. **Named sub-agent** bắt đầu fresh, không thấy parent context → dễ báo sai. **Fork** kế thừa toàn bộ history nên ít bị vấn đề này hơn. Summary trivial (vd "đã đọc 5 file, không tìm thấy X") thì có thể skip verify.
- Data trong parent context (WebFetch, tool output trước, conversation) → **paste subset relevant** vào prompt subagent. Data trên disk + subagent có `Read`/`Grep` → để subagent tự tìm.
- Không báo findings cho user mà chưa tự confirm ít nhất 1 lần *(self-imposed — không trong docs Anthropic)*.
- Subagent KHÔNG nhận full Claude Code system prompt — chỉ nhận system prompt riêng (markdown body của agent definition). **CLAUDE.md và rules/*.md**: main session load bình thường; `--agent` mode và `context: fork` skills — CLAUDE.md load (confirmed), rules/*.md load cùng mechanism nhưng chưa có docs tường minh cho sub-agent context. Agent-tool spawned named sub-agents: **KHÔNG load CLAUDE.md** từ working directory — open bug [#58942](https://github.com/anthropics/claude-code/issues/58942) (has repro); `@-imports` không expand trong **Agent-tool spawned** sub-agent context — bug [#58940](https://github.com/anthropics/claude-code/issues/58940) (scope confirmed chỉ Agent-tool, chưa verify context:fork/--agent); rules/*.md cũng không load. **→ Luôn inject convention cần thiết vào prompt hoặc dùng `skills` field**, không giả định CLAUDE.md/rules có sẵn trong Agent-tool spawned sub-agent. Hai cơ chế fork: (1) `CLAUDE_CODE_FORK_SUBAGENT=1` (env var) = fork kế thừa toàn bộ history + system prompt + tools. (2) `context: fork` (skill frontmatter) = chạy isolation, **KHÔNG kế thừa history** — skill content thành prompt cho subagent; CLAUDE.md vẫn load.
- **Background subagent** auto-deny mọi tool call chưa được grant trong session hiện tại (*"auto-deny any tool call that would otherwise prompt"*). Nếu cần ask clarifying questions, tool call đó fail nhưng subagent vẫn tiếp tục. Kết quả unexpected (ít findings, empty output) → có thể do tool bị deny silently. Retry foreground để có permission prompts đầy đủ.
- Consolidate output từ nhiều subagent → **đếm findings mỗi subagent** trước (tự đếm, không tin self-count), ghi tổng expected. Nếu consolidated report ít hơn → liệt kê rõ finding nào bị drop + lý do. KHÔNG drop ngầm. Hai subagent report cùng finding nhưng severity khác → lấy severity **cao hơn**. Finding partially valid → giữ phần đúng, ghi rõ phần sai.
- Audit/review spec thay đổi giữa chừng → **re-dispatch** subagent với spec mới. KHÔNG re-evaluate findings cũ từ memory — findings cũ chạy theo spec cũ, không đại diện cho spec mới.
- Subagent có thể **miss content** khi file dài hoặc task quá nhiều (fetch URLs + đọc files + evaluate + report cùng lúc). Không tin coverage rating tuyệt đối — subagent báo "not covered" → **grep verify trước khi chấp nhận**. Giới hạn scope: mỗi subagent ≤10 files hoặc ≤3 complex tasks đồng thời *(heuristic — không trong docs Anthropic)*.
- **Startup content** (CLAUDE.md, memory, environment info — loaded đầu session) ≠ disk state hiện tại. Disk changes trong session không tự reflect vào startup content. Sau `/compact`: **project-root CLAUDE.md** và **auto memory** được re-inject từ disk ✅, nhưng **nested CLAUDE.md trong subdirectories** và **path-scoped rules** thì **không** — lost cho đến khi đọc file trong thư mục đó. Ảnh hưởng **cả subagent lẫn lead agent**. Khi consolidate findings hoặc so sánh file → luôn dùng Read/Grep từ disk, KHÔNG dựa vào nội dung đã load trong context.
- **Resume subagent** (thay vì spawn mới): ask Claude tự nhiên ("Continue that code review") hoặc gọi `SendMessage` trực tiếp — cả 2 đều dùng `SendMessage` tool internally, đều cần `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Sub-agent giữ nguyên full conversation history + tool calls. Dùng khi task cần nhiều vòng lặp hoặc sub-agent đã tích lũy context quan trọng.
- **Sub-agents KHÔNG thể spawn sub-agents khác** — nesting bị chặn hoàn toàn. Nếu cần delegation lồng nhau → dùng Skills hoặc chain sub-agents từ main conversation.
- **Persistent memory cho subagent**: field `memory: user|project|local` trong frontmatter. Paths: `user` → `~/.claude/agent-memory/<name>/`; `project` → `.claude/agent-memory/<name>/`; `local` → `.claude/agent-memory-local/<name>/`. Dùng khi muốn sub-agent tích lũy knowledge (patterns, architecture decisions) qua nhiều session. Khác với main agent memory — đây là memory riêng của từng sub-agent type.

## Self-review bias

- Sau batch fixes (>5 edits) → dispatch **fresh subagent** review changes thay vì tự verify. Tự fix → tự review = bias (session này đã chứng minh: tự verify bằng grep miss 5 regressions, fresh subagent bắt được).
- Fresh subagent KHÔNG nhận context về intent sửa — chỉ nhận file paths + instruction "review for correctness". Đây là feature, không phải bug: independent review cần independent context.

## Batch edits

- Sau khi edit → verify **nội dung thay thế** đúng, không chỉ confirm nội dung cũ đã biến mất. Grep "pattern cũ removed" ≠ "pattern mới correct". Đặc biệt với factual claims (version, threshold, URL) → WebFetch verify source trước khi apply.
- Sửa claim xuất hiện ở **nhiều file** → grep claim đó across toàn repo sau khi edit. Sửa file A mà file B vẫn giữ giá trị cũ = tạo inconsistency mới.
- File có thể bị **edit bởi process khác** (user edit tay, hook, formatter, linter) giữa lúc edit và verify → read lại file trước khi kết luận edit thành công.
- Trước batch edit (>3 files) → đảm bảo **git clean** (commit hoặc stash WIP). Nếu edit fail giữa chừng → dùng `/rewind` hoặc `git checkout` để revert. KHÔNG để codebase ở trạng thái nửa-edit.
- Sửa **1 file** → **dùng Edit tool**, không viết Python script `open(file, 'w')` (tránh truncate). Batch op (rename N file, mass refactor) → script OK nhưng PHẢI: (1) preview list file affected, (2) backup hoặc git stash trước, (3) dry-run flag nếu có.

## Tool output reliability

- Output bị **truncate** (Read `limit`, Bash timeout, WebFetch summary) → không đủ để kết luận. Expand/retry trước khi confirm. Đặc biệt: Read file lớn mà không thấy pattern → chưa chắc không có, có thể nằm ngoài range đã đọc.
- WebFetch **output không reliable để verify** khi: cross-host redirect (không tự động follow — trả về redirect message với target URL, cần WebFetch lần 2), **15-min cache** (fetch lại cùng URL không có nghĩa là content mới), large page truncation. Ngoài ra: 404/timeout/auth-required là standard HTTP failures *(practical, không trong docs)*. Thử URL khác hoặc ghi rõ "không verify được, cần user confirm".
- WebFetch summary được tạo bởi **small model trong context riêng** → có thể sai factual. Data dùng để ra quyết định quan trọng (version, threshold, security advisory) → cross-check bằng URL thứ hai hoặc `Bash(curl)` nếu cần raw content.
- Verify qua **MCP tools** (GitHub MCP, database MCP...) → cùng nguyên tắc với subagent: output có impact → cross-check bằng tool khác. MCP server do user cấu hình (third-party, không qua Anthropic audit), có thể trả data stale hoặc không tin cậy.

## Git state

- Trước khi làm git operations → **verify branch** bằng `git branch --show-current`. Startup context phản ánh git state lúc SessionStart hook chạy gần nhất — hook fires khi: new session, `/resume`, `/clear`, hoặc `/compact` (source: `"startup"` / `"resume"` / `"clear"` / `"compact"`). Stale nếu git state thay đổi sau đó mà chưa trigger lại.
- Kiểm tra file trên branch khác → dùng `git ls-tree`/`git show branch:path`, **KHÔNG** dùng `ls`/`find` (working tree chỉ phản ánh branch hiện tại).
- Section này chỉ áp dụng khi project có **git repo**. Project không có git → skip, dùng file system trực tiếp.

## External dependencies

- Dùng GitHub Action / package bên ngoài → **verify tồn tại** (WebFetch check repo/tag) trước khi commit. WebFetch fail khi verify → áp dụng "Tool output reliability": thử URL khác hoặc ghi cần user confirm.
- Dep tồn tại nhưng **version mismatch** → cảnh báo user, không tự downgrade/upgrade.
