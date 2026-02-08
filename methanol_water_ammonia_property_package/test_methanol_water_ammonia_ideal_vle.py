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

import pytest
import pyomo.environ as pyo
from pyomo.environ import TerminationCondition, value

from idaes.core import FlowsheetBlock
from idaes.core.solvers import get_solver
from idaes.core.util.model_statistics import degrees_of_freedom

from methanol_water_ammonia_property_package import (
    MethanolWaterAmmoniaParameterBlock,
)


@pytest.mark.component
class TestMethanolWaterAmmoniaIdealVLE:
    @pytest.fixture(scope="class")
    def model(self):
        m = pyo.ConcreteModel()
        m.fs = FlowsheetBlock(dynamic=False)
        m.fs.params = MethanolWaterAmmoniaParameterBlock()
        m.fs.state = m.fs.params.build_state_block(
            [0],
            defined_state=True,
            has_phase_equilibrium=True,
        )

        s = m.fs.state[0]
        s.flow_mol.fix(1.0)
        s.temperature.fix(300.0)
        s.pressure.fix(1.2e5)
        s.mole_frac_comp["methanol"].fix(0.30)
        s.mole_frac_comp["water"].fix(0.40)
        s.mole_frac_comp["ammonia"].fix(0.30)

        return m

    def test_dof(self, model):
        assert degrees_of_freedom(model.fs.state[0]) == 0

    def test_property_build(self, model):
        s = model.fs.state[0]
        # Build commonly used properties
        _ = s.dens_mol_phase["Liq"]
        _ = s.dens_mol_phase["Vap"]
        _ = s.enth_mol_phase["Liq"]
        _ = s.enth_mol_phase["Vap"]
        _ = s.entr_mol_phase["Liq"]
        _ = s.entr_mol_phase["Vap"]
        _ = s.pressure_sat["methanol"]
        _ = s.pressure_sat["water"]
        _ = s.pressure_sat["ammonia"]

    def test_initialize_and_solve(self, model):
        solver = get_solver()
        if not solver.available(exception_flag=False):
            pytest.skip("No NLP solver available for component test.")

        model.fs.state.initialize()
        results = solver.solve(model, tee=False)
        assert results.solver.termination_condition == TerminationCondition.optimal

    def test_physical_ordering(self, model):
        solver = get_solver()
        if not solver.available(exception_flag=False):
            pytest.skip("No NLP solver available for component test.")

        s = model.fs.state[0]
        solver.solve(model, tee=False)

        p_sat_nh3 = value(s.pressure_sat["ammonia"])
        p_sat_meoh = value(s.pressure_sat["methanol"])
        p_sat_h2o = value(s.pressure_sat["water"])

        # At ~300 K: ammonia should be most volatile, then methanol, then water.
        assert p_sat_nh3 > p_sat_meoh > p_sat_h2o

        rho_l = value(s.dens_mol_phase["Liq"])
        rho_v = value(s.dens_mol_phase["Vap"])
        assert rho_l > rho_v > 0
