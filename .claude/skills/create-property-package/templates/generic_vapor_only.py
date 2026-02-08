#################################################################################
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES).
#
# Copyright (c) 2018-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory,
# National Technology & Engineering Solutions of Sandia, LLC, Carnegie Mellon
# University, West Virginia University Research Corporation, et al.
# All rights reserved.  Please see the files COPYRIGHT.md and LICENSE.md
# for full copyright and license information.
#################################################################################
"""
{{SYSTEM_NAME}} property package - vapor phase only.

Generic Property Package Framework configuration for {{SYSTEM_DESCRIPTION}}.
Single vapor phase using {{EOS_NAME}} equation of state.

Data Sources:
{{DATA_SOURCES}}
"""
from pyomo.environ import units as pyunits

from idaes.core import VaporPhase, Component, PhaseType
import idaes.logger as idaeslog

# State definition
from idaes.models.properties.modular_properties.state_definitions import FTPx

# Equation of state - choose one:
from idaes.models.properties.modular_properties.eos.ideal import Ideal

# Uncomment for Peng-Robinson:
# from idaes.models.properties.modular_properties.eos.ceos import Cubic, CubicType

# Pure component methods
from idaes.models.properties.modular_properties.pure import NIST

# Uncomment for RPP4 instead of NIST:
# from idaes.models.properties.modular_properties.pure import RPP4

# Optional transport properties
# from idaes.models.properties.modular_properties.pure import (
#     ChapmanEnskogLennardJones,
#     Eucken,
# )
# from idaes.models.properties.modular_properties.transport_properties import (
#     ViscosityWilke,
#     ThermalConductivityWMS,
# )

_log = idaeslog.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration dictionary
# ---------------------------------------------------------------------------

configuration = {
    # -----------------------------------------------------------------------
    # 1. Components (vapor-only: no liquid methods or Psat needed)
    # -----------------------------------------------------------------------
    "components": {
        "{{COMP_A}}": {
            "type": Component,
            "valid_phase_types": [PhaseType.vaporPhase],
            "elemental_composition": {{COMP_A_ELEMENTS}},
            "enth_mol_ig_comp": NIST,
            "entr_mol_ig_comp": NIST,
            "cp_mol_ig_comp": NIST,
            # No phase_equilibrium_form needed for single-phase
            "parameter_data": {
                "mw": ({{COMP_A_MW}}, pyunits.kg / pyunits.mol),  # {{REF}}
                "pressure_crit": ({{COMP_A_PC}}, pyunits.Pa),  # {{REF}}
                "temperature_crit": ({{COMP_A_TC}}, pyunits.K),  # {{REF}}
                # Shomate coefficients (NIST)
                "cp_mol_ig_comp_coeff": {
                    "A": {{A}},
                    "B": {{B}},
                    "C": {{C}},
                    "D": {{D}},
                    "E": {{E}},
                    "F": {{F}},
                    "G": {{G}},
                    "H": {{H}},
                },
                # If using Cubic EOS, also include:
                # "omega": {{COMP_A_OMEGA}},
            },
        },
        # Add more components following the same pattern.
        # "{{COMP_B}}": { ... },
    },
    # -----------------------------------------------------------------------
    # 2. Phases (vapor only)
    # -----------------------------------------------------------------------
    "phases": {
        "Vap": {
            "type": VaporPhase,
            "equation_of_state": Ideal,
            # For Peng-Robinson:
            # "equation_of_state": Cubic,
            # "equation_of_state_options": {"type": CubicType.PR},
            # Optional transport mixing rules:
            # "visc_d_phase": ViscosityWilke,
            # "therm_cond_phase": ThermalConductivityWMS,
        },
    },
    # -----------------------------------------------------------------------
    # 3. Base units
    # -----------------------------------------------------------------------
    "base_units": {
        "time": pyunits.s,
        "length": pyunits.m,
        "mass": pyunits.kg,
        "amount": pyunits.mol,
        "temperature": pyunits.K,
    },
    # -----------------------------------------------------------------------
    # 4. State definition (no VLE config needed)
    # -----------------------------------------------------------------------
    "state_definition": FTPx,
    "state_bounds": {
        "flow_mol": (0, 100, 1e4, pyunits.mol / pyunits.s),
        "temperature": (200, 350, 1500, pyunits.K),
        "pressure": (5e4, 1e5, 5e6, pyunits.Pa),
    },
    "pressure_ref": (1e5, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K),
    # No phases_in_equilibrium, phase_equilibrium_state, or bubble_dew_method
}
