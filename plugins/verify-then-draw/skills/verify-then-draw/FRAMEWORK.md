# FRAMEWORK — Verify-then-Draw (portable, oracle-anchored)

> Khung **generic** để vẽ sơ đồ (hoặc audit code) từ codebase với sai sót tối thiểu.
> Hạn chế tối đa tên tool/module cụ thể trong file này; **ví dụ minh hoạ stack-specific để ở**
> `PROJECT.yaml`, `invariants.<domain>.md`, `diagram-manifest.yaml` (tạo trong project đích — xem mẫu [`PROJECT.example.yaml`](PROJECT.example.yaml)).
> Vài thuật ngữ chung (quét văn bản, message bus, AST) là **khái niệm**, không phải tool — giữ generic.
> Copy thư mục này sang project khác → chỉ sửa 3 file kia + `PROJECT.<stack>.example.yaml`, **giữ nguyên FRAMEWORK.md**.

> **⚙️ TRẠNG THÁI ENFORCE (không phải honor-system):** gate đã được wire thành script chạy được.
> Gate = script chạy được, tên lệnh cụ thể ở **PROJECT.yaml** (`ledger_gate_cmd`, `mutation_critical_cmd`, `route_enumerator_cmd`, `property_glob`). Cổng tổng (`ledger_gate_cmd`) chạy chuỗi: lint-config (config trỏ đúng) → guard **GATE-A** (chặn khi invariant còn `[ ]`) → guard ledger (chặn khi sơ đồ logic_heavy chưa `signed`/GATE-D). Mutation tier wire qua mutation-config có **break-threshold ≠ null**; property tier qua property-test (property-based lib); denominator route qua enumerator **in TỔNG** (KHÔNG phải dead-route detector).
> ⚠️ GATE-C (review prompt) + GATE-D (ký sơ đồ) vẫn là **human-driven** (không thể tự động hoá) — đó là chủ đích, không phải thiếu sót.

---

## 0. Nguyên lý nền

1. **Code là ground-truth của sơ đồ, NHƯNG code chỉ cho biết "code LÀM GÌ", không cho biết "NÊN làm gì".** → mọi tầng phải neo ≥1 **oracle ngoài-model**.
2. **Đừng tin "code đúng" rồi vẽ.** Vẽ đúng cái-code-sai = sơ đồ khớp code nhưng sai nghiệp vụ. Bug nghiệp vụ vẫn lọt qua **test coverage cao** nếu test assert *"method được gọi"* thay vì assert **outcome** (ví dụ cụ thể của project: xem `invariants.<domain>.md` + ghi chú bug ở PROJECT-level).
3. **Self-bootstrap từ 1 agent có trần.** Thêm agent **cùng model** = nhân bản blind spot. Phá khép kín chỉ bằng **nguồn ngoài model** (human/spec, chạy-code RAW, denominator cấu trúc) + (nếu có) model **khác provider** làm verifier.

---

## 1. Khung 3 tầng — gate cứng

Không qua gate tầng dưới thì **không** lên tầng trên.

```
T0  Code đúng SEMANTICS nghiệp vụ   ──[GATE-A, GATE-C, GATE-B]──►
T1  Sơ đồ khớp source (đầy đủ)      ──[coverage-ledger]────────►
T2  Ký pháp + readability           ──[vision-check, GATE-D]───►
```

| Tầng | Mục tiêu | Oracle ngoài-model phải neo |
|---|---|---|
| **T0** | Code đúng nghiệp vụ | (a) oracle-nghiệp-vụ (human/spec) + (b) oracle-thực-thi (chạy code RAW + mutation + property) |
| **T1** | Sơ đồ phủ hết + đúng source | (c) denominator cấu trúc (route-table / enum-set / AST / DB-schema) |
| **T2** | Ký pháp đúng + đọc được | vision-check N điểm + GATE-D human |

---

## 2. Oracle layer — 3 nguồn ngoài vòng điều phối

Mỗi tầng **bắt buộc** neo ≥1:

- **(a) Oracle NGHIỆP VỤ** = human/spec ghi invariant **`WHEN <input> THEN <outcome PHẢI là Y>`** *trước* khi audit. Đây là **TIÊU CHÍ**. → file `invariants.<domain>.md`.
- **(b) Oracle THỰC THI** = chạy code thật, quan sát **outcome RAW**; **(nếu stack có)** + mutation testing + property/metamorphic. Đây là **DỮ LIỆU** + máy-đo-chất-lượng-assertion.
- **(c) DENOMINATOR cấu trúc** = enumerate route-table / enum-set / AST / public-method = **"có bao nhiêu đơn vị cần phủ"**.

