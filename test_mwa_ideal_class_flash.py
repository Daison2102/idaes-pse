# pylint: disable=all
"""Small flash-style convergence test for the class-based MWA ideal property package."""

from pyomo.environ import ConcreteModel, value
from pyomo.opt import TerminationCondition

from idaes.core import FlowsheetBlock
from idaes.core.solvers import get_solver

from mwa_ideal.mwa_ideal_class_property_package import MWAIdealParameterBlock


def build_model():
    m = ConcreteModel()
    m.fs = FlowsheetBlock(dynamic=False)

    m.fs.properties = MWAIdealParameterBlock()
    m.fs.state = m.fs.properties.build_state_block([0], defined_state=True)
    s = m.fs.state[0]

    # Overall feed conditions (flash-style specification)
    s.flow_mol.fix(100)
    s.temperature.fix(330)
    s.pressure.fix(101325)
    s.mole_frac_comp["Methanol"].fix(0.30)
    s.mole_frac_comp["Water"].fix(0.40)
    s.mole_frac_comp["Ammonia"].fix(0.30)

    # Provide simple starting guesses for split variables
    s.phase_frac["Liq"].set_value(0.5)
    s.phase_frac["Vap"].set_value(0.5)
    s.sum_phase_frac.deactivate()

    return m


def test_flash_converges():
    m = build_model()
    solver = get_solver("ipopt")
    results = solver.solve(m, tee=False)

    assert results.solver.termination_condition == TerminationCondition.optimal
    assert value(m.fs.state[0].phase_frac["Vap"]) >= 0
    assert value(m.fs.state[0].phase_frac["Liq"]) >= 0
