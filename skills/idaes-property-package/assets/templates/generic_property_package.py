"""Generic Property Package template (IDAES modular_properties).

Fill in TODO sections with system-specific data.
"""

import logging
from pyomo.environ import units as pyunits

from idaes.core import LiquidPhase, VaporPhase, Component, PhaseType

from idaes.models.properties.modular_properties.state_definitions import FTPx
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.phase_equil.forms import fugacity
from idaes.models.properties.modular_properties.phase_equil import SmoothVLE

from idaes.models.properties.modular_properties.pure import NIST, Perrys, RPP5
from idaes.models.properties.modular_properties.transport_properties import (
    NoMethod,
    ViscosityWilke,
    ThermalConductivityWMS,
)
from idaes.models.properties.modular_properties.transport_properties.viscosity_wilke import (
    wilke_phi_ij_callback,
)

_log = logging.getLogger(__name__)

# TODO: Replace with your system's components, phases, and parameters.

configuration = {
    "components": {
        "COMP_A": {
            "type": Component,
            "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
            "elemental_composition": {"C": 0},
            "enth_mol_ig_comp": NIST,
            "entr_mol_ig_comp": NIST,
            "cp_mol_ig_comp": NIST,
            "dens_mol_liq_comp": Perrys,
            "enth_mol_liq_comp": Perrys,
            "entr_mol_liq_comp": Perrys,
            "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
            # Optional transport properties per component
            # "visc_d_phase_comp": {"Vap": <method>},
            # "therm_cond_phase_comp": {"Vap": <method>},
            "parameter_data": {
                "mw": (0.0, pyunits.kg / pyunits.mol),
                "pressure_crit": (0.0, pyunits.Pa),
                "temperature_crit": (0.0, pyunits.K),
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
            },
        },
    },
    "phases": {
        "Liq": {
            "type": LiquidPhase,
            "equation_of_state": Ideal,
            # For non-ideal: swap EOS and add options
            # "equation_of_state": Cubic,
            # "equation_of_state_options": {"type": CubicType.PR},
            "visc_d_phase": NoMethod,
            "therm_cond_phase": NoMethod,
        },
        "Vap": {
            "type": VaporPhase,
            "equation_of_state": Ideal,
            "visc_d_phase": ViscosityWilke,
            "therm_cond_phase": ThermalConductivityWMS,
            "transport_property_options": {
                "viscosity_phi_ij_callback": wilke_phi_ij_callback,
            },
        },
    },
    "state_definition": FTPx,
    "phase_equilibrium": {("Vap", "Liq"): SmoothVLE},
    # Optional equilibrium options, if needed by the formulation
    # "phase_equilibrium_options": {("Vap", "Liq"): {"smooth": True}},
    "base_units": {
        "time": pyunits.s,
        "length": pyunits.m,
        "mass": pyunits.kg,
        "amount": pyunits.mol,
        "temperature": pyunits.K,
    },
}
