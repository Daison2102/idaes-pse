# pylint: disable=all
"""
Custom class-based IDAES property package for a methanol/water/ammonia mixture.

Assumptions:
- Two phases: ideal liquid + ideal vapor
- FTPx-style state variables (flow_mol, temperature, pressure, mole_frac_comp)
- Raoult-law style phase equilibrium using Antoine vapor pressure correlations
- Constant heat capacities and constant liquid molar densities (placeholders)
"""

from pyomo.environ import (
    Constraint,
    Expression,
    Param,
    Var,
    exp,
    log,
    units as pyunits,
    value,
)

from idaes.core import (
    Component,
    EnergyBalanceType,
    LiquidPhase,
    MaterialBalanceType,
    MaterialFlowBasis,
    PhysicalParameterBlock,
    StateBlock,
    StateBlockData,
    VaporPhase,
    declare_process_block_class,
)
from idaes.core.util.initialization import fix_state_vars, revert_state_vars
import idaes.logger as idaeslog

_log = idaeslog.getLogger(__name__)


@declare_process_block_class("MWAIdealParameterBlock")
class MWAIdealParameterData(PhysicalParameterBlock):
    def build(self):
        super().build()
        self._state_block_class = MWAIdealStateBlock

        # Phases
        self.Liq = LiquidPhase()
        self.Vap = VaporPhase()

        # Components
        self.Methanol = Component()
        self.Water = Component()
        self.Ammonia = Component()

        # References
        self.pressure_ref = Param(
            initialize=101325.0,
            mutable=True,
            units=pyunits.Pa,
            doc="Reference pressure",
        )
        self.temperature_ref = Param(
            initialize=298.15,
            mutable=True,
            units=pyunits.K,
            doc="Reference temperature",
        )
        self.gas_constant = Param(
            initialize=8.314462618,
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K,
            doc="Universal gas constant",
        )

        # Molecular weights
        self.mw = Param(
            self.component_list,
            initialize={
                "Methanol": 0.0320419,
                "Water": 0.01801528,
                "Ammonia": 0.0170305,
            },
            units=pyunits.kg / pyunits.mol,
            mutable=True,
        )

        # Critical properties
        self.temperature_crit = Param(
            self.component_list,
            initialize={
                "Methanol": 513.0,
                "Water": 647.0,
                "Ammonia": 405.4,
            },
            units=pyunits.K,
            mutable=True,
        )
        self.pressure_crit = Param(
            self.component_list,
            initialize={
                "Methanol": 79.0 * 101325.0,
                "Water": 220.64e5,
                "Ammonia": 111.52 * 101325.0,
            },
            units=pyunits.Pa,
            mutable=True,
        )

        # Antoine constants for log10(Psat) = A - B/(T + C)
        # Methanol, Water: Psat in bar; Ammonia: Psat in atm
        self.antoine_A = Param(
            self.component_list,
            initialize={
                "Methanol": 5.20409,
                "Water": 5.20389,
                "Ammonia": 4.86315,
            },
            mutable=True,
        )
        self.antoine_B = Param(
            self.component_list,
            initialize={
                "Methanol": 1581.341,
                "Water": 1733.926,
                "Ammonia": 1113.928,
            },
            mutable=True,
            units=pyunits.K,
        )
        self.antoine_C = Param(
            self.component_list,
            initialize={
                "Methanol": -33.50,
                "Water": -39.485,
                "Ammonia": -10.409,
            },
            mutable=True,
            units=pyunits.K,
        )
        self.antoine_pressure_scale = Param(
            self.component_list,
            initialize={
                "Methanol": 1e5,
                "Water": 1e5,
                "Ammonia": 101325.0,
            },
            mutable=True,
            units=pyunits.Pa,
        )

        self.cp_mol_liq_comp = Param(
            self.component_list,
            initialize={
                "Methanol": 81.0,
                "Water": 75.3,
                "Ammonia": 80.8,
            },
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K,
        )
        self.cp_mol_vap_comp = Param(
            self.component_list,
            initialize={
                "Methanol": 44.0,
                "Water": 33.6,
                "Ammonia": 37.0,
            },
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K,
        )

        self.dens_mol_liq_comp = Param(
            self.component_list,
            initialize={
                "Methanol": 24700.0,
                "Water": 55300.0,
                "Ammonia": 40000.0,
            },
            mutable=True,
            units=pyunits.mol / pyunits.m**3,
        )

    @classmethod
    def define_metadata(cls, obj):
        obj.add_properties(
            {
                "flow_mol": {"method": None},
                "temperature": {"method": None},
                "pressure": {"method": None},
                "mole_frac_comp": {"method": None},
                "phase_frac": {"method": None},
                "mole_frac_phase_comp": {"method": None},
                "flow_mol_phase": {"method": None},
                "flow_mol_phase_comp": {"method": None},
                "pressure_sat_comp": {"method": None},
                "enth_mol_phase": {"method": None},
                "dens_mol_phase": {"method": None},
            }
        )
        obj.add_default_units(
            {
                "time": pyunits.s,
                "length": pyunits.m,
                "mass": pyunits.kg,
                "amount": pyunits.mol,
                "temperature": pyunits.K,
            }
        )


class _MWAIdealStateBlock(StateBlock):
    def initialize(
        blk,
        state_args=None,
        state_vars_fixed=False,
        hold_state=False,
        outlvl=idaeslog.NOTSET,
        solver=None,
        optarg=None,
    ):
        if state_vars_fixed:
            flags = {}
        else:
            flags = fix_state_vars(blk, state_args)

        for b in blk.values():
            b._set_initial_phase_split()

        if hold_state:
            return flags
        if not state_vars_fixed:
            revert_state_vars(blk, flags)
        return None

    def release_state(blk, flags, outlvl=idaeslog.NOTSET):
        if flags is not None:
            revert_state_vars(blk, flags)


