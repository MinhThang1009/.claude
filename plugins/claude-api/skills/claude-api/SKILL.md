---
name: claude-api
description: "Build, debug, and optimize Claude API / Anthropic SDK apps. Apps built with this skill should include prompt caching. Also handles migrating existing Claude API code between Claude model versions (4.5 → 4.6, 4.6 → 4.7, retired-model replacements). TRIGGER when: code imports `anthropic`/`@anthropic-ai/sdk`; user asks for the Claude API, Anthropic SDK, or Managed Agents; user adds/modifies/tunes a Claude feature (caching, thinking, compaction, tool use, batch, files, citations, memory) or model (Opus/Sonnet/Haiku) in a file; questions about prompt caching / cache hit rate in an Anthropic SDK project. SKIP: file imports `openai`/other-provider SDK, filename like `*-openai.py`/`*-generic.py`, provider-neutral code, general programming/ML."
license: Complete terms in LICENSE.txt
---

# Xây dựng ứng dụng LLM với Claude

Skill này giúp bạn xây dựng ứng dụng LLM dựa trên Claude. Chọn surface phù hợp với nhu cầu, phát hiện ngôn ngữ project, sau đó đọc tài liệu language-specific tương ứng.

## Trước khi bắt đầu

Scan file mục tiêu (hoặc nếu không có file mục tiêu, scan prompt và project) để tìm marker của non-Anthropic provider — `import openai`, `from openai`, `langchain_openai`, `OpenAI(`, `gpt-4`, `gpt-5`, tên file kiểu `agent-openai.py` hay `*-generic.py`, hoặc bất kỳ instruction tường minh nào yêu cầu giữ code provider-neutral. Nếu tìm thấy bất kỳ marker nào, dừng lại và nói với user rằng skill này produce code Claude/Anthropic SDK; hỏi xem họ muốn chuyển file sang Claude hay muốn implementation non-Claude. Không edit file non-Anthropic với call Anthropic SDK.

## Yêu cầu Output

Khi user yêu cầu thêm, sửa, hoặc implement một feature Claude, code của bạn phải gọi Claude qua một trong các cách:

1. **Official Anthropic SDK** cho ngôn ngữ của project (`anthropic`, `@anthropic-ai/sdk`, `com.anthropic.*`, v.v.). Đây là mặc định bất cứ khi nào SDK được support tồn tại cho project.
2. **Raw HTTP** (`curl`, `requests`, `fetch`, `httpx`, v.v.) — chỉ khi user yêu cầu tường minh cURL/REST/raw HTTP, project là shell/cURL project, hoặc ngôn ngữ không có SDK chính thức.

Không bao giờ trộn cả hai — đừng với tay tới `requests`/`fetch` trong Python hay TypeScript project chỉ vì nó có vẻ nhẹ hơn. Không bao giờ fall back sang OpenAI-compatible shim.

**Không bao giờ đoán cách dùng SDK.** Tên function, tên class, namespace, method signature, và import path PHẢI đến từ tài liệu tường minh — hoặc từ file `{lang}/` trong skill này hoặc từ official SDK repo / link tài liệu liệt kê trong `shared/live-sources.md`. Nếu binding bạn cần không được document tường minh trong skill files, WebFetch SDK repo liên quan từ `shared/live-sources.md` trước khi viết code. Không suy đoán Ruby/Java/Go/PHP/C# API từ shape cURL hoặc từ SDK của ngôn ngữ khác.

## Mặc định

Trừ khi user yêu cầu khác:

Về Claude model version, hãy dùng Claude Opus 4.7, truy cập qua exact model string `claude-opus-4-7`. Mặc định dùng adaptive thinking (`thinking: {type: "adaptive"}`) cho bất cứ thứ gì hơi phức tạp. Và cuối cùng, mặc định stream cho bất kỳ request nào có thể có long input, long output, hoặc `max_tokens` cao — nó tránh bị HTTP request timeout. Dùng helper `.get_final_message()` / `.finalMessage()` của SDK để lấy complete response nếu bạn không cần handle individual stream event.

---

## Subcommands

Nếu User Request ở cuối prompt này là một bare subcommand string (không có prose), search mọi bảng **Subcommands** trong document này — bao gồm cả bảng trong các section append phía dưới — và follow theo Action column tương ứng trực tiếp. Cách này cho user invoke flow cụ thể qua `/claude-api <subcommand>`. Nếu không bảng nào trong document match, treat request như prose thông thường.


