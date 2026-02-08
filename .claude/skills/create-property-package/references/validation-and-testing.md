# Validation and Testing

Use this checklist to create and run tests for generated property packages.

## Marker Policy

Each test must have exactly one primary marker:
1. `@pytest.mark.unit`
2. `@pytest.mark.component`
3. `@pytest.mark.integration`
4. `@pytest.mark.performance`

For generated property package smoke tests, default to `@pytest.mark.component` unless the test is strictly unit-level and solver-free.

## Minimum Test Set

1. Parameter block builds successfully.
2. State block builds successfully.
3. Metadata/state vars are present as expected.
4. Units are consistent (`assert_units_consistent`).
5. Representative state can be fixed to zero DOF.
6. Initialization runs without errors.
7. Solve reaches acceptable termination.

## Comprehensive Test Set

1. All minimum tests.
2. Property value checks against expected ranges or reference values.
3. Equilibrium-specific checks (bubble/dew, phase split, equilibrium equations).
4. Transport property checks if included.
5. Stress sweep over selected T/P points where practical.

## Optional Integration Test

Attach property package to a simple unit model (for example flash or heater) and verify:
1. Model construction.
2. Initialization.
3. Solve success.

## Failure Diagnosis Flow

1. Check import path correctness and package construction arguments.
2. Run units consistency.
3. Check DOF and state fixing assumptions.
4. Check missing parameter keys and units.
5. Check scaling factor coverage.
6. Use diagnostics tooling for persistent nonlinear failures.

## Output for Users

Report:
1. Which tests were generated/run.
2. Pass/fail summary.
3. Key failure root-cause notes.
4. Recommended next changes.
