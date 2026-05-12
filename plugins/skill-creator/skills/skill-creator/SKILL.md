---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

Một skill để tạo mới và cải thiện các skills một cách iterative.

Nhìn ở cấp cao, quá trình tạo skill diễn ra như sau:

- Quyết định skill sẽ làm gì và sơ bộ sẽ làm như thế nào
- Viết draft đầu tiên của skill
- Tạo vài test prompts và chạy claude-với-skill trên chúng
- Giúp user đánh giá kết quả cả về chất lượng và định lượng
  - Trong khi các runs đang diễn ra ở background, draft một số quantitative evals nếu chưa có (nếu đã có, dùng hoặc chỉnh sửa nếu cần thay đổi gì). Sau đó giải thích chúng cho user (hoặc nếu đã có sẵn, giải thích các evals hiện có)
  - Dùng script `eval-viewer/generate_review.py` để hiển thị kết quả cho user xem, và cũng cho họ xem các quantitative metrics
- Viết lại skill dựa trên feedback từ việc user đánh giá kết quả (và nếu có lỗi rõ ràng từ quantitative benchmarks)
- Lặp lại cho đến khi hài lòng
- Mở rộng test set và thử lại ở quy mô lớn hơn

Khi dùng skill này, công việc của bạn là xác định user đang ở đâu trong quy trình này rồi nhảy vào giúp họ tiến qua các giai đoạn. Ví dụ, có thể họ nói "Tôi muốn tạo skill cho X". Bạn có thể giúp thu hẹp ý họ muốn, viết draft, viết test cases, tìm cách đánh giá, chạy tất cả prompts, và lặp lại.

Hoặc có thể họ đã có draft của skill. Trong trường hợp này bạn có thể đi thẳng vào phần eval/iterate.

Tất nhiên, hãy linh hoạt — nếu user nói "Tôi không cần chạy nhiều evaluations, cứ vibe với tôi", bạn có thể làm vậy.

Sau khi skill hoàn thành (thứ tự linh hoạt), bạn cũng có thể chạy skill description improver — chúng ta có script riêng cho việc đó — để tối ưu triggering của skill.

## Giao tiếp với user

Skill creator có thể được dùng bởi người có nhiều mức độ quen thuộc khác nhau với jargon kỹ thuật. Hiện có xu hướng sức mạnh của Claude đang truyền cảm hứng cho thợ ống nước mở terminal, cha mẹ và ông bà google "how to install npm". Mặt khác, phần lớn users có thể khá thành thạo máy tính.

Vì vậy hãy chú ý đến context cues để hiểu cách diễn đạt! Để bạn có khái niệm mặc định:

- "evaluation" và "benchmark" là borderline, nhưng OK
- Với "JSON" và "assertion", bạn cần thấy cues nghiêm túc từ user rằng họ hiểu những khái niệm đó trước khi dùng mà không giải thích

OK để giải thích thuật ngữ ngắn gọn nếu bạn không chắc, và hãy làm rõ với định nghĩa ngắn nếu bạn nghi ngờ user không hiểu.

---

## Tạo skill

### Thu thập Intent

Bắt đầu bằng cách hiểu intent của user. Conversation hiện tại có thể đã chứa workflow mà user muốn capture (ví dụ họ nói "biến cái này thành skill"). Nếu vậy, trích xuất câu trả lời từ conversation history trước — tools được dùng, trình tự các bước, corrections user đã thực hiện, input/output formats quan sát được. User có thể cần điền các gaps, và nên xác nhận trước khi tiếp tục bước tiếp theo.

1. Skill này nên cho phép Claude làm gì?
2. Khi nào skill này nên trigger? (các phrases/contexts của user)
3. Format output mong đợi là gì?
4. Chúng ta có nên thiết lập test cases để verify skill hoạt động không? Skills với outputs có thể verify khách quan (file transforms, data extraction, code generation, fixed workflow steps) được hưởng lợi từ test cases. Skills với outputs chủ quan (phong cách viết, nghệ thuật) thường không cần. Đề xuất mặc định phù hợp dựa trên loại skill, nhưng để user quyết định.

### Phỏng vấn và Nghiên cứu

Chủ động hỏi về edge cases, input/output formats, example files, success criteria, và dependencies. Đợi viết test prompts cho đến khi bạn đã rõ phần này.

