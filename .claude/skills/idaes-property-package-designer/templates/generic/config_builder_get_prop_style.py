"""Template: configurable builder for generic property packages (get_prop style)."""

import copy
import enum
from pyomo.environ import units as pyunits
from idaes.core import LiquidPhase, VaporPhase, Component
from idaes.models.properties.modular_properties.state_definitions import FTPx
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.eos.ceos import Cubic, CubicType


class EosType(enum.Enum):
    PR = "PR"
    SRK = "SRK"
    IDEAL = "IDEAL"


_PHASES_PR = {
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
}

_PHASES_IDEAL = {
    "Vap": {
        "type": VaporPhase,
        "equation_of_state": Ideal,
    }
}

_COMPONENTS = {
    "component_a": {
        "type": Component,
        "parameter_data": {"mw": (0.03, pyunits.kg / pyunits.mol)},
    },
    "component_b": {
        "type": Component,
        "parameter_data": {"mw": (0.04, pyunits.kg / pyunits.mol)},
    },
}


def get_prop(components=None, phases=None, eos=EosType.PR):
    """Return a generic property-package configuration dictionary."""
    if components is None:
        components = list(_COMPONENTS.keys())
    if phases is None:
        phases = ["Vap", "Liq"] if eos != EosType.IDEAL else ["Vap"]

    cfg = {
        "components": {},
        "phases": {},
        "base_units": {
            "time": pyunits.s,
            "length": pyunits.m,
            "mass": pyunits.kg,
            "amount": pyunits.mol,
            "temperature": pyunits.K,
        },
        "state_definition": FTPx,
        "state_bounds": {
            "flow_mol": (1e-12, 100.0, 1e6, pyunits.mol / pyunits.s),
            "temperature": (200.0, 300.0, 1200.0, pyunits.K),
            "pressure": (1e3, 1e5, 1e8, pyunits.Pa),
        },
        "pressure_ref": (101325.0, pyunits.Pa),
        "temperature_ref": (298.15, pyunits.K),
        "parameter_data": {},
    }

    for c in components:
        cfg["components"][c] = copy.deepcopy(_COMPONENTS[c])

    for p in phases:
        if eos == EosType.IDEAL:
            cfg["phases"][p] = copy.deepcopy(_PHASES_IDEAL[p])
        else:
            cfg["phases"][p] = copy.deepcopy(_PHASES_PR[p])

    if len(phases) > 1:
        pair = tuple(phases[:2])
        cfg["phases_in_equilibrium"] = [pair]

    # Fill with defaults for cubic EOS use cases.
    cfg["parameter_data"]["PR_kappa"] = {(i, j): 0.0 for i in components for j in components}

    return cfg
