# Component Parameter Data Requirements

This document lists the exact parameters required for each pure component
property method and EOS in the IDAES Generic Framework.

---

## Always Required

| Parameter | Format | Description |
|-----------|--------|-------------|
| `mw` | `(value, pyunits.kg/pyunits.mol)` | Molecular weight |
| `pressure_crit` | `(value, pyunits.Pa)` | Critical pressure |
| `temperature_crit` | `(value, pyunits.K)` | Critical temperature |

If using Cubic EOS, also required:
| Parameter | Format | Description |
|-----------|--------|-------------|
| `omega` | `value` (dimensionless) | Acentric factor |

---

## Vapor Phase: RPP4 Method

Used for: `enth_mol_ig_comp`, `entr_mol_ig_comp`, `cp_mol_ig_comp`, `pressure_sat_comp`

### Heat Capacity Coefficients

Equation: `Cp = A + B*T + C*T^2 + D*T^3`

```python
"cp_mol_ig_comp_coeff": {
    "A": (value, pyunits.J / pyunits.mol / pyunits.K),
    "B": (value, pyunits.J / pyunits.mol / pyunits.K**2),
    "C": (value, pyunits.J / pyunits.mol / pyunits.K**3),
    "D": (value, pyunits.J / pyunits.mol / pyunits.K**4),
},
```

Source: Reid, Prausnitz & Polling, 4th edition

### Reference Enthalpies & Entropies

```python
"enth_mol_form_vap_comp_ref": (value, pyunits.J / pyunits.mol),
"entr_mol_form_vap_comp_ref": (value, pyunits.J / pyunits.mol / pyunits.K),
```

### Saturation Pressure Coefficients (RPP4)

Equation: `ln(Psat/Pc) = (1-Tr)^(-1) * [A*(1-Tr) + B*(1-Tr)^1.5 + C*(1-Tr)^3 + D*(1-Tr)^6]`
where `Tr = T/Tc`

```python
"pressure_sat_comp_coeff": {
    "A": (value, None),
    "B": (value, None),
    "C": (value, None),
    "D": (value, None),
},
```

Source: Reid, Prausnitz & Polling

---

## Vapor Phase: NIST (Shomate) Method

Used for: `enth_mol_ig_comp`, `entr_mol_ig_comp`, `cp_mol_ig_comp`

### Heat Capacity Coefficients

Equation (Shomate): `Cp = A + B*t + C*t^2 + D*t^3 + E/t^2`
where `t = T/1000` (kiloKelvin)

```python
"cp_mol_ig_comp_coeff": {
    "A": (value, pyunits.J / pyunits.mol / pyunits.K),
    "B": (value, pyunits.J / pyunits.mol / pyunits.K / pyunits.kiloK),
    "C": (value, pyunits.J / pyunits.mol / pyunits.K / pyunits.kiloK**2),
    "D": (value, pyunits.J / pyunits.mol / pyunits.K / pyunits.kiloK**3),
    "E": (value, pyunits.J * pyunits.kiloK**2 / pyunits.mol / pyunits.K),
    "F": (value, pyunits.kJ / pyunits.mol),
    "G": (value, pyunits.J / pyunits.mol / pyunits.K),
    "H": (value, pyunits.kJ / pyunits.mol),
},
```

