##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2020, by the
# software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia
# University Research Corporation, et al. All rights reserved.
#
# Please see the files COPYRIGHT.txt and LICENSE.txt for full copyright and
# license information, respectively. Both files are also available online
# at the URL "https://github.com/IDAES/idaes-pse".
##############################################################################
"""
Methanol-Water-Ammonia phase equilibrium package using ideal liquid and vapor.

Generic property package implementation using IDAES modular framework.

State definition: FTPx
Phases: Liq + Vap
EOS: Ideal (both phases)
Equilibrium: fugacity form with SmoothVLE + IdealBubbleDew
"""

# Import Python libraries
import logging

# Import Pyomo libraries
from pyomo.environ import units as pyunits

# Import IDAES libraries
from idaes.core import LiquidPhase, VaporPhase, Component
from idaes.models.properties.modular_properties.state_definitions import FTPx
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.phase_equil import SmoothVLE
from idaes.models.properties.modular_properties.phase_equil.bubble_dew import (
    IdealBubbleDew,
)
from idaes.models.properties.modular_properties.phase_equil.forms import fugacity
from idaes.models.properties.modular_properties.pure import Constant, NIST

# Set up logger
_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Data sources for physically reasonable placeholder values
#
# Antoine + critical + molecular weight (NIST WebBook)
# Water:    https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Type=ANTOINE&Mask=4
# Methanol: https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Type=ANTOINE&Mask=4
# Ammonia:  https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Type=ANTOINE&Mask=4
#
# Heat capacities (NIST WebBook / Engineering Toolbox)
# Water liquid Cp(298K): ~75.37 J/mol/K
# Methanol gas Cp(298K): ~44.06 J/mol/K
# Methanol liquid Cp(298K): ~81.08 J/mol/K
# Ammonia gas Cp(298K): ~35.65 J/mol/K
# Ammonia liquid Cp(near ambient): ~80.9 J/mol/K
#
# Densities converted to molar density placeholders at near-ambient conditions.
# ---------------------------------------------------------------------

configuration = {
    # Components
    "components": {
        "methanol": {
            "type": Component,
            "elemental_composition": {"C": 1, "H": 4, "O": 1},
            "cp_mol_ig_comp": Constant,
            "enth_mol_ig_comp": Constant,
            "cp_mol_liq_comp": Constant,
            "enth_mol_liq_comp": Constant,
            "dens_mol_liq_comp": Constant,
            "pressure_sat_comp": NIST,
            "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
            "parameter_data": {
                "mw": (0.0320419, pyunits.kg / pyunits.mol),
                "pressure_crit": (80.97e5, pyunits.Pa),
                "temperature_crit": (512.6, pyunits.K),
                "cp_mol_ig_comp_coeff": (
                    44.06,
                    pyunits.J / pyunits.mol / pyunits.K,
                ),
                "enth_mol_form_ig_comp_ref": (-201.0e3, pyunits.J / pyunits.mol),
                "cp_mol_liq_comp_coeff": (
                    81.08,
                    pyunits.J / pyunits.mol / pyunits.K,
                ),
                "enth_mol_form_liq_comp_ref": (-238.4e3, pyunits.J / pyunits.mol),
                "dens_mol_liq_comp_coeff": (
                    24549.0,
                    pyunits.mol / pyunits.m**3,
                ),
                # NIST Antoine form: log10(P_bar)=A-B/(T_K+C)
                "pressure_sat_comp_coeff": {
                    "A": 5.20409,
                    "B": (1581.341, pyunits.K),
                    "C": (-33.50, pyunits.K),
                },
            },
        },
        "water": {
            "type": Component,
            "elemental_composition": {"H": 2, "O": 1},
            "cp_mol_ig_comp": Constant,
            "enth_mol_ig_comp": Constant,
            "cp_mol_liq_comp": Constant,
            "enth_mol_liq_comp": Constant,
            "dens_mol_liq_comp": Constant,
            "pressure_sat_comp": NIST,
            "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
            "parameter_data": {
                "mw": (0.01801528, pyunits.kg / pyunits.mol),
                "pressure_crit": (220.64e5, pyunits.Pa),
                "temperature_crit": (647.0, pyunits.K),
                "cp_mol_ig_comp_coeff": (
                    33.59,
                    pyunits.J / pyunits.mol / pyunits.K,
                ),
                "enth_mol_form_ig_comp_ref": (-241.83e3, pyunits.J / pyunits.mol),
                "cp_mol_liq_comp_coeff": (
                    75.37,
                    pyunits.J / pyunits.mol / pyunits.K,
                ),
                "enth_mol_form_liq_comp_ref": (-285.83e3, pyunits.J / pyunits.mol),
                "dens_mol_liq_comp_coeff": (
                    55343.0,
                    pyunits.mol / pyunits.m**3,
                ),
                # NIST Antoine form: log10(P_bar)=A-B/(T_K+C)
                "pressure_sat_comp_coeff": {
                    "A": 5.40221,
                    "B": (1838.675, pyunits.K),
                    "C": (-31.737, pyunits.K),
                },
            },
        },
        "ammonia": {
            "type": Component,
            "elemental_composition": {"N": 1, "H": 3},
            "cp_mol_ig_comp": Constant,
            "enth_mol_ig_comp": Constant,
            "cp_mol_liq_comp": Constant,
            "enth_mol_liq_comp": Constant,
            "dens_mol_liq_comp": Constant,
            "pressure_sat_comp": NIST,
            "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
            "parameter_data": {
                "mw": (0.01703052, pyunits.kg / pyunits.mol),
                "pressure_crit": (113.5e5, pyunits.Pa),
                "temperature_crit": (405.4, pyunits.K),
                "cp_mol_ig_comp_coeff": (
                    35.65,
                    pyunits.J / pyunits.mol / pyunits.K,
                ),
                "enth_mol_form_ig_comp_ref": (-45.90e3, pyunits.J / pyunits.mol),
                "cp_mol_liq_comp_coeff": (
                    80.90,
                    pyunits.J / pyunits.mol / pyunits.K,
                ),
                "enth_mol_form_liq_comp_ref": (-80.29e3, pyunits.J / pyunits.mol),
                "dens_mol_liq_comp_coeff": (
                    35759.0,
                    pyunits.mol / pyunits.m**3,
                ),
                # NIST Antoine form: log10(P_bar)=A-B/(T_K+C)
                "pressure_sat_comp_coeff": {
                    "A": 4.86886,
                    "B": (1113.928, pyunits.K),
                    "C": (-10.409, pyunits.K),
                },
            },
        },
    },
    # Phases
    "phases": {
        "Liq": {
            "type": LiquidPhase,
            "equation_of_state": Ideal,
        },
        "Vap": {
            "type": VaporPhase,
            "equation_of_state": Ideal,
        },
    },
    # Base units
    "base_units": {
        "time": pyunits.s,
        "length": pyunits.m,
        "mass": pyunits.kg,
        "amount": pyunits.mol,
        "temperature": pyunits.K,
    },
    # State definition
    "state_definition": FTPx,
    "state_bounds": {
        "flow_mol": (1e-8, 100.0, 1e6, pyunits.mol / pyunits.s),
        "temperature": (250.0, 330.0, 600.0, pyunits.K),
        "pressure": (1e4, 101325.0, 2e7, pyunits.Pa),
    },
    "pressure_ref": (101325.0, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K),
    # Phase equilibrium
    "phases_in_equilibrium": [("Vap", "Liq")],
    "phase_equilibrium_state": {("Vap", "Liq"): SmoothVLE},
    "bubble_dew_method": IdealBubbleDew,
}
