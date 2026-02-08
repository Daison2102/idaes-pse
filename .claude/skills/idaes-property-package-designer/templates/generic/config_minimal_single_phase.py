"""Template: minimal generic property package (single phase)."""

from pyomo.environ import units as pyunits
from idaes.core import VaporPhase, Component
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.state_definitions import FTPx

# Replace component and methods with your target system.
configuration = {
    "components": {
        "component_1": {
            "type": Component,
            "parameter_data": {
                "mw": (18e-3, pyunits.kg / pyunits.mol),
            },
        },
    },
    "phases": {
        "Vap": {
            "type": VaporPhase,
            "equation_of_state": Ideal,
        }
    },
    "base_units": {
        "time": pyunits.s,
        "length": pyunits.m,
        "mass": pyunits.kg,
        "amount": pyunits.mol,
        "temperature": pyunits.K,
    },
    "state_definition": FTPx,
    "state_bounds": {
        "flow_mol": (1e-12, 1.0, 1e3, pyunits.mol / pyunits.s),
        "temperature": (200.0, 300.0, 1500.0, pyunits.K),
        "pressure": (1e3, 1e5, 1e7, pyunits.Pa),
    },
    "pressure_ref": (1e5, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K),
}
