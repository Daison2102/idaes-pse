# Initialization and Scaling

This reference defines robust initialization and scaling guidance for both approaches.

## Initialization Strategy

## Generic Framework

1. Build parameter block.
2. Build state block with `defined_state=True` for inlet-like states.
3. Fix state variables at nominal values.
4. Trigger key properties needed by target unit model.
5. Run state initialization.
6. Solve and verify optimal termination.

## Class-Based Framework

Implement staged initialization in `StateBlock` methods class:

1. Fix state vars (unless already fixed).
2. Deactivate constraints that conflict during temporary fixing (if needed).
3. Initialize derived/equilibrium helper variables.
4. Solve staged system or full system.
5. Reactivate constraints.
6. Release states when `hold_state=False`, else return flags.

## Scaling Strategy

1. Set scaling for state variables first (`flow`, `pressure`, `temperature`, composition variables).
2. Add scaling for derived thermo properties (`enth`, `dens`, equilibrium helpers).
3. Scale constraints based on inverse max magnitude or known physical scales.
4. Recompute/validate scaling before final solve.

## Typical Starting Factors

These are starting heuristics; adapt to system magnitude.

| Quantity | Typical scale idea |
|---|---|
| Pressure (Pa) | ~`1e-5` |
| Temperature (K) | by bounds-based scale |
| Molar flow | inverse nominal flow |
| Mole fractions | around order `1` |
| Enthalpy | inverse nominal enthalpy |

## Convergence Aids for VLE/Cubic Systems

1. Use reasonable initial `temperature`, `pressure`, and phase splits.
2. Initialize with smoother settings where applicable, then tighten if needed.
3. Avoid unbounded sweep transitions without intermediate continuation.

## Acceptance Checks After Initialization

1. Degrees of freedom are zero for initialized solve case.
2. No obvious variable bound violations.
3. Key properties are finite and physically plausible.
4. Solver termination is optimal or acceptable.
