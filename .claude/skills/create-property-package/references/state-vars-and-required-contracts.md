# State Variables and Required Contracts

This reference is used for class-based implementations and to validate state-definition consistency in generic packages.

## Supported State Definitions

| State definition | Typical primary state variables | Typical use |
|---|---|---|
| `FTPx` | `flow_mol`, `temperature`, `pressure`, `mole_frac_comp` | Common VLE and general process models |
| `FpcTP` | `flow_mol_phase_comp`, `temperature`, `pressure` | Explicit phase-component flow tracking |
| `FcTP` | `flow_mol_comp`, `temperature`, `pressure` | Component-flow driven systems |
| `FPhx` | `flow_mol`, `pressure`, `enth_mol`, `mole_frac_comp` | Enthalpy-based flash/energy coupling |
| `FcPh` | `flow_mol_comp`, `pressure`, `enth_mol` | Component-flow + enthalpy formulations |

When uncertain, confirm exact variable names/behavior using official state-definition modules and tests.

## Mandatory Class-Based Contract Methods

The class-based `StateBlockData` implementation must provide:

1. `get_material_flow_terms(p, j)`
2. `get_enthalpy_flow_terms(p)`
3. `get_material_density_terms(p, j)`
4. `get_energy_density_terms(p)`
5. `default_material_balance_type()`
6. `default_energy_balance_type()`
7. `get_material_flow_basis()`
8. `define_state_vars()`
9. `define_display_vars()`

The `StateBlock` methods class must provide:
1. `initialize(...)`
2. `release_state(...)`

## Metadata Synchronization Rules

1. Every build-on-demand property listed in `define_metadata` must map to a real method name.
2. Every always-built property should declare method `None`.
3. Property naming should follow IDAES naming conventions to avoid downstream unit-model mismatch.

## Consistency Checks

1. State variable set yields correct degrees of freedom when fixed.
2. Material and energy flow terms are dimensionally consistent.
3. Report/display vars align with expected process interface semantics.
4. Initialization can fix/unfix the chosen state vars without algebraic conflict.
