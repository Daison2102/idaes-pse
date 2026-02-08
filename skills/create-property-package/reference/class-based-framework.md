# Class-Based Property Package Guide

## Overview

A class-based property package should implement four classes manually:

1. **PhysicalParameterBlock subclass** - Defines components, phases, parameters
2. **InitializerBase subclass** - Owns the full property initialization routine
3. **StateBlock container class** - Defines block-wide helpers and default initializer
4. **StateBlockData subclass** - Implements state variables, properties, constraints

## File Structure

A single `.py` file containing all core classes, structured as:

```python
# 1. Imports
# 2. PhysicalParameterBlock subclass  (the "parameter block")
# 3. InitializerBase subclass         (property initialization logic)
# 4. StateBlock container class       (the "block class")
# 5. StateBlockData subclass          (the "state block data")
```

---

## Class 1: PhysicalParameterBlock

```python
@declare_process_block_class("MyParameterBlock")
class MyParameterData(PhysicalParameterBlock):

    CONFIG = PhysicalParameterBlock.CONFIG()
    # Add custom config args here if needed

    def build(self):
        super().build()

        # 1. Assign the state block class
        self._state_block_class = MyStateBlock

        # 2. Define components
        self.water = Component()
        self.ethanol = Component()

        # 3. Define phases
        self.Liq = LiquidPhase()
        self.Vap = VaporPhase()

        # 4. Define reference state
        self.pressure_ref = Param(
            mutable=True,
            default=101325,
            units=pyunits.Pa,
            doc="Reference pressure [Pa]",
        )
        self.temperature_ref = Param(
            mutable=True,
            default=298.15,
            units=pyunits.K,
            doc="Reference temperature [K]",
        )

        # 5. Define component parameters (molecular weight, critical props, etc.)
        self.mw_comp = Param(
            self.component_list,
            initialize={"water": 18.015e-3, "ethanol": 46.069e-3},
            units=pyunits.kg / pyunits.mol,
            doc="Molecular weight [kg/mol]",
        )
        # ... all other parameters (cp coefficients, critical T/P, etc.)

        # 6. (Optional) Phase equilibrium sets
        self.phase_equilibrium_idx = Set(initialize=[1, 2])
        self.phase_equilibrium_list = {
            1: ["water", ("Vap", "Liq")],
            2: ["ethanol", ("Vap", "Liq")],
        }

    @classmethod
    def define_metadata(cls, obj):
        # 7. Register properties
        obj.add_properties({
            "flow_mol": {"method": None},           # Built in build()
            "temperature": {"method": None},
            "pressure": {"method": None},
            "mole_frac_comp": {"method": None},
            "enth_mol_phase": {"method": "_enth_mol_phase"},  # Built on demand
            "dens_mol_phase": {"method": "_dens_mol_phase"},
            # ... other properties
        })

        # 8. Set base units
        obj.add_default_units({
            "time": pyunits.s,
            "length": pyunits.m,
            "mass": pyunits.kg,
            "amount": pyunits.mol,
            "temperature": pyunits.K,
        })
```

### Property Registration Rules

