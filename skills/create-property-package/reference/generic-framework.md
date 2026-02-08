# Generic Property Package Framework Guide

## Overview

The Generic Framework creates property packages from a Python configuration
dictionary. No subclassing is needed - IDAES's `GenericParameterBlock`
consumes the dictionary and constructs all variables, constraints, and
property methods automatically.

## Configuration Dictionary Structure

A configuration dictionary has these top-level keys:

```python
configuration = {
    "components": { ... },           # Required
    "phases": { ... },               # Required
    "base_units": { ... },           # Required
    "state_definition": FTPx,        # Required
    "state_bounds": { ... },         # Required
    "pressure_ref": (...),           # Required
    "temperature_ref": (...),        # Required
    "phases_in_equilibrium": [...],  # If VLE
    "phase_equilibrium_state": {},   # If VLE
    "bubble_dew_method": ...,        # If VLE
    "parameter_data": { ... },       # If cubic EOS (binary params)
}
```

---

## Section 1: Components

Each component entry defines its type, available property methods, and
parameter data.

```python
"components": {
    "component_name": {
        "type": Component,                    # or Solvent, Cation, Anion for electrolytes
        "elemental_composition": {"C": 1, "H": 4},  # Optional but recommended
        "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],  # Optional

        # --- Pure component property methods ---
        # Select methods based on available data and EOS choice

        # Vapor phase properties (pick ONE library per property)
        "enth_mol_ig_comp": RPP4,       # or NIST, RPP5, RPP3
        "entr_mol_ig_comp": RPP4,       # must match enth_mol_ig_comp choice
        "cp_mol_ig_comp": RPP4,         # optional, often auto-derived

        # Liquid phase properties
        "dens_mol_liq_comp": Perrys,    # liquid molar density
        "enth_mol_liq_comp": Perrys,    # liquid molar enthalpy
        "entr_mol_liq_comp": Perrys,    # liquid molar entropy

        # Saturation pressure
        "pressure_sat_comp": RPP4,      # or NIST

        # Transport properties (optional)
        "visc_d_phase_comp": {"Vap": ChapmanEnskogLennardJones},
        "therm_cond_phase_comp": {"Vap": Eucken},

        # Phase equilibrium form (required if VLE)
        "phase_equilibrium_form": {("Vap", "Liq"): fugacity},

        # Parameter data
        "parameter_data": { ... },      # See component-parameters.md
    },
}
```

### Method Selection Guidelines

| System Type | Vapor Methods | Liquid Methods | Psat Method |
|------------|---------------|----------------|-------------|
| Ideal + RPP data | RPP4 | Perrys | RPP4 |
| Ideal + NIST data | NIST | Perrys | NIST |
| Cubic (PR/SRK) + RPP | RPP4 | Perrys | RPP4 |
| Cubic + NIST data | NIST | Perrys | NIST |
| Vapor-only | RPP4 or NIST | (none) | (none) |

### Components That Only Exist in One Phase

If a component only exists in the vapor phase (e.g., non-condensable gas):

```python
"H2": {
    "type": Component,
    "valid_phase_types": [PhaseType.vaporPhase],
    # Only vapor-phase methods needed, no liquid or Psat
    "enth_mol_ig_comp": NIST,
    "entr_mol_ig_comp": NIST,
    # No phase_equilibrium_form needed
    "parameter_data": { ... },
},
```

---

## Section 2: Phases

```python
"phases": {
    "Vap": {
        "type": VaporPhase,
        "equation_of_state": Ideal,     # or Cubic
        # If Cubic:
        # "equation_of_state_options": {"type": CubicType.PR},  # or CubicType.SRK

        # Transport property mixing rules (optional)
        # "visc_d_phase": ViscosityWilke,
        # "therm_cond_phase": ThermalConductivityWMS,
    },
    "Liq": {
        "type": LiquidPhase,
        "equation_of_state": Ideal,     # or Cubic
    },
}
```

### EOS-Specific Notes

**Ideal EOS:**
- No additional parameters needed
- Liquid: Raoult's law for VLE
- Vapor: ideal gas law

**Cubic EOS (PR or SRK):**
- Requires `omega` (acentric factor) for each component
- Requires `PR_kappa` binary interaction parameters in `parameter_data`
- Use `CubicComplementarityVLE` instead of `SmoothVLE`
- Use `LogBubbleDew` instead of `IdealBubbleDew`
- Use `log_fugacity` instead of `fugacity`

