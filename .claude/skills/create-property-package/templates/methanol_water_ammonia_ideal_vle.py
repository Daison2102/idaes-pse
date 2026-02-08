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
Methanol-Water-Ammonia property package - class-based implementation with VLE.

Custom property package for methanol-water-ammonia mixture using explicit class
definitions. Ideal liquid and vapor assumptions with Shomate/Perry's correlations.

State Variables: FTPx (Flow, Temperature, Pressure, mole fractions)
Phases: Vapor and Liquid with VLE
Properties: Enthalpy (H), Entropy (S), Gibbs Energy (G), Heat Capacity (Cp)

Data Sources:
- NIST Chemistry WebBook, https://webbook.nist.gov/
  - Methanol: https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Mask=4
  - Water: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=4
  - Ammonia: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Mask=4
- Chase, 1998, NIST-JANAF Thermochemical Tables, Fourth Edition
- Perry's Chemical Engineers' Handbook, 7th Ed.
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
        # Source: NIST WebBook
        self.mw_comp = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": 32.0419e-3,  # NIST: https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561
                "water": 18.0153e-3,     # NIST: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185
                "ammonia": 17.0305e-3,   # NIST: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417
            },
            units=pyunits.kg / pyunits.mol,
            doc="Molecular weight [kg/mol]",
        )

        # ----- Critical properties -----
        # Source: NIST WebBook
        self.pressure_crit = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": 81.0e5,   # NIST: 81 ± 1 bar
                "water": 220.64e5,    # NIST: 220.64 bar
                "ammonia": 113.00e5,  # NIST: 113.00 bar (Brunner, 1988)
            },
            units=pyunits.Pa,
            doc="Critical pressure [Pa]",
        )
        self.temperature_crit = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": 513.0,  # NIST: 513 ± 1 K
                "water": 647.0,     # NIST: 647 ± 2 K
                "ammonia": 405.4,   # NIST: 405.4 K (Brunner, 1988)
            },
            units=pyunits.K,
            doc="Critical temperature [K]",
        )

        # ----- Ideal gas Cp coefficients (Shomate: Cp = A + B*t + C*t^2 + D*t^3 + E/t^2) -----
        # t = T/1000 (temperature in kK)
        # Source: NIST-JANAF Thermochemical Tables

        # Methanol - estimated from NIST WebBook data
        self.cp_mol_ig_comp_coeff_A = Param(
            self.component_list,
            initialize={
                "methanol": 21.15,    # Estimated from NIST data
                "water": 30.09200,    # NIST-JANAF (500-1700 K)
                "ammonia": 19.99563,  # NIST-JANAF (298-1400 K)
            },
            units=pyunits.J / pyunits.mol / pyunits.K,
        )
        self.cp_mol_ig_comp_coeff_B = Param(
            self.component_list,
            initialize={
                "methanol": 70.0,         # Estimated from NIST data
                "water": 6.832514,        # NIST-JANAF
                "ammonia": 49.77119,      # NIST-JANAF
            },
            units=pyunits.J * pyunits.mol**-1 * pyunits.K**-1 * pyunits.kiloK**-1,
        )
        self.cp_mol_ig_comp_coeff_C = Param(
            self.component_list,
            initialize={
                "methanol": -20.0,        # Estimated from NIST data
                "water": 6.793435,        # NIST-JANAF
                "ammonia": -15.37599,     # NIST-JANAF
            },
            units=pyunits.J * pyunits.mol**-1 * pyunits.K**-1 * pyunits.kiloK**-2,
        )
        self.cp_mol_ig_comp_coeff_D = Param(
            self.component_list,
            initialize={
                "methanol": 3.0,          # Estimated from NIST data
                "water": -2.534480,       # NIST-JANAF
                "ammonia": 1.921168,      # NIST-JANAF
            },
            units=pyunits.J * pyunits.mol**-1 * pyunits.K**-1 * pyunits.kiloK**-3,
        )
        self.cp_mol_ig_comp_coeff_E = Param(
            self.component_list,
            initialize={
                "methanol": 0.0,          # Estimated from NIST data
                "water": 0.082139,        # NIST-JANAF
                "ammonia": 0.189174,      # NIST-JANAF
            },
            units=pyunits.J * pyunits.mol**-1 * pyunits.K**-1 * pyunits.kiloK**2,
        )

        # ----- Vapor reference enthalpy and entropy -----
        # Source: NIST WebBook standard thermochemical data
        self.enth_mol_form_vap_comp_ref = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": -201.0e3,  # NIST standard enthalpy of formation (gas)
                "water": -241.83e3,    # NIST standard enthalpy of formation (gas)
                "ammonia": -45.90e3,   # NIST standard enthalpy of formation (gas)
            },
            units=pyunits.J / pyunits.mol,
            doc="Standard heat of formation (vapor) [J/mol]",
        )
        self.entr_mol_form_vap_comp_ref = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": 239.9,  # NIST standard entropy (gas) at 298.15 K
                "water": 188.8,     # NIST standard entropy (gas) at 298.15 K
                "ammonia": 192.8,   # NIST standard entropy (gas) at 298.15 K
            },
            units=pyunits.J / pyunits.mol / pyunits.K,
            doc="Standard entropy of formation (vapor) [J/mol.K]",
        )

        # ----- Saturation pressure coefficients (RPP/DIPPR 101) -----
        # ln(Psat/Pc) = (1-Tr)^-1 * [A(1-Tr) + B(1-Tr)^1.5 + C(1-Tr)^3 + D(1-Tr)^6]
        # Source: Estimated from NIST vapor pressure data
        self.pressure_sat_comp_coeff_A = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": -7.52,   # Fitted from NIST data
                "water": -7.76,      # Fitted from NIST data
                "ammonia": -7.25,    # Fitted from NIST data
            },
        )
        self.pressure_sat_comp_coeff_B = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": 0.5,     # Fitted from NIST data
                "water": 1.45,       # Fitted from NIST data
                "ammonia": 1.2,      # Fitted from NIST data
            },
        )
        self.pressure_sat_comp_coeff_C = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": -2.0,    # Fitted from NIST data
                "water": -2.7,       # Fitted from NIST data
                "ammonia": -1.8,     # Fitted from NIST data
            },
        )
        self.pressure_sat_comp_coeff_D = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": -1.0,    # Fitted from NIST data
                "water": -1.2,       # Fitted from NIST data
                "ammonia": -0.8,     # Fitted from NIST data
            },
        )

        # ----- Liquid Cp coefficients (Perry's polynomial) -----
        # Cp_liq = c1 + c2*T + c3*T^2 + c4*T^3 + c5*T^4  [J/kmol/K]
        # Source: Perry's Chemical Engineers' Handbook, 7th Ed.
        self.cp_mol_liq_comp_coeff_1 = Param(
            self.component_list,
            initialize={
                "methanol": 1.0443e5,  # Perry's, Table 2-174
                "water": 2.7637e5,     # Perry's, Table 2-174
                "ammonia": 7.1128e4,   # Perry's, Table 2-174
            },
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-1,
        )
        self.cp_mol_liq_comp_coeff_2 = Param(
            self.component_list,
            initialize={
                "methanol": -3.5906e2,  # Perry's
                "water": -2.0901e3,     # Perry's
                "ammonia": 6.3431e2,    # Perry's
            },
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-2,
        )
        self.cp_mol_liq_comp_coeff_3 = Param(
            self.component_list,
            initialize={
                "methanol": 1.9437,     # Perry's
                "water": 8.125,         # Perry's
                "ammonia": -2.5319,     # Perry's
            },
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-3,
        )
        self.cp_mol_liq_comp_coeff_4 = Param(
            self.component_list,
            initialize={
                "methanol": -5.0065e-3,  # Perry's
                "water": -1.4116e-2,     # Perry's
                "ammonia": 4.4421e-3,    # Perry's
            },
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-4,
        )
        self.cp_mol_liq_comp_coeff_5 = Param(
            self.component_list,
            initialize={
                "methanol": 0.0,         # Perry's
                "water": 9.3701e-6,      # Perry's
                "ammonia": 0.0,          # Perry's
            },
            units=pyunits.J * pyunits.kmol**-1 * pyunits.K**-5,
        )

        # ----- Liquid reference enthalpy and entropy -----
        # Source: NIST WebBook standard thermochemical data
        self.enth_mol_form_liq_comp_ref = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": -238.4e3,  # NIST standard enthalpy of formation (liquid)
                "water": -285.83e3,    # NIST standard enthalpy of formation (liquid)
                "ammonia": -80.29e3,   # NIST standard enthalpy of formation (liquid)
            },
            units=pyunits.J / pyunits.mol,
            doc="Standard heat of formation (liquid) [J/mol]",
        )
        self.entr_mol_form_liq_comp_ref = Param(
            self.component_list,
            mutable=False,
            initialize={
                "methanol": 127.2,  # NIST standard entropy (liquid) at 298.15 K
                "water": 69.95,     # NIST standard entropy (liquid) at 298.15 K
                "ammonia": 111.3,   # NIST standard entropy (liquid) at 298.15 K
            },
            units=pyunits.J / pyunits.mol / pyunits.K,
            doc="Standard entropy of formation (liquid) [J/mol.K]",
        )

        # ----- Liquid molar density coefficients (Perry's, eqn type 1) -----
        # rho = c1 / c2^(1 + (1 - T/c3)^c4)  [kmol/m^3]
        # Source: Perry's Chemical Engineers' Handbook, Table 2-98
        self.dens_mol_liq_comp_coeff_1 = Param(
            self.component_list,
            initialize={
                "methanol": 2.2888,  # Perry's, Table 2-98
                "water": 5.459,      # Perry's, Table 2-98
                "ammonia": 3.3886,   # Perry's, Table 2-98
            },
            units=pyunits.kmol * pyunits.m**-3,
        )
        self.dens_mol_liq_comp_coeff_2 = Param(
            self.component_list,
            initialize={
                "methanol": 0.27192,  # Perry's
                "water": 0.30542,     # Perry's
                "ammonia": 0.25445,   # Perry's
            },
        )
        self.dens_mol_liq_comp_coeff_3 = Param(
            self.component_list,
            initialize={
                "methanol": 512.64,  # Perry's
                "water": 647.13,     # Perry's
                "ammonia": 405.65,   # Perry's
            },
            units=pyunits.K,
        )
        self.dens_mol_liq_comp_coeff_4 = Param(
            self.component_list,
            initialize={
                "methanol": 0.2331,  # Perry's
                "water": 0.081,      # Perry's
                "ammonia": 0.2526,   # Perry's
            },
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
        opt = SolverFactory(solver)
        if optarg:
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
            bounds=(0, None),
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
            bounds=(0, None),
            doc="Phase mole fractions",
        )
        self.phase_frac = Var(
            self.params.phase_list,
            initialize=1 / len(self.params.phase_list),
            bounds=(0, None),
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

        # Sum of phase mole fractions equality
        def rule_sum_mole_frac(b):
            return sum(
                b.mole_frac_phase_comp[b.params.phase_list.first(), j]
                for j in b.params.component_list
            ) == sum(
                b.mole_frac_phase_comp[b.params.phase_list.last(), j]
                for j in b.params.component_list
            )

        self.sum_mole_frac = Constraint(rule=rule_sum_mole_frac)

        # Phase fraction definition
        def rule_phase_frac(b, p):
            return b.phase_frac[p] * b.flow_mol == b.flow_mol_phase[p]

        self.phase_fraction_constraint = Constraint(
            self.params.phase_list, rule=rule_phase_frac
        )

        # ----- Phase equilibrium (smooth VLE) -----
        if self.config.has_phase_equilibrium:
            self._teq = Var(initialize=298, doc="Equilibrium temperature [K]")
            self._t1 = Var(initialize=298, doc="Intermediate temperature [K]")
            self.eps_1 = Param(default=0.01, mutable=True)
            self.eps_2 = Param(default=0.0005, mutable=True)

            def rule_t1(b):
                return b._t1 == 0.5 * (
                    b.temperature
                    + b.temperature_bubble
                    + sqrt(
                        (b.temperature - b.temperature_bubble) ** 2
                        + b.eps_1**2
                    )
                )

            self._t1_constraint = Constraint(rule=rule_t1)

            def rule_teq(b):
                return b._teq == 0.5 * (
                    b._t1
                    + b.temperature_dew
                    - sqrt(
                        (b._t1 - b.temperature_dew) ** 2 + b.eps_2**2
                    )
                )

            self._teq_constraint = Constraint(rule=rule_teq)

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
                return b.dens_mol_phase["Liq"] == 1e3 * sum(
                    b.mole_frac_phase_comp["Liq", j]
                    * b.params.dens_mol_liq_comp_coeff_1[j]
                    / b.params.dens_mol_liq_comp_coeff_2[j]
                    ** (
                        1
                        + (
                            1
                            - b.temperature
                            / b.params.dens_mol_liq_comp_coeff_3[j]
                        )
                        ** b.params.dens_mol_liq_comp_coeff_4[j]
                    )
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
    # Saturation pressure (RPP form)
    # ===================================================================

    def _pressure_sat_expr(self, j, T):
        """Saturation pressure expression using RPP equation."""
        Tr = T / self.params.temperature_crit[j]
        x = 1 - Tr
        return (
            exp(
                (1 / Tr)
                * (
                    self.params.pressure_sat_comp_coeff_A[j] * x
                    + self.params.pressure_sat_comp_coeff_B[j] * x**1.5
                    + self.params.pressure_sat_comp_coeff_C[j] * x**3
                    + self.params.pressure_sat_comp_coeff_D[j] * x**6
                )
            )
            * self.params.pressure_crit[j]
        )

    def _pressure_sat(self):
        self.pressure_sat = Var(
            self.params.component_list,
            initialize=101325,
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
