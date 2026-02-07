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
# Source: NIST WebBook
# - Molecular weights and most phase-equilibrium/thermo reference values.
#
# Source: IDAES examples / placeholder engineering correlations
# - Heat-capacity and liquid-density coefficients adapted for generic-framework use.

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
    "methanol": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
        "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
        "elemental_composition": {"C": 1, "H": 4, "O": 1},
        "dens_mol_liq_comp": Perrys,
        "enth_mol_liq_comp": Perrys,
        "entr_mol_liq_comp": Perrys,
        "enth_mol_ig_comp": RPP4,
        "entr_mol_ig_comp": RPP4,
        "cp_mol_ig_comp": RPP4,
        "pressure_sat_comp": NIST,
        "visc_d_phase_comp": {"Vap": ChapmanEnskogLennardJones},
        "therm_cond_phase_comp": {"Vap": Eucken},
        "parameter_data": {
            "mw": (0.0320419, pyunits.kg / pyunits.mol),
            "pressure_crit": (80.9e5, pyunits.Pa),
            "temperature_crit": (512.6, pyunits.K),
            "omega": 0.556,
            "dens_mol_liq_comp_coeff": {
                "eqn_type": 1,
                "1": (2.3267, pyunits.kmol * pyunits.m**-3),
                "2": (0.27073, None),
                "3": (512.5, pyunits.K),
                "4": (0.24713, None),
            },
            "cp_mol_ig_comp_coeff": {
                "A": (21.15, pyunits.J / pyunits.mol / pyunits.K),
                "B": (7.09e-2, pyunits.J / pyunits.mol / pyunits.K**2),
                "C": (2.587e-5, pyunits.J / pyunits.mol / pyunits.K**3),
                "D": (-2.852e-8, pyunits.J / pyunits.mol / pyunits.K**4),
            },
            "cp_mol_liq_comp_coeff": {
                "1": (256.040e3, pyunits.J / pyunits.kmol / pyunits.K),
                "2": (-2.7414e3, pyunits.J / pyunits.kmol / pyunits.K**2),
                "3": (14.777, pyunits.J / pyunits.kmol / pyunits.K**3),
                "4": (-0.035, pyunits.J / pyunits.kmol / pyunits.K**4),
                "5": (32.79e-6, pyunits.J / pyunits.kmol / pyunits.K**5),
            },
            "pressure_sat_comp_coeff": {  # NIST-derived Antoine set
                "A": (5.20409, None),
                "B": (1581.341, pyunits.K),
                "C": (-33.50, pyunits.K),
            },
            "enth_mol_form_liq_comp_ref": (-238.4e3, pyunits.J / pyunits.mol),
            "entr_mol_form_liq_comp_ref": (127.19, pyunits.J / pyunits.mol / pyunits.K),
            "entr_mol_form_vap_comp_ref": (239.81, pyunits.J / pyunits.mol / pyunits.K),
            "enth_mol_form_vap_comp_ref": (-205e3, pyunits.J / pyunits.mol),
            "lennard_jones_sigma": (3.626, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (481.8, pyunits.K),
            "f_int_eucken": 1,
        },
    },
    "water": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
        "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
        "elemental_composition": {"H": 2, "O": 1},
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
            "mw": (0.01801528, pyunits.kg / pyunits.mol),
            "pressure_crit": (221.2e5, pyunits.Pa),
            "temperature_crit": (647.3, pyunits.K),
            "omega": 0.344,
            "dens_mol_liq_comp_coeff": {
                "eqn_type": 1,
                "1": (5.459, pyunits.kmol * pyunits.m**-3),
                "2": (0.30542, None),
                "3": (647.13, pyunits.K),
                "4": (0.081, None),
            },
            "cp_mol_ig_comp_coeff": {
                "A": 30.092,
                "B": 6.832,
                "C": 6.793,
                "D": -2.534,
                "E": 0.082139,
                "F": -250.881,
                "G": 223.3967,
                "H": 0,
            },
            "cp_mol_liq_comp_coeff": {
                "1": (2.7637e5, pyunits.J / pyunits.kmol / pyunits.K),
                "2": (-2.0901e3, pyunits.J / pyunits.kmol / pyunits.K**2),
                "3": (8.125, pyunits.J / pyunits.kmol / pyunits.K**3),
                "4": (-1.4116e-2, pyunits.J / pyunits.kmol / pyunits.K**4),
                "5": (9.3701e-6, pyunits.J / pyunits.kmol / pyunits.K**5),
            },
            "pressure_sat_comp_coeff": {
                "A": (4.6543, None),
                "B": (1435.264, pyunits.K),
                "C": (-64.848, pyunits.K),
            },
            "enth_mol_form_liq_comp_ref": (-285.83e3, pyunits.J / pyunits.mol),
            "entr_mol_form_liq_comp_ref": (69.95, pyunits.J / pyunits.mol / pyunits.K),
            "entr_mol_form_vap_comp_ref": (188.84, pyunits.J / pyunits.mol / pyunits.K),
            "enth_mol_form_vap_comp_ref": (-241.83e3, pyunits.J / pyunits.mol),
            "lennard_jones_sigma": (2.641, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (809.1, pyunits.K),
            "f_int_eucken": 1,
        },
    },
    "ammonia": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
        "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
        "elemental_composition": {"N": 1, "H": 3},
        "dens_mol_liq_comp": Perrys,
        "enth_mol_liq_comp": Perrys,
        "entr_mol_liq_comp": Perrys,
        "enth_mol_ig_comp": RPP4,
        "entr_mol_ig_comp": RPP4,
        "cp_mol_ig_comp": RPP4,
        "pressure_sat_comp": NIST,
        "visc_d_phase_comp": {"Vap": ChapmanEnskogLennardJones},
        "therm_cond_phase_comp": {"Vap": Eucken},
        "parameter_data": {
            "mw": (0.0170305, pyunits.kg / pyunits.mol),
            "pressure_crit": (113.0e5, pyunits.Pa),
            "temperature_crit": (405.4, pyunits.K),
            "omega": 0.25,
            "dens_mol_liq_comp_coeff": {
                "eqn_type": 1,
                "1": (36.259, pyunits.kmol * pyunits.m**-3),
                "2": (0.28, None),
                "3": (405.4, pyunits.K),
                "4": (0.29, None),
            },
            "cp_mol_ig_comp_coeff": {
                "A": (27.31, pyunits.J / pyunits.mol / pyunits.K),
                "B": (2.383e-2, pyunits.J / pyunits.mol / pyunits.K**2),
                "C": (1.707e-5, pyunits.J / pyunits.mol / pyunits.K**3),
                "D": (-1.185e-8, pyunits.J / pyunits.mol / pyunits.K**4),
            },
            "cp_mol_liq_comp_coeff": {
                "1": (8.08e4, pyunits.J / pyunits.kmol / pyunits.K),
                "2": (0.0, pyunits.J / pyunits.kmol / pyunits.K**2),
                "3": (0.0, pyunits.J / pyunits.kmol / pyunits.K**3),
                "4": (0.0, pyunits.J / pyunits.kmol / pyunits.K**4),
                "5": (0.0, pyunits.J / pyunits.kmol / pyunits.K**5),
            },
            "pressure_sat_comp_coeff": {
                "A": (4.86886, None),
                "B": (1113.928, pyunits.K),
                "C": (-10.409, pyunits.K),
            },
            "enth_mol_form_liq_comp_ref": (-69.2e3, pyunits.J / pyunits.mol),
            "entr_mol_form_liq_comp_ref": (112.0, pyunits.J / pyunits.mol / pyunits.K),
            "entr_mol_form_vap_comp_ref": (192.77, pyunits.J / pyunits.mol / pyunits.K),
            "enth_mol_form_vap_comp_ref": (-45.90e3, pyunits.J / pyunits.mol),
            "lennard_jones_sigma": (2.900, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (558.3, pyunits.K),
            "f_int_eucken": 1.61,
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
            "flow_mol": (1e-10, 100, 1e10, pyunits.mol / pyunits.s),
            "temperature": (250.0, 330.0, 450.0, pyunits.K),
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
        ph = tuple(phases)
        configuration["phases_in_equilibrium"] = [ph]
        configuration["phase_equilibrium_state"] = {ph: SmoothVLE}
        if eos == EosType.IDEAL:
            configuration["bubble_dew_method"] = IdealBubbleDew

    if eos == EosType.PR:
        d = configuration["parameter_data"]
        d["PR_kappa"] = {(a, b): 0 for a in c for b in c}

    if scaled:
        configuration["base_units"]["mass"] = pyunits.Mg
        configuration["base_units"]["amount"] = pyunits.kmol

    return configuration


configuration = get_prop(
    components=["methanol", "water", "ammonia"],
    phases=("Vap", "Liq"),
    eos=EosType.IDEAL,
    scaled=False,
)