---

## Phát hiện ngôn ngữ

Trước khi đọc code example, xác định user đang work với ngôn ngữ nào:

1. **Nhìn vào file của project** để infer ngôn ngữ:

   - `*.py`, `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` → **Python** — đọc từ `python/`
   - `*.ts`, `*.tsx`, `package.json`, `tsconfig.json` → **TypeScript** — đọc từ `typescript/`
   - `*.js`, `*.jsx` (không có file `.ts`) → **TypeScript** — JS dùng cùng SDK, đọc từ `typescript/`
   - `*.java`, `pom.xml`, `build.gradle` → **Java** — đọc từ `java/`
   - `*.kt`, `*.kts`, `build.gradle.kts` → **Java** — Kotlin dùng Java SDK, đọc từ `java/`
   - `*.scala`, `build.sbt` → **Java** — Scala dùng Java SDK, đọc từ `java/`
   - `*.go`, `go.mod` → **Go** — đọc từ `go/`
   - `*.rb`, `Gemfile` → **Ruby** — đọc từ `ruby/`
   - `*.cs`, `*.csproj` → **C#** — đọc từ `csharp/`
   - `*.php`, `composer.json` → **PHP** — đọc từ `php/`

2. **Nếu detect nhiều ngôn ngữ** (ví dụ: cả Python và TypeScript files):

   - Kiểm tra file hoặc câu hỏi hiện tại của user liên quan tới ngôn ngữ nào
   - Nếu vẫn ambiguous, hỏi: "I detected both Python and TypeScript files. Which language are you using for the Claude API integration?"

3. **Nếu không infer được ngôn ngữ** (project rỗng, không có source file, hoặc unsupported language):

   - Dùng AskUserQuestion với option: Python, TypeScript, Java, Go, Ruby, cURL/raw HTTP, C#, PHP
   - Nếu AskUserQuestion không khả dụng, default sang Python example và lưu ý: "Showing Python examples. Let me know if you need a different language."

4. **Nếu detect ngôn ngữ unsupported** (Rust, Swift, C++, Elixir, v.v.):

   - Đề xuất cURL/raw HTTP example từ `curl/` và lưu ý rằng community SDK có thể tồn tại
   - Đề nghị show Python hoặc TypeScript example như reference implementation

5. **Nếu user cần cURL/raw HTTP example**, đọc từ `curl/`.

### Hỗ trợ feature theo ngôn ngữ

| Language   | Tool Runner | Managed Agents | Notes                                 |
| ---------- | ----------- | -------------- | ------------------------------------- |
| Python     | Yes (beta)  | Yes (beta)     | Full support — `@beta_tool` decorator |
| TypeScript | Yes (beta)  | Yes (beta)     | Full support — `betaZodTool` + Zod    |
| Java       | Yes (beta)  | Yes (beta)     | Beta tool use with annotated classes  |
| Go         | Yes (beta)  | Yes (beta)     | `BetaToolRunner` in `toolrunner` pkg  |
| Ruby       | Yes (beta)  | Yes (beta)     | `BaseTool` + `tool_runner` in beta    |
| C#         | No          | No             | Official SDK                          |
| PHP        | Yes (beta)  | Yes (beta)     | `BetaRunnableTool` + `toolRunner()`   |
| cURL       | N/A         | Yes (beta)     | Raw HTTP, no SDK features             |

> **Managed Agents code examples**: README dedicated language-specific được cung cấp cho Python, TypeScript, Go, Ruby, PHP, Java, và cURL (`{lang}/managed-agents/README.md`, `curl/managed-agents.md`). Đọc README của ngôn ngữ bạn dùng cùng các file concept language-agnostic `shared/managed-agents-*.md`. **Agent là persistent — tạo một lần, reference bằng ID.** Lưu agent ID return từ `agents.create` và pass nó vào mọi `sessions.create` tiếp theo; không gọi `agents.create` trong request path. Anthropic CLI là một cách tiện lợi để tạo agent và environment từ YAML version-controlled — URL của nó nằm trong `shared/live-sources.md`. Nếu binding bạn cần không có trong README, WebFetch entry liên quan từ `shared/live-sources.md` thay vì đoán. C# hiện chưa support Managed Agents; dùng cURL-style raw HTTP request gọi vào API.

---

## Nên dùng Surface nào?

