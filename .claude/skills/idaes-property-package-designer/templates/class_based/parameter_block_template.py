"""Template: class-based parameter block for IDAES property packages."""

from pyomo.environ import Param, units as pyunits
from idaes.core import (
    declare_process_block_class,
    PhysicalParameterBlock,
    LiquidPhase,
    VaporPhase,
    Component,
)


@declare_process_block_class("TemplateParameterBlock")
class TemplateParameterData(PhysicalParameterBlock):
    """Replace all placeholders and extend this class for your system."""

    def build(self):
        super().build()

        # Set associated state block class in your module.
        # self._state_block_class = TemplateStateBlock

        self.Liq = LiquidPhase()
        self.Vap = VaporPhase()

        self.component_a = Component()
        self.component_b = Component()

        self.pressure_ref = Param(
            initialize=101325.0,
            units=pyunits.Pa,
            mutable=True,
            doc="Reference pressure",
        )
        self.temperature_ref = Param(
            initialize=298.15,
            units=pyunits.K,
            mutable=True,
            doc="Reference temperature",
        )

    @classmethod
    def define_metadata(cls, obj):
        obj.add_properties(
            {
                "flow_mol": {"method": None},
                "temperature": {"method": None},
                "pressure": {"method": None},
                "mole_frac_comp": {"method": None},
                "enth_mol": {"method": "_enth_mol"},
            }
        )
        obj.add_default_units(
            {
                "time": pyunits.s,
                "length": pyunits.m,
                "mass": pyunits.kg,
                "amount": pyunits.mol,
                "temperature": pyunits.K,
            }
        )
