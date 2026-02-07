# Validation and Testing

Use the IDAES Property Test Harness to validate the package.

## Step-by-step checklist

1. Build a minimal flowsheet.
- Instantiate `FlowsheetBlock` and the parameter block.
- Build a single state block instance.

2. Check unit consistency.
- Call `assert_units_consistent`.

3. Check degrees of freedom.
- Verify DOF is zero for a defined state.

4. Initialize.
- Run the property package initialization routine.
- Ensure no initialization errors.

5. Run harness tests.
- Use `PropertyTestHarness`.
- Confirm required properties exist.

6. Add targeted property tests.
- Validate a few known values at representative conditions.
- Check phase equilibrium behavior where applicable.

## Harness

Use `idaes/models/properties/tests/test_harness.py` as the baseline. See `references/test_harness.md` for details.

## Template

Start from `assets/templates/test_property_package.py`.