> **Bắt đầu đơn giản.** Mặc định dùng tier đơn giản nhất đáp ứng được nhu cầu. Single API call và workflow handle phần lớn use case — chỉ chọn agent khi task thực sự yêu cầu open-ended, model-driven exploration.

| Use Case                                        | Tier            | Surface đề xuất           | Lý do                                                          |
| ----------------------------------------------- | --------------- | ------------------------- | ------------------------------------------------------------ |
| Classification, summarization, extraction, Q&A  | Single LLM call | **Claude API**            | Một request, một response                                    |
| Batch processing hoặc embedding                  | Single LLM call | **Claude API**            | Endpoint chuyên dụng                                        |
| Multi-step pipeline với code-controlled logic | Workflow        | **Claude API + tool use** | Bạn orchestrate loop                                     |
| Custom agent với tool của riêng bạn                | Agent           | **Claude API + tool use** | Linh hoạt tối đa                                          |
| Server-managed stateful agent với workspace    | Agent           | **Managed Agents**        | Anthropic chạy loop và host tool-execution sandbox |
| Agent config persisted, versioned                 | Agent           | **Managed Agents**        | Agent là stored object; session pin vào version         |
| Long-running multi-turn agent với file mount  | Agent           | **Managed Agents**        | Per-session container, SSE event stream, Skills + MCP       |

> **Lưu ý:** Managed Agents là lựa chọn đúng khi bạn muốn Anthropic chạy agent loop *và* host container nơi tool execute — file ops, bash, code execution đều chạy trong per-session workspace. Nếu bạn muốn tự host compute hoặc chạy custom tool runtime của riêng mình, Claude API + tool use là lựa chọn đúng — dùng tool runner để loop handling tự động, hoặc manual loop cho fine-grained control (approval gate, custom logging, conditional execution).

> **Third-party provider (Amazon Bedrock, Google Vertex AI, Microsoft Foundry):** Managed Agents **không khả dụng** trên Bedrock, Vertex, hay Foundry. Nếu bạn deploy qua bất kỳ third-party provider nào, dùng **Claude API + tool use** cho mọi use case — kể cả case mà Managed Agents lẽ ra là surface đề xuất.

### Decision Tree

```
Ứng dụng của bạn cần gì?

0. Bạn deploy qua Amazon Bedrock, Google Vertex AI, hoặc Microsoft Foundry?
   └── Yes → Claude API (+ tool use cho agent) — Managed Agents chỉ 1P.
   No → tiếp tục.

1. Single LLM call (classification, summarization, extraction, Q&A)
   └── Claude API — một request, một response

2. Bạn muốn Anthropic chạy agent loop và host per-session
   container nơi Claude execute tool (bash, file ops, code)?
   └── Yes → Managed Agents — server-managed session, agent config persisted,
       SSE event stream, Skills + MCP, file mount.
       Ví dụ: "stateful coding agent với workspace per task",
                 "long-running research agent stream event lên UI",
                 "agent với config persisted, versioned dùng across many session"

3. Workflow (multi-step, code-orchestrated, với tool của riêng bạn)
   └── Claude API với tool use — bạn control loop

4. Open-ended agent (model tự quyết định trajectory, tool riêng, bạn host compute)
   └── Claude API agentic loop (linh hoạt tối đa)
```

### Có nên build Agent không?

Trước khi chọn agent tier, check cả 4 tiêu chí:

- **Complexity** — Task có multi-step và khó specify đầy đủ trước không? (vd: "turn this design doc into a PR" vs. "extract the title from this PDF")
- **Value** — Outcome có justify được higher cost và latency không?
- **Viability** — Claude có capable với task type này không?
- **Cost of error** — Lỗi có catch và recover được không? (test, review, rollback)

Nếu trả lời "no" cho bất kỳ tiêu chí nào, ở lại tier đơn giản hơn (single call hoặc workflow).

---

## Architecture

Mọi thứ đi qua `POST /v1/messages`. Tool và output constraint là feature của single endpoint này — không phải API riêng.

**User-defined tools** — Bạn define tool (qua decorator, Zod schema, hoặc raw JSON), và tool runner của SDK handle việc gọi API, execute function của bạn, và loop cho tới khi Claude xong. Để full control, bạn có thể viết loop bằng tay.

**Server-side tools** — Tool Anthropic-hosted chạy trên infrastructure của Anthropic. Code execution là fully server-side (declare nó trong `tools`, Claude tự chạy code). Computer use có thể server-hosted hoặc self-hosted.

