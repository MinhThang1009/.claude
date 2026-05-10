# Nhiệm vụ: Audit 3 file `.md` trong `C:\Users\Admin\.claude\rules`

## Mục tiêu
Đánh giá xem nội dung hiện tại của 3 file trong thư mục `C:\Users\Admin\.claude\rules` đã **đầy đủ, chặt chẽ, và cover được 100% các vấn đề có thể gặp phải khi sử dụng agent và subagent** hay chưa.

---

## Bước 1: Thu thập context trước khi audit

Trước khi đọc file, fetch đủ các nguồn sau để có context đầy đủ:

1. **Claude Code docs** (ưu tiên cao nhất):
   - `https://code.claude.com/docs/en/sub-agents` (subagent behavior, limitations)
   - `https://code.claude.com/docs/en/hooks` (hook system, events)
   - `https://code.claude.com/docs/en/permissions` (permission model, risks)
   - `https://code.claude.com/docs/en/security` (security model, sandbox)
   - `https://code.claude.com/docs/en/best-practices` (best practices)
   - `https://code.claude.com/docs/en/settings` (settings, configuration)

2. **Anthropic platform docs** (khi cần verify model capabilities):
   - `https://platform.claude.com/docs/en/about-claude/models/overview`

3. **GitHub official repos** (của Anthropic hoặc tác giả liên quan)
4. **Blog kỹ thuật** (khi cần)

> Nếu các nguồn mâu thuẫn nhau, ưu tiên nguồn có thứ tự cao hơn. Ghi rõ mâu thuẫn trong report.
>
> **Không được bắt đầu audit khi chưa fetch xong các nguồn ở mục 1.**

---

## Bước 2: Đọc toàn bộ 3 file trong scope

- Đọc lần lượt từng file, không bỏ qua dòng nào
- Đọc thêm `CLAUDE.md` để hiểu context tổng và phát hiện overlap/trùng lặp
- Ghi nhận cấu trúc, nội dung, và mối liên hệ giữa các file

---

## Bước 3: Kiểm tra coverage bắt buộc

Kiểm tra riêng xem 3 file đã cover đầy đủ các section sau chưa — đây là các vấn đề thực tế phổ biến nhất khi dùng agent/subagent.

### Coverage chung (verification.md)

| # | Section | Nội dung cần cover |
|---|---------|-------------------|
| 1 | **Subagent** | Orchestrate, giới hạn quyền, truyền context, xử lý kết quả, **subagent không load CLAUDE.md/rules** |
| 2 | **Batch edits** | Edit nhiều file, rollback khi lỗi, **cross-file consistency check**, race condition |
| 3 | **Tool output reliability** | Tool trả về sai/thiếu/timeout, **WebFetch summary bởi small model**, MCP output |
| 4 | **Git state** | Trạng thái repo trước/sau thay đổi, tránh conflict, non-git fallback |
| 5 | **External dependencies** | Dependency không available, version mismatch, network error |

### Coverage security (security.md)

| # | Section | Nội dung cần cover |
|---|---------|-------------------|
| 6 | **Prompt injection vào Claude** | Untrusted files/repos, CLAUDE.md injection, web content |
| 7 | **Permission model limitations** | Deny rule không block Bash, sandbox boundaries |
| 8 | **MCP security** | MCP server là third-party, output cần validate |
| 9 | **Secrets management** | Detect, mask, rotate, gitignore |
| 10 | **Dangerous commands** | Blacklist lệnh nguy hiểm, platform-specific risks (Windows WebDAV) |

### Coverage communication (communication.md)

| # | Section | Nội dung cần cover |
|---|---------|-------------------|
| 11 | **Uncertainty handling** | Khi không chắc, WebFetch data có thể outdated, source attribution |
| 12 | **Conflict resolution** | User sai vs agent sai, giữ quan điểm khi có bằng chứng |
| 13 | **Format consistency** | Response format, tone, ngôn ngữ rules |

Với mỗi section, kết luận một trong:
- ✅ **Covered** — đã đề cập đầy đủ
- ⚠️ **Partially covered** — có đề cập nhưng chưa đủ, chỉ rõ phần còn thiếu
- ❌ **Not covered** — chưa đề cập, cần bổ sung

---

## Bước 4: Audit theo 7 dạng vấn đề

Với mỗi đoạn nội dung, kiểm tra xem có thuộc các dạng sau không:

1. **Ambiguous (Mơ hồ)** — có thể hiểu theo nhiều cách, agent chọn cách hiểu sai
2. **Overly conservative (Quá thận trọng)** — dùng từ ngữ dè dặt, mở khiến agent không dám hành động dứt khoát khi lẽ ra phải làm
3. **Unsubstantiated (Thiếu căn cứ)** — đưa ra quy tắc hoặc giả định không có nguồn hỗ trợ, dễ bị agent bỏ qua hoặc override
4. **Partially incorrect (Sai một phần)** — phần lõi đúng nhưng có chi tiết sai, thiếu, hoặc outdated
5. **Completely incorrect (Sai hoàn toàn)** — trái với thực tế hoặc tài liệu chính thống
6. **Uncited (Không có trích dẫn)** — claim về hệ thống/công cụ/spec bên ngoài đúng và có căn cứ nhưng không có mention/tham chiếu/hyperlink. **Không áp dụng** cho internal conventions (team rules, style preferences)
7. **Internally inconsistent (Mâu thuẫn nội bộ)** — hai hoặc nhiều file trong scope nói khác nhau về cùng chủ đề. Khi phát hiện, ghi rõ cả hai vị trí và đề xuất file nào nên là source of truth theo: `CLAUDE.md` > `rules/` > `references/` > `agents/` > `skills/` > `docs/`

