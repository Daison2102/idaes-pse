# Required Properties Catalog

This file defines the property-coverage gates used by the skill.

## Coverage Modes

1. `minimum`: mandatory baseline for a viable package.
2. `comprehensive`: full-featured package target.

If equilibrium is requested, equilibrium entries marked `Equilibrium-required` become mandatory even in `minimum` mode.

## Minimum Required Properties

| Property / Method | Applicability | Notes |
|---|---|---|
| `flow` state variable set (from chosen state definition) | Always | Exact variables depend on `FTPx`/`FpcTP`/`FcTP`/`FPhx`/`FcPh`. |
| `temperature` | Always | State variable or derived variable per definition. |
| `pressure` | Always | State variable or derived variable per definition. |
| Composition state variables | Always | Examples: `mole_frac_comp`, `flow_mol_comp`, `mole_frac_phase_comp`. |
| `phase_frac` | Multiphase | Mandatory for multiphase formulations. |
| `flow_mol_phase_comp` or equivalent flow representation | Always | Must support material flow terms consistently. |
| `get_material_flow_terms(p, j)` | Class-based | Required IDAES contract method. |
| `get_enthalpy_flow_terms(p)` | Class-based | Required IDAES contract method. |
| `get_material_density_terms(p, j)` | Class-based | Required IDAES contract method. |
| `get_energy_density_terms(p)` | Class-based | Required IDAES contract method. |
| `default_material_balance_type()` | Class-based | Required IDAES contract method. |
| `default_energy_balance_type()` | Class-based | Required IDAES contract method. |
| `get_material_flow_basis()` | Class-based | Required IDAES contract method. |
| `define_state_vars()` | Class-based | Required state-variable exposure. |
| `define_display_vars()` | Class-based | Required report-facing exposure. |
| `initialize(...)` | Class-based | StateBlock method class contract. |
| `release_state(...)` | Class-based | StateBlock method class contract. |
| `phase_equilibrium_form` | Equilibrium-required | Required for equilibrium components. |
| `phases_in_equilibrium` | Equilibrium-required | Pair list required when equilibrium is active. |
| `phase_equilibrium_state` | Equilibrium-required | Must match EOS/equilibrium method. |

## Comprehensive Required Properties

Comprehensive mode includes all minimum entries plus the following.

### Core Thermodynamics

| Property | Applicability | Notes |
|---|---|---|
| `mw` / `mw_phase` | Recommended all | Useful for mass/molar conversions and checks. |
| `dens_mol` / `dens_mol_phase` | All practical packages | Commonly needed by unit models and diagnostics. |
| `enth_mol` / `enth_mol_phase` | All practical packages | Required for energy balances in most units. |
| `entr_mol` / `entr_mol_phase` | Recommended | Needed for broader thermodynamic analysis. |
| `cp_mol_ig_comp` | Vapor or gas methods | Method-dependent parameter set required. |
| `enth_mol_ig_comp` | Vapor or gas methods | Method-dependent parameter set required. |
| `entr_mol_ig_comp` | Vapor or gas methods | Method-dependent parameter set required. |
| `dens_mol_liq_comp` | Liquid packages | Required for many liquid formulations. |
| `enth_mol_liq_comp` | Liquid packages | Required for liquid enthalpy calculations. |
| `entr_mol_liq_comp` | Liquid packages | Required for liquid entropy calculations. |

### Equilibrium and Phase Transition

| Property | Applicability | Notes |
|---|---|---|
| `pressure_sat_comp` | VLE or phase-change systems | Pure component saturation model support. |
| `temperature_bubble` | Equilibrium-focused | Bubble point calculations. |
| `temperature_dew` | Equilibrium-focused | Dew point calculations. |
| `pressure_bubble` | Equilibrium-focused | Bubble pressure calculations. |
| `pressure_dew` | Equilibrium-focused | Dew pressure calculations. |
| EOS interaction parameters (for example `PR_kappa`) | Cubic EOS | Package-level parameters for binary interactions. |

### Transport (include when requested)

| Property | Applicability | Notes |
|---|---|---|
| Phase viscosity method | Transport-required | Example: Wilke + component transport inputs. |
| Phase thermal conductivity method | Transport-required | Example: WMS + component transport inputs. |
| Required component transport parameters | Transport-required | Example: Lennard-Jones and Eucken-related coefficients. |

### Robustness and Diagnostics

| Property / capability | Applicability | Notes |
|---|---|---|
| `model_check` | Recommended | Bounds and consistency sanity checks. |
| Scaling factors for major vars/constraints | Recommended | Improves solve robustness. |
| Unit consistency validation support | Always | Required test gate. |

## Coverage Table Template

Use this format in skill output before scaffold generation.

| Item | Mode-required? | Status (`covered`/`missing`/`custom-implementation-needed`) | Branch | Notes |
|---|---|---|---|---|
| `get_enthalpy_flow_terms` | Minimum | covered | class | Implemented in StateBlockData |

## Gate Rules

1. Do not scaffold if any minimum-required item is `missing`.
2. In comprehensive mode, unresolved items require explicit user-accepted deferral notes.
3. If equilibrium is requested, equilibrium-required entries cannot be deferred.