> **Graceful degradation (stack thiếu công cụ):** mutation/property là *thành phần mạnh nhất* của (b) nhưng **KHÔNG bắt buộc** — nếu stack chưa có mutation/property tool (xem `denominator_tools` PROJECT.yaml), tier (b) **giảm cấp** về "chạy code RAW + assert outcome" và **PHẢI ghi rõ** tier mutation/property đang thiếu (đừng coi như đã phủ). Oracle (a)+(c) vẫn bắt buộc.

> **Test = so (b) DỮ LIỆU vs (a) TIÊU CHÍ.** Lệch → **human phân xử** code-sai-hay-invariant-sai; agent **KHÔNG** tự hòa giải. Điều này biến integration test từ "agent tự kiểm hiểu biết của mình" (lại bias) thành "máy đo thực-tế vs human-kỳ-vọng".

> Ghi minh bạch: *adversarial subagent + N-of-M quorum CHỈ giảm bias trong-model, KHÔNG phá khép kín.*

---

## 3. Finder ↔ Verifier (tách rời)

- **Finder** = coverage tối đa: report **MỌI** candidate kèm confidence. KHÔNG bảo "be conservative / chỉ high-severity" (model mới làm theo nghĩa đen → tụt recall).
- **Verifier** = agent **fresh, độc-lập-context**, lọc false-positive. Nếu có model **khác provider** → ưu tiên dùng làm verifier (giảm correlation cùng-model).
- Một số finder chạy **OPEN-ENDED** (không nhận danh sách nghi vấn, chỉ "đọc trọn module, report MỌI hành vi đáng ngờ theo lens X") → framing của coordinator không bó hẹp recall.
- **Bơm nghi vấn từ NGUỒN MÁY-SINH** thay câu coordinator tự nghĩ: mutation-survivor-list + invariant/property-fail + checklist chuẩn ngoài (CWE/OWASP, TOCTOU/lost-update) → feed thẳng verifier.

---

## 4. CONFIRM-mode vs DISCOVER-mode (bắt buộc chạy CẢ HAI mỗi tầng)

- **CONFIRM** = quét-văn-bản/đọc cái finder **đã** chỉ ra → chỉ là *confirmation*.
- **DISCOVER** = quét **KHÔNG** có danh sách candidate, dùng nguồn-liệt-kê **structural độc lập với pattern của coordinator**: reverse `diagram→code`, enumerate write-site từ AST/route-manifest/DB-schema, **column-centric** (tìm TÊN-cột rồi đọc từng hit phân loại read/write).

> Vì sao confirmation không đủ: một pattern gán-trực-tiếp dễ **MISS** các dạng ghi-state khác (ghi qua hàm `update()`/`save()` của ORM, bulk-update...). Fallback **bắt buộc, độc-lập-stack**: nghi pattern thiếu → **đọc TRỌN file** business-layer thay vì tin quét-cú-pháp. (Tập pattern cụ thể theo ORM: xem `mutation_signature_set` trong PROJECT.yaml + ví dụ thật trong `fallback_rule`.)

---

## 5. Coverage-ledger 2 chiều (phá "loop-dry ≠ hết lỗi")

- **Thuận:** mọi đơn-vị-cần-phủ (route / enum-state / mutation-site / public-method) có ≥1 finding/test/diagram.
- **Ngược:** mọi code **reachable** (từ dead-code tool) map vào ≥1 sơ đồ; method reachable không thuộc sơ đồ nào = **gap** hoặc **lược-có-chủ-đích-phải-ghi-rõ**.

---

## 6. Điều kiện DỪNG loop = 3 điều kiện ĐỒNG THỜI

Không dừng chỉ vì "agent ngừng tìm thấy". Dừng khi **cả 3**:

1. **≥2 vòng LLM liên tiếp 0 finding mới**, mỗi vòng **đổi lens/seed**.
2. **Coverage-ledger đạt ngưỡng** (%route / %enum-state / %mutation-site critical map vào ≥1 test/diagram, hoặc justified).
3. **0 mutation-survivor CHƯA-GIẢI-THÍCH** trong vùng critical.

> (1) đo *agent ngừng tìm*; (2)+(3) đo *còn-bao-nhiêu-chưa-phủ*. Trước mỗi loop ghi **baseline 3-số** (mutation-score, %route-trong-sơ-đồ, %enum-state-có-node) + report **delta** mỗi vòng.
> **Đo được, không vacuous:** (2) qua `ledger_gate_cmd` + `route_enumerator_cmd` (denominator route THẬT, KHÔNG dùng dead-route detector); (3) qua `mutation_critical_cmd` (mutation-config có break-threshold ≠ null). Nếu stack thiếu mutation/property tool → đánh dấu điều kiện tương ứng "chưa đo được" thay vì mặc-định-pass.

---

## 7. Chống blind-spot của test (mutation + property)

