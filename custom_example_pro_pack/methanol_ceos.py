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

# Source: NIST webbook
# Properties: Heat capacity coefficients for all species except ethane,
# propane, and butane. Reference enthalpies and entropies for all species.

# Source: The Properties of Gases and Liquids (1987)
# 4th edition, Chemical Engineering Series - Robert C. Reid
# Properties: Critical temperatures and pressures. Omega.
# Heat capacity coefficients for ethane, propane, and butane.

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
}

_component_params = {
    "H2": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase],
        "elemental_composition": {"H": 2},
        "enth_mol_ig_comp": NIST,
        "entr_mol_ig_comp": NIST,
        "cp_mol_ig_comp": NIST,
        "visc_d_phase_comp": {"Vap": ChapmanEnskogLennardJones},
        "therm_cond_phase_comp": {"Vap": Eucken},
        "parameter_data": {
            "mw": (0.0020159, pyunits.kg / pyunits.mol),
            "pressure_crit": (13e5, pyunits.Pa),
            "temperature_crit": (33.2, pyunits.K),
            "omega": -0.218,
            "cp_mol_ig_comp_coeff": {
                "A": 33.066178,
                "B": -11.363417,
                "C": 11.432816,
                "D": -2.772874,
                "E": -0.158558,
                "F": -9.980797,
                "G": 172.707974,
                "H": 0.0,
            },
            "lennard_jones_sigma": (2.826, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (59.7, pyunits.K),
            "f_int_eucken": 1,
        },
    },
    "CO": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase],
        "elemental_composition": {"C": 1, "O": 1},
        "enth_mol_ig_comp": NIST,
        "entr_mol_ig_comp": NIST,
        "cp_mol_ig_comp": NIST,
        "visc_d_phase_comp": {"Vap": ChapmanEnskogLennardJones},
        "therm_cond_phase_comp": {"Vap": Eucken},
        "parameter_data": {
            "mw": (0.0280101, pyunits.kg / pyunits.mol),
            "pressure_crit": (34.99e5, pyunits.Pa),
            "temperature_crit": (132.9, pyunits.K),
            "omega": 0.066,
            "cp_mol_ig_comp_coeff": {
                "A": 25.56759,
                "B": 6.09613,
                "C": 4.054656,
                "D": -2.671301,
                "E": 0.131021,
                "F": -118.0089,
                "G": 227.3665,
                "H": 0,
            },
            "lennard_jones_sigma": (3.690, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (91.7, pyunits.K),
            "f_int_eucken": 1,
        },
    },
    "CO2": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
        "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
        "elemental_composition": {"C": 1, "O": 2},
        "enth_mol_ig_comp": NIST,
        "entr_mol_ig_comp": NIST,
        "cp_mol_ig_comp": NIST,
        "dens_mol_liq_comp": Perrys,
        "enth_mol_liq_comp": Perrys,
        "entr_mol_liq_comp": Perrys,
        "pressure_sat_comp": NIST,
        "parameter_data": {
            "mw": (0.04401, pyunits.kg / pyunits.mol),
            "pressure_crit": (73.8e5, pyunits.Pa),
            "temperature_crit": (304.1, pyunits.K),
            "omega": 0.239,
            "dens_mol_liq_comp_coeff": {
                'eqn_type': 1,
                '1': (2.768, pyunits.kmol*pyunits.m**-3),  # [2] pg. 2-98
                '2': (0.26212, None),
                '3': (304.21, pyunits.K),
                '4': (0.2908, None)
            },
            "cp_mol_ig_comp_coeff": {
                "A": 24.99735,
                "B": 55.18696,
                "C": -33.69137,
                "D": 7.948387,
                "E": -0.136638,
                "F": -403.6075,
                "G": 228.2431,
                "H": 0,
            },
            "cp_mol_liq_comp_coeff": {
                '1': (-8304300, pyunits.J/pyunits.kmol/pyunits.K),  # [2]
                '2': (104370, pyunits.J/pyunits.kmol/pyunits.K**2),
                '3': (-433.33, pyunits.J/pyunits.kmol/pyunits.K**3),
                '4': (0.60052, pyunits.J/pyunits.kmol/pyunits.K**4),
                '5': (0, pyunits.J/pyunits.kmol/pyunits.K**5)
            },
            "pressure_sat_comp_coeff": {  # NIST <- Stull 1947
                "A": 6.81228,
                "B": 1301.679,
                "C": -3.494,
            },
            "enth_mol_form_liq_comp_ref": (
                14.6e3, pyunits.J/pyunits.mol
                ),  # [3]
            "entr_mol_form_liq_comp_ref": (
                63.57, pyunits.J/pyunits.mol/pyunits.K
                ),
            "entr_mol_form_vap_comp_ref": (
                213.785, pyunits.J/pyunits.mol/pyunits.K
                ),
            "enth_mol_form_vap_comp_ref": (
                -393.51e3, pyunits.J/pyunits.mol
                ), 
            "lennard_jones_sigma": (3.941, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (195.2, pyunits.K),
            "f_int_eucken": 1,
        },
    },
    "H2O": {
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
        "parameter_data": {
            "mw": (0.01801528, pyunits.kg / pyunits.mol),
            "pressure_crit": (221.2e5, pyunits.Pa),
            "temperature_crit": (647.3, pyunits.K),
            "omega": 0.344,
            "dens_mol_liq_comp_coeff": {
                "eqn_type": 1,
                "1": (5.459, pyunits.kmol * pyunits.m**-3),  # [2] pg. 2-98, temperature range 273.16 K - 333.15 K
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
                "1": (2.7637e5, pyunits.J / pyunits.kmol / pyunits.K),  # [2] pg 2-174, temperature range 273.16 K - 533.15 K
                "2": (-2.0901e3, pyunits.J / pyunits.kmol / pyunits.K**2),
                "3": (8.125, pyunits.J / pyunits.kmol / pyunits.K**3),
                "4": (-1.4116e-2, pyunits.J / pyunits.kmol / pyunits.K**4),
                "5": (9.3701e-6, pyunits.J / pyunits.kmol / pyunits.K**5),
            },
            "pressure_sat_comp_coeff": {  # NIST <- Stull 1947
                "A": 5.402,
                "B": 1838.675,
                "C": -31.737,
            },
            "enth_mol_form_liq_comp_ref": (
                -285.83e3, pyunits.J/pyunits.mol
                ),  # [3]
            "entr_mol_form_liq_comp_ref": (
                69.95, pyunits.J/pyunits.mol/pyunits.K
                ),
            "entr_mol_form_vap_comp_ref": (
                188.84, pyunits.J/pyunits.mol/pyunits.K
                ),
            "enth_mol_form_vap_comp_ref": (
                -241.83e3, pyunits.J/pyunits.mol
                ),  # [3]
            "lennard_jones_sigma": (2.641, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (809.1, pyunits.K),
            "f_int_eucken": 1,
        },
    },
    "CH3OH": {
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
        "parameter_data": {
            "mw": (0.0320419, pyunits.kg / pyunits.mol),
            "pressure_crit": (80.9e5, pyunits.Pa),
            "temperature_crit": (512.6, pyunits.K),
            "omega": 0.556,
            "dens_mol_liq_comp_coeff": {
                'eqn_type': 1,
                '1': (2.3267, pyunits.kmol*pyunits.m**-3),
                '2': (0.27073, None),
                '3': (512.5, pyunits.K),
                '4': (0.24713, None)
            },
            "cp_mol_ig_comp_coeff": {
                "A": 21.15,
                "B": 0.0709,
                "C": 2.587E-5,
                "D": -2.852E-8,
            },
            "cp_mol_liq_comp_coeff": {
                '1': (256.040e3, pyunits.J/pyunits.kmol/pyunits.K),
                '2': (-2.7414e3, pyunits.J/pyunits.kmol/pyunits.K**2),
                '3': (14.777, pyunits.J/pyunits.kmol/pyunits.K**3),
                '4': (-0.035, pyunits.J/pyunits.kmol/pyunits.K**4),
                '5': (32.79e-6, pyunits.J/pyunits.kmol/pyunits.K**5)
            },
            "pressure_sat_comp_coeff": {  # NIST <- Stull 1947
                "A": 5.1583,
                "B": 1569.613,
                "C": -34.846,
            },
            "enth_mol_form_liq_comp_ref": (
                -238.4e3, pyunits.J/pyunits.mol
                ),  # [3]
            "entr_mol_form_liq_comp_ref": (
                127.19, pyunits.J/pyunits.mol/pyunits.K
                ),
            "entr_mol_form_vap_comp_ref": (
                239.81, pyunits.J/pyunits.mol/pyunits.K
                ),
            "enth_mol_form_vap_comp_ref": (
                -205e3, pyunits.J/pyunits.mol
                ),  # [3]
            "lennard_jones_sigma": (3.626, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (481.8, pyunits.K),
            "f_int_eucken": 1
        },
    },
    "DME2": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
        "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
        "elemental_composition": {"C": 2, "H": 6, "O": 1},
        "dens_mol_liq_comp": Perrys,
        "enth_mol_liq_comp": Perrys,
        "entr_mol_liq_comp": Perrys,
        "enth_mol_ig_comp": NIST,
        "entr_mol_ig_comp": NIST,
        "cp_mol_ig_comp": NIST,
        "pressure_sat_comp": NIST,
        "parameter_data": {
            "mw": (0.04606, pyunits.kg / pyunits.mol),
            "pressure_crit": (53e5, pyunits.Pa),
            "temperature_crit": (401, pyunits.K),
            "omega": 0.196,
            "dens_mol_liq_comp_coeff": {
                'eqn_type': 1,
                '1': (1.5693, pyunits.kmol*pyunits.m**-3),  # [2] pg. 2-98
                '2': (0.2679, None),
                '3': (400.1, pyunits.K),
                '4': (0.2882, None)
            },
            "cp_mol_ig_comp_coeff": {
                "A": 25.94,
                "B": 0.178,
                "C": -0.186e-3,
                "D": 0,
                "E": 0,
                "F": 0,
                "G": 0,
                "H": 0,
            },
            "cp_mol_liq_comp_coeff": {
                '1': (110100, pyunits.J/pyunits.kmol/pyunits.K),  # [2]
                '2': (-157.47, pyunits.J/pyunits.kmol/pyunits.K**2),
                '3': (0.51853, pyunits.J/pyunits.kmol/pyunits.K**3),
                '4': (0, pyunits.J/pyunits.kmol/pyunits.K**4),
                '5': (0, pyunits.J/pyunits.kmol/pyunits.K**5)
            },
            "pressure_sat_comp_coeff": {  # NIST <- Stull 1947
                "A": 4.11475,
                "B": 894.66,
                "C": -30.604,
            },
            "enth_mol_form_liq_comp_ref": (
                -210.6e3, pyunits.J/pyunits.mol
                ),  # [3]
            "entr_mol_form_liq_comp_ref": (
                146.57, pyunits.J/pyunits.mol/pyunits.K
                ),
            "entr_mol_form_vap_comp_ref": (
                342.2, pyunits.J/pyunits.mol/pyunits.K
                ),
            "enth_mol_form_vap_comp_ref": (
                -184.1e3, pyunits.J/pyunits.mol
                ),  # [3]
            "lennard_jones_sigma": (4.307, pyunits.angstrom),
            "lennard_jones_epsilon_reduced": (395, pyunits.K),
            "f_int_eucken": 1
        },
    },
}