---

## Section 3: Base Units

Always specify all 5 base quantities:

```python
"base_units": {
    "time": pyunits.s,
    "length": pyunits.m,
    "mass": pyunits.kg,
    "amount": pyunits.mol,
    "temperature": pyunits.K,
},
```

For scaled systems (large-scale processes), consider:
```python
"base_units": {
    "time": pyunits.s,
    "length": pyunits.m,
    "mass": pyunits.Mg,        # megagrams instead of kg
    "amount": pyunits.kmol,    # kilomoles instead of mol
    "temperature": pyunits.K,
},
```

---

## Section 4: State Definition

| Formulation | State Variables | Best For |
|-------------|----------------|----------|
| `FTPx` | flow_mol, temperature, pressure, mole_frac_comp | General VLE, unknown phase split |
| `FpcTP` | flow_mol_phase_comp, temperature, pressure | Known phase split, no flash needed |
| `FcTP` | flow_mol_comp, temperature, pressure | Component flows known, flash needed |
| `FPhx` | flow_mol, enth_mol, pressure, phase_frac, temperature | Energy specs (isenthalpic) |
| `FcPh` | flow_mol_comp, pressure, enth_mol | Component flows + energy spec |

**Default recommendation**: `FTPx` for most VLE systems.

```python
"state_definition": FTPx,
"state_bounds": {
    "flow_mol": (lower, default, upper, pyunits.mol/pyunits.s),
    "temperature": (lower, default, upper, pyunits.K),
    "pressure": (lower, default, upper, pyunits.Pa),
},
```

The 4-tuple format is: `(lower_bound, default_value, upper_bound, units)`.

---

## Section 5: Phase Equilibrium (if VLE)

### For Ideal EOS:

```python
"phases_in_equilibrium": [("Vap", "Liq")],
"phase_equilibrium_state": {("Vap", "Liq"): SmoothVLE},
"bubble_dew_method": IdealBubbleDew,
```

And on each VLE-participating component:
```python
"phase_equilibrium_form": {("Vap", "Liq"): fugacity},
```

### For Cubic EOS (PR/SRK):

```python
"phases_in_equilibrium": [("Vap", "Liq")],
"phase_equilibrium_state": {("Vap", "Liq"): CubicComplementarityVLE},
"bubble_dew_method": LogBubbleDew,
```

And on each VLE-participating component:
```python
"phase_equilibrium_form": {("Vap", "Liq"): log_fugacity},
```

---

## Section 6: Global Parameter Data

### Binary Interaction Parameters (Cubic EOS)

```python
"parameter_data": {
    "PR_kappa": {
        ("comp_a", "comp_b"): 0.0,
        ("comp_b", "comp_a"): 0.0,
        # ... all pairs including self-interactions
    }
}
```

If binary interaction parameters are unknown, default to 0.0 for all pairs.

---

## Usage: Creating the Parameter Block

```python
from idaes.models.properties.modular_properties.base.generic_property import (
    GenericParameterBlock,
)

# Direct instantiation
m = pyo.ConcreteModel()
m.params = GenericParameterBlock(**configuration)

# Or with a helper function for configurability
m.params = GenericParameterBlock(**get_prop(
    components=["H2O", "CH3OH"],
    phases=["Vap", "Liq"],
    eos=EosType.PR
))
```

---

## Runtime-Configurable Pattern (Advanced)

For packages that need to support different component subsets or EOS choices
at runtime (like the methanol_ceos.py example):

```python
def get_prop(components=None, phases="Vap", eos="PR", scaled=False):
    """Build configuration dictionary with selected options."""
    if components is None:
        components = list(_component_params.keys())

    configuration = {
        "components": {c: _component_params[c] for c in components},
        "phases": {p: _phase_dicts[eos][p] for p in phases},
        "base_units": { ... },
        "state_definition": FTPx,
        "state_bounds": { ... },
        "pressure_ref": (101325, pyunits.Pa),
        "temperature_ref": (298.15, pyunits.K),
    }

    if len(phases) > 1:
        configuration["phases_in_equilibrium"] = [tuple(phases)]
        configuration["phase_equilibrium_state"] = {tuple(phases): SmoothVLE}

    if eos == "PR":
        configuration["parameter_data"] = {
            "PR_kappa": {(a, b): 0 for a in components for b in components}
        }

    return configuration
```
