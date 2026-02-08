"""Template: generic cubic VLE package (PR or SRK)."""

from pyomo.environ import units as pyunits
from idaes.core import LiquidPhase, VaporPhase, Component
from idaes.models.properties.modular_properties.eos.ceos import Cubic, CubicType
from idaes.models.properties.modular_properties.state_definitions import FTPx
from idaes.models.properties.modular_properties.phase_equil import (
    CubicComplementarityVLE,
)
from idaes.models.properties.modular_properties.phase_equil.bubble_dew import LogBubbleDew
from idaes.models.properties.modular_properties.phase_equil.forms import log_fugacity
from idaes.models.properties.modular_properties.pure import RPP4

configuration = {
    "components": {
        "component_a": {
            "type": Component,
            "enth_mol_ig_comp": RPP4,
            "entr_mol_ig_comp": RPP4,
            "pressure_sat_comp": RPP4,
            "phase_equilibrium_form": {("Vap", "Liq"): log_fugacity},
            "parameter_data": {
                "mw": (0.05, pyunits.kg / pyunits.mol),
                "pressure_crit": (4e6, pyunits.Pa),
                "temperature_crit": (500.0, pyunits.K),
                "omega": 0.1,
            },
        },
        "component_b": {
            "type": Component,
            "enth_mol_ig_comp": RPP4,
            "entr_mol_ig_comp": RPP4,
            "pressure_sat_comp": RPP4,
            "phase_equilibrium_form": {("Vap", "Liq"): log_fugacity},
            "parameter_data": {
                "mw": (0.08, pyunits.kg / pyunits.mol),
                "pressure_crit": (3e6, pyunits.Pa),
                "temperature_crit": (550.0, pyunits.K),
                "omega": 0.2,
            },
        },
    },
    "phases": {
        "Liq": {
            "type": LiquidPhase,
            "equation_of_state": Cubic,
            "equation_of_state_options": {"type": CubicType.PR},
        },
        "Vap": {
            "type": VaporPhase,
            "equation_of_state": Cubic,
            "equation_of_state_options": {"type": CubicType.PR},
        },
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
        "temperature": (250.0, 350.0, 900.0, pyunits.K),
        "pressure": (1e4, 1e5, 1e7, pyunits.Pa),
    },
    "pressure_ref": (1e5, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K),
    "phases_in_equilibrium": [("Vap", "Liq")],
    "phase_equilibrium_state": {("Vap", "Liq"): CubicComplementarityVLE},
    "bubble_dew_method": LogBubbleDew,
    "parameter_data": {
        "PR_kappa": {
            ("component_a", "component_a"): 0.0,
            ("component_a", "component_b"): 0.0,
            ("component_b", "component_a"): 0.0,
            ("component_b", "component_b"): 0.0,
        }
    },
}
