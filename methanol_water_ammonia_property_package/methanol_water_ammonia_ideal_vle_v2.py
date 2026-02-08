#################################################################################
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES).
#
# Copyright (c) 2018-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory,
# National Technology & Engineering Solutions of Sandia, LLC, Carnegie Mellon
# University, West Virginia University Research Corporation, et al.
# All rights reserved.  Please see the files COPYRIGHT.md and LICENSE.md
# for full copyright and license information.
#################################################################################
"""
Methanol-water-ammonia property package (class-based IDAES implementation).

This package uses FTPx state variables and ideal-liquid/ideal-vapor assumptions
for a three-component VLE system.

Primary sources are NIST WebBook pages for component constants and Antoine
coefficients. Publicly available liquid density/heat-capacity values are used
as physically reasonable placeholder constants where direct open NIST values
are not exposed in a directly machine-readable form for this workflow.
"""
from pyomo.environ import (
    Constraint,
    Expression,
    log,
    exp,
    sqrt,
    NonNegativeReals,
    Param,
    Set,
    units as pyunits,
    value,
    Var,
)
from pyomo.common.config import ConfigValue, In
from pyomo.opt import SolverFactory
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
from idaes.core.solvers import get_solver
from idaes.core.util.initialization import (
    fix_state_vars,
    revert_state_vars,
    solve_indexed_blocks,
)
from idaes.core.util.model_statistics import (
    degrees_of_freedom,
    number_unfixed_variables,
)
from idaes.core.util.constants import Constants
import idaes.logger as idaeslog

_log = idaeslog.getLogger(__name__)


# ===========================================================================
# Physical Parameter Block
# ===========================================================================