**Structured outputs** — Constrain format response của Messages API (`output_config.format`) và/hoặc tool parameter validation (`strict: true`). Approach đề xuất là `client.messages.parse()` — tự động validate response theo schema của bạn. Lưu ý: parameter `output_format` cũ đã deprecated; dùng `output_config: {format: {...}}` trên `messages.create()`.

**Supporting endpoint** — Batches (`POST /v1/messages/batches`), Files (`POST /v1/files`), Token Counting, và Models (`GET /v1/models`, `GET /v1/models/{id}` — live capability/context-window discovery) feed vào hoặc support Messages API request.

---

## Current Models (cached: 2026-04-15)

| Model             | Model ID            | Context        | Input $/1M | Output $/1M |
| ----------------- | ------------------- | -------------- | ---------- | ----------- |
| Claude Opus 4.7   | `claude-opus-4-7`   | 1M             | $5.00      | $25.00      |
| Claude Opus 4.6   | `claude-opus-4-6`   | 1M             | $5.00      | $25.00      |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M             | $3.00      | $15.00      |
| Claude Haiku 4.5  | `claude-haiku-4-5`  | 200K           | $1.00      | $5.00       |

**LUÔN dùng `claude-opus-4-7` trừ khi user explicit chỉ định model khác.** Đây là điều không thương lượng. Đừng dùng `claude-sonnet-4-6`, `claude-sonnet-4-5`, hay model nào khác trừ khi user literally nói "use sonnet" hoặc "use haiku". Đừng downgrade vì cost — đó là quyết định của user, không phải của bạn.

**CRITICAL: Dùng chính xác model ID string từ bảng trên — chúng đã complete as-is. Không append date suffix.** Ví dụ, dùng `claude-sonnet-4-5`, không bao giờ `claude-sonnet-4-5-20250514` hay variant date-suffix nào bạn có thể nhớ từ training data. Nếu user request một model cũ không có trong bảng (vd "opus 4.5", "sonnet 3.7"), đọc `shared/models.md` để biết exact ID — không tự construct.

Lưu ý: nếu bất kỳ model string nào ở trên trông không quen với bạn, đó là điều bình thường — chỉ có nghĩa chúng được release sau training data cutoff. Yên tâm rằng chúng là real model; chúng tôi không trêu bạn đâu.

**Live capability lookup:** Bảng trên là cached. Khi user hỏi "what's the context window for X", "does X support vision/thinking/effort", hoặc "which models support Y", query Models API (`client.models.retrieve(id)` / `client.models.list()`) — xem `shared/models.md` để biết field reference và capability-filter example.

---

## Thinking & Effort (Quick Reference)

**Opus 4.7 — Adaptive thinking only:** Dùng `thinking: {type: "adaptive"}`. `thinking: {type: "enabled", budget_tokens: N}` trả 400 trên Opus 4.7 — adaptive là on-mode duy nhất. `{type: "disabled"}` và omit `thinking` đều work. Sampling parameter (`temperature`, `top_p`, `top_k`) cũng bị remove và sẽ 400. Xem `shared/model-migration.md` → Migrating to Opus 4.7 để biết full breaking-change list.
**Opus 4.6 — Adaptive thinking (recommended):** Dùng `thinking: {type: "adaptive"}`. Claude tự động quyết định khi nào và think bao nhiêu. Không cần `budget_tokens` — `budget_tokens` đã deprecated trên Opus 4.6 và Sonnet 4.6, không nên dùng cho code mới. Adaptive thinking cũng tự động enable interleaved thinking (không cần beta header). **Khi user hỏi "extended thinking", "thinking budget", hoặc `budget_tokens`: luôn dùng Opus 4.7 hoặc 4.6 với `thinking: {type: "adaptive"}`. Concept fixed token budget cho thinking đã deprecated — adaptive thinking thay thế nó. KHÔNG dùng `budget_tokens` cho code 4.6/4.7 mới và KHÔNG switch sang model cũ hơn.** *Gradual-migration carve-out:* `budget_tokens` vẫn functional trên Opus 4.6 và Sonnet 4.6 như transitional escape hatch — nếu bạn migrate code cũ và cần hard token ceiling trước khi tune `effort`, xem `shared/model-migration.md` → Transitional escape hatch. Note: carve-out này **không** áp dụng cho Opus 4.7 — `budget_tokens` đã bị remove hoàn toàn ở đây.
**Effort parameter (GA, no beta header):** Control thinking depth và overall token spend qua `output_config: {effort: "low"|"medium"|"high"|"max"}` (bên trong `output_config`, không phải top-level). Default là `high` (tương đương omit). `max` chỉ dành cho Opus-tier (Opus 4.6 trở về sau — không Sonnet hay Haiku). Opus 4.7 thêm `"xhigh"` (giữa `high` và `max`) — setting tốt nhất cho hầu hết coding và agentic use case trên 4.7, và là default trong Claude Code; dùng tối thiểu `high` cho hầu hết intelligence-sensitive work. Work trên Opus 4.5, Opus 4.6, Opus 4.7, và Sonnet 4.6. Sẽ error trên Sonnet 4.5 / Haiku 4.5. Trên Opus 4.7, effort quan trọng hơn bất kỳ Opus nào trước đó — re-tune nó khi migrate. Combine với adaptive thinking để có trade-off cost-quality tốt nhất. Effort thấp hơn nghĩa là fewer và more-consolidated tool call, ít preamble hơn, và terser confirmation — `high` thường là sweet spot balance giữa quality và token efficiency; dùng `max` khi correctness quan trọng hơn cost; dùng `low` cho subagent hoặc task đơn giản.

