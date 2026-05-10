# Nhiệm vụ: Audit các file `.md` để phát hiện diễn đạt gây hiểu sai

## Mục tiêu
Rà soát toàn bộ các file `.md` trong scope, xác định những chỗ diễn đạt có thể khiến agent suy luận sai hoặc thực hiện action ngoài ý muốn. Cụ thể là các dạng:

1. **Ambiguous (Mơ hồ)** — có thể hiểu theo nhiều cách, agent chọn cách hiểu sai
2. **Overly conservative (Quá thận trọng)** — dùng từ ngữ dè dặt, mở ("có thể", "nên cân nhắc") khiến agent không dám hành động dứt khoát khi lẽ ra phải làm
3. **Unsubstantiated (Thiếu căn cứ)** — đưa ra quy tắc hoặc giả định không có nguồn hỗ trợ
4. **Partially incorrect (Sai một phần)** — phần lõi đúng nhưng có chi tiết sai, thiếu, hoặc outdated so với tài liệu chính thống, dẫn đến agent thực hiện đúng hướng nhưng sai ở một bước cụ thể
5. **Completely incorrect (Sai hoàn toàn)** — trái với thực tế hoặc tài liệu chính thống, khiến agent làm đúng theo hướng dẫn nhưng kết quả chắc chắn sai
6. **Uncited (Không có trích dẫn)** — claim về hệ thống/công cụ/spec bên ngoài có thể đúng và có căn cứ, nhưng không có mention/tham chiếu/hyperlink đi kèm trong file, khiến agent không thể verify và dễ deprioritize. **Không áp dụng** cho internal conventions (team rules, style preferences, workflow choices) — những thứ đó chỉ cần ghi rõ là quy tắc nội bộ
7. **Internally inconsistent (Mâu thuẫn nội bộ)** — hai hoặc nhiều file trong scope nói khác nhau về cùng một chủ đề. Khác với dạng 4/5 (sai so với nguồn ngoài): dạng này là mâu thuẫn **giữa các file trong repo**. Khi phát hiện, ghi rõ cả hai vị trí và đề xuất file nào nên là source of truth theo thứ tự: `CLAUDE.md` > `rules/` > `references/` > `agents/` > `skills/` > `output-styles/` > `docs/` > `templates/` > `.github/` > `README.md`

Ngoài ra, đánh giá thêm:

- **Gap (Thiếu nội dung)** — vấn đề thực tế khi dùng agent/subagent mà các file trong scope chưa đề cập. Không cần trích dẫn, chỉ cần mô tả vấn đề và đề xuất bổ sung.

---

## Scope

- **Thư mục gốc:** root của repo (không phải working directory lúc chạy), trừ khi được chỉ định rõ đường dẫn khác
- Bao gồm tất cả subfolders đệ quy
- **Default exclusions** (không audit trừ khi chỉ định rõ): `.pytest_cache/`, `node_modules/`, `.git/`, `dist/`, `build/`, và các file/thư mục trong `.gitignore`
- Không exclude file nào khác trừ khi được chỉ định rõ

---

## Quy trình kiểm chứng trước khi kết luận từ dạng 3 đến 7

> Không được kết luận vội. Phải lần lượt kiểm tra **toàn bộ** các nguồn sau:

