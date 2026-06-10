# Audit-Logic Plugin Improvement Proposals

> ⚠️ **Historical log** — entries below reference phase numbers and rules of the skill version at the time they were written. Notable drift vs the current skill: pre-v0.9.0 numbering ("Phase 4 step 6" = today's Phase 5 step 6; "Phase 6" summary/retrospective = today's Phase 7); P-3's implicit-approval rule was **reversed** in v0.10.0 (Phase 3 now requires explicit user confirmation; the hook never suggests `findings_confirmed: true`); P-6's order was also reversed (retrospective now runs BEFORE deleting the state file). Do not treat old entries as descriptions of current behavior.
>
> This file is a historical archive shipped with the plugin — distinct from the **project-level** `.claude/improvement-proposals.md` that `/pipeline-retrospective` writes during a run.

Generated: 2026-06-11 (v1.0.1 — benchmark fixture wallet, headless 2-stage, sau audit-plugin convergence 3 rounds)

## v1.0.1 Benchmark (fixture wallet: 1 HIGH + 1 MEDIUM + 1 INFO gài, model claude-sonnet-4-6)
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | GOOD | 6/6 file đọc đủ; "Reading patterns loaded" + coverage summary in đúng |
| D2 Finding quality | PARTIAL | 2/2 HIGH+MEDIUM gài tìm thấy, 0 false positive. **MISS INFO dead-code lần 2 liên tiếp** (validate_wallet: không production caller + comment "checkout" trỏ flow không tồn tại — executor phân tích semantics rồi dismiss "by design", bullet self-check P-7 có trong skill text nhưng không được THỰC THI). **Severity miscalibration:** pagination bug (chỉ trả sai dữ liệu hiển thị, không ghi sai DB) bị xếp HIGH thay vì MEDIUM theo rubric |
| D3 Completion | GOOD | 7/7 phase; Phase 4 completeness table; Phase 7 Exception (mở rộng v1.0.1 "installed but fails to run") fired đúng khi /pipeline-retrospective lỗi headless |
| D4 Pipeline health | GOOD | Stage A dừng THẬT ở gate Phase 3 (tree sạch); headless fallback v1.0.1 (track gates trong report khi Write .claude/ bị deny) hoạt động; clean-tree check trước Phase 5 (fix V11) fired |
| D5 Fix quality | GOOD− | 1 commit/bug, message đạt what/why/change, tests mới assert đúng items (không chỉ len); verification agent dùng template nguyên văn, intent-blind, 2 lần. Minus: KHÔNG chứng minh empirically test fail trên code cũ (không dùng git stash dù được grant) |
| D6 Skill triggering | GOOD | SKILL.md v1.0.1 load đủ (quote được text mới: orphan guard, headless fallback, no-git pointers) |

Chi phí: Stage A $0.42 (15 turns) + Stage B $0.90 (21 turns) ≈ $1.32.

**Đề xuất từ benchmark (cả 3 APPLIED 2026-06-11 cùng session, user duyệt):**
- **P-9 (MEDIUM, recall):** INFO dead-code miss tái diễn dù rule P-7 đã có trong Phase 2 self-check — rule tồn tại nhưng không được thực thi dạng prose. Đề xuất: Phase 2 self-check bắt buộc in BẢNG per-public-function: `| function | production caller(s) | unit test | gaps |` — hàng nào cột caller trống → tự động vào running issue list (INFO). Bảng ép thực thi tốt hơn bullet. **Status: APPLIED 2026-06-11** (Phase 2 self-check — bảng bắt buộc, cấm dismiss bằng semantics).
- **P-10 (LOW, calibration):** thêm 1 dòng vào Phase 3 severity calibration: "Dữ liệu SAI được TRẢ VỀ (display/response) nhưng không GHI sai vào storage → MEDIUM tối đa" — benchmark xếp pagination bug HIGH vì lý do 'UX tài chính nghiêm trọng'. **Status: APPLIED 2026-06-11** (Phase 3 — calibration mới cho read-path bugs).
- **P-11 (LOW, verification):** Phase 5 step 2: khi project có git, yêu cầu chứng minh REGRESSION label bằng cách chạy test trên code cũ (git stash / checkout tạm) thay vì chỉ suy luận — run này label đúng nhưng không chứng minh. **Status: APPLIED 2026-06-11** (Phase 5 step 2 — git stash proof bắt buộc khi có git).