**Opus 4.7 — thinking content omit by default:** Block `thinking` vẫn stream nhưng text của nó rỗng trừ khi bạn opt in với `thinking: {type: "adaptive", display: "summarized"}` (default là `"omitted"`). Silent change — không error. Nếu bạn stream reasoning tới user, default sẽ trông như long pause trước output; set `"summarized"` để restore visible progress.

**Task Budgets (beta, Opus 4.7):** `output_config: {task_budget: {type: "tokens", total: N}}` cho model biết nó có bao nhiêu token cho full agentic loop — nó thấy running countdown và tự self-moderate (minimum 20,000; beta header `task-budgets-2026-03-13`). Khác với `max_tokens`, là enforced per-response ceiling mà model không aware. Xem `shared/model-migration.md` → Task Budgets.

**Sonnet 4.6:** Support adaptive thinking (`thinking: {type: "adaptive"}`). `budget_tokens` đã deprecated trên Sonnet 4.6 — dùng adaptive thinking thay thế.

**Older models (chỉ khi explicit request):** Nếu user request cụ thể Sonnet 4.5 hoặc model cũ khác, dùng `thinking: {type: "enabled", budget_tokens: N}`. `budget_tokens` phải nhỏ hơn `max_tokens` (minimum 1024). Đừng bao giờ chọn model cũ chỉ vì user nhắc `budget_tokens` — dùng Opus 4.7 với adaptive thinking thay thế.

---

## Compaction (Quick Reference)

**Beta, Opus 4.7, Opus 4.6, và Sonnet 4.6.** Cho long-running conversation có thể vượt quá 1M context window, enable server-side compaction. API tự động summarize earlier context khi approach trigger threshold (default: 150K token). Cần beta header `compact-2026-01-12`.

**Critical:** Append `response.content` (không chỉ text) back vào messages mỗi turn. Compaction block trong response phải được preserve — API dùng chúng để thay thế compacted history trên request tiếp theo. Extract chỉ text string và append cái đó sẽ silently lose compaction state.

Xem `{lang}/claude-api/README.md` (Compaction section) để có code example. Full docs qua WebFetch trong `shared/live-sources.md`.

---

## Prompt Caching (Quick Reference)

**Prefix match.** Bất kỳ byte change nào ở prefix sẽ invalidate mọi thứ sau nó. Render order là `tools` → `system` → `messages`. Giữ stable content đầu tiên (frozen system prompt, deterministic tool list), đặt volatile content (timestamp, per-request ID, varying question) sau `cache_control` breakpoint cuối.

**Top-level auto-caching** (`cache_control: {type: "ephemeral"}` trên `messages.create()`) là option đơn giản nhất khi bạn không cần fine-grained placement. Max 4 breakpoint per request. Minimum cacheable prefix là ~1024 token — prefix ngắn hơn silently không cache.

**Verify với `usage.cache_read_input_tokens`** — nếu nó zero qua nhiều request lặp lại, có silent invalidator đang hoạt động (`datetime.now()` trong system prompt, unsorted JSON, tool set thay đổi).

