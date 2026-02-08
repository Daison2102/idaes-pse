import importlib.util
import sys
from pathlib import Path

import pytest
from pyomo.environ import ConcreteModel
from pyomo.util.check_units import assert_units_consistent

from idaes.core import FlowsheetBlock
from idaes.core.solvers import get_solver
from idaes.core.util.model_statistics import degrees_of_freedom


pytestmark = pytest.mark.component


def _load_module():
    p = Path(__file__).resolve().parent / "MWA_ideal_FTPx_class.py"
    spec = importlib.util.spec_from_file_location("mwa_pkg", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_mwa_class_property_package_build_and_solve():
    mod = _load_module()

    m = ConcreteModel()
    m.fs = FlowsheetBlock(dynamic=False)
    m.fs.props = mod.MWAParameterBlock()
    m.fs.state = m.fs.props.build_state_block([0], defined_state=True)

    s = m.fs.state[0]
    s.flow_mol.fix(100.0)
    s.mole_frac_comp["water"].fix(0.40)
    s.mole_frac_comp["methanol"].fix(0.40)
    s.mole_frac_comp["ammonia"].fix(0.20)
    s.temperature.fix(330.0)
    s.pressure.fix(101325.0)

    assert degrees_of_freedom(s) == 0
    assert_units_consistent(m)

    m.fs.state.initialize()

    solver = get_solver("ipopt_v2")
    res = solver.solve(m)

    assert str(res.solver.termination_condition).lower() == "optimal"
    assert s.phase_frac["Liq"].value > 0.0
    assert s.phase_frac["Vap"].value > 0.0
    assert s.pressure_sat["ammonia"].value > s.pressure_sat["water"].value