---

Generated: 2026-06-10 (v1.0.0 — benchmark fixture có kiểm soát, headless 2-stage, 7/7 phase)

## v1.0.0 Benchmark (fixture cart 3 bug gài, headless -p + resume)
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | GOOD | 100% dòng của 4 file; coverage summary Phase 2 in ra đúng (fix T-6 hoạt động); "Reading patterns loaded" ✓ |
| D2 Finding quality | GOOD− | 2/2 HIGH gài đều tìm thấy kèm runtime repro + 1 MEDIUM thật không gài (variant_id không validate); 0 false positive (deferred đều có lý do đúng). **MISS: INFO gài (dead code `validate_cart` + stale comment "trước checkout" khi không tồn tại checkout flow) — cả 2 run đều phân tích semantics của hàm nhưng không flag "không có production caller"** |
| D3 Completion | GOOD | 7/7 phase; exception paths fire đúng: tests-blocked → code-only → recover; /pipeline-retrospective lỗi headless → dùng đúng Phase 7 Exception (record skip + reason + đóng gate) |
| D4 Pipeline health | PARTIAL | Human gate Phase 3 hoạt động THẬT (dừng chờ duyệt, git sạch); nhưng state file không tạo được trong headless (Write vào `.claude/` bị permission chặn) → Stop-hook gate không được vũ trang trong run; executor track gates trong báo cáo thay thế — graceful |
| D5 Fix quality | GOOD | 1 commit/bug, commit message Conventional + tiếng Việt đúng repo rule; regression test CHỨNG MINH fail trên code cũ qua git stash; verification agent intent-blind dùng đúng template nguyên văn |
| D6 Skill triggering | GOOD | SKILL.md v0.10.0 load đầy đủ (sau khi sửa lỗi môi trường MSYS path-mangle — không phải lỗi plugin) |

**Đề xuất từ benchmark:**
- **P-7 (MEDIUM) — ✅ APPLIED (v1.0.0):** Recall gap — pattern "dead code / hàm không có production caller / comment tham chiếu flow không tồn tại" bị miss dù có trong reading-patterns.md §Dead Code. **Đã thêm** bullet thứ 3 vào Phase 2 self-check (SKILL.md): mọi public symbol phải khai báo production caller; chỉ test gọi → dead-code candidate (INFO); "test coverage ≠ evidence hàm còn sống".
- **P-8 (LOW) — ✅ APPLIED (v1.0.0):** **Đã thêm** section "Headless / Windows notes" vào README: (1) MSYS path-mangle prompt từ Git Bash, không dùng `MSYS_NO_PATHCONV=1` (phá hook con) — dùng PowerShell/CMD hoặc stdin; (2) headless không tạo được state file → gate hook không arm, skill track gate trong báo cáo.

---

Generated: 2026-06-06 (latest: wishlist v0.8.0 — 6th run, GOOD)
wishlist: 1 MEDIUM found+fixed (null.toJSON crash on soft-deleted product). 6 consecutive runs GOOD.

---

Generated: 2026-06-06 (users v0.8.0 — 5th run, CLEAN MODULE, all GOOD)
5 consecutive clean runs. users module had 0 bugs — audit correctly identified clean codebase.

---

Generated: 2026-06-06 (reviews v0.8.0 — 4th run, all GOOD)
4 consecutive clean runs. Skill stable.

---

Generated: 2026-06-06 (discount-code v0.8.0 — 3rd run, all GOOD)

## v0.8.0 3rd Run (discount-code)
All 6 dimensions GOOD. No new proposals. 3 consecutive clean runs confirms v0.8.0 stability.

---

Generated: 2026-06-06 (cart v0.8.0 — 2nd run)
Source: audit-logic v0.8.0 run on backend/src/modules/cart — CLEAN RUN, no new proposals

## v0.8.0 2nd Run Result (cart module — HIGH + MEDIUM bugs found)
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | GOOD | 10 source + 10 test suites read; reading-patterns.md loaded ✓ |
| D2 Finding quality | GOOD | 1 HIGH (addToCart duplicate CartItems) + 1 MEDIUM (getCart merge no cap). Agent surfaced 9/9 pre-existing — executor correctly filtered. |
| D3 Completion | GOOD | 7 phases + 2 commits + docs + retrospective complete |
| D4 Pipeline health | GOOD | Phase 7 gate blocked until retrospective — v0.8.0 enforcement working ✓ |
| D5 Fix quality | GOOD | Surgical commits, no scope spill |
| D6 Skill triggering | GOOD | All mandatory steps triggered correctly |

