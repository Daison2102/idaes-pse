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
{{SYSTEM_NAME}} property package using Cubic EOS ({{CUBIC_TYPE}}) with VLE.

Generic Property Package Framework configuration for {{SYSTEM_DESCRIPTION}}.
Uses the Peng-Robinson (or SRK) equation of state for both liquid and vapor
phases, with property methods from the IDAES built-in libraries.

Data Sources:
{{DATA_SOURCES}}
"""
import copy
import logging
import enum

from pyomo.environ import units as pyunits

from idaes.core import VaporPhase, LiquidPhase, Component, PhaseType
import idaes.logger as idaeslog

# State definition
from idaes.models.properties.modular_properties.state_definitions import FTPx

# Equation of state
from idaes.models.properties.modular_properties.eos.ceos import Cubic, CubicType

# Phase equilibrium
from idaes.models.properties.modular_properties.phase_equil import SmoothVLE
from idaes.models.properties.modular_properties.phase_equil.forms import fugacity

# Pure component methods
from idaes.models.properties.modular_properties.pure import (
    NIST,
    RPP4,
    Perrys,
    ChapmanEnskogLennardJones,
    Eucken,
)

# Transport properties (optional)
from idaes.models.properties.modular_properties.transport_properties import (
    ViscosityWilke,
    ThermalConductivityWMS,
    NoMethod,
)

_log = idaeslog.getLogger(__name__)


# ---------------------------------------------------------------------------
# Phase configuration dictionaries
# ---------------------------------------------------------------------------

_phase_dicts = {
    "Vap": {
        "type": VaporPhase,
        "equation_of_state": Cubic,
        "equation_of_state_options": {"type": CubicType.PR},
        # Optional transport property mixing rules:
        # "visc_d_phase": ViscosityWilke,
        # "therm_cond_phase": ThermalConductivityWMS,
    },
    "Liq": {
        "type": LiquidPhase,
        "equation_of_state": Cubic,
        "equation_of_state_options": {"type": CubicType.PR},
        # "visc_d_phase": NoMethod,
        # "therm_cond_phase": NoMethod,
    },
}

# ---------------------------------------------------------------------------
# Component parameter dictionaries
# ---------------------------------------------------------------------------

_component_params = {
    "{{COMP_A}}": {
        "type": Component,
        "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
        "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
        "elemental_composition": {{COMP_A_ELEMENTS}},
        # Vapor-phase property methods
        "enth_mol_ig_comp": NIST,
        "entr_mol_ig_comp": NIST,
        "cp_mol_ig_comp": NIST,
        # Liquid-phase property methods
        "dens_mol_liq_comp": Perrys,
        "enth_mol_liq_comp": Perrys,
        "entr_mol_liq_comp": Perrys,
        "pressure_sat_comp": NIST,
        # Optional transport methods:
        # "visc_d_phase_comp": {"Vap": ChapmanEnskogLennardJones},
        # "therm_cond_phase_comp": {"Vap": Eucken},
        "parameter_data": {
            "mw": ({{COMP_A_MW}}, pyunits.kg / pyunits.mol),  # {{REF}}
            "pressure_crit": ({{COMP_A_PC}}, pyunits.Pa),  # {{REF}}
            "temperature_crit": ({{COMP_A_TC}}, pyunits.K),  # {{REF}}
            "omega": {{COMP_A_OMEGA}},  # {{REF}}
            # Shomate equation coefficients (NIST)
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
            "pressure_sat_comp_coeff": {  # Antoine (NIST)
                "A": {{PSA}},
                "B": {{PSB}},
                "C": {{PSC}},
            },
            # Liquid density (Perry's)
            "dens_mol_liq_comp_coeff": {
                "eqn_type": 1,
                "1": ({{D1}}, pyunits.kmol * pyunits.m**-3),
                "2": ({{D2}}, None),
                "3": ({{D3}}, pyunits.K),
                "4": ({{D4}}, None),
            },
            # Liquid heat capacity (Perry's)
            "cp_mol_liq_comp_coeff": {
                "1": ({{L1}}, pyunits.J / pyunits.kmol / pyunits.K),
                "2": ({{L2}}, pyunits.J / pyunits.kmol / pyunits.K**2),
                "3": ({{L3}}, pyunits.J / pyunits.kmol / pyunits.K**3),
                "4": ({{L4}}, pyunits.J / pyunits.kmol / pyunits.K**4),
                "5": ({{L5}}, pyunits.J / pyunits.kmol / pyunits.K**5),
            },
            # Reference state enthalpies and entropies
            "enth_mol_form_liq_comp_ref": (
                {{COMP_A_HLIQ}}, pyunits.J / pyunits.mol
            ),
            "entr_mol_form_liq_comp_ref": (
                {{COMP_A_SLIQ}}, pyunits.J / pyunits.mol / pyunits.K
            ),
            "enth_mol_form_vap_comp_ref": (
                {{COMP_A_HVAP}}, pyunits.J / pyunits.mol
            ),
            "entr_mol_form_vap_comp_ref": (
                {{COMP_A_SVAP}}, pyunits.J / pyunits.mol / pyunits.K
            ),
            # Optional transport parameters:
            # "lennard_jones_sigma": ({{LJ_SIGMA}}, pyunits.angstrom),
            # "lennard_jones_epsilon_reduced": ({{LJ_EPS}}, pyunits.K),
            # "f_int_eucken": 1,
        },
    },
    # Add more components here following the same pattern.
    # "{{COMP_B}}": { ... },
}


# ---------------------------------------------------------------------------
# Helper function for runtime configurability
# ---------------------------------------------------------------------------


def get_prop(components=None, phases=None, scaled=False):
    """
    Build a configuration dictionary for the selected components and phases.

    Args:
        components: list of component names (default: all)
        phases: list of phase names, e.g. ["Vap", "Liq"] (default: both)
        scaled: if True, use Mg/kmol as base units for large-scale models

    Returns:
        dict: Configuration dictionary for GenericParameterBlock
    """
    if components is None:
        components = list(_component_params.keys())
    if phases is None:
        phases = ["Vap", "Liq"]

    configuration = {
        "components": {c: copy.deepcopy(_component_params[c]) for c in components},
        "phases": {p: copy.deepcopy(_phase_dicts[p]) for p in phases},
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
            "temperature": (198.15, 298.15, 612.75, pyunits.K),
            "pressure": (1e-10, 1e5, 1e10, pyunits.Pa),
        },
        "pressure_ref": (101325, pyunits.Pa),
        "temperature_ref": (298.15, pyunits.K),
    }

    # Phase equilibrium (only if multiple phases)
    if len(phases) > 1:
        p = tuple(phases)
        configuration["phases_in_equilibrium"] = [p]
        configuration["phase_equilibrium_state"] = {p: SmoothVLE}

    # Binary interaction parameters (PR kappa) - default all zeros
    c = configuration["components"]
    configuration["parameter_data"] = {
        "PR_kappa": {(a, b): 0 for a in c for b in c}
    }

    # Scaled base units for large-scale models
    if scaled:
        configuration["base_units"]["mass"] = pyunits.Mg
        configuration["base_units"]["amount"] = pyunits.kmol

    return configuration
