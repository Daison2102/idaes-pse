# Class-Based Property Package Patterns

## Step-by-step checklist

1. Identify a closest class-based example in the codebase.
- Search under `idaes/models/properties/` for non-modular packages.

2. Define the parameter block.
- Subclass `PhysicalParameterBlock`.
- Add component and phase sets.
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
- Register properties.
- Define default units.

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
