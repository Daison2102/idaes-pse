# Validation Checklist

After generating the property package, validate it by working through this
checklist in order.

---

## 1. Static Checks

- [ ] File has IDAES copyright header
- [ ] All imports resolve (no `ImportError`)
- [ ] Uses current import paths (`idaes.models.properties.modular_properties.*`)
- [ ] All parameter values have Pyomo units attached
- [ ] All parameter values cite a data source in comments
- [ ] Black formatting passes (`black --check <file>`)

## 2. Build Check

```python
import pyomo.environ as pyo
from <module> import configuration  # or MyParameterBlock

m = pyo.ConcreteModel()

# Generic approach:
from idaes.models.properties.modular_properties.base.generic_property import (
    GenericParameterBlock,
)
m.params = GenericParameterBlock(**configuration)

# Class-based approach:
# m.params = MyParameterBlock()
```

- [ ] Parameter block builds without errors
- [ ] `m.params.phase_list` contains expected phases
- [ ] `m.params.component_list` contains expected components

## 3. State Block Check

```python
m.state = m.params.build_state_block(
    [0], defined_state=True, has_phase_equilibrium=True,
)

# Fix state variables to physically reasonable values
m.state[0].flow_mol.fix(1.0)       # mol/s
m.state[0].temperature.fix(350)     # K
m.state[0].pressure.fix(1e5)        # Pa
m.state[0].mole_frac_comp["comp_a"].fix(0.5)
m.state[0].mole_frac_comp["comp_b"].fix(0.5)
```

- [ ] State block builds without errors
- [ ] State variables can be fixed

## 4. Degrees of Freedom

```python
from idaes.core.util.model_statistics import degrees_of_freedom
assert degrees_of_freedom(m.state[0]) == 0
```

- [ ] DoF == 0 after fixing all state variables

## 5. Initialization

```python
initializer = m.state.default_initializer()
initializer.initialize(m.state, output_level=idaeslog.INFO)
```

- [ ] Initialization completes without exceptions
- [ ] Initialization log reports successful convergence

## 6. Solve

```python
from idaes.core.solvers import get_solver
solver = get_solver()
results = solver.solve(m.state, tee=True)

from pyomo.environ import TerminationCondition
assert results.solver.termination_condition == TerminationCondition.optimal
```

- [ ] Solver terminates with `optimal` status
- [ ] No warnings about infeasible constraints

## 7. Property Values

```python
from pyomo.environ import value

# Check key properties are physically reasonable
T = value(m.state[0].temperature)
P = value(m.state[0].pressure)

# Density should be positive
if hasattr(m.state[0], "dens_mol_phase"):
    for p in m.params.phase_list:
        rho = value(m.state[0].dens_mol_phase[p])
        assert rho > 0, f"Density of {p} phase is non-positive: {rho}"

# Vapor density ~ P/(RT) for ideal gas
if "Vap" in m.params.phase_list:
    rho_vap = value(m.state[0].dens_mol_phase["Vap"])
    rho_expected = P / (8.314 * T)  # rough ideal gas estimate
    assert 0.1 * rho_expected < rho_vap < 10 * rho_expected

# Phase fractions should sum to ~1
if hasattr(m.state[0], "phase_frac"):
    pf_sum = sum(value(m.state[0].phase_frac[p]) for p in m.params.phase_list)
    assert abs(pf_sum - 1.0) < 1e-6
```

- [ ] Densities are positive
- [ ] Enthalpies are in reasonable range for the temperature
- [ ] Phase fractions sum to 1.0
- [ ] Mole fractions per phase are between 0 and 1

## 8. Unit Model Integration (Optional)

```python
from idaes.models.unit_models import Heater
import idaes.core.FlowsheetBlock as FlowsheetBlock

m = pyo.ConcreteModel()
m.fs = FlowsheetBlock(dynamic=False)
m.fs.params = GenericParameterBlock(**configuration)
m.fs.heater = Heater(property_package=m.fs.params)

# Fix inlet state + heater duty
m.fs.heater.inlet.flow_mol.fix(1.0)
m.fs.heater.inlet.temperature.fix(300)
m.fs.heater.inlet.pressure.fix(1e5)
m.fs.heater.inlet.mole_frac_comp[0, "comp_a"].fix(0.5)
m.fs.heater.inlet.mole_frac_comp[0, "comp_b"].fix(0.5)
m.fs.heater.heat_duty.fix(1000)

assert degrees_of_freedom(m) == 0
```

- [ ] Heater (or other simple unit) builds with this property package
- [ ] DoF is correct
- [ ] System solves to optimality

## 9. Diagnostics (If Solver Fails)

```python
from idaes.core.util.model_diagnostics import DiagnosticsToolbox

dt = DiagnosticsToolbox(m.state[0])
dt.report_structural_issues()
dt.report_numerical_issues()
```

- [ ] No structural singularities
- [ ] No numerically problematic variables or constraints
- [ ] No unit consistency warnings