Để biết placement pattern, architectural guidance, và silent-invalidator audit checklist: đọc `shared/prompt-caching.md`. Language-specific syntax: `{lang}/claude-api/README.md` (Prompt Caching section).

---

## Managed Agents (Beta)

**Managed Agents** là surface thứ ba: server-managed stateful agent với Anthropic-hosted tool execution. Bạn tạo Agent config persisted, versioned (`POST /v1/agents`), sau đó start Session reference nó. Mỗi session provision một container như workspace của agent — bash, file ops, và code execution chạy ở đó; agent loop tự chạy trên orchestration layer của Anthropic và act lên container qua tool. Session stream event; bạn gửi message và tool result back.

**Managed Agents là first-party only.** Không khả dụng trên Amazon Bedrock, Google Vertex AI, hay Microsoft Foundry. Cho agent trên third-party provider, dùng Claude API + tool use.

**Mandatory flow:** Agent (một lần) → Session (mỗi run). `model`/`system`/`tools` ở trên agent, không bao giờ trên session. Xem `shared/managed-agents-overview.md` để có full reading guide, beta header, và pitfall.

**Beta header:** `managed-agents-2026-04-01` — SDK set nó tự động cho mọi call `client.beta.{agents,environments,sessions,vaults,memory_stores}.*`. Skills API dùng `skills-2025-10-02` và Files API dùng `files-api-2025-04-14`, nhưng bạn không cần explicit pass chúng cho endpoint khác `/v1/skills` và `/v1/files`.

**Subcommands** — invoke trực tiếp với `/claude-api <subcommand>`:

| Subcommand | Action |
|---|---|
| `managed-agents-onboard` | Walk user qua việc setup Managed Agent từ đầu. **Đọc `shared/managed-agents-onboarding.md` ngay lập tức** và follow interview script của nó: mental model → know-or-explore branch → template config → session setup → emit code. Không summarize — chạy interview. |

**Reading guide:** Bắt đầu với `shared/managed-agents-overview.md`, sau đó các file `shared/managed-agents-*.md` theo chủ đề (core, environments, tools, events, outcomes, multiagent, webhooks, memory, client-patterns, onboarding, api-reference). Cho Python, TypeScript, Go, Ruby, PHP, và Java, đọc `{lang}/managed-agents/README.md` để có code example. Cho cURL, đọc `curl/managed-agents.md`. **Agent là persistent — tạo một lần, reference bằng ID.** Lưu agent ID return từ `agents.create` và pass nó vào mọi `sessions.create` tiếp theo; không gọi `agents.create` trong request path. Anthropic CLI là một cách tiện lợi để tạo agent và environment từ YAML version-controlled (URL trong `shared/live-sources.md`). Nếu binding bạn cần không có trong language README, WebFetch entry liên quan từ `shared/live-sources.md` thay vì đoán. C# hiện chưa support Managed Agents; dùng raw HTTP từ `curl/managed-agents.md` như reference.

**Khi user muốn setup Managed Agent từ đầu** (vd "how do I get started", "walk me through creating one", "set up a new agent"): đọc `shared/managed-agents-onboarding.md` và chạy interview của nó — cùng flow với subcommand `managed-agents-onboard`.

**Khi user hỏi "how do I write the client code for X":** với tay tới `shared/managed-agents-client-patterns.md` — cover lossless stream reconnect, `processed_at` queued/processed gate, interrupt, `tool_confirmation` round-trip, idle/terminated break gate đúng, post-idle status race, stream-first ordering, file-mount gotcha, giữ credential host-side qua custom tool, v.v.

---

## Reading Guide

Sau khi detect ngôn ngữ, đọc các file liên quan tùy theo nhu cầu user:

### Quick Task Reference

**Single text classification/summarization/extraction/Q&A:**
→ Chỉ đọc `{lang}/claude-api/README.md`

**Chat UI hoặc real-time response display:**
→ Đọc `{lang}/claude-api/README.md` + `{lang}/claude-api/streaming.md`

**Long-running conversation (có thể vượt context window):**
→ Đọc `{lang}/claude-api/README.md` — xem Compaction section
**Migrate sang newer model (Opus 4.7 / Opus 4.6 / Sonnet 4.6) hoặc thay retired model:**
→ Đọc `shared/model-migration.md`
**Prompt caching / optimize caching / "why is my cache hit rate low":**
→ Đọc `shared/prompt-caching.md` + `{lang}/claude-api/README.md` (Prompt Caching section)

