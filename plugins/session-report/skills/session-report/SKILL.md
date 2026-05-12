---
name: session-report
description: Generate an explorable HTML report of Claude Code session usage (tokens, cache, subagents, skills, expensive prompts) from ~/.claude/projects transcripts.
---

# Session Report

Tạo ra một báo cáo HTML self-contained về việc sử dụng Claude Code và lưu vào thư mục làm việc hiện tại.

## Các bước

1. **Lấy data.** Chạy analyzer bundled (window mặc định: 7 ngày gần nhất; honor range khác nếu user truyền vào, vd `24h`, `30d`, hoặc `all`). Script `analyze-sessions.mjs` nằm cùng thư mục với SKILL.md này — dùng đường dẫn tuyệt đối của nó:
   ```sh
   node <skill-dir>/analyze-sessions.mjs --json --since 7d > /tmp/session-report.json
   ```
   Để lấy all-time, bỏ `--since`.

2. **Đọc** `/tmp/session-report.json`. Skim qua `overall`, `by_project`, `by_subagent_type`, `by_skill`, `cache_breaks`, `top_prompts`.

3. **Copy template** (cũng bundled cùng thư mục với SKILL.md này) đến output path trong thư mục làm việc hiện tại:
   ```sh
   cp <skill-dir>/template.html ./session-report-$(date +%Y%m%d-%H%M).html
   ```

4. **Sửa file output** (dùng Edit, không dùng Write — giữ nguyên JS/CSS của template):
   - Thay nội dung của `<script id="report-data" type="application/json">` bằng JSON đầy đủ từ bước 1. JS của page tự động render hero total, tất cả bảng, bar, và drill-down từ blob này.
   - Điền block `<!-- AGENT: anomalies -->` với **3–5 finding 1 dòng**. Biểu thị số liệu dưới dạng **% của tổng token** bất cứ khi nào có thể (total = `overall.input_tokens.total + overall.output_tokens`). Một dòng cho mỗi finding, markup chính xác:
     ```html
     <div class="take bad"><div class="fig">41.2%</div><div class="txt"><b>cc-monitor</b> consumed 41% of the week across just 3 sessions</div></div>
     ```
     Class: `.take bad` cho waste/anomaly (đỏ), `.take good` cho tín hiệu healthy (xanh lá), `.take info` cho fact trung tính (xanh dương). `.fig` là một số ngắn (%, count, hoặc multiplier như `12×`). `.txt` là một câu plain-English đặt tên project/skill/prompt; bọc subject trong `<b>`. Tìm các pattern: một project hoặc skill chiếm tỷ lệ không cân xứng, cache-hit <85%, một prompt đơn lẻ >2% tổng, subagent type trung bình >1M token/call, cache break tụm cụm.
   - Điền block `<!-- AGENT: optimizations -->` (ở **dưới cùng** của page) với 1–4 suggestion `<div class="callout">` gắn vào row cụ thể (vd "`/weekly-status` spawn 7 subagent cho 8.1% tổng — scope nó về ít parallel agent hơn").
   - Đừng restructure các section đã có.

5. **Report** đường dẫn file đã lưu cho user. Đừng mở hoặc render nó.

## Lưu ý

- Template là nguồn của tính tương tác (sort, expand/collapse, block-char bar). Việc của bạn là data + narrative, không phải markup.
- Giữ commentary ngắn gọn và cụ thể — tham chiếu tên project, số liệu, timestamp thực tế từ JSON.
- `top_prompts` đã include token của subagent và roll task-notification continuation vào prompt gốc.
- Nếu JSON >2MB, trim `top_prompts` xuống 100 entry và `cache_breaks` xuống 100 trước khi embed (chúng đã nên được cap rồi).
