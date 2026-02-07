# Property Test Harness

Use the standard IDAES test harness to validate property packages.

## Step-by-step checklist

1. Create a test class inheriting `PropertyTestHarness`.
2. Set `self.prop_pack` to your parameter block class.
3. Provide `self.param_args` and `self.prop_args` if needed.
4. Run unit tests and fix any missing methods.
5. Confirm unit consistency and DOF checks pass.

## Location

- `idaes/models/properties/tests/test_harness.py`

## Typical usage

- Create a test class and inherit `PropertyTestHarness`.
- Provide the property package class and constructor args.
- Run harness tests for state variables and property methods.

Also check:

- DOF is zero for a defined state.
- Unit consistency via `assert_units_consistent`.

Use `assets/templates/test_property_package.py` as a starting point.