Kiểm tra các MCPs có sẵn — nếu hữu ích để nghiên cứu (tìm kiếm docs, tìm skills tương tự, tra cứu best practices), nghiên cứu song song qua subagents nếu có, nếu không thì inline. Chuẩn bị context đầy đủ để giảm gánh nặng cho user.

### Viết SKILL.md

Dựa trên phỏng vấn user, điền các components này:

- **name**: Skill identifier
- **description**: Khi nào trigger, làm gì. Đây là primary triggering mechanism — bao gồm cả "skill làm gì" VÀ "contexts cụ thể khi nào dùng". Tất cả thông tin "khi nào dùng" đặt ở đây, không đặt trong body. Lưu ý: Claude hiện có xu hướng "undertrigger" skills — không dùng khi đáng lẽ nên dùng. Để khắc phục, hãy làm cho descriptions của skill hơi "pushy". Ví dụ thay vì "Cách build dashboard đơn giản nhanh để hiển thị data nội bộ Anthropic.", bạn có thể viết "Cách build dashboard đơn giản nhanh để hiển thị data nội bộ Anthropic. Nhớ dùng skill này bất cứ khi nào user đề cập dashboards, data visualization, internal metrics, hoặc muốn hiển thị bất kỳ loại company data nào, kể cả khi họ không yêu cầu rõ 'dashboard'."
- **compatibility**: Tools cần thiết, dependencies (optional, hiếm khi cần)
- **phần còn lại của skill :)**

### Hướng dẫn Viết Skill

#### Cấu trúc của một Skill

```
skill-name/
├── SKILL.md (bắt buộc)
│   ├── YAML frontmatter (name, description bắt buộc)
│   └── Hướng dẫn Markdown
└── Bundled Resources (tùy chọn)
    ├── scripts/    - Executable code cho các task deterministic/lặp lại
    ├── references/ - Docs được load vào context khi cần
    └── assets/     - Files dùng trong output (templates, icons, fonts)
```

#### Progressive Disclosure

Skills dùng hệ thống loading ba cấp:
1. **Metadata** (name + description) - Luôn trong context (~100 words)
2. **SKILL.md body** - Trong context khi skill trigger (<500 dòng lý tưởng)
3. **Bundled resources** - Khi cần (không giới hạn, scripts có thể execute mà không cần load)

Các word counts này là approximate, bạn có thể viết dài hơn nếu cần.

**Các pattern chính:**
- Giữ SKILL.md dưới 500 dòng; nếu đang tiến gần giới hạn này, thêm layer hierarchy bổ sung kèm con trỏ rõ ràng về nơi model dùng skill nên đến tiếp theo.
- Tham chiếu files rõ ràng từ SKILL.md với hướng dẫn khi nào nên đọc chúng
- Với reference files lớn (>300 dòng), bao gồm mục lục

**Tổ chức theo domain**: Khi skill hỗ trợ nhiều domains/frameworks, tổ chức theo variant:
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```
Claude chỉ đọc reference file liên quan.

#### Nguyên tắc Không Bất Ngờ

Skills không được chứa malware, exploit code, hoặc bất kỳ content nào có thể ảnh hưởng đến system security. Nội dung của skill không nên làm user bất ngờ về intent nếu được mô tả. Đừng làm theo yêu cầu tạo misleading skills hoặc skills được thiết kế để hỗ trợ unauthorized access, data exfiltration, hoặc hoạt động độc hại khác. Tuy nhiên "roleplay as an XYZ" là OK.

#### Các Pattern Viết

Ưu tiên dùng dạng imperative trong instructions.

**Định nghĩa output formats** — Bạn có thể làm như này:
```markdown
## Cấu trúc Report
LUÔN dùng template chính xác này:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Pattern Examples** — Hữu ích khi bao gồm examples. Bạn có thể format như này (nhưng nếu "Input" và "Output" có trong examples, bạn có thể muốn thay đổi một chút):
```markdown
## Format commit message
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Phong cách Viết

Cố gắng giải thích cho model tại sao mọi thứ quan trọng thay vì dùng MUST nặng tay. Dùng theory of mind và cố gắng làm skill chung chung, không cực kỳ hẹp với các ví dụ cụ thể. Bắt đầu bằng cách viết draft rồi nhìn lại với con mắt mới và cải thiện.

### Test Cases

Sau khi viết skill draft, nghĩ ra 2-3 test prompts thực tế — loại mà user thực sự sẽ nói. Chia sẻ với user: "Đây là vài test cases tôi muốn thử. Trông có vẻ đúng không, hay bạn muốn thêm?" Rồi chạy chúng.

Lưu test cases vào `evals/evals.json`. Chưa cần viết assertions — chỉ cần prompts. Bạn sẽ draft assertions ở bước tiếp theo trong khi runs đang chạy.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Task prompt của user",
      "expected_output": "Mô tả kết quả mong đợi",
      "files": []
    }
  ]
}
```

