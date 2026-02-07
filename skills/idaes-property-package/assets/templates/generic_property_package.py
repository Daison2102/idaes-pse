# pylint: disable=all

# Import Python libraries
import logging
import copy
import enum

# Import Pyomo units
from pyomo.environ import units as pyunits

# Import IDAES cores
from idaes.core import VaporPhase, LiquidPhase, Component, PhaseType

from idaes.models.properties.modular_properties.state_definitions import FTPx
from idaes.models.properties.modular_properties.eos.ceos import Cubic, CubicType
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.phase_equil.forms import (
    fugacity,
)
from idaes.models.properties.modular_properties.phase_equil import SmoothVLE
from idaes.models.properties.modular_properties.phase_equil.bubble_dew import (
    IdealBubbleDew,
)
from idaes.models.properties.modular_properties.pure import (
    NIST,
    RPP4,
    RPP5,
    Perrys,
    ChapmanEnskogLennardJones,
    Eucken,
)
from idaes.models.properties.modular_properties.base.generic_reaction import (
    ConcentrationForm,
)
from idaes.models.properties.modular_properties.transport_properties import (
    ViscosityWilke,
    ThermalConductivityWMS,
    NoMethod,
)
from idaes.models.properties.modular_properties.transport_properties.viscosity_wilke import (
    wilke_phi_ij_callback,
)

from idaes.models.properties.modular_properties.reactions.dh_rxn import constant_dh_rxn
from idaes.models.properties.modular_properties.reactions.rate_constant import arrhenius
from idaes.models.properties.modular_properties.reactions.rate_forms import (
    power_law_rate,
)
from idaes.core.util.exceptions import ConfigurationError

# Set up logger
_log = logging.getLogger(__name__)


class EosType(enum.Enum):
    PR = 1
    IDEAL = 2


# Property Sources
#
# Source: TODO add source
# Properties: TODO list parameter groups sourced here

_phase_dicts_pr = {
    "Vap": {
        "type": VaporPhase,
        "equation_of_state": Cubic,
        "equation_of_state_options": {"type": CubicType.PR},
        "visc_d_phase": ViscosityWilke,
        "therm_cond_phase": ThermalConductivityWMS,
    },
    "Liq": {
        "type": LiquidPhase,
        "equation_of_state": Cubic,
        "equation_of_state_options": {"type": CubicType.PR},
        "visc_d_phase": NoMethod,
        "therm_cond_phase": NoMethod,
    },
}

_phase_dicts_ideal = {
    "Vap": {
        "type": VaporPhase,
        "equation_of_state": Ideal,
        "visc_d_phase": ViscosityWilke,
        "transport_property_options": {
            "viscosity_phi_ij_callback": wilke_phi_ij_callback,
        },
        "therm_cond_phase": ThermalConductivityWMS,
    },
    "Liq": {
        "type": LiquidPhase,
        "equation_of_state": Ideal,
        "visc_d_phase": NoMethod,
        "therm_cond_phase": NoMethod,
    },
}

_component_params = {
    "COMP_A": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
        "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
        "elemental_composition": {"C": 0},
        "dens_mol_liq_comp": Perrys,
        "enth_mol_liq_comp": Perrys,
        "entr_mol_liq_comp": Perrys,
        "enth_mol_ig_comp": NIST,
        "entr_mol_ig_comp": NIST,
        "cp_mol_ig_comp": NIST,
        "pressure_sat_comp": NIST,
        "visc_d_phase_comp": {"Vap": ChapmanEnskogLennardJones},
        "therm_cond_phase_comp": {"Vap": Eucken},
        "parameter_data": {
            "mw": (0.0, pyunits.kg / pyunits.mol),  # TODO source + valid range
            "pressure_crit": (0.0, pyunits.Pa),  # TODO source + valid range
            "temperature_crit": (0.0, pyunits.K),  # TODO source + valid range
            "omega": 0.0,  # unitless
            "cp_mol_ig_comp_coeff": {
                "A": 0.0,
                "B": 0.0,
                "C": 0.0,
                "D": 0.0,
                "E": 0.0,
                "F": 0.0,
                "G": 0.0,
                "H": 0.0,
            },
            "dens_mol_liq_comp_coeff": {
                "eqn_type": 1,
                "1": (0.0, pyunits.kmol * pyunits.m**-3),
                "2": (0.0, None),
                "3": (0.0, pyunits.K),
                "4": (0.0, None),
            },
            "pressure_sat_comp_coeff": {
                "A": (0.0, None),
                "B": (0.0, pyunits.K),
                "C": (0.0, pyunits.K),
            },
            "lennard_jones_sigma": (0.0, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (0.0, pyunits.K),
            "f_int_eucken": 1,  # unitless
        },
    },
}


def get_prop(components=None, phases=("Vap", "Liq"), eos=EosType.IDEAL, scaled=False):
    if components is None:
        components = list(_component_params.keys())

    configuration = {
        "components": {},
        "parameter_data": {},
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
            "flow_mol": (1e-10, 1.0, 1e10, pyunits.mol / pyunits.s),
            "temperature": (200.0, 300.0, 1000.0, pyunits.K),
            "pressure": (1e-10, 1e5, 1e10, pyunits.Pa),
        },
        "pressure_ref": (101325, pyunits.Pa),
        "temperature_ref": (298.15, pyunits.K),
    }

    if isinstance(phases, str):
        phases = [phases]

    c = configuration["components"]
    for comp in components:
        c[comp] = copy.deepcopy(_component_params[comp])

    for p in phases:
        if eos == EosType.PR:
            configuration["phases"][p] = copy.deepcopy(_phase_dicts_pr[p])
        elif eos == EosType.IDEAL:
            configuration["phases"][p] = copy.deepcopy(_phase_dicts_ideal[p])
        else:
            raise ValueError("Invalid EoS.")

    if len(phases) > 1:
        p_tuple = tuple(phases)
        configuration["phases_in_equilibrium"] = [p_tuple]
        configuration["phase_equilibrium_state"] = {p_tuple: SmoothVLE}
        if eos == EosType.IDEAL:
            configuration["bubble_dew_method"] = IdealBubbleDew

    if eos == EosType.PR:
        d = configuration["parameter_data"]
        d["PR_kappa"] = {(a, b): 0 for a in c for b in c}

    if scaled:
        configuration["base_units"]["mass"] = pyunits.Mg
        configuration["base_units"]["amount"] = pyunits.kmol

    return configuration


# Default exported configuration used by GenericParameterBlock(**configuration)
configuration = get_prop(
    components=["COMP_A"],
    phases=("Vap", "Liq"),
    eos=EosType.IDEAL,
    scaled=False,
)

