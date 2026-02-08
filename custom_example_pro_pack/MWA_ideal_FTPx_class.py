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
Class-based property package for an ideal liquid methanol-water-ammonia mixture.

Modeling assumptions:
1. Single liquid phase only.
2. Ideal mixture behavior.
3. Constant pure-component liquid molar heat capacities.
4. Constant pure-component liquid molar densities.
5. No phase equilibrium calculations.
"""

from pyomo.environ import (
    Constraint,
    Expression,
    NonNegativeReals,
    Param,
    Reals,
    Var,
    units,
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
    declare_process_block_class,
)
from idaes.core.util.initialization import fix_state_vars, revert_state_vars
from idaes.core.util.model_statistics import degrees_of_freedom

import idaes.logger as idaeslog


__author__ = "Daison Caballero, Codex"

_log = idaeslog.getLogger(__name__)


@declare_process_block_class("MWAParameterBlock")
class MWAParameterData(PhysicalParameterBlock):
    """Parameter block for methanol-water-ammonia liquid mixture."""

    def build(self):
        super().build()

        self._state_block_class = MWAStateBlock

        self.Liq = LiquidPhase()

        self.methanol = Component()
        self.water = Component()
        self.ammonia = Component()

        self.mw_comp = Param(
            self.component_list,
            initialize={
                "methanol": 32.04186e-3,
                "water": 18.01528e-3,
                "ammonia": 17.03052e-3,
            },
            mutable=False,
            units=units.kg / units.mol,
            doc="Molecular weight [kg/mol]",
        )

        self.cp_mol_liq_comp = Param(
            self.component_list,
            initialize={
                "methanol": 81.1,
                "water": 75.3,
                "ammonia": 80.0,
            },
            mutable=False,
            units=units.J / units.mol / units.K,
            doc="Constant liquid molar heat capacity [J/mol/K]",
        )

        self.dens_mol_liq_comp = Param(
            self.component_list,
            initialize={
                "methanol": 24700.0,
                "water": 55388.0,
                "ammonia": 40000.0,
            },
            mutable=False,
            units=units.mol / units.m**3,
            doc="Constant liquid molar density [mol/m^3]",
        )

        self.pressure_ref = Param(
            mutable=True,
            initialize=101325.0,
            units=units.Pa,
            doc="Reference pressure [Pa]",
        )

        self.temperature_ref = Param(
            mutable=True,
            initialize=298.15,
            units=units.K,
            doc="Reference temperature [K]",
        )

    @classmethod
    def define_metadata(cls, obj):
        obj.add_properties(
            {
                "flow_mol": {"method": None},
                "pressure": {"method": None},
                "temperature": {"method": None},
                "mole_frac_comp": {"method": None},
                "flow_mol_comp": {"method": "_flow_mol_comp"},
                "mw": {"method": "_mw"},
                "cp_mol": {"method": "_cp_mol"},
                "dens_mol": {"method": "_dens_mol"},
                "enth_mol": {"method": "_enth_mol"},
            }
        )

        obj.add_default_units(
            {
                "time": units.s,
                "length": units.m,
                "mass": units.kg,
                "amount": units.mol,
                "temperature": units.K,
            }
        )


class _MWAStateBlock(StateBlock):
    """Methods applied to all indexed states in the block."""

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

        init_log = idaeslog.getInitLogger(blk.name, outlvl, tag="properties")

        if not state_vars_fixed:
            flags = fix_state_vars(blk, state_args)
        else:
            flags = None
            for b in blk.values():
                if degrees_of_freedom(b) != 0:
                    raise RuntimeError(
                        "State vars fixed but degrees of freedom is not zero during initialization."
                    )

        # This package uses explicit algebraic state definitions and expressions only,
        # so no solve call is required in initialization.

        if not state_vars_fixed:
            if hold_state:
                return flags
            blk.release_state(flags)

        init_log.info("Initialization Complete.")
        return None

    def release_state(blk, flags, outlvl=idaeslog.NOTSET):
        init_log = idaeslog.getInitLogger(blk.name, outlvl, tag="properties")

        if flags is None:
            return

        revert_state_vars(blk, flags)
        init_log.info("State Released.")


@declare_process_block_class("MWAStateBlock", block_class=_MWAStateBlock)
class MWAStateBlockData(StateBlockData):
    """State block data for methanol-water-ammonia ideal liquid mixture."""

    def build(self):
        super().build()

        self.flow_mol = Var(
            initialize=1.0,
            domain=NonNegativeReals,
            bounds=(1e-12, 1e5),
            units=units.mol / units.s,
            doc="Total molar flow [mol/s]",
        )
        self.temperature = Var(
            initialize=298.15,
            domain=Reals,
            bounds=(250.0, 450.0),
            units=units.K,
            doc="State temperature [K]",
        )
        self.pressure = Var(
            initialize=101325.0,
            domain=Reals,
            bounds=(5e4, 5e6),
            units=units.Pa,
            doc="State pressure [Pa]",
        )
        self.mole_frac_comp = Var(
            self.params.component_list,
            initialize=1 / len(self.params.component_list),
            domain=NonNegativeReals,
            bounds=(0.0, 1.0),
            doc="Mixture mole fraction [-]",
        )

        if not self.config.defined_state:
            self.sum_mole_frac = Constraint(
                expr=sum(self.mole_frac_comp[j] for j in self.params.component_list)
                == 1.0
            )

    def _flow_mol_comp(self):
        self.flow_mol_comp = Expression(
            self.params.component_list,
            rule=lambda b, j: b.flow_mol * b.mole_frac_comp[j],
            doc="Component molar flow [mol/s]",
        )

    def _mw(self):
        self.mw = Expression(
            expr=sum(
                self.mole_frac_comp[j] * self.params.mw_comp[j]
                for j in self.params.component_list
            ),
            doc="Mixture molecular weight [kg/mol]",
        )

    def _cp_mol(self):
        self.cp_mol = Expression(
            expr=sum(
                self.mole_frac_comp[j] * self.params.cp_mol_liq_comp[j]
                for j in self.params.component_list
            ),
            doc="Mixture molar heat capacity [J/mol/K]",
        )

    def _dens_mol(self):
        self.dens_mol = Expression(
            expr=sum(
                self.mole_frac_comp[j] * self.params.dens_mol_liq_comp[j]
                for j in self.params.component_list
            ),
            doc="Mixture molar density [mol/m^3]",
        )

    def _enth_mol(self):
        self.enth_mol = Expression(
            expr=self.cp_mol * (self.temperature - self.params.temperature_ref),
            doc="Mixture molar enthalpy relative to reference [J/mol]",
        )

    def get_material_flow_terms(self, p, j):
        return self.flow_mol_comp[j]

    def get_enthalpy_flow_terms(self, p):
        return self.flow_mol * self.enth_mol

    def get_material_density_terms(self, p, j):
        return self.dens_mol * self.mole_frac_comp[j]

    def get_energy_density_terms(self, p):
        return self.dens_mol * self.enth_mol

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
            "Molar Flowrate": self.flow_mol,
            "Mole Fraction": self.mole_frac_comp,
            "Temperature": self.temperature,
            "Pressure": self.pressure,
        }

    def get_material_flow_basis(self):
        return MaterialFlowBasis.molar

    def model_check(self):
        if value(self.temperature) < self.temperature.lb:
            _log.error("%s Temperature below lower bound.", self.name)
        if value(self.temperature) > self.temperature.ub:
            _log.error("%s Temperature above upper bound.", self.name)

        if value(self.pressure) < self.pressure.lb:
            _log.error("%s Pressure below lower bound.", self.name)
        if value(self.pressure) > self.pressure.ub:
            _log.error("%s Pressure above upper bound.", self.name)
