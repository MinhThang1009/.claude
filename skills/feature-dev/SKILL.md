---
name: feature-dev
description: Guided feature development — explore codebase → hỏi clarify → thiết kế architecture → implement → review. Dùng khi cần implement feature mới có ảnh hưởng nhiều module. Gọi /feature-dev hoặc khi user mô tả feature lớn cần plan.
allowed-tools: Read Grep Glob Bash Edit Write WebFetch WebSearch
argument-hint: "[mô tả feature cần implement]"
---

# Feature Development — Multi-phase Orchestration

Quy trình phát triển feature có hệ thống: hiểu → khảo sát → hỏi → thiết kế → implement → review → tổng kết.

## Phase 1: Discovery

**Mục tiêu**: Hiểu feature cần build.

1. Tạo todo list với tất cả phases.
2. Yêu cầu feature: `$ARGUMENTS`
3. Nếu chưa rõ, hỏi user:
   - Giải quyết vấn đề gì?
   - Feature cần làm gì cụ thể?
   - Constraints hoặc requirements?
4. Tóm tắt hiểu biết, confirm với user trước khi tiếp.

## Phase 2: Codebase Exploration

**Mục tiêu**: Hiểu code hiện tại liên quan đến feature.

**Skip nếu**: user nói đã hiểu codebase ("tôi biết rồi", "skip explore") — chuyển thẳng Phase 3.

Launch **2-3 code-explorer agents song song**, mỗi agent focus khác nhau:
- Agent 1: "Tìm features tương tự [feature] và trace implementation"
- Agent 2: "Map architecture và abstractions cho [khu vực liên quan]"
- Agent 3: "Phân tích UI patterns / testing approaches / extension points liên quan"

Mỗi agent trả về **danh sách 5-10 key files**. Sau khi agents xong → đọc tất cả files được liệt kê để build context sâu.

Trình bày summary findings cho user.

## Phase 3: Clarifying Questions

**CRITICAL — KHÔNG ĐƯỢC SKIP.**

**Mục tiêu**: Loại bỏ mọi ambiguity trước khi thiết kế.

1. Review findings từ Phase 2 + feature request
2. Xác định aspects chưa rõ: edge cases, error handling, integration points, scope boundaries, backward compatibility, performance needs
3. **Trình bày TẤT CẢ câu hỏi cho user** — organized, rõ ràng
4. **ĐỢI user trả lời** trước khi sang Phase 4

Nếu user nói "tùy bạn" → đưa recommendation cụ thể, xin explicit confirmation.

## Phase 4: Architecture Design

**Mục tiêu**: Thiết kế approaches với trade-offs.

**Feature nhỏ** (1-2 files, pattern rõ từ codebase): 1 approach đủ, không cần dispatch architect agents — lead tự propose.
**Feature vừa/lớn**: Launch **2-3 code-architect agents song song** với focuses khác:
- Agent 1: "Minimal changes — smallest diff, maximum reuse"
- Agent 2: "Clean architecture — maintainability, elegant abstractions"
- Agent 3: "Pragmatic balance — speed + quality"

Review tất cả approaches, form opinion. Trình bày user:
- Summary mỗi approach
- Trade-offs comparison
- **Đề xuất rõ approach nào** + lý do
- **Hỏi user chọn**

## Phase 5: Implementation

**KHÔNG bắt đầu khi chưa có user approval.**

1. Đợi user explicit approve approach
2. Đọc lại files liên quan từ Phase 2
3. Implement theo architecture đã chọn
4. Follow codebase conventions (đọc CLAUDE.md)
5. Update todo list theo tiến độ

## Phase 6: Quality Review

**Mục tiêu**: Verify code quality trước khi báo xong.

**Feature nhỏ** (≤3 files changed): 1 code-reviewer agent đủ.
**Feature vừa/lớn**: Launch **2-3 agents song song**:
- Agent 1 (code-reviewer): simplicity, DRY, readability
- Agent 2 (code-reviewer): bugs, functional correctness
- Agent 3 (code-reviewer): project conventions, abstractions

Consolidate findings (đếm, dedup, severity cao hơn wins). Trình bày user:
- Issues tìm được (grouped by severity)
- **Hỏi user**: fix ngay, fix sau, hoặc proceed as-is?
- Fix theo user decision

## Phase 7: Summary

1. Mark tất cả todos complete
2. Tóm tắt:
   - Đã build gì
   - Key decisions đã chốt
   - Files modified
   - Suggested next steps

## KHÔNG làm

- KHÔNG skip Phase 3 (Clarifying Questions) — đây là phase quan trọng nhất
- KHÔNG implement trước khi user approve architecture
- KHÔNG dispatch >3 agents cùng lúc (cost + quality)
- KHÔNG assume codebase conventions — đọc CLAUDE.md + scan existing code