**No new improvements needed for v0.9.0.**

---

## v0.8.0 Benchmark Result (inventory module)
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | GOOD | All 7 source + 4 test files read; reading-patterns.md loaded pre-Phase 2 ✓ |
| D2 Finding quality | GOOD | 1 MEDIUM real, 4 agent false positives correctly dismissed ✓ |
| D3 Completion | GOOD | All 7 phases complete including Phase 4 completeness check ✓ |
| D4 Pipeline health | GOOD | Phase 4 gate enforced; incremental hint correct; no stalls ✓ |
| D5 Fix quality | GOOD | Surgical: 2 files + separate doc commit ✓ |
| D6 Skill triggering | GOOD | reading-patterns.md ✓; Phase 4 ✓; pipeline-retrospective ✓ |

**No new improvements needed for v0.8.0. All gates working correctly.**

---

# Previous Proposals (payment module — v0.5.0 baseline)
Source: audit-logic run on backend/src/modules/payment (TechStore e-commerce)

## Performance Summary
| Dimension | Score | Evidence |
|-----------|-------|---------|
| D1 Coverage | PARTIAL | references/reading-patterns.md not consulted during Phase 2 file reading |
| D2 Finding quality | PARTIAL | vnp_RequestId HHmmss collision identified internally, never surfaced in Phase 3 or Phase 6 |
| D3 Completion | PARTIAL | Phase 4 Exit Gate passed despite INFO-1 test being documentation-only, not a regression test |
| D4 Pipeline health | PARTIAL | Phase 3 → Phase 4 transition skipped user confirmation gate |
| D5 Fix quality | GOOD | Commits surgical, lint+tests pass, correct scope |
| D6 Skill triggering | POOR | verification-techniques.md prompt template not used (custom prompt written instead); no completeness critic phase in skill |

## Applied Changes

### P-1 (HIGH): Phase 2 — enforce reading reading-patterns.md before first file
**Target:** `skills/audit-logic/SKILL.md` Phase 2
**Applied:** Added mandatory step at the top of Phase 2 requiring the executor to read
`references/reading-patterns.md` in full and print a one-line summary of the 5 most
relevant categories before reading the first source file.

### P-2 (HIGH): Add Phase 3.5 — Completeness Check
**Target:** `skills/audit-logic/SKILL.md` — new phase between Phase 3 and Phase 4
**Applied:** New phase requiring the executor to account for every item from the Phase 2
running issue list — either in Phase 3 findings or in the Phase 6 deferred table. No item
may silently disappear. Explicit "No dismissed findings." is required if nothing was dropped.

### P-3 (MEDIUM): State file + implicit approval rule
**Target:** `skills/audit-logic/SKILL.md` Phase 1 + Phase 3, and `hooks/audit-logic-gate.py`
**Applied:**
- State file now includes `findings_confirmed: false`
- Phase 3 now specifies the implicit approval rule (user silence = proceed for MEDIUM/HIGH,
  print "Proceeding with implicit approval.")
- Hook: non-blocking warning when `phase4_gate: true` but `findings_confirmed: false`

### P-4 (MEDIUM): Phase 4 Exit Gate — label regression vs documentation tests
**Target:** `skills/audit-logic/SKILL.md` Phase 4 Exit Gate
**Applied:** The test checkbox now requires explicit labeling — either REGRESSION (fails
before fix, passes after) or DOCUMENTATION (behavior unchanged, commit must say so).
DOCUMENTATION label is not permitted for MEDIUM or HIGH severity fixes.

### P-5 (MEDIUM): Phase 4 step 6 — inline verification prompt, ban custom prompts
**Target:** `skills/audit-logic/SKILL.md` Phase 4 step 6
**Applied:** The exact 3-question verification agent prompt is now inlined in SKILL.md
with an explicit "Do NOT write a custom prompt" instruction. Previously it only referenced
an external file, which was easy to ignore.

### P-6 (LOW): Phase 6 — mandatory retrospective
**Target:** `skills/audit-logic/SKILL.md` Phase 6
**Applied:** After deleting the state file, executor must run `/pipeline-retrospective`.
Marked as mandatory, not optional.