Ngoài ra, đánh giá thêm:

- **Gap (Thiếu nội dung)** — các vấn đề phổ biến khi dùng agent/subagent mà 3 file chưa đề cập đến

---

## Quy trình kiểm chứng trước khi kết luận dạng 3–7

Không được kết luận vội. Phải lần lượt:

1. **Fetch tài liệu chính thống** — đối chiếu theo thứ tự ưu tiên: `code.claude.com` > `platform.claude.com` > GitHub official repos > blog kỹ thuật
2. **Verify bằng thực thi** — nếu claim nói về runtime behavior (path mapping, tool output, command result) → **chạy lệnh/tool trực tiếp**. Bằng chứng thực thi ưu tiên hơn docs khi có mâu thuẫn
3. **Kiểm tra chéo** giữa 3 file + CLAUDE.md — thông tin có thể được định nghĩa ở file khác trong cùng scope

> Nếu các nguồn mâu thuẫn nhau, ưu tiên nguồn có thứ tự cao hơn và ghi rõ mâu thuẫn trong report.

---

## Yêu cầu về trích dẫn

Với mọi kết luận dạng 3–7, bắt buộc đính kèm ít nhất một trong:

- **Mention** — tên tài liệu / file `.md` / section cụ thể
- **Tham chiếu** — trích nội dung liên quan từ nguồn
- **Hyperlink** — link trực tiếp đến trang docs, commit, hoặc file trong repo
- **Execution evidence** — output thực tế từ lệnh/tool đã chạy (cho claims về runtime behavior)

---

## Xử lý finding thuộc nhiều category

Nếu 1 vấn đề thuộc nhiều category (ví dụ: vừa sai threshold vừa thiếu citation) → report dưới **category có priority cao nhất**. Liệt kê các category phụ trong field "Vấn đề".

---

## Mức độ ưu tiên xử lý

| Mức | Dạng | Lý do |
|-----|------|-------|
| P0 | Completely incorrect | Chắc chắn dẫn đến action sai |
| P1 | Partially incorrect | Sai ở bước cụ thể, khó debug |
| P2 | Internally inconsistent | Agent theo file sai → action sai; khó phát hiện vì mỗi file đọc riêng đều "đúng" |
| P2 | Gap | Vấn đề thực tế không được cover |
| P3 | Unsubstantiated | Có thể bị agent bỏ qua |
| P4 | Uncited | Agent không thể verify, dễ deprioritize |
| P5 | Ambiguous | Agent có thể chọn đúng hoặc sai |
| P6 | Overly conservative | Agent vẫn hoạt động, chỉ kém hiệu quả |

> **Exposure modifier**: Nếu cùng dạng, ưu tiên file có exposure cao hơn: `CLAUDE.md`/`rules/` (load mọi session) > `references/`/`output-styles/` (load khi cần) > `agents/`/`skills/` (khi invoke) > `docs/`/`templates/`/`.github/`/`README.md` (reference only).

---

## Output format

Với mỗi vấn đề phát hiện, report theo cấu trúc:

    **File:** <tên file>
    **Dòng/Section:** <số dòng hoặc tên section>
    **Dạng:** <1–7 hoặc Gap, kèm tên tiếng Anh>
    **Mức ưu tiên:** <P0–P6, kèm exposure modifier nếu cần>
    **Nội dung gốc:** <trích nguyên văn đoạn có vấn đề>
    **Vấn đề:** <giải thích; nếu thuộc nhiều category → liệt kê category phụ>
    **Căn cứ:** <mention / tham chiếu / hyperlink / execution evidence>
    **Đề xuất sửa/bổ sung:** <nội dung thay thế hoặc cần thêm>

Cuối report, tổng hợp:

    **Tổng số vấn đề:**
    - Ambiguous: X
    - Overly conservative: X
    - Unsubstantiated: X
    - Partially incorrect: X
    - Completely incorrect: X
    - Uncited: X
    - Internally inconsistent: X
    - Gap: X

    **Coverage sections bắt buộc:**
    - [Liệt kê 13 sections với ✅ / ⚠️ / ❌]

    **Đánh giá tổng thể:** <X>% các vấn đề agent/subagent thực tế đã được cover
    **Kết luận:** <đầy đủ / cần bổ sung / cần sửa đáng kể>

---

## Hành động sau audit

- **Mặc định:** Report only — liệt kê toàn bộ vấn đề, không tự sửa
- **Nếu được chỉ định `--fix`:** Với mỗi vấn đề, xuất diff dạng before/after và **dừng lại chờ xác nhận** ("y" để áp dụng, "n" để bỏ qua, "q" để thoát) trước khi ghi vào file. Nếu môi trường non-interactive, tự động disable `--fix` và chỉ report.
- **Không tự ý sửa file** nếu chưa nhận được xác nhận rõ ràng từ người dùng
