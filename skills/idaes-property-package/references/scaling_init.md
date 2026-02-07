# Scaling and Initialization

Scaling and initialization are critical for convergence and stability.

## Step-by-step checklist

1. Identify key state variables and constraints.
- Focus on variables in balances and equilibrium constraints.

2. Apply scaling factors.
- Use IDAES scaling utilities.
- Apply scaling to state vars and property expressions.

3. Add initialization logic.
- Fix state variables as needed.
- Provide initial guesses for key properties.

4. Verify initialization.
- Confirm initialization does not raise errors.
- Revert fixed variables after initialization.

## Patterns

- Apply scaling factors to state vars and key constraints.
- Use IDAES scaling utilities where possible.
- Add initialization routines that respect phase conditions.

## Codebase pointers

- Scaling utilities: `idaes/core/util/scaling.py`
- Initializers: `idaes/core/initialization/`

Keep initialization minimal but robust, and validate with the test harness.