Xem `references/schemas.md` để biết full schema (bao gồm field `assertions`, sẽ thêm sau).

## Chạy và đánh giá test cases

Section này là một chuỗi liên tục — không dừng giữa chừng. KHÔNG dùng `/skill-test` hoặc skill testing nào khác.

Đặt kết quả vào `<skill-name>-workspace/` như sibling với skill directory. Trong workspace, tổ chức kết quả theo iteration (`iteration-1/`, `iteration-2/`, v.v.) và trong đó, mỗi test case có directory riêng (`eval-0/`, `eval-1/`, v.v.). Đừng tạo tất cả upfront — chỉ tạo directories khi cần.

### Bước 1: Spawn tất cả runs (with-skill VÀ baseline) trong cùng một turn

Cho mỗi test case, spawn hai subagents trong cùng turn — một với skill, một không. Quan trọng: đừng spawn with-skill runs trước rồi quay lại để lấy baselines sau. Launch tất cả cùng lúc để tất cả hoàn thành gần cùng thời điểm.

**With-skill run:**

```
Thực hiện task này:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files nếu có, hoặc "none">
- Lưu outputs vào: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs cần lưu: <những gì user quan tâm — ví dụ "file .docx", "CSV cuối cùng">
```

**Baseline run** (cùng prompt, nhưng baseline phụ thuộc vào context):
- **Tạo skill mới**: không có skill nào cả. Cùng prompt, không có skill path, lưu vào `without_skill/outputs/`.
- **Cải thiện skill có sẵn**: version cũ. Trước khi edit, snapshot skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), rồi chỉ baseline subagent đến snapshot. Lưu vào `old_skill/outputs/`.

Viết `eval_metadata.json` cho mỗi test case (assertions có thể để trống cho bây giờ). Đặt tên mô tả cho mỗi eval dựa trên những gì nó đang test — không chỉ "eval-0". Dùng tên này cho directory cũng vậy. Nếu iteration này dùng eval prompts mới hoặc được sửa đổi, tạo các files này cho mỗi eval directory mới — đừng giả định chúng carryover từ iteration trước.

```json
{
  "eval_id": 0,
  "eval_name": "tên-mô-tả-ở-đây",
  "prompt": "Task prompt của user",
  "assertions": []
}
```

### Bước 2: Trong khi runs đang chạy, draft assertions

Đừng chỉ ngồi chờ runs hoàn thành — bạn có thể dùng thời gian này hiệu quả. Draft quantitative assertions cho mỗi test case và giải thích chúng cho user. Nếu assertions đã tồn tại trong `evals/evals.json`, review và giải thích chúng kiểm tra gì.

Assertions tốt có thể verify khách quan và có tên mô tả — nên đọc rõ ràng trong benchmark viewer để ai nhìn thoáng qua kết quả cũng hiểu ngay mỗi assertion kiểm tra gì. Skills chủ quan (phong cách viết, chất lượng thiết kế) tốt hơn nên đánh giá định tính — đừng ép assertions vào những thứ cần phán đoán của con người.

Cập nhật files `eval_metadata.json` và `evals/evals.json` với assertions sau khi draft. Cũng giải thích cho user những gì họ sẽ thấy trong viewer — cả qualitative outputs và quantitative benchmark.

### Bước 3: Khi runs hoàn thành, capture timing data

Khi mỗi subagent task hoàn thành, bạn nhận notification chứa `total_tokens` và `duration_ms`. Lưu data này ngay vào `timing.json` trong run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