- `"method": None` - Property is created directly in `StateBlockData.build()`
  (i.e., it's a state variable or always-constructed property)
- `"method": "_method_name"` - Property is built on demand when first accessed
  by calling `_method_name()` on the StateBlockData instance

---

## Class 2: InitializerBase Subclass

Use an explicit initializer class (HDA-style) for the full initialization workflow.
Put the full routine in `initialization_routine()` instead of `_MyStateBlock.initialize()`.

```python
class MyPropsInitializer(InitializerBase):
    CONFIG = InitializerBase.CONFIG()
    CONFIG.declare("solver", ConfigValue(default=None, domain=str))
    CONFIG.declare("solver_options", ConfigValue(default=None))

    def initialization_routine(self, blk):
        init_log = idaeslog.getInitLogger(
            blk.name, self.config.output_level, tag="properties"
        )
        solve_log = idaeslog.getSolveLogger(
            blk.name, self.config.output_level, tag="properties"
        )
        solver = get_solver(self.config.solver, self.config.solver_options)

        # 1) Initialize bubble/dew (if present)
        # 2) Initialize equilibrium helper vars (if present)
        # 3) Solve indexed state block if square
        free_vars = sum(number_unfixed_variables(blk[k]) for k in blk.keys())
        dof = sum(degrees_of_freedom(blk[k]) for k in blk.keys())
        if free_vars > 0 and dof == 0:
            with idaeslog.solver_log(solve_log, idaeslog.DEBUG) as slc:
                res = solve_indexed_blocks(solver, [blk], tee=slc.tee)
            init_log.info(f"Initialization complete: {idaeslog.condition(res)}")
            return res
        return None
```

## Class 3: StateBlock Container

Keep this class focused on block-wide helpers and initializer wiring.

```python
class _MyStateBlock(StateBlock):
    default_initializer = MyPropsInitializer

    def fix_initialization_states(self):
        fix_state_vars(self)
        for b in self.values():
            if b.config.defined_state is False:
                j = b.params.component_list.last()
                b.mole_frac_comp[j].unfix()
```

---

## Class 4: StateBlockData

This is where all the actual thermodynamic calculations happen.

```python
@declare_process_block_class("MyStateBlock", block_class=_MyStateBlock)
class MyStateBlockData(StateBlockData):
    """Individual state point calculations."""

    def build(self):
        super().build()
        units = self.params.get_metadata().derived_units

        # --- State Variables ---
        self.flow_mol = Var(
            initialize=1.0,
            domain=NonNegativeReals,
            units=units["flow_mole"],
            doc="Total molar flow rate",
        )
        self.mole_frac_comp = Var(
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            bounds=(0, None),
            doc="Mixture mole fractions",
        )
        self.pressure = Var(
            initialize=1e5,
            domain=NonNegativeReals,
            units=units["pressure"],
            doc="State pressure",
        )
        self.temperature = Var(
            initialize=298.15,
            domain=NonNegativeReals,
            units=units["temperature"],
            doc="State temperature",
        )

        # --- Supporting Variables ---
        self.flow_mol_phase = Var(
            self.params.phase_list,
            initialize=0.5,
            domain=NonNegativeReals,
            units=units["flow_mole"],
        )
        self.mole_frac_phase_comp = Var(
            self.params._phase_component_set,
            initialize=1 / len(self.params.component_list),
            bounds=(0, None),
        )
        self.phase_frac = Var(
            self.params.phase_list,
            initialize=1 / len(self.params.phase_list),
            bounds=(0, None),
        )

        # --- Supporting Constraints ---
        # Sum of mole fractions (outlet only)
        if not self.config.defined_state:
            self.sum_mole_frac_out = Constraint(
                expr=sum(
                    self.mole_frac_comp[j]
                    for j in self.params.component_list
                ) == 1
            )

        # Total flow balance
        self.total_flow_balance = Constraint(
            expr=sum(
                self.flow_mol_phase[p] for p in self.params.phase_list
            ) == self.flow_mol
        )

        # Component flow balances
        def rule_comp_flow(b, j):
            return b.flow_mol * b.mole_frac_comp[j] == sum(
                b.flow_mol_phase[p] * b.mole_frac_phase_comp[p, j]
                for p in b.params.phase_list
                if (p, j) in b.params._phase_component_set
            )
        self.component_flow_balances = Constraint(
            self.params.component_list, rule=rule_comp_flow,
        )

        # Phase fraction
        def rule_phase_frac(b, p):
            return b.phase_frac[p] * b.flow_mol == b.flow_mol_phase[p]
        self.phase_fraction_constraint = Constraint(
            self.params.phase_list, rule=rule_phase_frac,
        )

        # Sum of phase mole fractions
        def rule_sum_mole_frac(b):
            return sum(
                b.mole_frac_phase_comp[b.params.phase_list.first(), j]
                for j in b.params.component_list
            ) == sum(
                b.mole_frac_phase_comp[b.params.phase_list.last(), j]
                for j in b.params.component_list
            )
        self.sum_mole_frac = Constraint(rule=rule_sum_mole_frac)

        # --- Phase Equilibrium (if VLE) ---
        if self.config.has_phase_equilibrium:
            self._build_phase_equilibrium()

    def _build_phase_equilibrium(self):
        """Build VLE constraints using smooth formulation."""
        # Equilibrium temperature (smooth VLE)
        self._teq = Var(initialize=298, doc="Equilibrium temperature [K]")
        self._t1 = Var(initialize=298, doc="Intermediate temperature [K]")
        self.eps_1 = Param(default=0.01, mutable=True)
        self.eps_2 = Param(default=0.0005, mutable=True)

        # Smooth max/min for Teq
        def rule_t1(b):
            return b._t1 == 0.5 * (
                b.temperature + b.temperature_bubble
                + sqrt((b.temperature - b.temperature_bubble) ** 2 + b.eps_1 ** 2)
            )
        self._t1_constraint = Constraint(rule=rule_t1)

        def rule_teq(b):
            return b._teq == 0.5 * (
                b._t1 + b.temperature_dew
                - sqrt((b._t1 - b.temperature_dew) ** 2 + b.eps_2 ** 2)
            )
        self._teq_constraint = Constraint(rule=rule_teq)

        # Fugacity equality
        def rule_eq(b, j):
            return b.fug_phase_comp["Vap", j] == b.fug_phase_comp["Liq", j]
        self.equilibrium_constraint = Constraint(
            self.params.component_list, rule=rule_eq,
        )

    # ------------------------------------------------------------------
    # Required Contract Methods (all 8 must be implemented)
    # ------------------------------------------------------------------

    def get_material_flow_basis(self):
        return MaterialFlowBasis.molar

    def get_material_flow_terms(self, p, j):
        return self.flow_mol_phase[p] * self.mole_frac_phase_comp[p, j]

    def get_enthalpy_flow_terms(self, p):
        return self.flow_mol_phase[p] * self.enth_mol_phase[p]

    def get_material_density_terms(self, p, j):
        return self.dens_mol_phase[p] * self.mole_frac_phase_comp[p, j]

    def get_energy_density_terms(self, p):
        return self.dens_mol_phase[p] * self.enth_mol_phase[p]

    def default_material_balance_type(self):
        return MaterialBalanceType.componentTotal

    def default_energy_balance_type(self):
        return EnergyBalanceType.enthalpyTotal

    def define_state_vars(self):
        return {
            "flow_mol": self.flow_mol,
            "mole_frac_comp": self.mole_frac_comp,
            "temperature": self.temperature,
            "pressure": self.pressure,
        }

    # ------------------------------------------------------------------
    # On-Demand Property Methods
    # ------------------------------------------------------------------
    # These are called automatically when the property is first accessed,
    # based on the metadata registered in define_metadata().

    def _enth_mol_phase(self):
        """Build phase molar enthalpy."""
        self.enth_mol_phase = Var(
            self.params.phase_list, initialize=0, units=pyunits.J / pyunits.mol,
        )
        def rule(b, p):
            if p == "Vap":
                return b.enth_mol_phase[p] == sum(
                    b.mole_frac_phase_comp[p, j] * b._enth_mol_vap(j)
                    for j in b.params.component_list
                )
            else:
                return b.enth_mol_phase[p] == sum(
                    b.mole_frac_phase_comp[p, j] * b._enth_mol_liq(j)
                    for j in b.params.component_list
                )
        self.eq_enth_mol_phase = Constraint(self.params.phase_list, rule=rule)
```

---

## Required Imports

```python
from pyomo.environ import (
    ConcreteModel, Constraint, Expression, log, exp, sqrt,
    NonNegativeReals, Param, Set, units as pyunits, value, Var,
)
from pyomo.common.config import ConfigValue, In
from pyomo.util.calc_var_value import calculate_variable_from_constraint

from idaes.core import (
    declare_process_block_class,
    MaterialFlowBasis,
    PhysicalParameterBlock,
    StateBlockData,
    StateBlock,
    MaterialBalanceType,
    EnergyBalanceType,
    LiquidPhase,
    VaporPhase,
    Component,
)
from idaes.core.initialization import InitializerBase
from idaes.core.solvers import get_solver
from idaes.core.util.initialization import (
    fix_state_vars,
    solve_indexed_blocks,
)
from idaes.core.util.model_statistics import (
    degrees_of_freedom,
    number_unfixed_variables,
)
from idaes.core.util.constants import Constants
import idaes.core.util.scaling as iscale
import idaes.logger as idaeslog
```

---

## Common Thermodynamic Equations

### Ideal Gas Heat Capacity (RPP polynomial)

```
Cp_ig = A + B*T + C*T^2 + D*T^3
```

### Ideal Gas Molar Enthalpy

```
H_ig = integral(Cp_ig, T_ref, T) + H_form_ref
     = A*(T - T_ref) + B/2*(T^2 - T_ref^2) + C/3*(T^3 - T_ref^3)
       + D/4*(T^4 - T_ref^4) + H_form_ref
```

### Ideal Gas Molar Entropy

```
S_ig = A*ln(T/T_ref) + B*(T - T_ref) + C/2*(T^2 - T_ref^2)
       + D/3*(T^3 - T_ref^3) + S_form_ref
```

### Liquid Heat Capacity (Perry's polynomial)

```
Cp_liq = c1 + c2*T + c3*T^2 + c4*T^3 + c5*T^4
```

### Liquid Molar Density (Perry's equation, type 1)

```
rho_liq = c1 / c2^(1 + (1 - T/c3)^c4)    [kmol/m^3]
```

### Saturation Pressure (Antoine-type, RPP)

```
ln(Psat/Pc) = (1/(1 - T/Tc)) * (A*(1-T/Tc) + B*(1-T/Tc)^1.5
              + C*(1-T/Tc)^3 + D*(1-T/Tc)^6)
```

### Ideal Fugacity

```
f_vap = y_j * P           (vapor)
f_liq = x_j * Psat(T)     (liquid, Raoult's law)
```

---

## Scaling Hints

Add default scaling in the PhysicalParameterBlock:

```python
def build(self):
    super().build()
    # ... phases, components, params ...

    # Default scaling factors
    self.set_default_scaling("flow_mol", 1)
    self.set_default_scaling("temperature", 1e-2)
    self.set_default_scaling("pressure", 1e-5)
    self.set_default_scaling("mole_frac_comp", 10)
    self.set_default_scaling("enth_mol_phase", 1e-4)
    self.set_default_scaling("dens_mol_phase", 1e-2)
```