1. **Fetch tài liệu chính thống** theo thứ tự ưu tiên giảm dần:
   - `code.claude.com` — Claude Code docs (ưu tiên cao nhất). Các trang quan trọng: [sub-agents](https://code.claude.com/docs/en/sub-agents), [hooks](https://code.claude.com/docs/en/hooks), [permissions](https://code.claude.com/docs/en/permissions), [security](https://code.claude.com/docs/en/security), [best-practices](https://code.claude.com/docs/en/best-practices), [settings](https://code.claude.com/docs/en/settings)
   - `platform.claude.com` / `docs.anthropic.com` (API & model docs)
   - GitHub official repos (của Anthropic hoặc tác giả liên quan)
   - Blog kỹ thuật, v.v.

   > Nếu các nguồn mâu thuẫn nhau, ưu tiên nguồn có thứ tự cao hơn. Ghi rõ mâu thuẫn trong report.

2. **Verify bằng thực thi** — nếu claim nói về runtime behavior (path mapping, tool output, command result, file system) → **chạy lệnh/tool trực tiếp** để confirm/deny. Bằng chứng thực thi ưu tiên hơn docs khi có mâu thuẫn (docs có thể outdated, runtime là ground truth hiện tại)

3. **Kiểm tra chéo trong scope** — xem thông tin đó có được giải thích hoặc định nghĩa trong một file `.md` khác trong cùng scope không

Sau khi có đủ bằng chứng, áp dụng ngưỡng kết luận như sau:

- **"Unsubstantiated (Thiếu căn cứ)"** → khi cả ba bước trên **không tìm thấy** nguồn hỗ trợ
- **"Partially incorrect (Sai một phần)"** → khi bằng chứng cho thấy nội dung **đúng một phần**, phần còn lại mâu thuẫn hoặc không còn chính xác — cần chỉ rõ **phần nào đúng, phần nào sai** thay vì bác bỏ toàn bộ
- **"Completely incorrect (Sai hoàn toàn)"** → khi cả ba bước trên **tìm thấy bằng chứng trái chiều rõ ràng** — mức độ chắc chắn phải cao hơn, vì sửa sai mà thực ra đúng sẽ gây hại nhiều hơn không sửa
- **"Uncited (Không có trích dẫn)"** → khi tìm thấy nguồn hỗ trợ ở bước 1, 2, hoặc 3, nhưng file gốc **không có mention/tham chiếu/hyperlink** nào dẫn đến nguồn đó. Chỉ áp dụng cho claims về hệ thống/công cụ/spec bên ngoài — internal conventions không cần citation
- **"Internally inconsistent (Mâu thuẫn nội bộ)"** → khi bước 3 phát hiện **hai file trở lên** trong scope nói khác nhau về cùng chủ đề, bất kể bên nào đúng so với nguồn ngoài

---

## Yêu cầu về trích dẫn

Với mọi kết luận từ dạng 3 đến 7, bắt buộc phải đính kèm ít nhất một trong các hình thức sau:

- **Mention** — nêu rõ tên tài liệu / file `.md` / section cụ thể làm căn cứ
- **Tham chiếu** — trích dẫn nội dung liên quan từ nguồn đó
- **Hyperlink** — dán link trực tiếp đến trang docs, commit, hoặc file trong repo
- **Execution evidence** — output thực tế từ lệnh/tool đã chạy (cho claims về runtime behavior)

> Không được đưa ra kết luận dạng 3–7 nếu không có ít nhất một hình thức trích dẫn ở trên.

---

## Mức độ ưu tiên xử lý

Nếu tìm thấy nhiều vấn đề, ưu tiên fix theo thứ tự sau (cao → thấp):

| Mức | Dạng | Lý do ưu tiên |
|-----|------|---------------|
| P0 | Completely incorrect | Chắc chắn dẫn đến action sai |
| P1 | Partially incorrect | Sai ở bước cụ thể, khó debug |
| P2 | Internally inconsistent | Agent theo file sai → action sai; khó phát hiện vì mỗi file đọc riêng đều "đúng" |
| P2 | Gap | Vấn đề thực tế không được cover |
| P3 | Unsubstantiated | Có thể bị agent bỏ qua |
| P4 | Uncited | Đúng nhưng agent không thể verify, dễ deprioritize |
| P5 | Ambiguous | Agent có thể chọn đúng hoặc sai |
| P6 | Overly conservative | Agent vẫn hoạt động, chỉ kém hiệu quả |

> **Exposure modifier**: Nếu cùng dạng, ưu tiên file có exposure cao hơn: `CLAUDE.md`/`rules/` (load mọi session) > `references/`/`output-styles/` (load khi cần) > `agents/`/`skills/` (khi invoke) > `docs/`/`templates/`/`.github/`/`README.md` (reference only).

---

## Xử lý finding thuộc nhiều category

Nếu 1 vấn đề thuộc nhiều category (ví dụ: vừa sai threshold vừa thiếu citation) → report dưới **category có priority cao nhất**. Liệt kê các category phụ trong field "Vấn đề".

---

## Output format

Với mỗi vấn đề phát hiện, report theo cấu trúc sau:

    **File:** <đường dẫn file tính từ root repo>
    **Dòng/Section:** <số dòng hoặc tên section>
    **Dạng:** <1–7 hoặc Gap, kèm tên tiếng Anh> (xem §Mục tiêu)
    **Mức ưu tiên:** <P0–P6, kèm exposure modifier nếu cần>
    **Nội dung gốc:** <trích nguyên văn đoạn có vấn đề>
    **Vấn đề:** <giải thích tại sao gây hiểu sai; nếu thuộc nhiều category → liệt kê category phụ>
    **Căn cứ:** <mention / tham chiếu / hyperlink / execution evidence>
    **Đề xuất sửa:** <nội dung thay thế>

---

## Hành động sau audit

- **Mặc định:** Report only — liệt kê toàn bộ vấn đề, không tự sửa
- **Nếu được chỉ định `--fix`:** Với mỗi vấn đề, xuất diff dạng before/after và **dừng lại chờ xác nhận** ("y" để áp dụng, "n" để bỏ qua, "q" để thoát) trước khi ghi vào file. Nếu môi trường non-interactive, tự động disable `--fix` và chỉ report.
- **Không tự ý sửa file** nếu chưa nhận được xác nhận rõ ràng từ người dùng