Đây là cơ hội duy nhất để capture data này — nó đến qua task notification và không được persist ở nơi khác. Xử lý mỗi notification khi nó đến thay vì cố gắng batch chúng.

### Bước 4: Grade, aggregate, và launch viewer

Sau khi tất cả runs xong:

1. **Grade mỗi run** — spawn grader subagent (hoặc grade inline) đọc `agents/grader.md` và đánh giá mỗi assertion theo outputs. Lưu kết quả vào `grading.json` trong mỗi run directory. Mảng expectations trong grading.json phải dùng các field `text`, `passed`, và `evidence` (không phải `name`/`met`/`details` hoặc variants khác) — viewer phụ thuộc vào tên field chính xác này. Với assertions có thể kiểm tra theo chương trình, viết và chạy script thay vì eyeballing — scripts nhanh hơn, đáng tin cậy hơn, và có thể tái sử dụng qua các iterations.

2. **Aggregate vào benchmark** — chạy aggregation script từ skill-creator directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   Tạo ra `benchmark.json` và `benchmark.md` với pass_rate, time, và tokens cho mỗi configuration, kèm mean ± stddev và delta. Nếu tạo benchmark.json thủ công, xem `references/schemas.md` để biết schema chính xác mà viewer mong đợi.
   Đặt mỗi phiên bản with_skill trước baseline counterpart của nó.

3. **Thực hiện analyst pass** — đọc benchmark data và nêu bật các patterns mà aggregate stats có thể ẩn. Xem `agents/analyzer.md` (section "Analyzing Benchmark Results") để biết cần tìm gì — những thứ như assertions luôn pass bất kể skill (non-discriminating), evals có variance cao (có thể flaky), và time/token tradeoffs.

4. **Launch viewer** với cả qualitative outputs và quantitative data:
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   Với iteration 2+, cũng truyền `--previous-workspace <workspace>/iteration-<N-1>`.

   **Môi trường Cowork / headless:** Nếu `webbrowser.open()` không có hoặc môi trường không có display, dùng `--static <output_path>` để viết standalone HTML file thay vì start server. Feedback sẽ được download như file `feedback.json` khi user click "Submit All Reviews". Sau khi download, copy `feedback.json` vào workspace directory để iteration tiếp theo sử dụng.

   Lưu ý: hãy dùng generate_review.py để tạo viewer; không cần viết custom HTML.

5. **Báo user** điều gì đó như: "Tôi đã mở kết quả trong browser của bạn. Có hai tabs — 'Outputs' cho phép bạn click qua mỗi test case và để lại feedback, 'Benchmark' hiển thị so sánh định lượng. Khi xong, quay lại đây và cho tôi biết."

### User thấy gì trong viewer

Tab "Outputs" hiển thị từng test case một:
- **Prompt**: task đã được giao
- **Output**: files skill tạo ra, render inline khi có thể
- **Previous Output** (iteration 2+): section thu gọn hiển thị output của iteration trước
- **Formal Grades** (nếu grading đã chạy): section thu gọn hiển thị assertion pass/fail
- **Feedback**: textbox tự lưu khi họ gõ
- **Previous Feedback** (iteration 2+): bình luận của họ lần trước, hiển thị bên dưới textbox

Tab "Benchmark" hiển thị stats summary: pass rates, timing, và token usage cho mỗi configuration, với per-eval breakdowns và analyst observations.

Điều hướng qua nút prev/next hoặc phím mũi tên. Khi xong, họ click "Submit All Reviews" sẽ lưu tất cả feedback vào `feedback.json`.

### Bước 5: Đọc feedback

