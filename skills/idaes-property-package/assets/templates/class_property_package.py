"""Class-based Property Package template.

Fill in TODO sections with system-specific data and equations.
"""

from pyomo.environ import Constraint, Expression, Param, Set, Var, units as pyunits
from idaes.core import (
    PhysicalParameterBlock,
    StateBlock,
    StateBlockData,
    declare_process_block_class,
)
from idaes.core.util.initialization import fix_state_vars, revert_state_vars


@declare_process_block_class("MyParameterBlock")
class MyParameterData(PhysicalParameterBlock):
    """Template parameter block with explicit PhysicalParameterBlock contract."""

    def build(self):
        super().build()

        # Required indexing sets.
        self.component_list = Set(initialize=["COMP_A"])  # TODO: update
        self.phase_list = Set(initialize=["Liq"])  # TODO: update

        # Optional elemental sets (uncomment when elemental balances are required).
        # self.element_list = Set(initialize=["C", "H", "O"])
        # self.element_comp = {
        #     "COMP_A": {"C": 1, "H": 4, "O": 1},
        # }

        # TODO: add parameters.
        self.mw = Param(
            self.component_list,
            initialize={"COMP_A": 0.050},
            units=pyunits.kg / pyunits.mol,
            mutable=True,
        )

        # Required state block linkage for downstream model construction.
        self._state_block_class = MyStateBlock

    @classmethod
    def define_metadata(cls, obj):
        """Required metadata registration: units + supported properties."""
        obj.add_default_units(
            {
                "time": pyunits.s,
                "length": pyunits.m,
                "mass": pyunits.kg,
                "amount": pyunits.mol,
                "temperature": pyunits.K,
            }
        )

        obj.add_properties(
            {
                # TODO: keep this list aligned with state block implementations.
                "flow_mol": {"method": None},
                "temperature": {"method": None},
                "pressure": {"method": None},
                "mole_frac_comp": {"method": None},
                "enth_mol_phase": {"method": "_enth_mol_phase"},
            }
        )


@declare_process_block_class("MyStateBlock", block_class=StateBlock)
class MyStateBlockData(StateBlockData):
    """Template state block."""

    def build(self):
        super().build()

        # TODO: define state variables and sensible defaults/bounds.
        self.flow_mol = Var(initialize=1.0, units=pyunits.mol / pyunits.s)
        self.temperature = Var(initialize=300.0, units=pyunits.K)
        self.pressure = Var(initialize=101325.0, units=pyunits.Pa)
        self.mole_frac_comp = Var(
            self.params.component_list, initialize=1.0, bounds=(0, 1), units=pyunits.dimensionless
        )

        # Example constructed property referenced by metadata.
        self._enth_mol_phase = Expression(
            self.params.phase_list,
            rule=lambda b, p: 0.0 * pyunits.J / pyunits.mol,  # TODO: replace
        )

        # TODO: add system-specific constraints.
        self._sum_x = Constraint(
            expr=sum(self.mole_frac_comp[j] for j in self.params.component_list) == 1.0
        )

    # Required by IDAES unit model interfaces.
    def get_material_flow_terms(self, p, j):
        # TODO: update if phase-split flows are required.
        return self.flow_mol * self.mole_frac_comp[j]

    def get_enthalpy_flow_terms(self, p):
        return self.flow_mol * self._enth_mol_phase[p]

    def initialize(self, **kwargs):
        # TODO: add robust initialization logic.
        flags = fix_state_vars(self, state_args=kwargs.pop("state_args", None))
        revert_state_vars(self, flags)
        return flags
