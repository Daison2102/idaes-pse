# pylint: disable=all

from pyomo.environ import ConcreteModel, value
from pyomo.util.check_units import assert_units_consistent

from idaes.core import FlowsheetBlock
from idaes.core.solvers import get_solver
from idaes.core.util.model_statistics import degrees_of_freedom
from idaes.models.properties.modular_properties.base.generic_property import GenericParameterBlock
from idaes.models.unit_models import Flash

try:
    from mwa_ideal.mwa_ideal_generic_property_package import configuration
except ModuleNotFoundError:
    from mwa_ideal_generic_property_package import configuration


def build_and_solve():
    m = ConcreteModel()
    m.fs = FlowsheetBlock(dynamic=False)

    m.fs.props = GenericParameterBlock(**configuration)
    m.fs.flash = Flash(property_package=m.fs.props)

    # Inlet conditions
    m.fs.flash.inlet.flow_mol.fix(100)
    m.fs.flash.inlet.temperature.fix(330)

    m.fs.flash.heat_duty.fix(0)
    m.fs.flash.deltaP.fix(0)

    # Additional required specs
    m.fs.flash.inlet.pressure.fix(101325)
    m.fs.flash.inlet.mole_frac_comp[0, "Methanol"].fix(0.30)
    m.fs.flash.inlet.mole_frac_comp[0, "Water"].fix(0.50)
    m.fs.flash.inlet.mole_frac_comp[0, "Ammonia"].fix(0.20)

    assert_units_consistent(m)
    print("Model DOF before solve:", degrees_of_freedom(m))

    solver = get_solver("ipopt_v2")
    res = solver.solve(m, tee=True)

    print("Solver status:", res.solver.status)
    print("Termination condition:", res.solver.termination_condition)
    print("--- Outlet Summary ---")
    print("Vap flow [mol/s]:", value(m.fs.flash.vap_outlet.flow_mol[0]))
    print("Liq flow [mol/s]:", value(m.fs.flash.liq_outlet.flow_mol[0]))
    print("Vap y_methanol:", value(m.fs.flash.vap_outlet.mole_frac_comp[0, "Methanol"]))
    print("Vap y_water:", value(m.fs.flash.vap_outlet.mole_frac_comp[0, "Water"]))
    print("Vap y_ammonia:", value(m.fs.flash.vap_outlet.mole_frac_comp[0, "Ammonia"]))

    return m, res


if __name__ == "__main__":
    m, res = build_and_solve()
    m.fs.flash.report()

