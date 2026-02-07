"""Class-based Property Package template.

Fill in TODO sections with system-specific data and equations.
"""

from pyomo.environ import Var, Param, Constraint, Set, units as pyunits
from idaes.core import (
    PhysicalParameterBlock,
    StateBlock,
    StateBlockData,
    declare_process_block_class,
)
from idaes.core.util.initialization import fix_state_vars, revert_state_vars


@declare_process_block_class("MyParameterBlock")
class MyParameterData(PhysicalParameterBlock):
    def build(self):
        super().build()

        # TODO: define components and phases
        self.component_list = Set(initialize=["COMP_A"])  # update
        self.phase_list = Set(initialize=["Liq"])  # update

        # TODO: add parameters
        self.mw = Param(self.component_list, initialize={"COMP_A": 0.0})

        self._state_block_class = MyStateBlock

    @classmethod
    def define_metadata(cls, obj):
        # TODO: add properties metadata and default units
        obj.add_default_units({
            "time": pyunits.s,
            "length": pyunits.m,
            "mass": pyunits.kg,
            "amount": pyunits.mol,
            "temperature": pyunits.K,
        })


@declare_process_block_class("MyStateBlock", block_class=StateBlock)
class MyStateBlockData(StateBlockData):
    def build(self):
        super().build()

        # TODO: define state variables
        self.flow_mol = Var(initialize=1.0, units=pyunits.mol / pyunits.s)
        self.temperature = Var(initialize=300.0, units=pyunits.K)
        self.pressure = Var(initialize=101325.0, units=pyunits.Pa)

        # TODO: define property constraints and expressions
        # Example placeholders:
        # - phase equilibrium constraints (VLE/LLE/SLE)
        # - transport property expressions (viscosity, thermal conductivity)

    # Required by IDAES
    def get_material_flow_terms(self, p, j):
        # TODO: return material flow term for phase p and component j
        raise NotImplementedError

    def get_enthalpy_flow_terms(self, p):
        # TODO: return enthalpy flow term for phase p
        raise NotImplementedError

    def initialize(self, **kwargs):
        # TODO: implement initialization if needed
        flags = fix_state_vars(self)
        revert_state_vars(self, flags)
        return flags
