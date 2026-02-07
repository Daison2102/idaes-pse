# Class-Based Property Package Patterns

## Step-by-step checklist

1. Identify a closest class-based example in the codebase.
- Search under `idaes/models/properties/` for non-modular packages.

2. Define the parameter block.
- Subclass `PhysicalParameterBlock`.
- Add component and phase sets (`component_list`, `phase_list`).
- Set state block linkage (`state_block_class` or `_state_block_class`).
- Add `element_list` and `element_comp` when elemental balances are required.
- Add required parameters and defaults.

3. Define the state block.
- Subclass `StateBlockData`.
- Define state variables and bounds.
- Add expressions and constraints for properties.

4. Implement required interface methods.
- `get_material_flow_terms`
- `get_enthalpy_flow_terms`
- `get_material_density_terms` and `get_energy_density_terms` as needed.

5. Define metadata.
- Implement `define_metadata`.
- Register properties with `add_properties(...)`.
- Define default units with `add_default_units(...)`.
- Keep metadata entries aligned with implemented variables/expressions.

6. Add scaling and initialization.
- Use IDAES scaling utilities.
- Provide an initialization method.

7. Validate with test harness.
- Use `PropertyTestHarness`.

## Codebase Pointers

- Base classes: `idaes/core/base/` and `idaes/core/util/`
- Property examples: `idaes/models/properties/` (non-modular packages)
- Test harness: `idaes/models/properties/tests/test_harness.py`

## Required Interfaces

- `get_material_flow_terms`
- `get_enthalpy_flow_terms`
- `get_material_density_terms` or `get_energy_density_terms` if needed
- `default_initializer` (optional but recommended)

Use this when modular methods are insufficient or customization is heavy.

## Canonical Minimal Pattern

1. `PhysicalParameterBlock` subclass
- declares `component_list` and `phase_list`
- declares optional `element_list` and `element_comp`
- assigns state block linkage
- defines shared parameters

2. `StateBlockData` subclass
- defines state variables
- defines property relations
- implements required IDAES interface methods

3. Metadata contract
- `define_metadata` includes units and property registration
- each registered property is constructible on the state block

## Common Errors to Avoid

- Missing state block linkage in parameter block.
- Registering properties in metadata that are never constructed.
- Omitting `element_list`/`element_comp` when elemental balances are expected.
- Inconsistent phase/component indexing between parameters and constraints.
