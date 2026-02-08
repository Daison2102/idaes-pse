# Class-Based Playbook

Use this playbook when Generic framework is insufficient or user requires explicit classes.

## Required Class Structure

Create three classes:
1. Parameter block class (`PhysicalParameterBlock` descendant).
2. State block methods class (`StateBlock` descendant).
3. State block data class (`StateBlockData` descendant).

## Parameter Block Requirements

1. Decorate with `@declare_process_block_class("<Name>")`.
2. In `build()`:
1. call `super().build()`.
2. set `self._state_block_class`.
3. define components and phases.
4. define global parameters.
3. In `define_metadata(cls, obj)`:
1. add supported properties and methods.
2. define default base units.

## StateBlock Methods Requirements

Implement on StateBlock class:
1. `initialize(...)`
2. `release_state(...)`

Initialization should include:
1. state fixing strategy;
2. optional staged solves;
3. clean state release behavior;
4. clear handling of `hold_state`.

## StateBlockData Requirements

1. Build and expose state variables.
2. Implement core contract methods:
1. `get_material_flow_terms(p, j)`
2. `get_enthalpy_flow_terms(p)`
3. `get_material_density_terms(p, j)`
4. `get_energy_density_terms(p)`
5. `default_material_balance_type()`
6. `default_energy_balance_type()`
7. `get_material_flow_basis()`
8. `define_state_vars()`
9. `define_display_vars()`
3. Add build-on-demand property methods referenced by metadata.
4. Add equilibrium equations, bubble/dew equations, and helper variables if equilibrium is required.

## Implementation Flow

1. Define parameter data and units.
2. Define state variable formulation and closure equations.
3. Add property methods in dependency order.
4. Add equilibrium features.
5. Add initialization.
6. Add scaling factors.
7. Add tests.

## Class-Based Output Expectations

Generated class-based package should include:
1. complete class skeleton with required contracts.
2. clear TODO sections for method equations and parameters.
3. metadata synchronized with actual property method names.
4. explicit initialization and scaling hooks.
