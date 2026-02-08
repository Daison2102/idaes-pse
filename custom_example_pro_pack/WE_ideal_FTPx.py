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
Water-Ethanol phase equilibrium package using ideal liquid and vapor.

Example property package using the Generic Property Package Framework.
This exmample shows how to set up a property package to do water-ethanol
phase equilibrium in the generic framework using ideal liquid and vapor
assumptions along with methods drawn from the pre-built IDAES property
libraries.
"""
# Import Python libraries
import logging

# Import Pyomo libraries
from pyomo.environ import units as pyunits

# Import IDAES libraries
# Import method to define phases and component types
from idaes.core import LiquidPhase, VaporPhase, Component
# Import method to define the state definition
from idaes.generic_models.properties.core.state_definitions import FTPx
# Import methods to define phase equilibria
# EOS
from idaes.generic_models.properties.core.eos.ideal import Ideal
# Phase equilibrium state formulation
from idaes.generic_models.properties.core.phase_equil import smooth_VLE
# Bubble and dew point methods
from idaes.generic_models.properties.core.phase_equil.bubble_dew import IdealBubbleDew
#  Phase Equilibrium Formulation
from idaes.generic_models.properties.core.phase_equil.forms import fugacity
# Import modules for pure component property methods
import idaes.generic_models.properties.core.pure.Perrys as Perrys
import idaes.generic_models.properties.core.pure.NIST as NIST
import idaes.generic_models.properties.core.pure.RPP as RPP

# Set up logger
_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration dictionary for an ideal Water-Ethanol system

# Data Sources:
# [1] The Properties of Gases and Liquids (2000)
#     5th edition, Chemical Engineering Series: Bruce E. Poling - John M. Prausnitz - John P. O’Connell
# [2] Perry's Chemical Engineers' Handbook 7th Ed.
# [3] Engineering Toolbox, https://www.engineeringtoolbox.com
# [4] NIST, https://webbook.nist.gov/chemistry/name-ser/
# [5] DIPPR Database
#     Retrieved 3rd October, 2020

configuration = {
    # 1) Specifying components
    "components": {
        "water": {# 1.1) Type of chemical specie 
                  "type": Component,
                  # 1.2) Valid phases
                  #"valid_phase_types": [list of phases where the component exists]
                  # 1.3) Elemental composition
                  "elemental_composition": {"H": 2, "O": 1},
                  # 1.4) Pure component property methods - from IDAES library
                  # Heat capacity, molar enthalpy, molar entropy and saturation pressure for vapor ==> from RPP module
                  #"cp_mol_ig_comp": RPP,
                  "enth_mol_ig_comp": RPP, 
                  "entr_mol_ig_comp": RPP,
                  "pressure_sat_comp": RPP,
                  # Heat capacity, molar enthalpy, molar entropy and molar density for liquid ==> from PERRY module
                  #"cp_mol_liq_comp": Perrys,
                  "enth_mol_liq_comp": Perrys,
                  "entr_mol_liq_comp": Perrys,
                  "dens_mol_liq_comp": Perrys,
                  # 1.5) Phase Equilibrium Formulation
                  "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
                  # 1.6) Parameter Data
                  "parameter_data": {
                  # Molecular weight
                                     "mw": (18.015E-3, pyunits.kg/pyunits.mol),  # Reference [1] p A.19
                  # Critical Pressure
                                     "pressure_crit": (220.64e5, pyunits.Pa),  # Reference [1] p A.19
                  # Critical Temperature
                                     "temperature_crit": (647.14, pyunits.K),  # Reference [1] p A.19
                  # Parameters for heat capacity, molar enthalpy, molar entropy and saturation pressure for vapor ==> from RPP
                                     "cp_mol_ig_comp_coeff": {# Range of temperature ()-() K. Reference [1] 3rd Ed. p 668
                                                              'A': (3.224E1, pyunits.J/pyunits.mol/pyunits.K),  
                                                              'B': (1.924E-3, pyunits.J/pyunits.mol/pyunits.K**2),
                                                              'C': (1.055E-5, pyunits.J/pyunits.mol/pyunits.K**3),
                                                              'D': (-3.596E-9, pyunits.J/pyunits.mol/pyunits.K**4)
                                                              },
                                     "pressure_sat_comp_coeff": {# Range of temperature 275-Tc K. Reference [1] 3rd Ed. p 669
                                                                 'A': (-7.76451, None),  
                                                                 'B': (1.45838, None),
                                                                 'C': (-2.77580, None),
                                                                 'D': (-1.23303, None)
                                                                },
                                     "enth_mol_form_vap_comp_ref": (-241.81E3, pyunits.J/pyunits.mol),  # Reference [5] - Needed in calculating the ideal gas molar enthalpy
                                     "entr_mol_form_vap_comp_ref": (1.8872E2, pyunits.J/pyunits.mol/pyunits.K),  # Reference [5] - Needed in calculating the ideal gas molar entropy
                  # Parameters for heat capacity, molar enthalpy, molar entropy and molar density for liquid ==> from Perry's handbook
                                     "cp_mol_liq_comp_coeff": {# Range of temperature 273.16-533.15 K. Reference [2] p 2-174
                                                               '1': (2.7637E5, pyunits.J/pyunits.kmol/pyunits.K),
                                                               '2': (-2.0901E3, pyunits.J/pyunits.kmol/pyunits.K**2),
                                                               '3': (8.1250, pyunits.J/pyunits.kmol/pyunits.K**3),
                                                               '4': (-1.4116E-2, pyunits.J/pyunits.kmol/pyunits.K**4),
                                                               '5': (9.3701E-6, pyunits.J/pyunits.kmol/pyunits.K**5)
                                                               },
                                     "dens_mol_liq_comp_coeff": {# Range of temperature 273.16-333.15 K. Reference [2] p 2-98
                                                                 '1': (5.459, pyunits.kmol/pyunits.m**3),
                                                                 '2': (0.30542, None),
                                                                 '3': (647.13, pyunits.K),
                                                                 '4': (0.081, None)
                                                                },
                                     "enth_mol_form_liq_comp_ref": (-2.8583E5, pyunits.J/pyunits.mol),  # Reference [5] - Needed in calculating the ideal liquid molar enthalpy
                                     "entr_mol_form_liq_comp_ref": (70.033, pyunits.J/pyunits.mol/pyunits.K),  # Reference [5] - Needed in calculating the ideal liquid molar entropy
                                    }
                 },
        "ethanol": {# 1.1) Type of chemical specie 
                    "type": Component,
                    # 1.3) Elemental composition
                    "elemental_composition": {"C": 2, "H": 6, "O": 1},
                    # 1.4) Pure component property methods - from IDAES library
                    # Heat capacity, molar enthalpy, molar entropy and saturation pressure for vapor ==> from RPP module
                    #"cp_mol_ig_comp": RPP,
                    "enth_mol_ig_comp": RPP, 
                    "entr_mol_ig_comp": RPP,
                    "pressure_sat_comp": RPP,
                    # Heat capacity, molar enthalpy, molar entropy and molar density for liquid ==> from PERRY module
                    #"cp_mol_liq_comp": Perrys,
                    "enth_mol_liq_comp": Perrys,
                    "entr_mol_liq_comp": Perrys,
                    "dens_mol_liq_comp": Perrys,
                    # 1.5) Phase Equilibrium Formulation
                    "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
                    # 1.6) Parameter Data
                    "parameter_data": {
                    # Molecular weight
                                       "mw": (46.069E-3, pyunits.kg/pyunits.mol),  # Reference [1] p A.7
                    # Critical Pressure
                                       "pressure_crit": (61.48E5, pyunits.Pa),  # Reference [1] p A.7
                    # Critical Temperature
                                       "temperature_crit": (513.92, pyunits.K),  # Reference [1] p A.7
                    # Parameters for heat capacity, molar enthalpy, molar entropy and saturation pressure for vapor ==> from RPP
                                       "cp_mol_ig_comp_coeff": {# Range of temperature ()-() K. Reference [1] 3rd Ed. p 677
                                                                'A': (9.014, pyunits.J/pyunits.mol/pyunits.K),  
                                                                'B': (2.141E-1, pyunits.J/pyunits.mol/pyunits.K**2),
                                                                'C': (-8.390E-5, pyunits.J/pyunits.mol/pyunits.K**3),
                                                                'D': (1.373E-9, pyunits.J/pyunits.mol/pyunits.K**4)
                                                                },
                                       "pressure_sat_comp_coeff": {# Range of temperature 293-Tc K. Reference [1] 3rd Ed. p 678
                                                                'A': (-8.51838, None),  
                                                                'B': (0.34163, None),
                                                                'C': (-5.73683, None),
                                                                'D': (8.32581, None)
                                                                  },
                                       "enth_mol_form_vap_comp_ref": (-234.95E3, pyunits.J/pyunits.mol),  # Reference [5] - Needed in calculating the ideal gas molar enthalpy
                                       "entr_mol_form_vap_comp_ref": (2.8064E2, pyunits.J/pyunits.mol/pyunits.K),  # Reference [5] - Needed in calculating the ideal gas molar entropy
                    # Parameters for heat capacity, molar enthalpy, molar entropy and molar density for liquid ==> from Perry's handbook
                                       "cp_mol_liq_comp_coeff": {# Range of temperature 159.05-390 K. Reference [2] p 2-171
                                                                 '1': (1.0264E+05, pyunits.J/pyunits.kmol/pyunits.K),
                                                                 '2': (-1.3963E+02, pyunits.J/pyunits.kmol/pyunits.K**2),
                                                                 '3': (-3.0341E-02, pyunits.J/pyunits.kmol/pyunits.K**3),
                                                                 '4': (2.0386E-03, pyunits.J/pyunits.kmol/pyunits.K**4),
                                                                 '5': (0, pyunits.J/pyunits.kmol/pyunits.K**5)
                                                                },
                                       "dens_mol_liq_comp_coeff": {# Range of temperature 159.05-513.92 K. Reference [2] p 2-95
                                                                   '1': (1.648, pyunits.kmol/pyunits.m**3),
                                                                   '2': (0.27627, None),
                                                                   '3': (513.92, pyunits.K),
                                                                   '4': (0.2331, None)
                                                                  },
                                       "enth_mol_form_liq_comp_ref": (-2.7698E5, pyunits.J/pyunits.mol),  # Reference [5] - Needed in calculating the ideal liquid molar enthalpy
                                       "entr_mol_form_liq_comp_ref": (1.5986E2, pyunits.J/pyunits.mol/pyunits.K),  # Reference [5] - Needed in calculating the ideal liquid molar entropy
                                      }
                   }
},
    # 2) Specifying phases
    "phases": {
        "Liq": {# 2.1) type of phase
                "type": LiquidPhase,
                # 2.2) Equation of state
                "equation_of_state": Ideal,
                # 2.3) Options for equation of state
                #"equation_of_state_options": {},
                # 2.4) Phase-specific parameters
                #"parameter_data": {},
                # 2.5) Specific component list for that phase
                "component_list": ['water', 'ethanol']
               },
        "Vap": {# 2.1) type of phase
                "type": VaporPhase,
                # 2.2) Equation of state
                "equation_of_state": Ideal,
                # 2.3) Options for equation of state
                #"equation_of_state_options": {},
                # 2.4) Phase-specific parameters
                #"parameter_data": {},
                # 2.5) Specific component list for that phase
                "component_list": ['water', 'ethanol']
               }
},
    # 3) Set base units of measurement
    "base_units": {
                   "time": pyunits.s,
                   "length": pyunits.m,
                   "mass": pyunits.kg,
                   "amount": pyunits.mol,
                   "temperature": pyunits.K
},
    # 4) Specifying the state definition
    # 4.1) State definition
    "state_definition": FTPx,
    # 4.2) State bounds
    "state_bounds": {"flow_mol": (0, 0.5, 100, pyunits.mol/pyunits.s),
                     "temperature": (200, 300, 500, pyunits.K),
                     "pressure": (1e4, 1e5, 1e7, pyunits.Pa)},
    # 4.3) Reference state
    "pressure_ref": (1e5, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K),

    # 5) Defining phase equilibria
    # 5.1) Phase equilibrium
    "phases_in_equilibrium": [("Vap", "Liq")],
    # 5.3) Phase equilibrium state
    "phase_equilibrium_state": {("Vap", "Liq"): smooth_VLE},
    # 5.4) Already defined in component section
    # 5.5) Bubble and dew methods
    "bubble_dew_method": IdealBubbleDew
}