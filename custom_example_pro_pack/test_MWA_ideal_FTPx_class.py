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
"""Smoke tests for the methanol-water-ammonia class-based property package."""

import pytest
from pyomo.environ import ConcreteModel, value
from pyomo.util.check_units import assert_units_consistent

from idaes.core.util.model_statistics import degrees_of_freedom

from custom_example_pro_pack.MWA_ideal_FTPx_class import MWAParameterBlock


@pytest.mark.unit
def test_parameter_block_build():
    m = ConcreteModel()
    m.params = MWAParameterBlock()

    assert len(m.params.phase_list) == 1
    assert "Liq" in m.params.phase_list

    assert len(m.params.component_list) == 3
    for c in ("methanol", "water", "ammonia"):
        assert c in m.params.component_list


@pytest.mark.unit
def test_state_block_smoke():
    m = ConcreteModel()
    m.params = MWAParameterBlock()
    m.props = m.params.build_state_block([1], defined_state=True)

    m.props[1].flow_mol.fix(10.0)
    m.props[1].temperature.fix(298.15)
    m.props[1].pressure.fix(101325.0)
    m.props[1].mole_frac_comp["methanol"].fix(0.30)
    m.props[1].mole_frac_comp["water"].fix(0.60)
    m.props[1].mole_frac_comp["ammonia"].fix(0.10)

    assert degrees_of_freedom(m.props[1]) == 0
    assert_units_consistent(m)

    assert value(m.props[1].mw) == pytest.approx(0.0227, rel=1e-2)
    assert value(m.props[1].dens_mol) > 0.0
    assert value(m.props[1].cp_mol) > 0.0