_water_visc_d = {"Vap": ChapmanEnskogLennardJones, "Liq": None}
_water_therm_cond = {"Vap": Eucken, "Liq": None}

def get_prop(components=None, phases="Vap", eos=EosType.PR, scaled=False):
    if components is None:
        components = list(_component_params.keys())
    configuration = {
        "components": {},  # fill in later based on selected components
        "parameter_data": {},
        "phases": {},
        # Set base units of measurement
        "base_units": {
            "time": pyunits.s,
            "length": pyunits.m,
            "mass": pyunits.kg,
            "amount": pyunits.mol,
            "temperature": pyunits.K,
        },
        # Specifying state definition
    "state_definition": FTPx,
    "state_bounds": {"flow_mol": (1e-10, 100, 1e10, pyunits.mol/pyunits.s),
                     "temperature": (198.15, 298.15, 612.75, pyunits.K),
                     "pressure": (1e-10, 1e5, 1e10, pyunits.Pa)},
    "pressure_ref": (101325, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K)
    }

    c = configuration["components"]
    if isinstance(phases, str):
        phases = [phases]
    for comp in components:
        c[comp] = copy.deepcopy(_component_params[comp])
        if comp == "H2O":
            c["H2O"]["visc_d_phase_comp"] = copy.deepcopy(
                {p: _water_visc_d[p] for p in phases}
            )
            c["H2O"]["therm_cond_phase_comp"] = copy.deepcopy(
                {p: _water_therm_cond[p] for p in phases}
            )
    for k in phases:
        if eos == EosType.PR:
            configuration["phases"][k] = copy.deepcopy(_phase_dicts_pr[k])
        elif eos == EosType.IDEAL:
            if k == "Liq":
                raise ConfigurationError(
                    "This parameter set does not support Ideal EOS with liquid"
                )
            configuration["phases"][k] = copy.deepcopy(_phase_dicts_ideal[k])
        else:
            raise ValueError("Invalid EoS.")
    if len(phases) > 1:
        p = tuple(phases)
        configuration["phases_in_equilibrium"] = [p]
        configuration["phase_equilibrium_state"] = {p: SmoothVLE}

    # Fill the binary parameters with zeros.
    d = configuration["parameter_data"]
    d["PR_kappa"] = {(a, b): 0 for a in c for b in c}

    # Change to scaled units if specified
    if scaled:
        configuration["base_units"]["mass"] = pyunits.Mg
        configuration["base_units"]["amount"] = pyunits.kmol

    return configuration