Source: NIST WebBook (https://webbook.nist.gov)

### Saturation Pressure Coefficients (NIST Antoine)

Equation: `log10(Pbar) = A - B/(T + C)`

```python
"pressure_sat_comp_coeff": {
    "A": (value, None),
    "B": (value, pyunits.K),
    "C": (value, pyunits.K),
},
```

Source: NIST WebBook

---

## Liquid Phase: Perrys Method

Used for: `dens_mol_liq_comp`, `enth_mol_liq_comp`, `entr_mol_liq_comp`

### Liquid Molar Density Coefficients

Equation (type 1): `rho = c1 / c2^(1 + (1 - T/c3)^c4)` [kmol/m^3]

```python
"dens_mol_liq_comp_coeff": {
    "eqn_type": 1,
    "1": (value, pyunits.kmol * pyunits.m**-3),
    "2": (value, None),
    "3": (value, pyunits.K),
    "4": (value, None),
},
```

Source: Perry's Chemical Engineers' Handbook, Table 2-32

### Liquid Heat Capacity Coefficients

Equation: `Cp = c1 + c2*T + c3*T^2 + c4*T^3 + c5*T^4` [J/kmol/K]

```python
"cp_mol_liq_comp_coeff": {
    "1": (value, pyunits.J / pyunits.kmol / pyunits.K),
    "2": (value, pyunits.J / pyunits.kmol / pyunits.K**2),
    "3": (value, pyunits.J / pyunits.kmol / pyunits.K**3),
    "4": (value, pyunits.J / pyunits.kmol / pyunits.K**4),
    "5": (value, pyunits.J / pyunits.kmol / pyunits.K**5),
},
```

Source: Perry's Chemical Engineers' Handbook, Table 2-153

### Reference Enthalpies & Entropies (Liquid)

```python
"enth_mol_form_liq_comp_ref": (value, pyunits.J / pyunits.mol),
"entr_mol_form_liq_comp_ref": (value, pyunits.J / pyunits.mol / pyunits.K),
```

---

## Transport Properties (Optional)

### Chapman-Enskog-Lennard-Jones (Gas Viscosity)

Used for: `visc_d_phase_comp` in the vapor phase

```python
"lennard_jones_sigma": (value, pyunits.angstrom),
"lennard_jones_epsilon_reduced": (value, pyunits.K),  # epsilon/k_B
```

### Eucken (Gas Thermal Conductivity)

Used for: `therm_cond_phase_comp` in the vapor phase

```python
"f_int_eucken": value,  # dimensionless, typically 1
```

---

## Cubic EOS: Global Binary Interaction Parameters

Located in the top-level `"parameter_data"` key, not per-component:

```python
"parameter_data": {
    "PR_kappa": {
        ("comp_a", "comp_a"): 0.0,
        ("comp_a", "comp_b"): value,
        ("comp_b", "comp_a"): value,
        ("comp_b", "comp_b"): 0.0,
    }
}
```

Self-interaction is always 0.0. Cross-interactions default to 0.0 if unknown.

---

## Quick Reference: What Each EOS + Method Combination Needs

### Ideal EOS + RPP4 + Perrys (VLE)
Per component:
- `mw`, `pressure_crit`, `temperature_crit`
- `cp_mol_ig_comp_coeff` (A, B, C, D)
- `pressure_sat_comp_coeff` (A, B, C, D)
- `enth_mol_form_vap_comp_ref`, `entr_mol_form_vap_comp_ref`
- `cp_mol_liq_comp_coeff` (1-5)
- `dens_mol_liq_comp_coeff` (eqn_type, 1-4)
- `enth_mol_form_liq_comp_ref`, `entr_mol_form_liq_comp_ref`

### Ideal EOS + NIST + Perrys (VLE)
Per component:
- `mw`, `pressure_crit`, `temperature_crit`
- `cp_mol_ig_comp_coeff` (A-H, Shomate)
- `pressure_sat_comp_coeff` (A, B, C - Antoine)
- `cp_mol_liq_comp_coeff` (1-5)
- `dens_mol_liq_comp_coeff` (eqn_type, 1-4)
- `enth_mol_form_liq_comp_ref`, `entr_mol_form_liq_comp_ref`

### Cubic (PR/SRK) + RPP4/NIST + Perrys (VLE)
Per component: Same as above, PLUS:
- `omega` (acentric factor)

Global:
- `PR_kappa` binary interaction matrix

### Vapor-Only (no VLE)
Per component:
- `mw`, `pressure_crit`, `temperature_crit`
- `cp_mol_ig_comp_coeff`
- `enth_mol_form_vap_comp_ref`, `entr_mol_form_vap_comp_ref`
- No liquid-phase or saturation pressure parameters needed