@declare_process_block_class("MWAIdealStateBlock", block_class=_MWAIdealStateBlock)
class MWAIdealStateBlockData(StateBlockData):
    def build(self):
        super().build()

        self.flow_mol = Var(initialize=1.0, bounds=(1e-12, 1e6), units=pyunits.mol / pyunits.s)
        self.temperature = Var(initialize=330.0, bounds=(200.0, 600.0), units=pyunits.K)
        self.pressure = Var(initialize=101325.0, bounds=(1e4, 5e7), units=pyunits.Pa)
        self.mole_frac_comp = Var(
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            bounds=(1e-12, 1.0),
            units=pyunits.dimensionless,
        )

        self.phase_frac = Var(
            self.params.phase_list,
            initialize={"Liq": 0.5, "Vap": 0.5},
            bounds=(1e-8, 1.0),
            units=pyunits.dimensionless,
        )
        self.mole_frac_phase_comp = Var(
            self.params.phase_list,
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            bounds=(1e-12, 1.0),
            units=pyunits.dimensionless,
        )

        if self.config.defined_state is False:
            self.sum_mole_frac_comp = Constraint(
                expr=sum(self.mole_frac_comp[j] for j in self.params.component_list) == 1.0
            )

        self.sum_phase_frac = Constraint(
            expr=sum(self.phase_frac[p] for p in self.params.phase_list) == 1.0
        )
        self.sum_phase_mole_frac = Constraint(
            self.params.phase_list,
            rule=lambda b, p: sum(b.mole_frac_phase_comp[p, j] for j in b.params.component_list)
            == 1.0,
        )
        self.component_split_eq = Constraint(
            self.params.component_list,
            rule=lambda b, j: b.mole_frac_comp[j]
            == sum(b.phase_frac[p] * b.mole_frac_phase_comp[p, j] for p in b.params.phase_list),
        )

        self.pressure_sat_comp = Expression(
            self.params.component_list,
            rule=lambda b, j: b.params.antoine_pressure_scale[j]
            * exp(
                log(10)
                * (
                    b.params.antoine_A[j]
                    - b.params.antoine_B[j] / (b.temperature + b.params.antoine_C[j])
                )
            ),
        )
        self.vle_eq = Constraint(
            self.params.component_list,
            rule=lambda b, j: b.mole_frac_phase_comp["Vap", j] * b.pressure
            == b.mole_frac_phase_comp["Liq", j] * b.pressure_sat_comp[j],
        )

        self.flow_mol_phase = Expression(self.params.phase_list, rule=lambda b, p: b.flow_mol * b.phase_frac[p])
        self.flow_mol_phase_comp = Expression(
            self.params.phase_list,
            self.params.component_list,
            rule=lambda b, p, j: b.flow_mol_phase[p] * b.mole_frac_phase_comp[p, j],
        )
        self.enth_mol_phase = Expression(
            self.params.phase_list,
            rule=lambda b, p: sum(
                b.mole_frac_phase_comp[p, j]
                * (
                    b.params.cp_mol_liq_comp[j]
                    if p == "Liq"
                    else b.params.cp_mol_vap_comp[j]
                )
                * (b.temperature - b.params.temperature_ref)
                for j in b.params.component_list
            ),
        )
        self.dens_mol_phase = Expression(
            self.params.phase_list,
            rule=lambda b, p: sum(
                b.mole_frac_phase_comp[p, j] * b.params.dens_mol_liq_comp[j]
                for j in b.params.component_list
            )
            if p == "Liq"
            else b.pressure / (b.params.gas_constant * b.temperature),
        )

    def _set_initial_phase_split(self):
        p_val = max(value(self.pressure), 1e4)
        z = {j: max(value(self.mole_frac_comp[j]), 1e-10) for j in self.params.component_list}
        z_sum = sum(z.values())
        z = {j: z[j] / z_sum for j in self.params.component_list}
        k = {j: max(value(self.pressure_sat_comp[j]) / p_val, 1e-6) for j in self.params.component_list}

        vf = 0.5
        x = {j: z[j] / (1.0 + vf * (k[j] - 1.0)) for j in self.params.component_list}
        xsum = sum(x.values())
        x = {j: x[j] / xsum for j in self.params.component_list}
        y = {j: k[j] * x[j] for j in self.params.component_list}
        ysum = sum(y.values())
        y = {j: y[j] / ysum for j in self.params.component_list}

        if not self.phase_frac["Vap"].fixed:
            self.phase_frac["Vap"].set_value(vf)
        if not self.phase_frac["Liq"].fixed:
            self.phase_frac["Liq"].set_value(1.0 - vf)
        for j in self.params.component_list:
            if not self.mole_frac_phase_comp["Liq", j].fixed:
                self.mole_frac_phase_comp["Liq", j].set_value(x[j])
            if not self.mole_frac_phase_comp["Vap", j].fixed:
                self.mole_frac_phase_comp["Vap", j].set_value(y[j])

    def define_state_vars(self):
        return {
            "flow_mol": self.flow_mol,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "mole_frac_comp": self.mole_frac_comp,
        }

    def get_material_flow_terms(self, p, j):
        return self.flow_mol_phase_comp[p, j]

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

    def get_material_flow_basis(self):
        return MaterialFlowBasis.molar

