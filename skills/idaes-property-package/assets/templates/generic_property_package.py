# pylint: disable=all

# Import Python libraries
import copy
import enum
import logging

# Import Pyomo units
from pyomo.environ import units as pyunits

# Import IDAES cores
from idaes.core import Component, LiquidPhase, PhaseType, VaporPhase
from idaes.core.util.exceptions import ConfigurationError

from idaes.models.properties.modular_properties.state_definitions import FTPx
from idaes.models.properties.modular_properties.eos.ceos import Cubic, CubicType
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.phase_equil import SmoothVLE
from idaes.models.properties.modular_properties.phase_equil.bubble_dew import IdealBubbleDew
from idaes.models.properties.modular_properties.phase_equil.forms import fugacity
from idaes.models.properties.modular_properties.pure import (
    ChapmanEnskogLennardJones,
    Eucken,
    NIST,
    Perrys,
)
from idaes.models.properties.modular_properties.transport_properties import (
    NoMethod,
    ThermalConductivityWMS,
    ViscosityWilke,
)
from idaes.models.properties.modular_properties.transport_properties.viscosity_wilke import (
    wilke_phi_ij_callback,
)

# Set up logger
_log = logging.getLogger(__name__)


class EosType(enum.Enum):
    PR = 1
    IDEAL = 2


# Property Sources
#
# Source: TODO add source reference(s)
# Properties: TODO list which parameter groups come from each source

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
        "transport_property_options": {"viscosity_phi_ij_callback": wilke_phi_ij_callback},
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
            "mw": (0.0, pyunits.kg / pyunits.mol),  # TODO source + range
            "pressure_crit": (0.0, pyunits.Pa),  # TODO source + range
            "temperature_crit": (0.0, pyunits.K),  # TODO source + range
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
    }
}


def _validate_generic_choices(configuration, eos, phases):
    """Validate generic framework compatibility before returning config."""
    required_keys = (
        "components",
        "phases",
        "base_units",
        "state_definition",
        "state_bounds",
        "pressure_ref",
        "temperature_ref",
    )
    missing = [k for k in required_keys if k not in configuration]
    if missing:
        raise ConfigurationError(f"Missing required generic configuration keys: {missing}")

    # Equilibrium triad consistency checks.
    if "phases_in_equilibrium" in configuration:
        pairs = configuration["phases_in_equilibrium"]
        pe_state = configuration.get("phase_equilibrium_state", {})
        for p in pairs:
            if p not in pe_state:
                raise ConfigurationError(f"Missing phase_equilibrium_state for pair {p}.")
            for comp, cobj in configuration["components"].items():
                pe_form = cobj.get("phase_equilibrium_form", {})
                if p[0] in phases and p[1] in phases:
                    # Only require per-component form when component appears in both phases.
                    if p not in pe_form:
                        _log.debug(
                            "Component %s does not define phase_equilibrium_form for pair %s.",
                            comp,
                            p,
                        )

    # Compatibility guard: ideal bubble/dew only in ideal two-phase assumptions.
    if "bubble_dew_method" in configuration:
        if eos != EosType.IDEAL or len(phases) != 2:
            raise ConfigurationError(
                "bubble_dew_method is configured but setup is not ideal two-phase."
            )

    # Placeholder completeness checks for common transport methods.
    for comp, cdata in configuration["components"].items():
        pdata = cdata.get("parameter_data", {})
        if "visc_d_phase_comp" in cdata or "therm_cond_phase_comp" in cdata:
            for required in ("lennard_jones_sigma", "lennard_jones_epsilon_reduced"):
                if required not in pdata:
                    raise ConfigurationError(
                        f"Component {comp} missing transport parameter: {required}"
                    )


def get_prop(components=None, phases=("Vap", "Liq"), eos=EosType.IDEAL, scaled=False):
    if components is None:
        components = list(_component_params.keys())
    if isinstance(phases, str):
        phases = [phases]

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
        # Global behavior option (default true in IDAES docs).
        "include_enthalpy_of_formation": True,
    }

    # Populate components.
    for comp in components:
        configuration["components"][comp] = copy.deepcopy(_component_params[comp])

    # Populate phases.
    for p in phases:
        if eos == EosType.PR:
            configuration["phases"][p] = copy.deepcopy(_phase_dicts_pr[p])
        elif eos == EosType.IDEAL:
            configuration["phases"][p] = copy.deepcopy(_phase_dicts_ideal[p])
        else:
            raise ValueError("Invalid EoS selection.")

    # Optional equilibrium block.
    if len(phases) > 1:
        p_tuple = tuple(phases)
        configuration["phases_in_equilibrium"] = [p_tuple]
        configuration["phase_equilibrium_state"] = {p_tuple: SmoothVLE}
        if eos == EosType.IDEAL:
            configuration["bubble_dew_method"] = IdealBubbleDew

    # EOS package-level parameters.
    if eos == EosType.PR:
        configuration["parameter_data"]["PR_kappa"] = {
            (a, b): 0.0 for a in components for b in components
        }

    # Optional base-unit scaling pattern.
    if scaled:
        configuration["base_units"]["mass"] = pyunits.Mg
        configuration["base_units"]["amount"] = pyunits.kmol

    _validate_generic_choices(configuration, eos, phases)
    return configuration


# Default exported configuration for GenericParameterBlock(**configuration).
configuration = get_prop(
    components=["COMP_A"],
    phases=("Vap", "Liq"),
    eos=EosType.IDEAL,
    scaled=False,
)