**Function calling / tool use / agent:**
→ Đọc `{lang}/claude-api/README.md` + `shared/tool-use-concepts.md` + `{lang}/claude-api/tool-use.md`

**Agent design (tool surface, context management, caching strategy):**
→ Đọc `shared/agent-design.md`

**Batch processing (non-latency-sensitive):**
→ Đọc `{lang}/claude-api/README.md` + `{lang}/claude-api/batches.md`

**File upload across multiple request:**
→ Đọc `{lang}/claude-api/README.md` + `{lang}/claude-api/files-api.md`

**Managed Agents (server-managed stateful agent với workspace):**
→ Đọc `shared/managed-agents-overview.md` + các file `shared/managed-agents-*.md` còn lại. Cho Python, TypeScript, Go, Ruby, PHP, và Java, đọc `{lang}/managed-agents/README.md` để có code example. Cho cURL, đọc `curl/managed-agents.md`. **Agent là persistent — tạo một lần, reference bằng ID.** Lưu agent ID return từ `agents.create` và pass nó vào mọi `sessions.create` tiếp theo; không gọi `agents.create` trong request path. Anthropic CLI là cách tiện lợi để tạo agent và environment từ YAML version-controlled (URL trong `shared/live-sources.md`). Nếu binding bạn cần không có trong language README, WebFetch entry liên quan từ `shared/live-sources.md` thay vì đoán. C# hiện chưa support Managed Agents — dùng raw HTTP từ `curl/managed-agents.md` như reference.

### Claude API (Full File Reference)

Đọc **language-specific Claude API folder** (`{language}/claude-api/`):

1. **`{language}/claude-api/README.md`** — **Đọc cái này trước.** Installation, quick start, common pattern, error handling.
2. **`shared/tool-use-concepts.md`** — Đọc khi user cần function calling, code execution, memory, hoặc structured output. Cover conceptual foundation.
3. **`shared/agent-design.md`** — Đọc khi design agent: bash vs. dedicated tool, programmatic tool calling, tool search/skills, context editing vs. compaction vs. memory, caching principle.
4. **`{language}/claude-api/tool-use.md`** — Đọc cho language-specific tool use code example (tool runner, manual loop, code execution, memory, structured output).
5. **`{language}/claude-api/streaming.md`** — Đọc khi build chat UI hoặc interface display response incremental.
6. **`{language}/claude-api/batches.md`** — Đọc khi process nhiều request offline (không latency-sensitive). Chạy asynchronously với 50% cost.
7. **`{language}/claude-api/files-api.md`** — Đọc khi gửi cùng file across multiple request mà không re-upload.
8. **`shared/prompt-caching.md`** — Đọc khi thêm hoặc optimize prompt caching. Cover prefix-stability design, breakpoint placement, và anti-pattern silently invalidate cache.
9. **`shared/error-codes.md`** — Đọc khi debug HTTP error hoặc implement error handling.
10. **`shared/model-migration.md`** — Đọc khi upgrade sang model mới hơn, thay retired model, hoặc translate pattern `budget_tokens` / prefill sang API hiện tại.
11. **`shared/live-sources.md`** — URL WebFetch để fetch official documentation mới nhất.

> **Lưu ý:** Cho Java, Go, Ruby, C#, PHP, và cURL — mỗi cái có một file cover hết basic. Đọc file đó cộng với `shared/tool-use-concepts.md` và `shared/error-codes.md` khi cần.

> **Lưu ý:** Để có Managed Agents file reference, xem section `## Managed Agents (Beta)` ở trên — nó liệt kê mọi file `shared/managed-agents-*.md` và language-specific README.

---

## Khi nào dùng WebFetch

Dùng WebFetch để lấy documentation mới nhất khi:

- User hỏi "latest" hoặc "current" information
- Cached data có vẻ không chính xác
- User hỏi về feature chưa được cover ở đây

URL documentation live nằm trong `shared/live-sources.md`.

## Common Pitfalls

