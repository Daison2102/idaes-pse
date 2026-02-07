# pylint: disable=all

"""Generic framework class-definition template.

Use this template only when user explicitly requests generic package
implementation via class definitions.
"""

from pyomo.environ import Var, units as pyunits

from idaes.core import Component, LiquidPhase, VaporPhase, declare_process_block_class
from idaes.models.properties.modular_properties.base.generic_property import GenericParameterData
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.state_definitions import FTPx


@declare_process_block_class("UserParameterBlock")
class UserParameterData(GenericParameterData):
    """Subclass GenericParameterData using configure/parameters hooks."""

    def configure(self):
        # Select model structure and methods.
        self.config.components = {
            "COMP_A": {
                "type": Component,
                # TODO: add selected pure methods and parameter_data mapping
            }
        }
        self.config.phases = {
            "Liq": {"type": LiquidPhase, "equation_of_state": Ideal},
            "Vap": {"type": VaporPhase, "equation_of_state": Ideal},
        }
        self.config.state_definition = FTPx
        self.config.state_bounds = {
            "flow_mol": (1e-8, 1.0, 1e6, pyunits.mol / pyunits.s),
            "temperature": (200.0, 300.0, 1000.0, pyunits.K),
            "pressure": (1e4, 101325.0, 1e8, pyunits.Pa),
        }
        self.config.pressure_ref = (101325.0, pyunits.Pa)
        self.config.temperature_ref = (298.15, pyunits.K)
        self.config.base_units = {
            "time": pyunits.s,
            "length": pyunits.m,
            "mass": pyunits.kg,
            "amount": pyunits.mol,
            "temperature": pyunits.K,
        }
        # Optional: if this IDAES build applies base units before configure(),
        # also call:
        # self.get_metadata().add_default_units(self.config.base_units)

    def parameters(self):
        # Define parameters required by selected methods.
        # Use this for user-defined extra parameters that are not automatically
        # created by selected modular methods.
        # TODO: include physically sensible values and units.
        self.user_param_1 = Var(
            initialize=1.0,
            units=pyunits.dimensionless,
            doc="Template placeholder parameter",
        )

        # TODO: if no custom parameters are needed, this method can be `pass`.


# Validation checklist for this template:
# 1. Class inherits from GenericParameterData.
# 2. configure(self) sets all required generic config keys.
# 3. parameters(self) defines only user-added parameters (or pass).
# 4. Package constructs and passes a flash smoke solve for intended use case.
