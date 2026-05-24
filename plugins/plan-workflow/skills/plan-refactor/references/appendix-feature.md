# Appendix C: Feature Addition

Read this appendix alongside the universal workflow when the plan adds new functionality.

## Core Constraint

Define the interface before the implementation. Interface changes are harder to reverse than implementation changes.

## Phase 1 Addition

Map integration points: where does the new feature connect to existing code? What existing contracts does it rely on? What existing behavior does it change?

## Phase 4 Addition

Define the public interface (API shape, function signatures, data types, error cases) before any implementation phase. Interface definition is Phase 4's first output — implementation phases come after.

## Phase 7 Addition

Verify edge cases the happy-path implementation does not cover: empty inputs, error states, concurrent access, missing optional dependencies. Verify existing features are not regressed by the new code path sharing infrastructure.