- Đừng truncate input khi pass file hoặc content vào API. Nếu content quá dài để fit vào context window, notify user và discuss option (chunking, summarization, v.v.) thay vì silently truncate.
- **Opus 4.7 thinking:** Adaptive only. `thinking: {type: "enabled", budget_tokens: N}` trả 400 trên Opus 4.7 — `budget_tokens` bị remove hoàn toàn ở đây (cùng với `temperature`, `top_p`, `top_k`). Dùng `thinking: {type: "adaptive"}`.
- **Opus 4.6 / Sonnet 4.6 thinking:** Dùng `thinking: {type: "adaptive"}` — KHÔNG dùng `budget_tokens` cho code 4.6 mới (deprecated trên cả Opus 4.6 và Sonnet 4.6; để migrate dần code hiện có, xem transitional escape hatch trong `shared/model-migration.md` — note carve-out này không áp dụng cho Opus 4.7). Cho model cũ hơn, `budget_tokens` phải nhỏ hơn `max_tokens` (minimum 1024). Sẽ throw error nếu sai.
- **4.6/4.7 family prefill removed:** Assistant message prefill (last-assistant-turn prefill) trả 400 error trên Opus 4.6, Opus 4.7, và Sonnet 4.6. Dùng structured output (`output_config.format`) hoặc system prompt instruction để control response format thay vì prefill.
- **Confirm migration scope trước khi edit:** Khi user yêu cầu migrate code sang newer Claude model mà không name một file, directory, hay file list cụ thể, **hỏi scope nào áp dụng trước** — toàn bộ working directory, subdirectory cụ thể, hay set file cụ thể. Đừng start edit cho tới khi user confirm. Phrase imperative kiểu "migrate my codebase", "move my project to X", "upgrade to Sonnet 4.6", hoặc bare "migrate to Opus 4.7" **vẫn ambiguous** — chúng nói bạn làm gì nhưng không nói ở đâu, nên hỏi. Proceed mà không hỏi chỉ khi prompt name một file cụ thể, directory cụ thể, hay file list tường minh ("migrate `app.py`", "migrate everything under `services/`", "update `a.py` and `b.py`"). Xem `shared/model-migration.md` Step 0.
- **`max_tokens` defaults:** Đừng lowball `max_tokens` — hit cap sẽ truncate output mid-thought và cần retry. Cho non-streaming request, default `~16000` (giữ response dưới SDK HTTP timeout). Cho streaming request, default `~64000` (timeout không phải concern, cho model room). Chỉ đi thấp hơn khi bạn có hard reason: classification (`~256`), cost cap, hoặc output ngắn có chủ đích.
- **128K output token:** Opus 4.6 và Opus 4.7 support tới 128K `max_tokens`, nhưng SDK require streaming cho value lớn vậy để tránh HTTP timeout. Dùng `.stream()` với `.get_final_message()` / `.finalMessage()`.
- **Tool call JSON parsing (4.6/4.7 family):** Opus 4.6, Opus 4.7, và Sonnet 4.6 có thể produce JSON string escaping khác nhau trong tool call `input` field (vd Unicode hoặc forward-slash escaping). Luôn parse tool input với `json.loads()` / `JSON.parse()` — đừng raw string matching trên serialized input.
- **Structured outputs (mọi model):** Dùng `output_config: {format: {...}}` thay vì parameter `output_format` deprecated trên `messages.create()`. Đây là general API change, không 4.6-specific.
- **Đừng reimplement SDK functionality:** SDK provide high-level helper — dùng chúng thay vì build từ đầu. Cụ thể: dùng `stream.finalMessage()` thay vì wrap `.on()` event trong `new Promise()`; dùng typed exception class (`Anthropic.RateLimitError`, v.v.) thay vì string-matching error message; dùng SDK type (`Anthropic.MessageParam`, `Anthropic.Tool`, `Anthropic.Message`, v.v.) thay vì redefine equivalent interface.
- **Đừng define custom type cho SDK data structure:** SDK export type cho mọi API object. Dùng `Anthropic.MessageParam` cho message, `Anthropic.Tool` cho tool definition, `Anthropic.ToolUseBlock` / `Anthropic.ToolResultBlockParam` cho tool result, `Anthropic.Message` cho response. Define `interface ChatMessage { role: string; content: unknown }` của riêng bạn duplicate cái SDK đã provide và lose type safety.
- **Report và document output:** Cho task produce report, document, hoặc visualization, code execution sandbox có `python-docx`, `python-pptx`, `matplotlib`, `pillow`, và `pypdf` pre-install. Claude có thể generate formatted file (DOCX, PDF, chart) và return chúng qua Files API — consider cái này cho "report" hoặc "document" type request thay vì plain stdout text.
