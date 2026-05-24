# Appendix B: Bug Fix

Read this appendix alongside the universal workflow when the plan is to fix a defect.

## Core Constraint

Do not fix a bug that cannot be reproduced. Do not close a bug that cannot be tested.

## Phase 1 Addition

Document exact reproduction steps. The inventory includes: where the bug manifests, what inputs trigger it, what the wrong behavior is, what the correct behavior should be.

## Phase 2 Addition

**Agent A:** Find the root cause, not the symptom. Also check: does the same root cause exist in similar code elsewhere?

**Agent B:** Check whether any existing test covers this behavior. If not, the test gap is part of the finding.

## Phase 4 Addition

The plan must include:
1. A test that fails on current code and passes after the fix (write before touching code)
2. Root cause statement (one sentence: "The bug occurs because X does Y when it should do Z")
3. The fix
4. A regression test for the future

## Phase 7 Addition

Verify the fix does not regress related behavior. Check all callers of the fixed function for assumptions that the old (buggy) behavior satisfied — they may break under the correct behavior.
