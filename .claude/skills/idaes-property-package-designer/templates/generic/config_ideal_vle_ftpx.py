"""Template: generic ideal VLE package with FTPx state definition."""

from pyomo.environ import units as pyunits
from idaes.core import LiquidPhase, VaporPhase, Component
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.state_definitions import FTPx
from idaes.models.properties.modular_properties.phase_equil import SmoothVLE
from idaes.models.properties.modular_properties.phase_equil.bubble_dew import (
    IdealBubbleDew,
)
from idaes.models.properties.modular_properties.phase_equil.forms import fugacity
from idaes.models.properties.modular_properties.pure import Perrys, RPP4

configuration = {
    "components": {
        "component_a": {
            "type": Component,
            "dens_mol_liq_comp": Perrys,
            "enth_mol_liq_comp": Perrys,
            "enth_mol_ig_comp": RPP4,
            "pressure_sat_comp": RPP4,
            "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
            "parameter_data": {
                "mw": (0.05, pyunits.kg / pyunits.mol),
                "pressure_crit": (4e6, pyunits.Pa),
                "temperature_crit": (500.0, pyunits.K),
            },
        },
        "component_b": {
            "type": Component,
            "dens_mol_liq_comp": Perrys,
            "enth_mol_liq_comp": Perrys,
            "enth_mol_ig_comp": RPP4,
            "pressure_sat_comp": RPP4,
            "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
            "parameter_data": {
                "mw": (0.08, pyunits.kg / pyunits.mol),
                "pressure_crit": (3e6, pyunits.Pa),
                "temperature_crit": (550.0, pyunits.K),
            },
        },
    },
    "phases": {
        "Liq": {"type": LiquidPhase, "equation_of_state": Ideal},
        "Vap": {"type": VaporPhase, "equation_of_state": Ideal},
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
        "flow_mol": (1e-12, 100.0, 1e4, pyunits.mol / pyunits.s),
        "temperature": (250.0, 300.0, 700.0, pyunits.K),
        "pressure": (1e4, 1e5, 1e7, pyunits.Pa),
    },
    "pressure_ref": (1e5, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K),
    "phases_in_equilibrium": [("Vap", "Liq")],
    "phase_equilibrium_state": {("Vap", "Liq"): SmoothVLE},
    "bubble_dew_method": IdealBubbleDew,
}
