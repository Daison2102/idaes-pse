# Build with Class-Based Property Package

Use this when you need full control over state variables, constraints, or property equations.

## Step-by-step checklist

1. Create the parameter block class.
- Subclass `PhysicalParameterBlock`.
- Define `component_list` and `phase_list`.
- Assign the state block pointer (`state_block_class` / `_state_block_class`).
- Add parameters and default values.
- If required by intake, define `element_list` and `element_comp`.

2. Create the state block class.
- Subclass `StateBlock` and `StateBlockData`.
- Define state variables and bounds.
- Define auxiliary variables and expressions.

3. Implement property constraints.
- Add material property constraints.
- Add energy property constraints.
- Add equilibrium constraints if needed.

4. Implement required interface methods.
- `get_material_flow_terms`
- `get_enthalpy_flow_terms`
- `get_material_density_terms` if needed
- `get_energy_density_terms` if needed

5. Provide metadata (required, not optional).
- Implement `define_metadata`.
- Define default units using `add_default_units(...)`.
- Register all supported constructed properties using `add_properties(...)`.
- Ensure every metadata property maps to an implemented variable/expression/method.

6. Add scaling.
- Apply scaling to state vars and constraints.
- Add scaling for key computed properties.

7. Add initialization.
- Implement `initialize()` or use an initializer.
- Ensure initialization can revert fixed vars.

8. Validate.
- Use the harness tests and unit checks.

## PhysicalParameterBlock Compliance Gates

Do not finalize a class-based package until all gates pass:

1. Parameter block exposes `component_list` and `phase_list`.
2. Parameter block sets state block linkage.
3. If elemental balance is in scope, `element_list` and `element_comp` exist.
4. `define_metadata` includes both units and property registrations.
5. State block implements required interface methods referenced by unit models.

## Useful References

- `references/class_patterns.md`
- `references/scaling_init.md`
- `references/test_harness.md`
- `references/mcp_search_tips.md`

## Template

Start from `assets/templates/class_property_package.py`.
