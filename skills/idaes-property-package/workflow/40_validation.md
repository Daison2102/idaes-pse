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

7. Run generic framework contract checks (generic packages).
- Verify required top-level keys exist.
- Verify phase/component compatibility (`valid_phase_types`, optional phase `component_list`).
- Verify equilibrium triad consistency when equilibrium is enabled.
- Verify method-parameter completeness for selected pure/transport/EOS methods.

8. Run generic smoke solve checks.
- Build `GenericParameterBlock(**configuration)`.
- Build a minimal unit model (Flash for VLE packages).
- Run with simple conditions (e.g., zero heat duty and zero pressure drop).
- Confirm solver convergence and physically sensible phase split.

9. Run generic class-definition checks (if selected).
- Confirm package class inherits from `GenericParameterData`.
- Confirm `configure` and `parameters` are implemented.
- Confirm class-based generic package constructs and solves a flash smoke test.

10. Run class contract checks (class-based packages).
- Verify `component_list` and `phase_list` exist.
- Verify state block linkage exists (`state_block_class` / `_state_block_class`).
- If elemental balance is in scope, verify `element_list` and `element_comp`.
- Verify `define_metadata` registers units and expected properties.

11. Run a minimal build smoke test.
- Instantiate `FlowsheetBlock` and parameter block.
- Build one state block and touch each metadata-registered property.
- Confirm no missing construction methods.

## Harness

Use `idaes/models/properties/tests/test_harness.py` as the baseline. See `references/test_harness.md` for details.

## Template

Start from `assets/templates/test_property_package.py`.
