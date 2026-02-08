# Available IDAES Methods Catalog

All imports from `idaes.models.properties.modular_properties.*`

---

## Equations of State

| EOS | Import | Phase | Options |
|-----|--------|-------|---------|
| Ideal | `eos.ideal.Ideal` | Vapor, Liquid | None |
| Peng-Robinson | `eos.ceos.Cubic` | Vapor, Liquid | `{"type": CubicType.PR}` |
| Soave-Redlich-Kwong | `eos.ceos.Cubic` | Vapor, Liquid | `{"type": CubicType.SRK}` |
| e-NRTL | `eos.enrtl.ENRTL` | Liquid (electrolyte) | Complex |

---

## State Definitions

| Formulation | Import | State Variables | Flash? |
|-------------|--------|----------------|--------|
| `FTPx` | `state_definitions.FTPx` | flow_mol, T, P, x | Yes |
| `FpcTP` | `state_definitions.FpcTP` | flow_mol_phase_comp, T, P | No |
| `FcTP` | `state_definitions.FcTP` | flow_mol_comp, T, P | Yes |
| `FPhx` | `state_definitions.FPhx` | flow_mol, H, P, phase_frac, T | Yes |
| `FcPh` | `state_definitions.FcPh` | flow_mol_comp, P, H | Yes |

---

## Pure Component Property Methods

### Vapor Phase (Ideal Gas)

| Method | Import | Coefficients | Equation Type |
|--------|--------|-------------|---------------|
| RPP3 | `pure.RPP3` | A, B, C | 3rd-order polynomial |
| RPP4 | `pure.RPP4` | A, B, C, D | 4th-order polynomial |
| RPP5 | `pure.RPP5` | A, B, C, D, E | 5th-order polynomial |
| NIST | `pure.NIST` | A-H (Shomate) | Shomate equation |

Each provides: `cp_mol_ig_comp`, `enth_mol_ig_comp`, `entr_mol_ig_comp`
RPP4 and NIST also provide: `pressure_sat_comp`

### Liquid Phase

| Method | Import | Properties Provided |
|--------|--------|-------------------|
| Perrys | `pure.Perrys` | `dens_mol_liq_comp`, `enth_mol_liq_comp`, `entr_mol_liq_comp` |
| ConstantProperties | `pure.ConstantProperties` | Constant-value properties |

### Transport Properties (Component-Level)

| Method | Import | Property |
|--------|--------|----------|
| ChapmanEnskogLennardJones | `pure.ChapmanEnskogLennardJones` | `visc_d_phase_comp` (gas) |
| Eucken | `pure.Eucken` | `therm_cond_phase_comp` (gas) |
| ChungPure | `pure.ChungPure` | `visc_d_phase_comp` (gas) |

---

## Phase Equilibrium

### VLE State Formulation

| Method | Import | Best For |
|--------|--------|----------|
| `SmoothVLE` | `phase_equil.SmoothVLE` | Ideal EOS systems |
| `CubicComplementarityVLE` | `phase_equil.CubicComplementarityVLE` | Cubic EOS systems |

### Equilibrium Form (per component)

| Form | Import | Equation |
|------|--------|----------|
| `fugacity` | `phase_equil.forms.fugacity` | `f_V = f_L` |
| `log_fugacity` | `phase_equil.forms.log_fugacity` | `ln(f_V) = ln(f_L)` |

### Bubble-Dew Methods

| Method | Import | Best For |
|--------|--------|----------|
| `IdealBubbleDew` | `phase_equil.bubble_dew.IdealBubbleDew` | Ideal EOS |
| `LogBubbleDew` | `phase_equil.bubble_dew.LogBubbleDew` | Cubic EOS |

---

## Transport Property Mixing Rules (Phase-Level)

| Method | Import | Property | Applies To |
|--------|--------|----------|-----------|
| `ViscosityWilke` | `transport_properties.ViscosityWilke` | `visc_d_phase` | Gas mixtures |
| `ThermalConductivityWMS` | `transport_properties.ThermalConductivityWMS` | `therm_cond_phase` | Gas mixtures |
| `NoMethod` | `transport_properties.NoMethod` | Placeholder | Phases without transport |

---

## Recommended Combinations

### Simple Ideal VLE (e.g., Benzene-Toluene)
```
EOS:           Ideal (both phases)
State:         FTPx
VLE:           SmoothVLE + IdealBubbleDew + fugacity
Vapor props:   RPP4
Liquid props:  Perrys
```

### Cubic EOS VLE (e.g., Methanol Synthesis)
```
EOS:           Cubic/PR (both phases)
State:         FTPx
VLE:           CubicComplementarityVLE + LogBubbleDew + log_fugacity
Vapor props:   NIST or RPP4
Liquid props:  Perrys
Transport:     ViscosityWilke + ThermalConductivityWMS (vapor)
               NoMethod (liquid)
```

### Vapor-Only (e.g., Combustion Gas)
```
EOS:           Ideal (vapor only)
State:         FTPx (single phase)
VLE:           None
Vapor props:   NIST or RPP4
Transport:     ViscosityWilke + ThermalConductivityWMS (optional)
```
