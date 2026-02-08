# Parameter Requirements by Method

Use this reference to build parameter completeness checks.

## Global Rules

1. All numeric parameters require explicit units (or explicit `None` when dimensionless).
2. Track source for each parameter value.
3. Maintain consistent unit basis within package configuration.

## Core Component Parameters

These are commonly required by many EOS/property methods.

| Key | Typical requirement |
|---|---|
| `mw` | Molecular weight |
| `temperature_crit` | Critical temperature |
| `pressure_crit` | Critical pressure |
| `omega` | Acentric factor (cubic EOS especially) |

## Ideal-Gas Thermo Methods (`NIST`, `RPP4`, `RPP5`)

Typical keys (method-specific variants may apply):

| Key | Purpose |
|---|---|
| `cp_mol_ig_comp_coeff` | Ideal-gas heat capacity coefficients |
| `enth_mol_form_vap_comp_ref` | Vapor formation enthalpy at reference |
| `entr_mol_form_vap_comp_ref` | Vapor formation entropy at reference |

## Liquid Property Methods (`Perrys` and similar)

Typical keys:

| Key | Purpose |
|---|---|
| `dens_mol_liq_comp_coeff` | Liquid density coefficients |
| `cp_mol_liq_comp_coeff` | Liquid heat-capacity coefficients |
| `enth_mol_form_liq_comp_ref` | Liquid formation enthalpy at reference |
| `entr_mol_form_liq_comp_ref` | Liquid formation entropy at reference |

## Saturation Pressure Methods

Typical keys (method-dependent):

| Key | Purpose |
|---|---|
| `pressure_sat_comp_coeff` | Saturation pressure coefficients |

## Cubic EOS Package-Wide Parameters

| Key | Purpose |
|---|---|
| `PR_kappa` (or EOS-specific interaction map) | Binary interaction parameters for component pairs |

For `n` components, provide a complete pair mapping for all `(i, j)` pairs.

## Transport-Related Parameters

Only required when transport properties are included.

| Key | Purpose |
|---|---|
| `lennard_jones_sigma` | Molecular diameter parameter |
| `lennard_jones_epsilon_reduced` | LJ energy parameter |
| `f_int_eucken` | Eucken correction/supporting factor |
| method-specific viscosity coefficients | if required by selected transport model |
| method-specific conductivity coefficients | if required by selected transport model |

## Parameter Gap Handling

When required values are missing:
1. Try official IDAES code examples and docs first.
2. If absent, search trusted external sources and record provenance.
3. If still unavailable, insert explicit placeholder with clear TODO tag and source-needed annotation.

Placeholder format recommendation:

```python
"temperature_crit": (TODO_Tc, pyunits.K),  # TODO source: NIST/Perry/etc.
```
