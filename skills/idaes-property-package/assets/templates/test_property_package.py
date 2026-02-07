"""Template tests for an IDAES property package."""

from pyomo.environ import ConcreteModel
from pyomo.util.check_units import assert_units_consistent

from idaes.core import FlowsheetBlock
from idaes.core.util.model_statistics import degrees_of_freedom
from idaes.models.properties.modular_properties.base.generic_property import GenericParameterBlock
from idaes.models.properties.tests.test_harness import PropertyTestHarness
from idaes.models.unit_models import Flash
from idaes.core.solvers import get_solver

# TODO: import your property package configuration/class
# from my_package import configuration


class TestBasic(PropertyTestHarness):
    def configure(self):
        # TODO: set either class-based or generic package target.
        # For class-based:
        # self.prop_pack = MyParameterBlock
        # self.param_args = {}
        # For generic:
        # self.prop_pack = GenericParameterBlock
        # self.param_args = configuration
        pass


def test_generic_build_units_dof():
    # TODO: enable once configuration import is set.
    # m = ConcreteModel()
    # m.fs = FlowsheetBlock(dynamic=False)
    # m.fs.properties = GenericParameterBlock(**configuration)
    # m.fs.state = m.fs.properties.build_state_block([0], defined_state=True)
    # assert_units_consistent(m)
    # assert degrees_of_freedom(m.fs.state[0]) == 0
    pass


def test_generic_flash_smoke():
    # TODO: enable once configuration import is set.
    # m = ConcreteModel()
    # m.fs = FlowsheetBlock(dynamic=False)
    # m.fs.properties = GenericParameterBlock(**configuration)
    # m.fs.flash = Flash(property_package=m.fs.properties)
    # m.fs.flash.inlet.flow_mol.fix(100)
    # m.fs.flash.inlet.temperature.fix(330)
    # m.fs.flash.inlet.pressure.fix(101325)
    # for j in m.fs.properties.component_list:
    #     m.fs.flash.inlet.mole_frac_comp[0, j].fix(1 / len(m.fs.properties.component_list))
    # m.fs.flash.heat_duty.fix(0)
    # m.fs.flash.deltaP.fix(0)
    # assert degrees_of_freedom(m) == 0
    # solver = get_solver("ipopt")
    # res = solver.solve(m)
    # assert str(res.solver.termination_condition).lower() in {"optimal", "locallyoptimal"}
    pass