Khi user báo xong, đọc `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "chart thiếu nhãn trục", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "hoàn hảo, tôi thích cái này", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Feedback rỗng nghĩa là user thấy ổn. Tập trung cải thiện vào các test cases mà user có complaints cụ thể.

Kill viewer server khi xong:

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## Cải thiện skill

Đây là trái tim của vòng lặp. Bạn đã chạy test cases, user đã review kết quả, và bây giờ bạn cần làm skill tốt hơn dựa trên feedback của họ.

### Cách nghĩ về cải thiện

1. **Tổng quát hóa từ feedback.** Điều quan trọng ở đây là chúng ta đang cố tạo skills có thể dùng hàng triệu lần (có thể thực sự là vậy, thậm chí hơn thế ai biết được) trên nhiều prompts khác nhau. Ở đây bạn và user đang iterate chỉ trên vài examples liên tục vì nó giúp tiến nhanh hơn. User biết rõ các examples này và có thể đánh giá outputs mới nhanh chóng. Nhưng nếu skill bạn và user đang cộng tác phát triển chỉ hoạt động cho các examples đó, nó vô dụng. Thay vì thực hiện các thay đổi fiddly overfitty, hoặc MUSTs cực kỳ hạn chế, nếu có vấn đề cứng đầu, bạn có thể thử phân nhánh và dùng các metaphors khác nhau, hoặc khuyến nghị các patterns làm việc khác. Tương đối rẻ để thử và có thể bạn sẽ tìm ra thứ gì đó tuyệt vời.

2. **Giữ prompt gọn.** Loại bỏ những thứ không đóng góp. Nhớ đọc transcripts, không chỉ final outputs — nếu có vẻ như skill đang khiến model lãng phí nhiều thời gian làm những thứ không hiệu quả, bạn có thể thử loại bỏ các phần của skill đang gây ra điều đó và xem điều gì xảy ra.

3. **Giải thích lý do.** Cố gắng thực sự giải thích **tại sao** đằng sau mọi thứ bạn yêu cầu model làm. LLMs ngày nay *thông minh*. Họ có good theory of mind và khi được trao harness tốt có thể vượt ra ngoài instructions thô và thực sự làm mọi thứ xảy ra. Kể cả khi feedback từ user ngắn gọn hay tức giận, hãy cố gắng thực sự hiểu task và lý do tại sao user viết những gì họ viết, và những gì họ thực sự viết, rồi truyền sự hiểu biết này vào instructions. Nếu thấy mình viết ALWAYS hoặc NEVER chữ hoa, hoặc dùng cấu trúc cứng nhắc siêu rigid, đó là yellow flag — nếu có thể, diễn đạt lại và giải thích lý do để model hiểu tại sao thứ bạn yêu cầu quan trọng. Đó là cách tiếp cận humane, powerful, và hiệu quả hơn.

4. **Tìm repeated work qua các test cases.** Đọc transcripts từ test runs và chú ý nếu tất cả subagents đều độc lập viết các helper scripts tương tự hoặc thực hiện cùng cách tiếp cận nhiều bước cho thứ gì đó. Nếu cả 3 test cases đều dẫn đến subagent viết `create_docx.py` hoặc `build_chart.py`, đó là signal mạnh rằng skill nên bundle script đó. Viết một lần, đặt trong `scripts/`, và bảo skill dùng nó. Điều này tiết kiệm mọi invocation trong tương lai phải tái phát minh bánh xe.

Task này khá quan trọng và thinking time của bạn không phải bottleneck; hãy dành thời gian và suy nghĩ thật kỹ. Tôi đề xuất viết draft revision rồi nhìn lại mới và cải thiện. Thực sự cố gắng đặt mình vào đầu user và hiểu họ muốn và cần gì.

### Vòng lặp iteration

Sau khi cải thiện skill:

1. Áp dụng cải thiện vào skill
2. Chạy lại tất cả test cases vào directory `iteration-<N+1>/` mới, bao gồm baseline runs. Nếu tạo skill mới, baseline luôn là `without_skill` (không có skill) — điều đó giữ nguyên qua các iterations. Nếu cải thiện skill hiện có, dùng phán đoán của bạn về điều gì hợp lý làm baseline: version gốc user đến với, hoặc iteration trước.
3. Launch reviewer với `--previous-workspace` chỉ đến iteration trước
4. Đợi user review và báo xong
5. Đọc feedback mới, cải thiện lại, lặp lại

Tiếp tục cho đến khi:
- User nói họ hài lòng
- Feedback đều rỗng (mọi thứ trông tốt)
- Bạn không tạo ra tiến bộ có ý nghĩa

---

## Nâng cao: Blind comparison

Với các tình huống bạn muốn so sánh nghiêm ngặt hơn giữa hai versions của skill (ví dụ user hỏi "version mới có thực sự tốt hơn không?"), có blind comparison system. Đọc `agents/comparator.md` và `agents/analyzer.md` để biết chi tiết. Ý tưởng cơ bản: đưa hai outputs cho independent agent mà không nói cái nào của skill nào, và để nó phán đoán chất lượng. Sau đó phân tích tại sao bên thắng thắng.

Đây là tùy chọn, yêu cầu subagents, và hầu hết users sẽ không cần. Human review loop thường đủ rồi.

---

## Tối ưu hóa Description

Field description trong SKILL.md frontmatter là cơ chế primary xác định Claude có invoke skill hay không. Sau khi tạo hoặc cải thiện skill, đề nghị tối ưu description để tăng độ chính xác triggering.

### Bước 1: Tạo trigger eval queries

Tạo 20 eval queries — mix giữa should-trigger và should-not-trigger. Lưu dạng JSON:

```json
[
  {"query": "prompt của user", "should_trigger": true},
  {"query": "prompt khác", "should_trigger": false}
]
```

Các queries phải thực tế và là thứ Claude Code hoặc Claude.ai user thực sự gõ. Không phải requests abstract, mà là requests cụ thể chi tiết. Ví dụ, file paths, personal context về công việc hoặc tình huống của user, column names và values, tên công ty, URLs. Một chút backstory. Một số có thể lowercase hoặc chứa abbreviations hoặc typos hoặc casual speech. Dùng mix độ dài khác nhau, và tập trung vào edge cases thay vì làm chúng rõ ràng quá.

Không tốt: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Tốt: `"ok so sếp tôi vừa gửi file xlsx này (trong Downloads, tên gì đó như 'Q4 sales final FINAL v2.xlsx') và cô ấy muốn tôi thêm cột hiển thị profit margin dưới dạng phần trăm. Revenue ở cột C và costs ở cột D tôi nghĩ vậy"`

Với **should-trigger** queries (8-10), nghĩ về coverage. Bạn muốn các cách diễn đạt khác nhau của cùng intent — một số formal, một số casual. Bao gồm các trường hợp user không đặt tên skill hay file type rõ ràng nhưng rõ ràng cần nó. Thêm một số use cases không phổ biến và cases nơi skill này cạnh tranh với skill khác nhưng nên thắng.

Với **should-not-trigger** queries (8-10), những cái có giá trị nhất là near-misses — queries chia sẻ keywords hoặc concepts với skill nhưng thực ra cần thứ khác. Nghĩ về adjacent domains, phrasing mơ hồ nơi keyword match naive sẽ trigger nhưng không nên, và cases nơi query chạm vào thứ skill làm nhưng trong context nơi tool khác phù hợp hơn.

Điều quan trọng cần tránh: đừng làm should-not-trigger queries quá rõ ràng không liên quan. "Write a fibonacci function" như negative test cho PDF skill quá dễ — nó không test gì cả. Các cases negative nên thực sự tricky.

### Bước 2: Review với user

Trình bày eval set cho user review bằng HTML template:

1. Đọc template từ `assets/eval_review.html`
2. Thay thế các placeholders:
   - `__EVAL_DATA_PLACEHOLDER__` → mảng JSON của eval items (không có quotes xung quanh — đó là JS variable assignment)
   - `__SKILL_NAME_PLACEHOLDER__` → tên của skill
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → description hiện tại của skill
3. Ghi vào temp file (ví dụ `/tmp/eval_review_<skill-name>.html`) và mở nó: `open /tmp/eval_review_<skill-name>.html`
4. User có thể edit queries, toggle should-trigger, thêm/xóa entries, rồi click "Export Eval Set"
5. File download về `~/Downloads/eval_set.json` — kiểm tra Downloads folder để tìm version mới nhất trong trường hợp có nhiều (ví dụ `eval_set (1).json`)

Bước này quan trọng — eval queries kém dẫn đến descriptions kém.

### Bước 3: Chạy optimization loop

Báo user: "Sẽ mất một chút thời gian — tôi sẽ chạy optimization loop ở background và kiểm tra định kỳ."

Lưu eval set vào workspace, rồi chạy ở background:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Dùng model ID từ system prompt (cái đang cấp nguồn cho session hiện tại) để triggering test khớp với những gì user thực sự trải nghiệm.

Trong khi chạy, định kỳ tail output để cập nhật cho user về iteration đang ở đâu và scores trông như thế nào.

Cái này xử lý toàn bộ optimization loop tự động. Nó chia eval set thành 60% train và 40% held-out test, đánh giá description hiện tại (chạy mỗi query 3 lần để có trigger rate đáng tin cậy), rồi gọi Claude để đề xuất cải thiện dựa trên những gì failed. Nó đánh giá lại mỗi description mới trên cả train và test, iterate tối đa 5 lần. Khi xong, mở HTML report trong browser hiển thị kết quả mỗi iteration và trả về JSON với `best_description` — được chọn theo test score thay vì train score để tránh overfitting.

### Cách skill triggering hoạt động

Hiểu triggering mechanism giúp thiết kế eval queries tốt hơn. Skills xuất hiện trong danh sách `available_skills` của Claude với name + description, và Claude quyết định có consult skill không dựa trên description đó. Điều quan trọng cần biết là Claude chỉ consult skills cho các tasks mà nó không thể xử lý dễ dàng bằng chính mình — simple, one-step queries như "đọc PDF này" có thể không trigger skill kể cả khi description match hoàn hảo, vì Claude có thể xử lý chúng trực tiếp với basic tools. Các queries phức tạp, multi-step, hoặc chuyên biệt trigger skills đáng tin cậy khi description match.

Điều này có nghĩa eval queries của bạn phải có đủ thực chất để Claude thực sự được hưởng lợi khi consult skill. Các queries đơn giản như "read file X" là test cases kém — chúng sẽ không trigger skills bất kể chất lượng description.

### Bước 4: Áp dụng kết quả

Lấy `best_description` từ JSON output và cập nhật SKILL.md frontmatter của skill. Hiển thị before/after cho user và báo cáo scores.

---

### Đóng gói và Trình bày (chỉ khi có tool `present_files`)

Kiểm tra xem bạn có quyền truy cập tool `present_files` không. Nếu không, bỏ qua bước này. Nếu có, đóng gói skill và trình bày file .skill cho user:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

Sau khi đóng gói, hướng user đến đường dẫn file `.skill` kết quả để họ có thể cài đặt nó.

---

## Hướng dẫn đặc thù cho Claude.ai

Trong Claude.ai, quy trình cốt lõi giống nhau (draft → test → review → improve → repeat), nhưng vì Claude.ai không có subagents nên một số mechanics thay đổi. Đây là những gì cần điều chỉnh:

**Chạy test cases**: Không có subagents nghĩa là không có parallel execution. Cho mỗi test case, đọc SKILL.md của skill, rồi làm theo instructions để hoàn thành test prompt. Làm từng cái một. Điều này kém nghiêm ngặt hơn independent subagents (bạn viết skill và cũng chạy nó, nên bạn có full context), nhưng là sanity check hữu ích — và human review step bù đắp. Bỏ qua baseline runs — chỉ dùng skill để hoàn thành task như được yêu cầu.

**Review kết quả**: Nếu bạn không thể mở browser (ví dụ VM của Claude.ai không có display, hoặc bạn đang trên remote server), bỏ qua browser reviewer hoàn toàn. Thay vào đó, trình bày kết quả trực tiếp trong conversation. Cho mỗi test case, hiển thị prompt và output. Nếu output là file user cần thấy (như .docx hoặc .xlsx), lưu vào filesystem và báo họ chỗ nào để download và kiểm tra. Hỏi feedback inline: "Cái này trông thế nào? Bạn muốn thay đổi gì không?"

**Benchmarking**: Bỏ qua quantitative benchmarking — nó dựa trên baseline comparisons không có ý nghĩa nếu không có subagents. Tập trung vào qualitative feedback từ user.

**Vòng lặp iteration**: Giống như trước — cải thiện skill, rerun test cases, hỏi feedback — chỉ không có browser reviewer ở giữa. Bạn vẫn có thể tổ chức kết quả vào iteration directories trên filesystem nếu có.

**Description optimization**: Section này yêu cầu tool `claude` CLI (cụ thể `claude -p`) chỉ có trong Claude Code. Bỏ qua nếu đang trên Claude.ai.

**Blind comparison**: Yêu cầu subagents. Bỏ qua.

**Packaging**: Script `package_skill.py` hoạt động bất cứ đâu có Python và filesystem. Trên Claude.ai, bạn có thể chạy nó và user có thể download file `.skill` kết quả.

**Cập nhật skill có sẵn**: User có thể yêu cầu bạn cập nhật skill có sẵn, không phải tạo mới. Trong trường hợp này:
- **Giữ nguyên tên gốc.** Chú ý directory name và `name` frontmatter field của skill -- dùng chúng không thay đổi. Ví dụ nếu skill được cài là `research-helper`, output `research-helper.skill` (không phải `research-helper-v2`).
- **Copy đến nơi có thể ghi trước khi edit.** Đường dẫn skill được cài có thể read-only. Copy sang `/tmp/skill-name/`, edit ở đó, và đóng gói từ bản copy.
- **Nếu đóng gói thủ công, stage trong `/tmp/` trước**, rồi copy sang output directory -- ghi trực tiếp có thể fail do permissions.

---

## Hướng dẫn đặc thù cho Cowork

Nếu bạn đang trong Cowork, những điều chính cần biết là:

- Bạn có subagents, nên quy trình chính (spawn test cases song song, chạy baselines, grade, v.v.) đều hoạt động. (Tuy nhiên nếu gặp vấn đề nghiêm trọng với timeouts, OK để chạy test prompts nối tiếp thay vì song song.)
- Bạn không có browser hoặc display, nên khi generate eval viewer, dùng `--static <output_path>` để viết standalone HTML file thay vì start server. Sau đó đưa link cho user click để mở HTML trong browser của họ.
- Vì lý do nào đó, setup Cowork có vẻ discourage Claude khỏi việc generate eval viewer sau khi chạy tests, nên nhắc lại: dù đang trong Cowork hay Claude Code, sau khi chạy tests, bạn phải luôn generate eval viewer cho human xem examples trước khi tự sửa skill và cố sửa lỗi, dùng `generate_review.py` (không viết boutique html code tùy chỉnh). Xin lỗi trước nhưng tôi sẽ viết hoa ở đây: HÃY GENERATE EVAL VIEWER *TRƯỚC KHI* tự đánh giá inputs. Bạn muốn đưa chúng đến tay human sớm nhất có thể!
- Feedback hoạt động khác: vì không có running server, nút "Submit All Reviews" của viewer sẽ download `feedback.json` như file. Sau đó bạn có thể đọc từ đó (có thể cần request access trước).
- Packaging hoạt động — `package_skill.py` chỉ cần Python và filesystem.
- Description optimization (`run_loop.py` / `run_eval.py`) nên hoạt động trong Cowork vì nó dùng `claude -p` qua subprocess, không phải browser, nhưng hãy để dành cho đến khi bạn hoàn toàn hoàn thiện skill và user đồng ý nó đã ổn.
- **Cập nhật skill có sẵn**: User có thể yêu cầu bạn cập nhật skill có sẵn, không phải tạo mới. Làm theo hướng dẫn update trong section claude.ai ở trên.

---

## Reference files

Thư mục `agents/` chứa instructions cho các specialized subagents. Đọc chúng khi cần spawn subagent liên quan.

- `agents/grader.md` — Cách đánh giá assertions theo outputs
- `agents/comparator.md` — Cách thực hiện blind A/B comparison giữa hai outputs
- `agents/analyzer.md` — Cách phân tích tại sao một version thắng version khác

Thư mục `references/` có tài liệu bổ sung:
- `references/schemas.md` — Cấu trúc JSON cho evals.json, grading.json, v.v.

---

Nhắc lại một lần nữa vòng lặp cốt lõi ở đây để nhấn mạnh:

- Tìm hiểu skill là về cái gì
- Draft hoặc edit skill
- Chạy claude-với-skill trên test prompts
- Cùng user đánh giá outputs:
  - Tạo benchmark.json và chạy `eval-viewer/generate_review.py` để giúp user review chúng
  - Chạy quantitative evals
- Lặp lại cho đến khi bạn và user hài lòng
- Đóng gói skill cuối cùng và trả về cho user.

Hãy thêm các bước vào TodoList của bạn, nếu bạn có cái đó, để đảm bảo bạn không quên. Nếu đang trong Cowork, hãy đặc biệt đặt "Tạo evals JSON và chạy `eval-viewer/generate_review.py` để human có thể review test cases" vào TodoList để đảm bảo nó xảy ra.

Chúc may mắn!
