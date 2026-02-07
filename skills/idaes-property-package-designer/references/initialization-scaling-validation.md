# Initialization, Scaling, and Validation

## Initialization Design

1. Specify state variables fixed at initialization entry.
2. Define conditional deactivation for constraints tied to `defined_state=False` behavior.
3. Define solve sequence and stopping conditions.
4. Define `hold_state` and release logic.

## Scaling Design

1. Provide default scaling factors for all state variables.
2. Provide explicit scaling for fragile algebraic constraints.
3. Document rationale for each non-default scaling factor.
4. Add a review step for extreme-value states.

## Validation Layers

1. `Structural`
- Parameter block and state block construct cleanly.
- Metadata includes properties and default units.

2. `Consistency`
- Units are consistent.
- Degrees of freedom are as expected at defined test points.

3. `Behavior`
- Initialization succeeds at representative states.
- Solve converges for at least one nominal and one edge case.

4. `Regression`
- Tests detect missing required methods and metadata regressions.

## Harness Guidance
When practical, mirror official property harness patterns from IDAES tests for method availability and model consistency checks.