- **Mutation testing** = đo chất-lượng-assertion **độc lập người-viết-test**. Mutant **SỐNG** = vùng không có assertion thực = blind spot khách quan. Survivor-list = **danh sách nghi vấn máy-sinh**, feed thẳng verifier ("mutant này sống, vì sao test không bắt?").
- **Property/metamorphic invariant** bắt outcome người-viết-không-nghĩ-tới: bảo toàn tài nguyên (tổng-resource const), quan hệ đếm (counter = COUNT thực), bảo toàn tổng (total = Σ thành phần) — tự-kiểm sau **mọi** test.
- **Tách vai:** agent confirm bug **KHÔNG** được viết integration test cho chính bug đó.

> **Wire mutation gate:** dùng mutation-config riêng có **break-threshold ≠ null** scope vào *file critical* (logic tiền/kho/trạng-thái) — survivor vượt ngưỡng **FAIL** pipeline (`mutation_critical_cmd` trong PROJECT.yaml). Mutation *toàn bộ* thường để **report-only** (break = null) vì quá chậm để gate — chủ đích. Đổi project: set break-threshold ≠ null + trỏ `mutation_critical_cmd` cho tool tương đương (mutmut/PIT/go-mutesting...).

---

## 8. Human-gate — 4 cổng HARD STOP, hỏi câu ĐỘC-LẬP-VỚI-CODE

Mỗi gate hỏi câu human trả lời được **không cần đọc sâu code** (chống rubber-stamp + chống "agent tự định nghĩa đúng"):

| Gate | Khi nào | Human xác nhận (câu hỏi độc-lập-với-code) |
|---|---|---|
| **GATE-A** | TRƯỚC T0, mỗi module chạm critical-resource | VIẾT bảng invariant `WHEN…THEN…` vào `invariants.<domain>.md`. Câu: *"nghiệp vụ NÊN làm gì"* (không phải code làm gì). Agent chỉ đọc để test, KHÔNG tự sinh/sửa. |
| **GATE-C** | TRƯỚC dispatch finder/verifier (module logic-đậm) | ĐỌC **prompt** (không đọc output): *"prompt này vô tình bỏ sót trường hợp nào?"* Review framing rẻ hơn review output; phá single-point-of-failure G1. |
| **GATE-B** | SAU T0, TRƯỚC khi vẽ | SO 2 artifact: *"integration test có assert đúng bảng invariant GATE-A không (không phải assert method-called)?"* + survivor critical = 0/justified. RAW lệch invariant → human phân xử. |
| **GATE-D** | SAU render T2, mỗi sơ đồ logic-đậm | KÝ: *"sơ đồ này đại diện ĐÚNG cái tôi hiểu + đủ cho mục đích?"* Agent DỪNG chờ, không rubber-stamp. |

---

## 9. Vision-check (T2) — CORE universal + CONTEXT tham-số

- **CORE (mọi project):** đúng-node · đúng-logic-flow · không-overlap · không-mồ-côi · không-rối · đọc-được-khi-chèn-trang · nhất-quán-thuật-ngữ.
- **CONTEXT (tham số `vision_context`):** ký pháp đọc theo `notation`; font/dấu + chế-độ-in đọc theo `language` + `print_mode`; cỡ theo `page`.

---

## 10. Residual risks — GHI RÕ, KHÔNG tạo ảo giác "0 lỗi"

> Workflow này **giảm** sai sót, **không** khử hết. Trần của nó:

1. **Invariant-sai không lớp nào bắt được.** Human cấp invariant sai → cả pipeline verify-đúng-tự-tin theo invariant sai. Lớp duy nhất bắt = GATE-B (human phân xử khi RAW lệch) — lại dựa chính human đó. Vòng tự-tham-chiếu **chuyển lên tầng human**, không bị xóa.
2. **Oracle ngoài-model không thực sự độc lập** nếu spec/human và code **cùng sai** theo cùng giả định (cùng nguồn tri-thức-tổ-chức).
3. **Human-gate rubber-stamp** dưới áp lực throughput (nhiều sơ đồ × nhiều module).
4. **Denominator sai vẫn trông "đạt ngưỡng"** nếu config (layer_globs/enum_source/route_parser) trật.
5. **Property/mutation chỉ bắt trong tập đã khai báo** — bug ngoài invariant + ngoài mutation-site (race không reproduce, side-effect qua message-bus/event không subscriber) vẫn lọt. Nâng sàn recall, KHÔNG đảm bảo completeness.
6. **Stack thiếu công cụ denominator** (mutation/property kém trưởng thành) → mất nguồn khách quan, phải bù bằng đọc-trọn-file thủ công (chậm + quay về phụ thuộc recall).
7. **Mutation chậm + scope chủ quan** ("module nào critical" vẫn là lựa chọn người).
