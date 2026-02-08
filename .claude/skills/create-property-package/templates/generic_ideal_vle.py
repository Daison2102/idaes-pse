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
{{SYSTEM_NAME}} property package using Ideal EOS with VLE.

Generic Property Package Framework configuration for {{SYSTEM_DESCRIPTION}}.
Uses Ideal liquid and vapor assumptions with property methods from the
IDAES built-in libraries.

Data Sources:
{{DATA_SOURCES}}
"""
# Import Pyomo units
from pyomo.environ import units as pyunits

# Import IDAES cores
from idaes.core import LiquidPhase, VaporPhase, Component
import idaes.logger as idaeslog

# State definition
from idaes.models.properties.modular_properties.state_definitions import FTPx

# Equation of state
from idaes.models.properties.modular_properties.eos.ideal import Ideal

# Phase equilibrium
from idaes.models.properties.modular_properties.phase_equil import SmoothVLE
from idaes.models.properties.modular_properties.phase_equil.bubble_dew import (
    IdealBubbleDew,
)
from idaes.models.properties.modular_properties.phase_equil.forms import fugacity

# Pure component property methods
from idaes.models.properties.modular_properties.pure import RPP4, Perrys

# Uncomment if using NIST data instead of RPP4:
# from idaes.models.properties.modular_properties.pure import NIST

_log = idaeslog.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration dictionary
# ---------------------------------------------------------------------------

configuration = {
    # -----------------------------------------------------------------------
    # 1. Components
    # -----------------------------------------------------------------------
    "components": {
        "{{COMP_A}}": {
            "type": Component,
            "elemental_composition": {{COMP_A_ELEMENTS}},
            # Vapor-phase property methods
            "enth_mol_ig_comp": RPP4,
            "entr_mol_ig_comp": RPP4,
            "pressure_sat_comp": RPP4,
            # Liquid-phase property methods
            "dens_mol_liq_comp": Perrys,
            "enth_mol_liq_comp": Perrys,
            "entr_mol_liq_comp": Perrys,
            # Phase equilibrium
            "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
            # Parameter data
            "parameter_data": {
                "mw": ({{COMP_A_MW}}, pyunits.kg / pyunits.mol),  # {{REF}}
                "pressure_crit": ({{COMP_A_PC}}, pyunits.Pa),  # {{REF}}
                "temperature_crit": ({{COMP_A_TC}}, pyunits.K),  # {{REF}}
                "cp_mol_ig_comp_coeff": {
                    "A": ({{A}}, pyunits.J / pyunits.mol / pyunits.K),
                    "B": ({{B}}, pyunits.J / pyunits.mol / pyunits.K**2),
                    "C": ({{C}}, pyunits.J / pyunits.mol / pyunits.K**3),
                    "D": ({{D}}, pyunits.J / pyunits.mol / pyunits.K**4),
                },
                "pressure_sat_comp_coeff": {
                    "A": ({{PSA}}, None),
                    "B": ({{PSB}}, None),
                    "C": ({{PSC}}, None),
                    "D": ({{PSD}}, None),
                },
                "enth_mol_form_vap_comp_ref": (
                    {{COMP_A_HVAP}}, pyunits.J / pyunits.mol
                ),  # {{REF}}
                "entr_mol_form_vap_comp_ref": (
                    {{COMP_A_SVAP}}, pyunits.J / pyunits.mol / pyunits.K
                ),  # {{REF}}
                "cp_mol_liq_comp_coeff": {
                    "1": ({{L1}}, pyunits.J / pyunits.kmol / pyunits.K),
                    "2": ({{L2}}, pyunits.J / pyunits.kmol / pyunits.K**2),
                    "3": ({{L3}}, pyunits.J / pyunits.kmol / pyunits.K**3),
                    "4": ({{L4}}, pyunits.J / pyunits.kmol / pyunits.K**4),
                    "5": ({{L5}}, pyunits.J / pyunits.kmol / pyunits.K**5),
                },
                "dens_mol_liq_comp_coeff": {
                    "eqn_type": 1,
                    "1": ({{D1}}, pyunits.kmol * pyunits.m**-3),
                    "2": ({{D2}}, None),
                    "3": ({{D3}}, pyunits.K),
                    "4": ({{D4}}, None),
                },
                "enth_mol_form_liq_comp_ref": (
                    {{COMP_A_HLIQ}}, pyunits.J / pyunits.mol
                ),  # {{REF}}
                "entr_mol_form_liq_comp_ref": (
                    {{COMP_A_SLIQ}}, pyunits.J / pyunits.mol / pyunits.K
                ),  # {{REF}}
            },
        },
        # Repeat for each additional component:
        # "{{COMP_B}}": { ... },
    },
    # -----------------------------------------------------------------------
    # 2. Phases
    # -----------------------------------------------------------------------
    "phases": {
        "Liq": {"type": LiquidPhase, "equation_of_state": Ideal},
        "Vap": {"type": VaporPhase, "equation_of_state": Ideal},
    },
    # -----------------------------------------------------------------------
    # 3. Base units of measurement
    # -----------------------------------------------------------------------
    "base_units": {
        "time": pyunits.s,
        "length": pyunits.m,
        "mass": pyunits.kg,
        "amount": pyunits.mol,
        "temperature": pyunits.K,
    },
    # -----------------------------------------------------------------------
    # 4. State definition
    # -----------------------------------------------------------------------
    "state_definition": FTPx,
    "state_bounds": {
        "flow_mol": (0, 100, 1000, pyunits.mol / pyunits.s),
        "temperature": (273.15, 300, 450, pyunits.K),
        "pressure": (5e4, 1e5, 1e6, pyunits.Pa),
    },
    "pressure_ref": (1e5, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K),
    # -----------------------------------------------------------------------
    # 5. Phase equilibrium
    # -----------------------------------------------------------------------
    "phases_in_equilibrium": [("Vap", "Liq")],
    "phase_equilibrium_state": {("Vap", "Liq"): SmoothVLE},
    "bubble_dew_method": IdealBubbleDew,
}
