##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2020, by the
# software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia
# University Research Corporation, et al. All rights reserved.
#
# Please see the files COPYRIGHT.txt and LICENSE.txt for full copyright and
# license information, respectively. Both files are also available online
# at the URL "https://github.com/IDAES/idaes-pse".
##############################################################################
"""
Methanol-Water-Ammonia property package using class-based definitions.

- State definition: FTPx
- Phases: ideal liquid + ideal vapor
- Equilibrium: Raoult-style relation y_i * P = x_i * P_sat_i(T)

This module is intended as a custom class-based template with physically
reasonable placeholder constants sourced from web references.
"""

from pyomo.environ import (
    Constraint,
    NonNegativeReals,
    Param,
    Set,
    Var,
    check_optimal_termination,
    value,
)
from pyomo.environ import units as pyunits

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
from idaes.core.solvers import get_solver
from idaes.core.util.constants import Constants
from idaes.core.util.exceptions import InitializationError
from idaes.core.util.initialization import (
    fix_state_vars,
    revert_state_vars,
    solve_indexed_blocks,
)
from idaes.core.util.model_statistics import degrees_of_freedom

import idaes.logger as idaeslog

__author__ = "Codex"

_log = idaeslog.getLogger(__name__)


# ----------------------------------------------------------------------------
# Data sources used for placeholder constants
#
# Antoine + critical + molecular weight (NIST WebBook)
# Water:    https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Type=ANTOINE&Mask=4
# Methanol: https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Type=ANTOINE&Mask=4
# Ammonia:  https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Type=ANTOINE&Mask=4
#
# Heat capacities (NIST WebBook)
# Water (liq, 298.15 K):
#   https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=2&Table=on&Type=JANAFL
# Methanol (gas/liq, 298.15 K):
#   https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Mask=2&Table=on&Type=JANAFG
#   https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Mask=2&Table=on&Type=JANAFL
# Ammonia (gas Shomate coeffs):
#   https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Mask=1&Table=on&Type=JANAFG
# Ammonia (liq cp):
#   https://www.engineeringtoolbox.com/ammonia-d_971.html
#
# Densities
# Water: https://en.wikipedia.org/wiki/Water
# Methanol: https://en.wikipedia.org/wiki/Methanol
# Ammonia: https://www.engineeringtoolbox.com/ammonia-d_971.html
# ----------------------------------------------------------------------------


