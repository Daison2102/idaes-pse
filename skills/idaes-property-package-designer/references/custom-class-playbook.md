# Custom Class Playbook

## Objective
Design a fully custom class-based property package with explicit control over equations and block behavior.

## Required Class Structure

1. `PhysicalParameterBlock` subclass
2. `StateBlock` methods class
3. `StateBlockData` subclass

## Procedure

### 1) Parameter Block Design
- In `build`, call `super().build()` first.
- Set `_state_block_class`.
- Define components and phases.
- Define shared parameters and reference state values.
- Implement `define_metadata` with:
  - `add_properties`
  - `add_default_units`

### 2) State Block Methods Design
- Implement `initialize`.
- Implement `release_state`.
- Include state fixing, solve sequence, and unfix policy.
- Include `hold_state` behavior and returned flags.

### 3) State Block Data Design
- In `build`, call `super().build()` first.
- Define state variables and principal constraints.
- Handle `defined_state` logic safely (for example sum-fraction constraints).
- Provide build-on-demand methods for optional properties.

### 4) Required Framework Methods
Provide and validate:

- `get_material_flow_basis`
- `get_material_flow_terms`
- `get_material_density_terms`
- `get_enthalpy_flow_terms`
- `get_energy_density_terms`
- `default_material_balance_type`
- `default_energy_balance_type`
- `define_state_vars`
- `define_display_vars` (or rely on default fallback)

### 5) Initialization and Scaling
- Define a staged initialization path.
- Add scaling factors for key variables and constraints.
- Include fallback behavior for poor initial guesses.

### 6) Validation
- Run structural checks and consistency checks.
- Add tests that verify method availability and solvability.