@declare_process_block_class("MethanolWaterAmmoniaParameterBlock")
class MethanolWaterAmmoniaParameterData(PhysicalParameterBlock):
    """Parameter block for Methanol-Water-Ammonia system."""

    CONFIG = PhysicalParameterBlock.CONFIG()

    def build(self):
        super().build()

        # Reference the StateBlock class
        self._state_block_class = MethanolWaterAmmoniaStateBlock

        # ----- Components -----
        self.methanol = Component()
        self.water = Component()
        self.ammonia = Component()

        # ----- Phases -----
        self.Liq = LiquidPhase()
        self.Vap = VaporPhase()

        # ----- Phase equilibrium index -----
        self.phase_equilibrium_idx = Set(
            initialize=list(range(1, len(self.component_list) + 1))
        )
        self.phase_equilibrium_list = {
            1: ["methanol", ("Vap", "Liq")],
            2: ["water", ("Vap", "Liq")],
            3: ["ammonia", ("Vap", "Liq")],
        }

        # ----- Reference state -----
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

        # Gas constant
        self.gas_const = Constants.gas_constant

        # ----- Molecular weights -----
        # Source: NIST WebBook species pages (CID C67561, C7732185, C7664417)
        self.mw_comp = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 32.0419e-3,
                "water": 18.0153e-3,
                "ammonia": 17.0305e-3,
            },
            units=pyunits.kg / pyunits.mol,
            doc="Molecular weight [kg/mol]",
        )

        # ----- Critical properties -----
        # Source: NIST WebBook phase-change data pages (Mask=4)
        self.pressure_crit = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 81.00e5,   # 81.00 bar
                "water": 220.64e5,     # 220.64 bar
                "ammonia": 113.00e5,   # 113.00 bar
            },
            units=pyunits.Pa,
            doc="Critical pressure [Pa]",
        )
        self.temperature_crit = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 513.0,   # K
                "water": 647.0,      # K
                "ammonia": 405.4,    # K
            },
            units=pyunits.K,
            doc="Critical temperature [K]",
        )

        # ----- Ideal-gas Cp coefficients (Shomate form) -----
        # Cp = A + B*t + C*t^2 + D*t^3 + E/t^2 ; t = T/1000
        # Water/ammonia: NIST-JANAF coefficients.
        # Methanol: constant-Cp placeholder anchored to NIST Cp(298.15 K)=44.06 J/mol/K.
        self.cp_mol_ig_comp_coeff_A = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 44.06,      # NIST Cp,gas at 298.15 K
                "water": 30.09200,      # NIST JANAF (500-1700 K)
                "ammonia": 19.99563,    # NIST JANAF (298-1400 K)
            },
            units=pyunits.J / pyunits.mol / pyunits.K,
        )
        self.cp_mol_ig_comp_coeff_B = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 0.0,         # constant-Cp placeholder
                "water": 6.832514,       # NIST JANAF
                "ammonia": 49.77119,     # NIST JANAF
            },
            units=pyunits.J * pyunits.mol**-1 * pyunits.K**-1 * pyunits.kiloK**-1,
        )
        self.cp_mol_ig_comp_coeff_C = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 0.0,         # constant-Cp placeholder
                "water": 6.793435,       # NIST JANAF
                "ammonia": -15.37599,    # NIST JANAF
            },
            units=pyunits.J * pyunits.mol**-1 * pyunits.K**-1 * pyunits.kiloK**-2,
        )
        self.cp_mol_ig_comp_coeff_D = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 0.0,         # constant-Cp placeholder
                "water": -2.534480,      # NIST JANAF
                "ammonia": 1.921168,     # NIST JANAF
            },
            units=pyunits.J * pyunits.mol**-1 * pyunits.K**-1 * pyunits.kiloK**-3,
        )
        self.cp_mol_ig_comp_coeff_E = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 0.0,         # constant-Cp placeholder
                "water": 0.082139,       # NIST JANAF
                "ammonia": 0.189174,     # NIST JANAF
            },
            units=pyunits.J * pyunits.mol**-1 * pyunits.K**-1 * pyunits.kiloK**2,
        )

        # ----- Vapor reference enthalpy and entropy -----
        # Source: NIST WebBook gas-phase thermochemistry pages.
        self.enth_mol_form_vap_comp_ref = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": -201.49e3,  # NIST-derived from Rossini data entry
                "water": -241.83e3,     # NIST Review/Chase
                "ammonia": -45.90e3,    # NIST Review/Chase
            },
            units=pyunits.J / pyunits.mol,
            doc="Standard heat of formation (vapor) [J/mol]",
        )
        self.entr_mol_form_vap_comp_ref = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 239.9,    # NIST WebBook (gas entropy, representative)
                "water": 188.84,      # NIST Review/Chase
                "ammonia": 192.77,    # NIST Review/Chase
            },
            units=pyunits.J / pyunits.mol / pyunits.K,
            doc="Standard entropy (vapor, 1 bar) [J/mol/K]",
        )

        # ----- Saturation pressure coefficients (NIST Antoine) -----
        # log10(P_bar) = A - B / (T + C), T in K
        # Source: NIST WebBook Antoine tables (Type=ANTOINE).
        self.pressure_sat_comp_coeff_A = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 5.20409,   # 288.1-356.8 K
                "water": 4.65430,      # 255.9-373.0 K
                "ammonia": 4.86886,    # 239.6-371.5 K
            },
        )
        self.pressure_sat_comp_coeff_B = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 1581.341,
                "water": 1435.264,
                "ammonia": 1113.928,
            },
            units=pyunits.K,
        )
        self.pressure_sat_comp_coeff_C = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": -33.50,
                "water": -64.848,
                "ammonia": -10.409,
            },
            units=pyunits.K,
        )

        # ----- Liquid Cp coefficients -----
        # We keep the 5-term form but use constant-Cp placeholders (terms 2-5 = 0).
        # c1 units are J/kmol/K.
        self.cp_mol_liq_comp_coeff_1 = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 8.111e4,   # NIST condensed-phase Cp(298.15 K) ~81.11 J/mol/K
                "water": 7.530e4,      # NIST condensed-phase Shomate at ~298 K
                "ammonia": 8.074e4,    # EngineeringToolBox: 4.74 kJ/kg/K at 20 C
            },
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-1,
        )
        self.cp_mol_liq_comp_coeff_2 = Param(
            self.component_list,
            mutable=True,
            initialize={"methanol": 0.0, "water": 0.0, "ammonia": 0.0},
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-2,
        )
        self.cp_mol_liq_comp_coeff_3 = Param(
            self.component_list,
            mutable=True,
            initialize={"methanol": 0.0, "water": 0.0, "ammonia": 0.0},
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-3,
        )
        self.cp_mol_liq_comp_coeff_4 = Param(
            self.component_list,
            mutable=True,
            initialize={"methanol": 0.0, "water": 0.0, "ammonia": 0.0},
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-4,
        )
        self.cp_mol_liq_comp_coeff_5 = Param(
            self.component_list,
            mutable=True,
            initialize={"methanol": 0.0, "water": 0.0, "ammonia": 0.0},
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-5,
        )

        # ----- Liquid reference enthalpy and entropy -----
        # Source: NIST for methanol/water; ammonia liquid values are
        # physically consistent placeholders estimated from gas values and
        # NIST vaporization data near ambient conditions.
        self.enth_mol_form_liq_comp_ref = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": -238.4e3,    # NIST condensed phase
                "water": -285.83e3,      # NIST condensed phase
                "ammonia": -68.8e3,      # Placeholder: ~ΔfHgas - ΔHvap(298 K)
            },
            units=pyunits.J / pyunits.mol,
            doc="Standard heat of formation (liquid) [J/mol]",
        )
        self.entr_mol_form_liq_comp_ref = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 127.19,      # NIST condensed phase
                "water": 69.95,          # NIST condensed phase
                "ammonia": 98.0,         # Placeholder from ΔSvap estimate near 298 K
            },
            units=pyunits.J / pyunits.mol / pyunits.K,
            doc="Standard entropy (liquid) [J/mol/K]",
        )

        # ----- Liquid molar density constants -----
        # Source: EngineeringToolBox values converted to mol/m^3.
        self.dens_mol_liq_comp_const = Param(
            self.component_list,
            mutable=True,
            initialize={
                "methanol": 2.448e4,   # 784.5 kg/m^3 @ ~300 K
                "water": 5.534e4,      # 997.05 kg/m^3 @ 25 C
                "ammonia": 3.576e4,    # 609 kg/m^3 @ 20 C sat. pressure
            },
            units=pyunits.mol / pyunits.m**3,
            doc="Constant liquid molar density [mol/m^3]",
        )

    @classmethod
    def define_metadata(cls, obj):
        obj.add_properties(
            {
                "flow_mol": {"method": None},
                "flow_mol_phase": {"method": None},
                "mole_frac_comp": {"method": None},
                "mole_frac_phase_comp": {"method": None},
                "phase_frac": {"method": None},
                "temperature": {"method": None},
                "pressure": {"method": None},
                "dens_mol_phase": {"method": "_dens_mol_phase"},
                "enth_mol_phase_comp": {"method": "_enth_mol_phase_comp"},
                "enth_mol_phase": {"method": "_enth_mol_phase"},
                "entr_mol_phase_comp": {"method": "_entr_mol_phase_comp"},
                "entr_mol_phase": {"method": "_entr_mol_phase"},
                "fug_phase_comp": {"method": "_fug_phase_comp"},
                "mw_phase": {"method": "_mw_phase"},
                "pressure_sat": {"method": "_pressure_sat"},
                "temperature_bubble": {"method": "_temperature_bubble"},
                "temperature_dew": {"method": "_temperature_dew"},
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


# ===========================================================================
# State Block (container for initialization)
# ===========================================================================


class _MethanolWaterAmmoniaStateBlock(StateBlock):
    """Methods applied to the whole indexed StateBlock."""

    def initialize(
        blk,
        state_args=None,
        state_vars_fixed=False,
        hold_state=False,
        outlvl=idaeslog.NOTSET,
        solver="ipopt",
        optarg=None,
    ):
        init_log = idaeslog.getInitLogger(blk.name, outlvl)
        solve_log = idaeslog.getSolveLogger(blk.name, outlvl)

        init_log.info("Starting initialization")

        if not state_vars_fixed:
            flags = fix_state_vars(blk, state_args)

        # Step 1: Initialize bubble/dew points from constraints
        for k in blk.keys():
            if hasattr(blk[k], "eq_temperature_bubble"):
                calculate_variable_from_constraint(
                    blk[k].temperature_bubble,
                    blk[k].eq_temperature_bubble,
                )
            if hasattr(blk[k], "eq_mole_frac_tbub"):
                for j in blk[k].params.component_list:
                    calculate_variable_from_constraint(
                        blk[k]._mole_frac_tbub[j],
                        blk[k].eq_mole_frac_tbub[j],
                    )
            if hasattr(blk[k], "eq_temperature_dew"):
                calculate_variable_from_constraint(
                    blk[k].temperature_dew,
                    blk[k].eq_temperature_dew,
                )
            if hasattr(blk[k], "eq_mole_frac_tdew"):
                for j in blk[k].params.component_list:
                    calculate_variable_from_constraint(
                        blk[k]._mole_frac_tdew[j],
                        blk[k].eq_mole_frac_tdew[j],
                    )

        init_log.info_high("Step 1 - Bubble/dew point init complete.")

        # Step 2: Initialize equilibrium temperature
        for k in blk.keys():
            if hasattr(blk[k], "_t1"):
                blk[k]._t1.value = max(
                    blk[k].temperature.value, blk[k].temperature_bubble.value
                )
                blk[k]._teq.value = min(
                    blk[k]._t1.value, blk[k].temperature_dew.value
                )

        init_log.info_high("Step 2 - Teq init complete.")

        # Step 3: Solve full system
        if hasattr(solver, "solve"):
            opt = solver
        elif solver is None:
            opt = get_solver()
        else:
            opt = SolverFactory(solver)

        if optarg and hasattr(opt, "options"):
            opt.options = optarg

        free_vars = sum(number_unfixed_variables(blk[k]) for k in blk.keys())
        if free_vars > 0:
            with idaeslog.solver_log(solve_log, idaeslog.DEBUG) as slc:
                res = solve_indexed_blocks(opt, [blk], tee=slc.tee)
            init_log.info(
                f"Step 3 - Solve complete: {idaeslog.condition(res)}"
            )

        if not state_vars_fixed:
            if hold_state:
                return flags
            else:
                blk.release_state(flags)

        init_log.info("Initialization Complete")

    def release_state(blk, flags, outlvl=idaeslog.NOTSET):
        init_log = idaeslog.getInitLogger(blk.name, outlvl)
        if flags is None:
            return
        revert_state_vars(blk, flags)
        init_log.info_high("State Released.")


# ===========================================================================
# State Block Data
# ===========================================================================


@declare_process_block_class(
    "MethanolWaterAmmoniaStateBlock", block_class=_MethanolWaterAmmoniaStateBlock
)
class MethanolWaterAmmoniaStateBlockData(StateBlockData):
    """Individual state point calculations for Methanol-Water-Ammonia system."""

    def build(self):
        super().build()
        units = self.params.get_metadata().derived_units

        # ----- State variables -----
        self.flow_mol = Var(
            initialize=1.0,
            domain=NonNegativeReals,
            bounds=(0, 1000),
            units=units["flow_mole"],
            doc="Total molar flow rate",
        )
        self.mole_frac_comp = Var(
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            bounds=(1e-12, 1.0),
            doc="Mixture mole fractions",
        )
        self.pressure = Var(
            initialize=1e5,
            domain=NonNegativeReals,
            bounds=(1e4, 1e7),
            units=units["pressure"],
            doc="State pressure",
        )
        self.temperature = Var(
            initialize=298.15,
            domain=NonNegativeReals,
            bounds=(200, 500),
            units=units["temperature"],
            doc="State temperature",
        )

        # ----- Supporting variables -----
        self.flow_mol_phase = Var(
            self.params.phase_list,
            initialize=0.5,
            domain=NonNegativeReals,
            units=units["flow_mole"],
            doc="Phase molar flow rates",
        )
        self.mole_frac_phase_comp = Var(
            self.params._phase_component_set,
            initialize=1 / len(self.params.component_list),
            bounds=(1e-12, 1.0),
            doc="Phase mole fractions",
        )
        self.phase_frac = Var(
            self.params.phase_list,
            initialize=1 / len(self.params.phase_list),
            bounds=(0.0, 1.0),
            doc="Phase fractions",
        )

        # ----- Supporting constraints -----
        # Sum of mole fractions = 1 (outlet only)
        if not self.config.defined_state:
            self.sum_mole_frac_out = Constraint(
                expr=sum(
                    self.mole_frac_comp[j]
                    for j in self.params.component_list
                )
                == 1
            )

        # Total flow balance
        self.total_flow_balance = Constraint(
            expr=sum(
                self.flow_mol_phase[p] for p in self.params.phase_list
            )
            == self.flow_mol
        )

        # Component flow balances
        def rule_comp_flow(b, j):
            return b.flow_mol * b.mole_frac_comp[j] == sum(
                b.flow_mol_phase[p] * b.mole_frac_phase_comp[p, j]
                for p in b.params.phase_list
                if (p, j) in b.params._phase_component_set
            )

        self.component_flow_balances = Constraint(
            self.params.component_list, rule=rule_comp_flow
        )

        # One phase normalization is sufficient with the flow/component balances.
        def rule_sum_mole_frac(b):
            p0 = b.params.phase_list.first()
            return sum(
                b.mole_frac_phase_comp[p0, j] for j in b.params.component_list
            ) == 1.0

        self.sum_mole_frac = Constraint(rule=rule_sum_mole_frac)

        # Phase fraction definition
        def rule_phase_frac(b, p):
            return b.phase_frac[p] * b.flow_mol == b.flow_mol_phase[p]

        self.phase_fraction_constraint = Constraint(
            self.params.phase_list, rule=rule_phase_frac
        )

        # ----- Phase equilibrium (smooth VLE) -----
        if self.config.has_phase_equilibrium:
            # Use stream temperature directly for evaluating phase equilibrium.
            self._teq = Expression(
                expr=self.temperature,
                doc="Equilibrium temperature [K]",
            )

            def rule_equilibrium(b, j):
                return (
                    b.fug_phase_comp["Vap", j]
                    == b.fug_phase_comp["Liq", j]
                )

            self.equilibrium_constraint = Constraint(
                self.params.component_list, rule=rule_equilibrium
            )

    # ===================================================================
    # Required contract methods
    # ===================================================================

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

    # ===================================================================
    # On-demand property methods
    # ===================================================================

    def _mw_phase(self):
        def rule_mw_phase(b, p):
            return sum(
                b.mole_frac_phase_comp[p, j] * b.params.mw_comp[j]
                for j in b.params.component_list
            )

        self.mw_phase = Expression(self.params.phase_list, rule=rule_mw_phase)

    def _dens_mol_phase(self):
        self.dens_mol_phase = Var(
            self.params.phase_list,
            units=pyunits.mol / pyunits.m**3,
            doc="Molar density [mol/m^3]",
        )

        def rule_dens_mol_phase(b, p):
            if p == "Vap":
                return b.pressure == (
                    b.dens_mol_phase["Vap"]
                    * b.params.gas_const
                    * b.temperature
                )
            else:
                return b.dens_mol_phase["Liq"] == sum(
                    b.mole_frac_phase_comp["Liq", j]
                    * b.params.dens_mol_liq_comp_const[j]
                    for j in b.params.component_list
                )

        self.eq_dens_mol_phase = Constraint(
            self.params.phase_list, rule=rule_dens_mol_phase
        )

    def _enth_mol_phase_comp(self):
        self.enth_mol_phase_comp = Var(
            self.params.phase_list,
            self.params.component_list,
            initialize=7e5,
            doc="Phase-component molar enthalpies [J/mol]",
        )

        def rule_enth_mol_phase_comp(b, p, j):
            T = b.temperature
            T_ref = b.params.temperature_ref
            t = T / 1000  # Shomate equation uses T in kK
            t_ref = T_ref / 1000

            if p == "Vap":
                # Shomate equation integration for enthalpy
                return b.enth_mol_phase_comp["Vap", j] == (
                    b.params.cp_mol_ig_comp_coeff_A[j] * (t - t_ref) * 1000
                    + (b.params.cp_mol_ig_comp_coeff_B[j] / 2) * (t**2 - t_ref**2) * 1000
                    + (b.params.cp_mol_ig_comp_coeff_C[j] / 3) * (t**3 - t_ref**3) * 1000
                    + (b.params.cp_mol_ig_comp_coeff_D[j] / 4) * (t**4 - t_ref**4) * 1000
                    - b.params.cp_mol_ig_comp_coeff_E[j] * (1/t - 1/t_ref) * 1000
                ) + b.params.enth_mol_form_vap_comp_ref[j]
            else:
                # Perry's equation integration for liquid
                return b.enth_mol_phase_comp["Liq", j] * 1e3 == (
                    (b.params.cp_mol_liq_comp_coeff_5[j] / 5)
                    * (T**5 - T_ref**5)
                    + (b.params.cp_mol_liq_comp_coeff_4[j] / 4)
                    * (T**4 - T_ref**4)
                    + (b.params.cp_mol_liq_comp_coeff_3[j] / 3)
                    * (T**3 - T_ref**3)
                    + (b.params.cp_mol_liq_comp_coeff_2[j] / 2)
                    * (T**2 - T_ref**2)
                    + b.params.cp_mol_liq_comp_coeff_1[j] * (T - T_ref)
                    + b.params.enth_mol_form_liq_comp_ref[j] * 1e3
                )

        self.eq_enth_mol_phase_comp = Constraint(
            self.params.phase_list,
            self.params.component_list,
            rule=rule_enth_mol_phase_comp,
        )

    def _enth_mol_phase(self):
        self.enth_mol_phase = Var(
            self.params.phase_list,
            initialize=7e5,
            doc="Phase molar enthalpies [J/mol]",
        )

        def rule_enth_mol_phase(b, p):
            return b.enth_mol_phase[p] == sum(
                b.enth_mol_phase_comp[p, j]
                * b.mole_frac_phase_comp[p, j]
                for j in b.params.component_list
            )

        self.eq_enth_mol_phase = Constraint(
            self.params.phase_list, rule=rule_enth_mol_phase
        )

    def _entr_mol_phase_comp(self):
        self.entr_mol_phase_comp = Var(
            self.params.phase_list,
            self.params.component_list,
            doc="Phase-component molar entropies [J/mol.K]",
        )

        def rule_entr_mol_phase_comp(b, p, j):
            T = b.temperature
            T_ref = b.params.temperature_ref
            t = T / 1000  # Shomate uses T in kK
            t_ref = T_ref / 1000

            if p == "Vap":
                # Shomate equation integration for entropy
                return b.entr_mol_phase_comp["Vap", j] == (
                    b.params.cp_mol_ig_comp_coeff_A[j] * log(T / T_ref)
                    + b.params.cp_mol_ig_comp_coeff_B[j] * (t - t_ref) * 1000
                    + (b.params.cp_mol_ig_comp_coeff_C[j] / 2) * (t**2 - t_ref**2) * 1000
                    + (b.params.cp_mol_ig_comp_coeff_D[j] / 3) * (t**3 - t_ref**3) * 1000
                    - (b.params.cp_mol_ig_comp_coeff_E[j] / 2) * (1/t**2 - 1/t_ref**2) * 1000
                    + b.params.entr_mol_form_vap_comp_ref[j]
                )
            else:
                # Perry's equation integration for liquid entropy
                return b.entr_mol_phase_comp["Liq", j] * 1e3 == (
                    (b.params.cp_mol_liq_comp_coeff_5[j] / 4)
                    * (T**4 - T_ref**4)
                    + (b.params.cp_mol_liq_comp_coeff_4[j] / 3)
                    * (T**3 - T_ref**3)
                    + (b.params.cp_mol_liq_comp_coeff_3[j] / 2)
                    * (T**2 - T_ref**2)
                    + b.params.cp_mol_liq_comp_coeff_2[j] * (T - T_ref)
                    + b.params.cp_mol_liq_comp_coeff_1[j] * log(T / T_ref)
                    + b.params.entr_mol_form_liq_comp_ref[j] * 1e3
                )

        self.eq_entr_mol_phase_comp = Constraint(
            self.params.phase_list,
            self.params.component_list,
            rule=rule_entr_mol_phase_comp,
        )

    def _entr_mol_phase(self):
        self.entr_mol_phase = Var(
            self.params.phase_list,
            doc="Phase molar entropies [J/mol.K]",
        )

        def rule_entr_mol_phase(b, p):
            return b.entr_mol_phase[p] == sum(
                b.entr_mol_phase_comp[p, j]
                * b.mole_frac_phase_comp[p, j]
                for j in b.params.component_list
            )

        self.eq_entr_mol_phase = Constraint(
            self.params.phase_list, rule=rule_entr_mol_phase
        )

    def _fug_phase_comp(self):
        """Fugacity expressions (Raoult's law for ideal VLE)."""

        def rule_fug_phase_comp(b, p, j):
            pobj = b.params.get_phase(p)
            if pobj.is_vapor_phase():
                return b.mole_frac_phase_comp[p, j] * b.pressure
            elif pobj.is_liquid_phase():
                return b.mole_frac_phase_comp[p, j] * b.pressure_sat[j]

        self.fug_phase_comp = Expression(
            self.params.phase_list,
            self.params.component_list,
            rule=rule_fug_phase_comp,
        )

    # ===================================================================
    # Saturation pressure (Antoine form)
    # ===================================================================

    def _pressure_sat_expr(self, j, T):
        """Saturation pressure expression using NIST Antoine coefficients."""
        return pyunits.convert(
            exp(
                log(10)
                * (
                    self.params.pressure_sat_comp_coeff_A[j]
                    - self.params.pressure_sat_comp_coeff_B[j]
                    / (T + self.params.pressure_sat_comp_coeff_C[j])
                )
            )
            * pyunits.bar,
            to_units=pyunits.Pa,
        )

    def _pressure_sat(self):
        self.pressure_sat = Var(
            self.params.component_list,
            initialize=101325,
            units=pyunits.Pa,
            doc="Saturation pressure [Pa]",
        )

        def rule_psat(b, j):
            return b.pressure_sat[j] == b._pressure_sat_expr(j, b._teq)

        self.eq_pressure_sat = Constraint(
            self.params.component_list, rule=rule_psat
        )

    # ===================================================================
    # Bubble and dew point temperatures
    # ===================================================================

    def _temperature_bubble(self):
        self.temperature_bubble = Var(
            initialize=298.15,
            bounds=(200, 500),
            units=pyunits.K,
            doc="Bubble point temperature [K]",
        )
        self._mole_frac_tbub = Var(
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            bounds=(0, None),
            doc="Vapor mole fractions at bubble point",
        )
        self._p_sat_tbub = Expression(
            self.params.component_list,
            rule=lambda b, j: b._pressure_sat_expr(j, b.temperature_bubble),
        )

        def rule_bubble_temp(b):
            return (
                sum(
                    b.mole_frac_comp[j] * b._p_sat_tbub[j]
                    for j in b.params.component_list
                )
                - b.pressure
                == 0
            )

        self.eq_temperature_bubble = Constraint(rule=rule_bubble_temp)

        def rule_mole_frac_tbub(b, j):
            return (
                b._mole_frac_tbub[j] * b.pressure
                == b.mole_frac_comp[j] * b._p_sat_tbub[j]
            )

        self.eq_mole_frac_tbub = Constraint(
            self.params.component_list, rule=rule_mole_frac_tbub
        )

    def _temperature_dew(self):
        self.temperature_dew = Var(
            initialize=298.15,
            bounds=(200, 500),
            units=pyunits.K,
            doc="Dew point temperature [K]",
        )
        self._mole_frac_tdew = Var(
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            bounds=(0, None),
            doc="Liquid mole fractions at dew point",
        )
        self._p_sat_tdew = Expression(
            self.params.component_list,
            rule=lambda b, j: b._pressure_sat_expr(j, b.temperature_dew),
        )

        def rule_dew_temp(b):
            return (
                b.pressure
                * sum(
                    b.mole_frac_comp[j] / b._p_sat_tdew[j]
                    for j in b.params.component_list
                )
                - 1
                == 0
            )

        self.eq_temperature_dew = Constraint(rule=rule_dew_temp)

        def rule_mole_frac_tdew(b, j):
            return (
                b._mole_frac_tdew[j] * b._p_sat_tdew[j]
                == b.mole_frac_comp[j] * b.pressure
            )

        self.eq_mole_frac_tdew = Constraint(
            self.params.component_list, rule=rule_mole_frac_tdew
        )