@declare_process_block_class("MWAParameterBlock")
class MWAParameterBlockData(PhysicalParameterBlock):
    """Parameter block for methanol-water-ammonia ideal FTPx package."""

    CONFIG = PhysicalParameterBlock.CONFIG()

    def build(self):
        super(MWAParameterBlockData, self).build()

        self._state_block_class = MWAStateBlock

        # Components
        self.methanol = Component()
        self.water = Component()
        self.ammonia = Component()

        # Phases
        self.Liq = LiquidPhase()
        self.Vap = VaporPhase()

        # Phase equilibrium metadata expected by some unit models
        self.phase_equilibrium_idx = Set(
            initialize=["PE_methanol", "PE_water", "PE_ammonia"]
        )
        self.phase_equilibrium_list = {
            "PE_methanol": ["methanol", ("Vap", "Liq")],
            "PE_water": ["water", ("Vap", "Liq")],
            "PE_ammonia": ["ammonia", ("Vap", "Liq")],
        }

        # Reference state
        self.pressure_ref = Param(
            mutable=True,
            default=101325.0,
            units=pyunits.Pa,
            doc="Reference pressure [Pa]",
        )
        self.temperature_ref = Param(
            mutable=True,
            default=298.15,
            units=pyunits.K,
            doc="Reference temperature [K]",
        )

        # Molecular weights [kg/mol]
        self.mw_comp = Param(
            self.component_list,
            initialize={
                "methanol": 0.0320419,
                "water": 0.01801528,
                "ammonia": 0.01703052,
            },
            units=pyunits.kg / pyunits.mol,
            doc="Molecular weight",
        )

        # Critical constants from NIST (converted from bar to Pa)
        self.temperature_crit = Param(
            self.component_list,
            initialize={
                "methanol": 512.6,
                "water": 647.0,
                "ammonia": 405.4,
            },
            units=pyunits.K,
            doc="Critical temperature [K]",
        )
        self.pressure_crit = Param(
            self.component_list,
            initialize={
                "methanol": 80.97e5,
                "water": 220.64e5,
                "ammonia": 113.5e5,
            },
            units=pyunits.Pa,
            doc="Critical pressure [Pa]",
        )

        # Antoine coefficients using NIST form:
        # log10(P_bar) = A - B / (T_K + C)
        self.antoine_A = Param(
            self.component_list,
            initialize={
                "methanol": 5.20409,
                "water": 5.40221,
                "ammonia": 4.86886,
            },
            doc="Antoine A coefficient (NIST form)",
        )
        self.antoine_B = Param(
            self.component_list,
            initialize={
                "methanol": 1581.341,
                "water": 1838.675,
                "ammonia": 1113.928,
            },
            doc="Antoine B coefficient (K in NIST form)",
        )
        self.antoine_C = Param(
            self.component_list,
            initialize={
                "methanol": -33.50,
                "water": -31.737,
                "ammonia": -10.409,
            },
            doc="Antoine C coefficient (K offset in NIST form)",
        )

        # Constant molar Cp placeholders [J/mol/K]
        self.cp_mol_vap_comp = Param(
            self.component_list,
            initialize={
                "methanol": 44.06,
                "water": 33.59,
                "ammonia": 35.65,
            },
            units=pyunits.J / pyunits.mol / pyunits.K,
            doc="Constant vapor Cp placeholders",
        )
        self.cp_mol_liq_comp = Param(
            self.component_list,
            initialize={
                "methanol": 81.08,
                "water": 75.37,
                "ammonia": 80.90,
            },
            units=pyunits.J / pyunits.mol / pyunits.K,
            doc="Constant liquid Cp placeholders",
        )

        # Constant liquid molar density placeholders [mol/m^3]
        self.dens_mol_liq_comp = Param(
            self.component_list,
            initialize={
                "methanol": 24549.0,
                "water": 55343.0,
                "ammonia": 35759.0,
            },
            units=pyunits.mol / pyunits.m**3,
            doc="Constant liquid molar density placeholders",
        )

    @classmethod
    def define_metadata(cls, obj):
        obj.add_properties(
            {
                "flow_mol": {"method": None},
                "flow_mol_phase": {"method": None},
                "flow_mol_phase_comp": {"method": None},
                "mole_frac_comp": {"method": None},
                "mole_frac_phase_comp": {"method": None},
                "phase_frac": {"method": None},
                "temperature": {"method": None},
                "pressure": {"method": None},
                "pressure_sat": {"method": None},
                "dens_mol_phase": {"method": None},
                "dens_mol": {"method": None},
                "enth_mol_phase": {"method": None},
                "enth_mol": {"method": None},
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


class _MWAStateBlock(StateBlock):
    """Methods applied to indexed state blocks."""

    def initialize(
        blk,
        state_args=None,
        state_vars_fixed=False,
        hold_state=False,
        outlvl=idaeslog.NOTSET,
        solver=None,
        optarg=None,
    ):
        if state_args is None:
            state_args = {}
        if optarg is None:
            optarg = {}

        init_log = idaeslog.getInitLogger(blk.name, outlvl, tag="properties")

        # For undefined outlet-like states, fixing all state vars can make
        # the sum(mole_frac_comp)=1 equation temporarily over-specify the
        # state. Deactivate during initialization, then reactivate.
        deactivated = []
        for b in blk.values():
            if b.config.defined_state is False and hasattr(b, "sum_mole_frac"):
                b.sum_mole_frac.deactivate()
                deactivated.append(b)

        if state_vars_fixed:
            flags = None
            for b in blk.values():
                dof = degrees_of_freedom(b)
                if dof != 0:
                    raise InitializationError(
                        f"State vars fixed but DOF for {b.name} is {dof}, expected 0."
                    )
        else:
            flags = fix_state_vars(blk, state_args)

        for b in blk.values():
            # Initial phase split guess
            if not b.phase_frac["Liq"].fixed:
                b.phase_frac["Liq"].set_value(0.5)
            if not b.phase_frac["Vap"].fixed:
                b.phase_frac["Vap"].set_value(0.5)

            if not b.flow_mol_phase["Liq"].fixed:
                b.flow_mol_phase["Liq"].set_value(0.5 * value(b.flow_mol))
            if not b.flow_mol_phase["Vap"].fixed:
                b.flow_mol_phase["Vap"].set_value(0.5 * value(b.flow_mol))

            z = {j: max(1e-8, value(b.mole_frac_comp[j])) for j in b.params.component_list}
            zsum = sum(z.values())
            for j in b.params.component_list:
                z[j] /= zsum

            # Start with liquid composition ~= feed composition
            for j in b.params.component_list:
                if not b.mole_frac_phase_comp["Liq", j].fixed:
                    b.mole_frac_phase_comp["Liq", j].set_value(z[j])

            # Vapor composition from simple K-value estimate
            p = max(1.0, value(b.pressure))
            y_raw = {}
            for j in b.params.component_list:
                psat = max(1.0, b._estimate_psat_pa(j, value(b.temperature)))
                kij = max(1e-6, psat / p)
                y_raw[j] = kij * z[j]
            ysum = sum(y_raw.values())
            for j in b.params.component_list:
                if not b.mole_frac_phase_comp["Vap", j].fixed:
                    b.mole_frac_phase_comp["Vap", j].set_value(y_raw[j] / ysum)

            for j in b.params.component_list:
                if not b.pressure_sat[j].fixed:
                    b.pressure_sat[j].set_value(b._estimate_psat_pa(j, value(b.temperature)))

        opt = get_solver(solver=solver, options=optarg)
        results = solve_indexed_blocks(opt, [blk], tee=(outlvl >= idaeslog.DEBUG))

        if not check_optimal_termination(results):
            for b in deactivated:
                b.sum_mole_frac.activate()
            raise InitializationError(
                f"Property initialization failed for {blk.name}. "
                f"Solver status: {results.solver.status}, "
                f"termination: {results.solver.termination_condition}."
            )

        for b in deactivated:
            b.sum_mole_frac.activate()

        init_log.info("Property initialization successful.")

        if hold_state:
            return flags
        if flags is not None:
            blk.release_state(flags)
        return None

    def release_state(blk, flags, outlvl=idaeslog.NOTSET):
        revert_state_vars(blk, flags)


@declare_process_block_class("MWAStateBlock", block_class=_MWAStateBlock)
class MWAStateBlockData(StateBlockData):
    """State block data for methanol-water-ammonia ideal FTPx package."""

    def build(self):
        super(MWAStateBlockData, self).build()

        # ------------------------------------------------------------------
        # State variables (FTPx)
        self.flow_mol = Var(
            domain=NonNegativeReals,
            initialize=1.0,
            bounds=(1e-8, None),
            units=pyunits.mol / pyunits.s,
            doc="Total molar flow rate",
        )
        self.mole_frac_comp = Var(
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            bounds=(1e-8, 1.0),
            units=pyunits.dimensionless,
            doc="Overall mole fractions",
        )
        self.temperature = Var(
            initialize=298.15,
            bounds=(250.0, 600.0),
            units=pyunits.K,
            doc="Temperature",
        )
        self.pressure = Var(
            initialize=101325.0,
            bounds=(1e4, 2e7),
            units=pyunits.Pa,
            doc="Pressure",
        )

        # Sum(z)=1 only for undefined outlet-like states
        if self.config.defined_state is False:
            self.sum_mole_frac = Constraint(
                expr=sum(self.mole_frac_comp[j] for j in self.params.component_list) == 1.0
            )

        # ------------------------------------------------------------------
        # Phase split and phase compositions
        self.phase_frac = Var(
            self.params.phase_list,
            initialize=0.5,
            bounds=(1e-8, 1.0),
            units=pyunits.dimensionless,
            doc="Phase fraction",
        )
        self.flow_mol_phase = Var(
            self.params.phase_list,
            initialize=0.5,
            bounds=(1e-8, None),
            units=pyunits.mol / pyunits.s,
            doc="Phase molar flow",
        )
        self.mole_frac_phase_comp = Var(
            self.params.phase_list,
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            bounds=(1e-8, 1.0),
            units=pyunits.dimensionless,
            doc="Phase-component mole fractions",
        )

        self.eq_phase_flow = Constraint(
            self.params.phase_list,
            rule=lambda b, p: b.flow_mol_phase[p] == b.phase_frac[p] * b.flow_mol,
        )

        self.eq_phase_frac = Constraint(
            expr=sum(self.phase_frac[p] for p in self.params.phase_list) == 1.0
        )

        self.eq_sum_mole_frac_phase = Constraint(
            self.params.phase_list,
            rule=lambda b, p: sum(
                b.mole_frac_phase_comp[p, j] for j in b.params.component_list
            )
            == 1.0,
        )

        # One component balance is dependent because overall composition sums
        # to one together with phase composition sums.
        _last_comp = list(self.params.component_list)[-1]
        self.eq_component_balance = Constraint(
            self.params.component_list,
            rule=lambda b, j: Constraint.Skip
            if j == _last_comp
            else b.flow_mol * b.mole_frac_comp[j]
            == sum(
                b.flow_mol_phase[p] * b.mole_frac_phase_comp[p, j]
                for p in b.params.phase_list
            ),
        )

        # ------------------------------------------------------------------
        # Saturation pressure (Antoine) and VLE relation
        self.pressure_sat = Var(
            self.params.component_list,
            initialize=1e5,
            bounds=(1.0, 5e7),
            units=pyunits.Pa,
            doc="Pure-component saturation pressure",
        )

        self.eq_pressure_sat = Constraint(
            self.params.component_list,
            rule=lambda b, j: b.pressure_sat[j]
            == 1e5
            * 10
            ** (
                b.params.antoine_A[j]
                - b.params.antoine_B[j]
                / ((b.temperature / pyunits.K) + b.params.antoine_C[j])
            )
            * pyunits.Pa,
        )

        self.eq_phase_equilibrium = Constraint(
            self.params.component_list,
            rule=lambda b, j: b.mole_frac_phase_comp["Vap", j] * b.pressure
            == b.mole_frac_phase_comp["Liq", j] * b.pressure_sat[j],
        )

        # ------------------------------------------------------------------
        # Enthalpy and density (placeholders with physically reasonable values)
        self.enth_mol_phase = Var(
            self.params.phase_list,
            initialize=0.0,
            units=pyunits.J / pyunits.mol,
            doc="Molar phase enthalpy",
        )
        self.enth_mol = Var(
            initialize=0.0,
            units=pyunits.J / pyunits.mol,
            doc="Overall molar enthalpy",
        )

        self.eq_enth_mol_phase_liq = Constraint(
            expr=self.enth_mol_phase["Liq"]
            == sum(
                self.mole_frac_phase_comp["Liq", j]
                * self.params.cp_mol_liq_comp[j]
                * (self.temperature - self.params.temperature_ref)
                for j in self.params.component_list
            )
        )
        self.eq_enth_mol_phase_vap = Constraint(
            expr=self.enth_mol_phase["Vap"]
            == sum(
                self.mole_frac_phase_comp["Vap", j]
                * self.params.cp_mol_vap_comp[j]
                * (self.temperature - self.params.temperature_ref)
                for j in self.params.component_list
            )
        )
        self.eq_enth_mol = Constraint(
            expr=self.enth_mol
            == sum(
                self.phase_frac[p] * self.enth_mol_phase[p]
                for p in self.params.phase_list
            )
        )

        self.dens_mol_phase = Var(
            self.params.phase_list,
            initialize=1e3,
            bounds=(1e-3, None),
            units=pyunits.mol / pyunits.m**3,
            doc="Molar phase density",
        )
        self.dens_mol = Var(
            initialize=1e3,
            bounds=(1e-3, None),
            units=pyunits.mol / pyunits.m**3,
            doc="Overall molar density",
        )

        self.eq_dens_mol_vap = Constraint(
            expr=self.dens_mol_phase["Vap"]
            == self.pressure / (Constants.gas_constant * self.temperature)
        )
        self.eq_dens_mol_liq = Constraint(
            expr=1.0
            == self.dens_mol_phase["Liq"]
            * sum(
                self.mole_frac_phase_comp["Liq", j] / self.params.dens_mol_liq_comp[j]
                for j in self.params.component_list
            )
        )
        self.eq_dens_mol = Constraint(
            expr=self.dens_mol
            == sum(
                self.phase_frac[p] * self.dens_mol_phase[p]
                for p in self.params.phase_list
            )
        )

    # ------------------------------------------------------------------
    # Helper for initialization
    def _estimate_psat_pa(self, j, temperature_k):
        a = value(self.params.antoine_A[j])
        b = value(self.params.antoine_B[j])
        c = value(self.params.antoine_C[j])
        # NIST form: log10(P_bar) = A - B/(T_K + C)
        p_bar = 10 ** (a - b / (temperature_k + c))
        return p_bar * 1e5

    # ------------------------------------------------------------------
    # IDAES property package contract methods
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
        return MaterialBalanceType.componentPhase

    def default_energy_balance_type(self):
        return EnergyBalanceType.enthalpyTotal

    def define_state_vars(self):
        return {
            "flow_mol": self.flow_mol,
            "mole_frac_comp": self.mole_frac_comp,
            "temperature": self.temperature,
            "pressure": self.pressure,
        }

    def define_display_vars(self):
        return {
            "Total Molar Flow": self.flow_mol,
            "Mole Fraction": self.mole_frac_comp,
            "Temperature": self.temperature,
            "Pressure": self.pressure,
        }

    def model_check(self):
        if value(self.temperature) < self.temperature.lb:
            _log.error("Temperature set below lower bound.")
        if value(self.temperature) > self.temperature.ub:
            _log.error("Temperature set above upper bound.")
        if value(self.pressure) < self.pressure.lb:
            _log.error("Pressure set below lower bound.")
        if value(self.pressure) > self.pressure.ub:
            _log.error("Pressure set above upper bound.")
        return None
