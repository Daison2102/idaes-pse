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

"""Small Flash example using the methanol-water-ammonia class-based property package."""

import pyomo.environ as pyo
from pyomo.environ import value

from idaes.core import FlowsheetBlock
from idaes.core.solvers import get_solver
from idaes.core.util.model_statistics import degrees_of_freedom
from idaes.models.unit_models import Flash

from methanol_water_ammonia_ideal_vle import MethanolWaterAmmoniaParameterBlock


def main():
    m = pyo.ConcreteModel()
    m.fs = FlowsheetBlock(dynamic=False)

    m.fs.props = MethanolWaterAmmoniaParameterBlock()
    m.fs.flash = Flash(property_package=m.fs.props)

    # Inlet conditions requested by user
    m.fs.flash.inlet.flow_mol.fix(100)
    m.fs.flash.inlet.temperature.fix(330)
    m.fs.flash.heat_duty.fix(0)
    m.fs.flash.deltaP.fix(0)

    # Additional flash specifications required for a square problem
    m.fs.flash.inlet.pressure.fix(101325)
    m.fs.flash.inlet.mole_frac_comp[0, "methanol"].fix(0.70)
    m.fs.flash.inlet.mole_frac_comp[0, "water"].fix(0.28)
    m.fs.flash.inlet.mole_frac_comp[0, "ammonia"].fix(0.02)

    print(f"Degrees of freedom: {degrees_of_freedom(m)}")

    solver = get_solver(options={"max_iter": 2000})
    if not solver.available(exception_flag=False):
        raise RuntimeError("No NLP solver available")

    results = solver.solve(m, tee=False)
    term = str(results.solver.termination_condition)
    print(f"Solver termination: {term}")

    if term != "optimal":
        raise RuntimeError(f"Flash solve did not converge to optimal: {term}")

    print("\nOutlet summary")
    print(f"  Vapor flow [mol/s]: {value(m.fs.flash.vap_outlet.flow_mol[0]):.6f}")
    print(f"  Liquid flow [mol/s]: {value(m.fs.flash.liq_outlet.flow_mol[0]):.6f}")
    print(f"  Vapor temperature [K]: {value(m.fs.flash.vap_outlet.temperature[0]):.6f}")
    print(f"  Liquid temperature [K]: {value(m.fs.flash.liq_outlet.temperature[0]):.6f}")
    print(f"  Outlet pressure [Pa]: {value(m.fs.flash.vap_outlet.pressure[0]):.2f}")

    comps = ["methanol", "water", "ammonia"]
    print("\nVapor composition y_i")
    for c in comps:
        print(f"  {c:8s}: {value(m.fs.flash.vap_outlet.mole_frac_comp[0, c]):.8f}")

    print("\nLiquid composition x_i")
    for c in comps:
        print(f"  {c:8s}: {value(m.fs.flash.liq_outlet.mole_frac_comp[0, c]):.8f}")

    return m


if __name__ == "__main__":
    m = main()
    m.fs.flash.report()
