from pyomo.environ import ConcreteModel, value

from idaes.core import FlowsheetBlock
from idaes.core.solvers import get_solver
from idaes.core.util.model_statistics import degrees_of_freedom
from idaes.models.properties.modular_properties.base.generic_property import (
    GenericParameterBlock,
)
from idaes.models.unit_models.flash import Flash

from MWA_ideal_FTPx import configuration


def main():
    m = ConcreteModel()
    m.fs = FlowsheetBlock(dynamic=False)

    m.fs.props = GenericParameterBlock(**configuration)

    m.fs.flash = Flash(
        dynamic=False,
        has_heat_transfer=True,
        has_pressure_change=True,
        property_package=m.fs.props,
    )

    # Inlet conditions requested by user
    m.fs.flash.inlet.flow_mol[0].fix(100)
    m.fs.flash.inlet.temperature[0].fix(330)

    m.fs.flash.heat_duty.fix(0)
    m.fs.flash.deltaP.fix(0)

    # Additional required specs for FTPx state definition
    m.fs.flash.inlet.pressure[0].fix(101325)
    m.fs.flash.inlet.mole_frac_comp[0, "water"].fix(0.40)
    m.fs.flash.inlet.mole_frac_comp[0, "methanol"].fix(0.40)
    m.fs.flash.inlet.mole_frac_comp[0, "ammonia"].fix(0.20)

    dof = degrees_of_freedom(m)
    if dof != 0:
        raise RuntimeError(f"Expected DOF=0 before solve, got {dof}")

    m.fs.flash.initialize()

    solver = get_solver("ipopt_v2")
    res = solver.solve(m)

    print("Solver status:", res.solver.status)
    print("Termination:", res.solver.termination_condition)
    print("DOF:", degrees_of_freedom(m))

    print("\nOutlet vapor flow [mol/s]:", value(m.fs.flash.vap_outlet.flow_mol[0]))
    print("Outlet liquid flow [mol/s]:", value(m.fs.flash.liq_outlet.flow_mol[0]))
    print("Vapor T [K]:", value(m.fs.flash.vap_outlet.temperature[0]))
    print("Liquid T [K]:", value(m.fs.flash.liq_outlet.temperature[0]))

    for c in ["water", "methanol", "ammonia"]:
        print(f"y_{c}:", value(m.fs.flash.vap_outlet.mole_frac_comp[0, c]))
    for c in ["water", "methanol", "ammonia"]:
        print(f"x_{c}:", value(m.fs.flash.liq_outlet.mole_frac_comp[0, c]))


if __name__ == "__main__":
    main()
