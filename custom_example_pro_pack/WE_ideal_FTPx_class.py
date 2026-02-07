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

Example of custom property package using python classes.
This exmample shows how to set up a new property package to calculate 
phase equilibrium of a mixture of water-ethanol, ideal assumptions is
used for both the liquid and vapor. All methods required are written here.
"""
# Import Pyomo libraries
from pyomo.environ import (Set, Param, Var, Constraint, Expression,
                           value, NonNegativeReals, log, exp, sqrt)
from pyomo.environ import units as pyunits
from pyomo.common.config import ConfigValue, In
from pyomo.opt import SolverFactory, TerminationCondition
from pyomo.util.calc_var_value import calculate_variable_from_constraint
# Import IDAES libraries
from idaes.core import (declare_process_block_class,
                        MaterialFlowBasis,
                        PhysicalParameterBlock,
                        StateBlockData,
                        StateBlock,
                        MaterialBalanceType,
                        EnergyBalanceType)
from idaes.core.util.initialization import (fix_state_vars,
                                            revert_state_vars,
                                            solve_indexed_blocks)
# Import method to define phases and component types
from idaes.core import LiquidPhase, VaporPhase, Component
from idaes.core.util.misc import extract_data
from idaes.core.util.constants import Constants
from idaes.core.util.model_statistics import (degrees_of_freedom,
                                              number_unfixed_variables,
                                              number_activated_constraints, number_variables)
from idaes.core.util.exceptions import ConfigurationError, PropertyPackageError # NOTE: not used
import idaes.core.util.scaling as iscale

import idaes.logger as idaeslog

# Author of this module
__author__ = "Daison Yancy Caballero"

# Set up logger
_log = idaeslog.getLogger(__name__)

# ---------------------------------------------------------------------
# Data Sources:
# [1] The Properties of Gases and Liquids (2000)
#     5th edition, Chemical Engineering Series: Bruce E. Poling - John M. Prausnitz - John P. O’Connell
# [2] Perry's Chemical Engineers' Handbook 7th Ed.
# [3] Engineering Toolbox, https://www.engineeringtoolbox.com
# [4] NIST, https://webbook.nist.gov/chemistry/name-ser/
# [5] DIPPR Database
#     Retrieved 3rd October, 2020
# ---------------------------------------------------------------------

# Physical Parameter Block Definition: defined by the PhysicalParameterBlock class
# Steps to create the NewPhysicalParameterBlock class
# 1) Call the decorator => @declare_process_block_class("NewPhysicalParameterBlock")
@declare_process_block_class("WEParameterBlock")
# 2) Create a NewPhysicalParameterData class which inherits attributes and methods from the PhysicalParameterBlock base class
class WEParameterBlockData(PhysicalParameterBlock):

    # 2.1)  Config arguments for the NewPhysicalParameterBlock
    # 2.1.1) Create a new instance of the CONFIG block of the base class
    CONFIG = PhysicalParameterBlock.CONFIG()
    # 2.1.2) Add custom configuration arguments by using the declare method in the CONFIG block object

    # 2.2) Define the Build method to construct the NewPhysicalParameterBlock
    def build(self):
        '''
        Callable method for Block construction.
        '''
        # 2.2.1) Call python’s super() function to access to the methods in the base class
        super(WEParameterBlockData, self).build()

        # 2.2.2) Reference the StateBlockData by adding a _state_block_class attibute
        self._state_block_class = WEStateBlock

        # 2.2.3) Define the components and phases objects in the system
        # Components
        self.water = Component()
        self.ethanol = Component()
        # Phases
        self.Liq = LiquidPhase()
        self.Vap = VaporPhase()
        # Define a list of components that appear in each phase (optional)
        self.phase_comp = {"Liq": self.component_list,"Vap": self.component_list}
        # List of phase equilibrium index
        self.phase_equilibrium_idx = Set(initialize=[1, 2])
        # Define a list of phases that are in equilibrium for each component
        self.phase_equilibrium_list = {1: ["water", ("Vap", "Liq")],
                                       2: ["ethanol", ("Vap", "Liq")]}

        # 2.2.4) Declare all global parameters used to calculate the properties
        # Molecular weights - Reference [1] p. A.7, A.19
        mw_comp_data = {'water': 18.015E-3, 'ethanol': 46.069E-3}
        self.mw_comp = Param(self.component_list,
                             mutable=False,
                             initialize=extract_data(mw_comp_data),
                             units=pyunits.kg/pyunits.mol,
                             doc="Molecular weight [kg/mol]")
        # Thermodynamic reference state
        self.pressure_ref = Param(mutable=True,
                                  default=101325,
                                  units=pyunits.Pa,
                                  doc='Reference pressure [Pa]')
        self.temperature_ref = Param(mutable=True,
                                     default=298.15,
                                     units=pyunits.K,
                                     doc='Reference temperature [K]')
        # Gas Constant
        self.gas_const = Constants.gas_constant
        # Critical parameters - Reference [1] p. A.7, A.19
        # critical pressure
        pressure_crit_data = {'water': 220.64e5, 'ethanol': 61.48E5}
        self.pressure_crit = Param(self.component_list,
                                   mutable=False,
                                   initialize=extract_data(pressure_crit_data),
                                   units=pyunits.Pa,
                                   doc='Critical pressure [Pa]')
        # critical temperature
        temperature_crit_data = {'water': 647.14, 'ethanol': 513.92}
        self.temperature_crit = Param(self.component_list,
                                      mutable=False,
                                      initialize=extract_data(temperature_crit_data),
                                      units=pyunits.K,
                                      doc='Critical temperature [K]')
        # Parameters for iedal specific heat capacities, molar enthalpies, and  molar 
        # entropies for vapor phase - Reference [1] 3rd edition p. 668, 677
        self.cp_mol_ig_comp_coeff_A = Param(self.component_list,
                                            initialize={'water': 3.224E1,'ethanol': 9.014},
                                            units=pyunits.J/pyunits.mol/pyunits.K,
                                            doc="Parameter A for ideal gas molar heat capacity [J/mol.K]")
        self.cp_mol_ig_comp_coeff_B = Param(self.component_list,
                                            initialize={'water': 1.924E-3,'ethanol': 2.141E-1},
                                            units=pyunits.J/pyunits.mol/pyunits.K**2,
                                            doc="Parameter B for ideal gas molar heat capacity [J/mol.K]")
        self.cp_mol_ig_comp_coeff_C = Param(self.component_list,
                                            initialize={'water': 1.055E-5,'ethanol': -8.390E-5},
                                            units=pyunits.J/pyunits.mol/pyunits.K**3,
                                            doc="Parameter C for ideal gas molar heat capacity [J/mol.K]")
        self.cp_mol_ig_comp_coeff_D = Param(self.component_list,
                                            initialize={'water': -3.596E-9,'ethanol': 1.373E-9},
                                            units=pyunits.J/pyunits.mol/pyunits.K**4,
                                            doc="Parameter D for ideal gas molar heat capacity [J/mol.K]")
        # Standard molar heat of formation for vapor at reference state - Reference [5]
        dh_form_vap_data = {'water': -241.81E3, 'ethanol': -234.95E3}
        self.enth_mol_form_vap_comp_ref = Param(self.component_list,
                                                mutable=False,
                                                initialize=extract_data(dh_form_vap_data),
                                                units=pyunits.J/pyunits.mol,
                                                doc="Standard heat of formation for vapor [J/mol]")
        # Standard molar entropy of formation for vapor at reference state - Reference [5]
        ds_form_vap_data = {'water': 1.8872E2, 'ethanol': 2.8064E2}
        self.entr_mol_form_vap_comp_ref = Param(self.component_list,
                                                mutable=False,
                                                initialize=extract_data(ds_form_vap_data),
                                                units=pyunits.J/pyunits.mol/pyunits.K,
                                                doc="Standard entropy of formation for vapor [J/mol.K]")
        # Parameters for saturation pressures - Reference [1] 3rd edition p. 669, 678
        self.pressure_sat_comp_coeff_A = Param(self.component_list,
                                               mutable=False,
                                               initialize={'water': -7.76451,'ethanol': -8.51838},
                                               units=None,
                                               doc="Parameter A for saturation pressure")
        self.pressure_sat_comp_coeff_B = Param(self.component_list,
                                               mutable=False,
                                               initialize={'water': 1.45838,'ethanol': 0.34163},
                                               units=None,
                                               doc="Parameter B for saturation pressure")
        self.pressure_sat_comp_coeff_C = Param(self.component_list,
                                               mutable=False,
                                               initialize={'water': -2.77580,'ethanol': -5.73683},
                                               units=None,
                                               doc="Parameter C for saturation pressure")
        self.pressure_sat_comp_coeff_D = Param(self.component_list,
                                               mutable=False,
                                               initialize={'water': -1.23303,'ethanol': 8.32581},
                                               units=None,
                                               doc="Parameter D for saturation pressure")
        # Parameters for molar heat capacities, molar enthalpies, and  molar entropies for 
        # liquid phase - Reference [2] p. 2-171, 2-174
        self.cp_mol_liq_comp_coeff_1 = Param(self.component_list,
                                             initialize={'water': 2.7637E5,'ethanol': 1.0264E+05},
                                             units=pyunits.J*pyunits.kmol**-1*pyunits.K**-1,
                                             doc="Parameter 1 for liquid phase molar heat capacity [J/kmol.K]")
        self.cp_mol_liq_comp_coeff_2 = Param(self.component_list,
                                             initialize={'water': -2.0901E3,'ethanol': -1.3963E+02},
                                             units=pyunits.J*pyunits.kmol**-1*pyunits.K**-2,
                                             doc="Parameter 2 for liquid phase molar heat capacity [J/kmol.K^2]")
        self.cp_mol_liq_comp_coeff_3 = Param(self.component_list,
                                             initialize={'water': 8.1250,'ethanol': -3.0341E-02},
                                             units=pyunits.J*pyunits.kmol**-1*pyunits.K**-3,
                                             doc="Parameter 3 for liquid phase molar heat capacity [J/kmol.K^3]")
        self.cp_mol_liq_comp_coeff_4 = Param(self.component_list,
                                             initialize={'water': -1.4116E-2,'ethanol': 2.0386E-03},
                                             units=pyunits.J*pyunits.kmol**-1*pyunits.K**-4,
                                             doc="Parameter 4 for liquid phase molar heat capacity [J/kmol.K^4]")
        self.cp_mol_liq_comp_coeff_5 = Param(self.component_list,
                                             initialize={'water': 9.3701E-6,'ethanol': 0},
                                             units=pyunits.J*pyunits.kmol**-1*pyunits.K**-5,
                                             doc="Parameter 5 for liquid phase molar heat capacity [J/kmol.K^5]")
        # Standard molar heat of formation for liquid at reference state - Reference [5]
        dh_form_liq_data = {'water': -2.8583E8, 'ethanol': -2.7698E8}
        self.enth_mol_form_liq_comp_ref = Param(self.component_list,
                                                mutable=False,
                                                initialize=extract_data(dh_form_liq_data),
                                                units=pyunits.J/pyunits.kmol,
                                                doc="Standard heat of formation for liquid [J/kmol]")
        # Standard molar entropy of formation for liquid at reference state - Reference [5]
        ds_form_liq_data = {'water': 70.033E3, 'ethanol': 1.5986E5}
        self.entr_mol_form_liq_comp_ref = Param(self.component_list,
                                                mutable=False,
                                                initialize=extract_data(ds_form_liq_data),
                                                units=pyunits.J/pyunits.kmol/pyunits.K,
                                                doc="Standard entropy of formation for liquid [J/kmol.K]")
        # Parameter for liquid molar density - Reference [2] p. 2-95, 2-98
        self.dens_mol_liq_comp_coeff_1 = Param(self.component_list,
                                               initialize={'water': 5.459,'ethanol': 1.648},
                                               units=pyunits.kmol*pyunits.m**-3,
                                               doc="Parameter 1 for liquid molar density [kmol/m^3]")
        self.dens_mol_liq_comp_coeff_2 = Param(self.component_list,
                                               initialize={'water': 0.30542,'ethanol': 0.27627},
                                               units=None,
                                               doc="Parameter 2 for liquid molar density [-]")
        self.dens_mol_liq_comp_coeff_3 = Param(self.component_list,
                                               initialize={'water': 647.13,'ethanol': 513.92},
                                               units=pyunits.K,
                                               doc="Parameter 3 for liquid molar density [K]")
        self.dens_mol_liq_comp_coeff_4 = Param(self.component_list,
                                               initialize={'water': 0.081,'ethanol': 0.2331},
                                               units=None,
                                               doc="Parameter 4 for liquid molar density [-]")   

    # 2.3) Define the metadata class method
    # 2.3.1) Call the classmethod decorator and declare the function "define_metadata"
    @classmethod
    def define_metadata(cls, obj):
        """Define properties supported and units."""
        # 2.3.2) Set up build on demand properties and properties that are always contructed
        # NOTE: units seems that are not required here
        obj.add_properties(
            {'flow_mol': {'method': None},
             'flow_mol_phase': {'method': None},
             'flow_mol_phase_comp': {'method': None},
             'flow_mol_comp': {'method': None},
             'mole_frac_comp': {'method': None},
             'mole_frac_phase_comp': {'method': None},
             'phase_frac': {'method': None},
             'temperature': {'method': None},
             'pressure': {'method': None},
             'dens_mass': {'method': '_dens_mass'},
             'dens_mass_phase': {'method': '_dens_mass_phase'},
             'dens_mol': {'method': '_dens_mol'},
             'dens_mol_phase': {'method': '_dens_mol_phase'},
             'enth_mol': {'method': '_enth_mol'},
             'enth_mol_phase': {'method': '_enth_mol_phase'},
             'enth_mol_phase_comp': {'method': '_enth_mol_phase_comp'},
             'entr_mol': {'method': '_entr_mol'},
             'entr_mol_phase': {'method': '_entr_mol_phase'},
             'entr_mol_phase_comp': {'method': '_entr_mol_phase_comp'},
             'fug_phase_comp': {'method': '_fug_phase_comp'},
             'gibbs_mol': {'method': '_gibbs_mol'},
             'gibbs_mol_phase': {'method': '_gibbs_mol_phase'},
             'gibbs_mol_phase_comp': {'method': '_gibbs_mol_phase_comp'},
             'mw': {'method': '_mw'},
             'mw_phase': {'method': '_mw_phase'},
             'pressure_sat': {'method': '_pressure_sat'},
             'temperature_bubble': {'method': '_temperature_bubble'},
             'temperature_dew': {'method': '_temperature_dew'},
             'pressure_bubble': {'method': '_pressure_bubble'},
             'pressure_dew': {'method': '_pressure_dew'}
             })
        # 2.3.3) Add units of measurements for base quantities
        obj.add_default_units({'time': pyunits.s,
                               'length': pyunits.m,
                               'mass': pyunits.kg,
                               'amount': pyunits.mol,
                               'temperature': pyunits.K
                               })

class _WEStateBlock(StateBlock):
    """
    This Class contains methods which should be applied to Property Blocks as a
    whole, rather than individual elements of indexed Property Blocks.
    """
    def initialize(blk, state_args={}, state_vars_fixed=False,
                   hold_state=False, outlvl=idaeslog.NOTSET,
                   solver='ipopt', optarg={'tol': 1e-8}):
        """
        Initialization routine for property package.
        Keyword Arguments:
            state_args : Dictionary with initial guesses for the state vars
                         defined by the property package. Note that if this 
						 method is triggered through the control volume, and 
						 if initial guesses were not provied at the unit model 
						 level, the control volume passes the inlet values as 
						 initial guess.
            outlvl : sets output level of initialization routine
                     * 0 = no output (default)
                     * 1 = return solver state for each step in routine
                     * 2 = include solver output infomation (tee=True)
            optarg : solver options dictionary object (default=None)
            state_vars_fixed: Flag to denote if state vars have already been
                              fixed.
                              - True - states have already been fixed by the
                                       control volume 1D. Control volume 0D
                                       does not fix the state vars, so will
                                       be False if this state block is used
                                       with 0D blocks.
                             - False - states have not been fixed. The state
                                       block will deal with fixing/unfixing.
            solver : str indicating which solver to use during
                     initialization (default = 'ipopt')
            hold_state : flag indicating whether the initialization routine
                         should unfix any state variables fixed during
                         initialization (default=False).
                         - True - states variables are not unfixed, and
                                 a dict of returned containing flags for
                                 which states were fixed during
                                 initialization.
                        - False - state variables are unfixed after
                                 initialization by calling the
                                 relase_state method
        Returns:
            If hold_states is True, returns a dict containing flags for
            which states were fixed during initialization.
        """

        init_log = idaeslog.getInitLogger(blk.name, outlvl, tag="properties")
        solve_log = idaeslog.getSolveLogger(blk.name, outlvl, tag="properties")

        init_log.info('Starting initialization')

        # Fix state variables if not already fixed
        if state_vars_fixed is False:
            flags = fix_state_vars(blk, state_args)
            # # Confirm DoF for sanity
            # for k in blk.keys():
            #     if degrees_of_freedom(blk[k]) != 0:
            #         raise Exception("Degrees of freedom were not zero [{}] "
            #                         "after atate vars were fixed during initialization"
            #                         "Please inform the IDAES developers.".format(degrees_of_freedom(blk[k])))
        else:
            # Check when the state vars are fixed already result in dof 0
            for k in blk.keys():
                if degrees_of_freedom(blk[k]) != 0:
                    raise Exception("Degrees of freedom were not zero [{}] "
                                    "after atate vars were fixed during initialization"
                                    "Please inform the IDAES developers.".format(degrees_of_freedom(blk[k])))
                                    
        # for k in blk.keys():  # need to remove this, as is to print variables for the moment 
        #     for v in blk[k].component_objects(Var, active=True):
        #         print("Variable", v)
        #         for index in v:
        #             print ("",index, value(v[index]))

        # Set solver options
        if optarg is None:
            sopt = {'tol': 1e-8}
        else:
            sopt = optarg

        opt = SolverFactory('ipopt')
        opt.options = sopt

        # ---------------------------------------------------------------------
        # if present, initialize bubble and dew point calculations
        # for k in blk.keys():
        #     # Bubble temperature initialization
        #     if hasattr(blk[k], "_mole_frac_tbub"):
        #        # Use lowest component temperature_crit as starting point
        #        # Starting high and moving down generally works better,
        #        # as it under-predicts next step due to exponential form of
        #        # Psat.
        #        # Subtract 1 to avoid potential singularities at Tcrit
        #        Tbub0 = min(blk[k].params.temperature_crit[j].value
        #                    for j in blk[k].params.component_list) - 1
        #        err = 1
        #        counter = 0

        #        # Newton solver with step limiter to prevent overshoot
        #        # Tolerance only needs to be ~1e-1
        #        # Iteration limit of 30
        #        while err > 1e-1 and counter < 30:
        #              f = value(sum(blk[k].pressure_saturation(j, Tbub0) * \
        #                            blk[k].mole_frac_comp[j] \
        #                            for j in blk[k].params.component_list) - blk[k].pressure)

        #              df = value(sum(blk[k].der_pressure_saturation(j, Tbub0) * \
        #                             blk[k].mole_frac_comp[j] for j in blk[k].params.component_list))

        #              # Limit temperature step to avoid excessive overshoot
        #              if f/df < -50:
        #                 Tbub1 = Tbub0 + 50
        #              elif f/df > 50:
        #                   Tbub1 = Tbub0 - 50
        #              else:
        #                   Tbub1 = Tbub0 - f/df
 
        #              err = abs(Tbub1 - Tbub0)
        #              counter += 1
        #              Tbub0 = Tbub1

        #        blk[k].temperature_bubble.value = Tbub0
               
        #        for j in blk[k].params.component_list:
        #            blk[k]._mole_frac_tbub[j].value = value(
        #                    blk[k].mole_frac_comp[j] *
        #                    blk[k].pressure_saturation(j, Tbub0) /
        #                    blk[k].pressure)

        #     # Dew temperature initialization
        #     if hasattr(blk[k], "_mole_frac_tdew"):

        #        if hasattr(blk[k], "_mole_frac_tbub"):
        #           # If Tbub has been calculated above, use this as the starting point
        #           Tdew0 = blk[k].temperature_bubble.value
        #        else:
        #            # Otherwise, use lowest component critical temperature as starting point
        #            # Subtract 1 to avoid potential singularities at Tcrit
        #           Tdew0 = min(blk[k].params.temperature_crit[j].value 
        #                       for j in blk[k].params.component_list) - 1
        #        err = 1
        #        counter = 0

        #        # Newton solver with step limiter to prevent overshoot
        #        # Tolerance only needs to be ~1e-1
        #        # Iteration limit of 30
        #        while err > 1e-1 and counter < 30:
        #            f = value(blk[k].pressure * sum(blk[k].mole_frac_comp[j] / \
        #                      blk[k].pressure_saturation(j, Tdew0) \
        #                      for j in blk[k].params.component_list) - 1)

        #            df = -value(blk[k].pressure * sum(blk[k].mole_frac_comp[j] / \
        #                       blk[k].pressure_saturation(j, Tdew0)**2 *
        #                        blk[k].der_pressure_saturation(j, Tdew0)
        #                        for j in blk[k].params.component_list))

        #            # Limit temperature step to avoid excessive overshoot
        #            if f/df < -50:
        #                Tdew1 = Tdew0 + 50
        #            elif f/df > 50:
        #                Tdew1 = Tdew0 - 50
        #            else:
        #                Tdew1 = Tdew0 - f/df

        #            err = abs(Tdew1 - Tdew0)
        #            Tdew0 = Tdew1
        #            counter += 1

        #        blk[k].temperature_dew.value = Tdew0

        #        for j in blk[k].params.component_list:
        #            blk[k]._mole_frac_tdew[j].value = value(
        #                    blk[k].mole_frac_comp[j]*blk[k].pressure /
        #                    blk[k].pressure_saturation(j, Tdew0))

        #     # Bubble pressure initialization
        #     if hasattr(blk[k], "_mole_frac_pbub"):

        #             blk[k].pressure_bubble.value = value(sum(blk[k].mole_frac_comp[j] * \
        #                                                      blk[k].pressure_saturation(j, blk[k].temperature) \
        #                                                      for j in blk[k].params.component_list))

        #             for j in blk[k].params.component_list:
        #                 blk[k]._mole_frac_pbub[j].value = value(blk[k].mole_frac_comp[j] * \
        #                                                         blk[k].pressure_saturation(j, blk[k].temperature) / \
        #                                                         blk[k].pressure_bubble)

        #     # Dew pressure initialization
        #     if hasattr(blk[k], "_mole_frac_pdew"):

        #             blk[k].pressure_dew.value = value(sum(1/(blk[k].mole_frac_comp[j] / \
        #                                               blk[k].pressure_saturation(j, blk[k].temperature)) \
        #                                               for j in blk[k].params.component_list))

        #             for j in blk[k].params.component_list:
        #                 blk[k]._mole_frac_pdew[j].value = value(blk[k].mole_frac_comp[j]*blk[k].pressure_bubble / \
        #                                                         blk[k].pressure_saturation(j, blk[k].temperature))

        #     # Solve bubble and dew point constraints
        #     for c in blk[k].component_objects(Constraint):
        #         # Deactivate all constraints not associated wtih bubble and dew
        #         # points
        #         if c.local_name not in ("eq_pressure_dew",
        #                                 "eq_pressure_bubble",
        #                                 "eq_temperature_dew",
        #                                 "eq_temperature_bubble",
        #                                 "eq_mole_frac_tbub",
        #                                 "eq_mole_frac_tdew",
        #                                 "eq_mole_frac_pbub",
        #                                 "eq_mole_frac_pdew",
        #                                 "mole_frac_comp_eq"):
        #             c.deactivate()

        # # If StateBlock has active constraints (i.e. has bubble and/or dew
        # # point calculations), solve the block to converge these
        # n_cons = 0
        # for k in blk:
        #     n_cons += number_activated_constraints(blk[k])
        # if n_cons > 0:
        #     with idaeslog.solver_log(solve_log, idaeslog.DEBUG) as slc:
        #         res = solve_indexed_blocks(opt, [blk], tee=slc.tee)
        #     init_log.info("Dew and bubble point initialization: {}."
        #                   .format(idaeslog.condition(res)))

        # ---------------------------------------------------------------------
        # If present, initialize bubble and dew point calculations
        for k in blk.keys():
            if hasattr(blk[k], "eq_temperature_bubble"):
                calculate_variable_from_constraint(blk[k].temperature_bubble,
                                                   blk[k].eq_temperature_bubble)

            if hasattr(blk[k], "eq_mole_frac_tbub"):
               for j in blk[k].params.component_list:
                   calculate_variable_from_constraint(blk[k]._mole_frac_tbub[j],
                                                      blk[k].eq_mole_frac_tbub[j])

            if hasattr(blk[k], "eq_temperature_dew"):
                calculate_variable_from_constraint(blk[k].temperature_dew,
                                                   blk[k].eq_temperature_dew)

            if hasattr(blk[k], "eq_mole_frac_tdew"):
               for j in blk[k].params.component_list:
                   calculate_variable_from_constraint(blk[k]._mole_frac_tdew[j],
                                                      blk[k].eq_mole_frac_tdew[j])

            if hasattr(blk[k], "eq_pressure_bubble"):
                calculate_variable_from_constraint(blk[k].pressure_bubble,
                                                   blk[k].eq_pressure_bubble)

            if hasattr(blk[k], "eq_pressure_dew"):
                calculate_variable_from_constraint(blk[k].pressure_dew,
                                                   blk[k].eq_pressure_dew)

        init_log.info_high("Initialization Step 1 - Dew and bubble points "
                           "calculation completed.")

        # ---------------------------------------------------------------------
        # If flash, initialize T1 and Teq
        for k in blk.keys():
            blk[k]._t1.value = max(blk[k].temperature.value,
                                    blk[k].temperature_bubble.value)
            blk[k]._teq.value = min(blk[k]._t1.value,
                                    blk[k].temperature_dew.value)

        init_log.info_high("Initialization Step 2 - Equilibrium temperature "
                           "calculation completed.")

        # ---------------------------------------------------------------------
        # for c in blk[k].component_objects(Constraint):
            
        #     c.activate()
            
        #     # if c.local_name in ("total_flow_balance",
        #     #                     "component_flow_balances",
        #     #                     "sum_mole_frac",
        #     #                     "phase_fraction_constraint",
        #     #                     "_t1_constraint",
        #     #                     "_teq",
        #     #                     "equilibrium_constraint"):
        #     #    c.activate()

        # # Initialize flow rates and compositions
        # for k in blk.keys():
        #     # Deactivate the constraints specific for outlet block i.e.
        #     # when defined state is False
        #     if blk[k].config.defined_state is False:
        #         try:
        #             blk[k].sum_mole_frac_out.deactivate()
        #         except AttributeError:
        #             pass

        # Initialize flow rates and compositions # NOTE: state vars already fixed
        for k in blk.keys():
            if (isinstance(blk[k].temperature, Var) and not blk[k].temperature.fixed):
                blk[k].temperature.value = value(blk[k]._teq)
            print(blk[k].temperature.value)

        # for k in blk.keys():
        #     # Deactivate equilibrium constraints, as state is fixed
        #     if hasattr(blk[k], 'enth_mol_phase'):
        #         blk[k].eq_enth_mol_phase.deactivate()
        #     if hasattr(blk[k], 'enth_mol_phase_comp'):
        #         blk[k].eq_enth_mol_phase_comp.deactivate()

        free_vars = 0
        for k in blk.keys():
            free_vars += number_unfixed_variables(blk[k])
            print(degrees_of_freedom(blk[k]))
        if free_vars > 0:
            res = solve_indexed_blocks(opt, [blk], tee=True)
            # try:
            #     with idaeslog.solver_log(solve_log, idaeslog.DEBUG) as slc:
            #         res = solve_indexed_blocks(opt, [blk], tee=slc.tee)
            # except:
            #     res = None
        else:
            res = None

        # print all variables
        for k in blk.keys():
            for v in blk[k].component_objects(Var, active=True):
                print("Variable", v)
                for index in v:
                    print ("",index, value(v[index]))
            print(number_variables(blk[k]))
            print(number_activated_constraints(blk[k]))

        # print all Constraint
        for k in blk.keys():
            for v in blk[k].component_objects(Constraint, active=True):
                print("Constraint", v)
                for index in v:
                    print ("",index, value(v[index]))

        # ---------------------------------------------------------------------
        # Return state to initial conditions
        if state_vars_fixed is False:
            if hold_state is True:
                return flags
            else:
                blk.release_state(flags)

        init_log.info("Initialization Complete")

    def release_state(blk, flags, outlvl=0):
        '''
        Method to relase state variables fixed during initialization.
        Keyword Arguments:
            flags : dict containing information of which state variables
                    were fixed during initialization, and should now be
                    unfixed. This dict is returned by initialize if
                    hold_state=True.
            outlvl : sets output level of of logging
        '''
        init_log = idaeslog.getInitLogger(blk.name, outlvl, tag="properties")
        if flags is None:
            init_log.debug("No flags passed to release_state().")
            return

        # Unfix state variables
        revert_state_vars(blk, flags)

        init_log.info_high("State Released.")


# Declare the NewStateBlockData class: used to contruct the NewStateBlock
# 1) Call the decorator => @declare_process_block_class
@declare_process_block_class("WEStateBlock", block_class=_WEStateBlock)
# 2) Create a NewStateBlockData Class by inheriting behavior from the StateBlockData base class
class WEStateBlockData(StateBlockData):
    """An example property package for ideal VLE."""

    # 2.1) Config arguments for the NewStateBlock

    # 2.2) Define the Build method to construct the NewStateBlockData
    def build(self):
        """Callable method for Block construction."""
        # 2.2.1) Call python’s super() function to access to the methods in the base class
        super(WEStateBlockData, self).build()

        # 2.2.2) Define variables, expressions and constrainsts that make up the property package
        units = self.params.get_metadata().derived_units
        # State definition
        self.state_definition(units)
        # Add supporting variables and constraints for the state definition
        self.supporting_vars_cons_state(units)

        # 2.2.4) Phase equilibrium calculation. First chek that config argument "has_phase_equilibrium" is true and "defined_state" is false 
        # equilibrium constraints can never be written for cases where the state is fully defined when config argument "defined_state" is true
        if self.config.has_phase_equilibrium:
            # Definition of equilibrium temperature for smooth VLE
            self._teq = Var(initialize=298,
                            doc='Temperature for calculating phase equilibrium [K]')
            self._t1 = Var(initialize=298,
                           doc='Intermediate temperature for calculating Teq [K]')
            self.eps_1 = Param(default=0.01,
                               mutable=True,
                               doc='Smoothing parameter for Teq')
            self.eps_2 = Param(default=0.0005,
                               mutable=True,
                               doc='Smoothing parameter for Teq')

            # PSE paper Eqn 13
            def rule_t1(b):
                return b._t1 == 0.5*(
                       b.temperature + b.temperature_bubble +
                       sqrt((b.temperature-b.temperature_bubble)**2 +
                             b.eps_1**2))
            self._t1_constraint = Constraint(rule=rule_t1)

            # PSE paper Eqn 14
            # TODO : Add option for supercritical extension
            def rule_teq(b):
                return b._teq == 0.5*(b._t1 + b.temperature_dew -
                                      sqrt((b._t1-b.temperature_dew)**2 +
                                            b.eps_2**2))
            self._teq_constraint = Constraint(rule=rule_teq)

            def rule_tr_eq(b, j):
                return b._teq / b.params.temperature_crit[j]
            self._tr_eq = Expression(self.params.component_list,
                                     rule=rule_tr_eq,
                                     doc='Component reduced temperatures [-]')

            def rule_equilibrium(b, j):
                return b.fug_phase_comp['Vap', j] == b.fug_phase_comp['Liq', j]
            self.equilibrium_constraint = Constraint(self.params.component_list, 
                                                     rule=rule_equilibrium)

        # Call other methods and expressions
        # self._mw_phase()
        # self._mw()
        # self._dens_mol_phase()
        # self._dens_mol()
        # self._dens_mass_phase()
        # self._dens_mass()
        # self._enth_mol()
        # self._entr_mol_phase_comp()
        # self._entr_mol_phase()
        # self._entr_mol()
        # self._gibbs_mol_phase_comp()
        # self._gibbs_mol_phase()
        # self._gibbs_mol()
        # self._pressure_bubble()
        # self._pressure_dew()

    # -----------------------------------------------------------------------------
    # Definition of methods 
    # -----------------------------------------------------------------------------
    
    # Auxiliary methods for state definition

    def state_definition(self, units):
        self.flow_mol = Var(initialize=1.0,
                            domain=NonNegativeReals,
                            bounds=(0, 100),
                            units=units["flow_mole"],
                            doc='Total molar flowrate')
        self.mole_frac_comp = Var(self.params.component_list,
                                  initialize=1/len(self.params.component_list),
                                  bounds=(0, None),
                                  units=None,
                                  doc='Mixture mole fractions')
        self.pressure = Var(initialize=1e5,
                            domain=NonNegativeReals,
                            bounds=(1e4, 1e7),
                            units=units["pressure"],
                            doc='State pressure')
        self.temperature = Var(initialize=298.15,
                               domain=NonNegativeReals,
                               bounds=(200, 500),
                               units=units["temperature"],
                               doc='State temperature')

    def supporting_vars_cons_state(self, units):
        # supporting variables
        self.flow_mol_phase = Var(self.params.phase_list,
                                  initialize=0.5,
                                  domain=NonNegativeReals,
                                  bounds=(0, 100),
                                  units=units["flow_mole"],
                                  doc='Phase molar flow rates')
        self.mole_frac_phase_comp = Var(self.params._phase_component_set,
                                        initialize=1/len(self.params.component_list),
                                        bounds=(0, None),
                                        units=None,
                                        doc='Phase mole fractions')
        self.phase_frac = Var(self.params.phase_list,
                              initialize=1/len(self.params.phase_list),
                              bounds=(0, None),
                              units=None,
                              doc='Phase fractions')
        # supporting constraints
        # Add supporting constraints
        if self.config.defined_state is False:
             # applied at outlet only. The sum of mole fractions constraint is 
             # not written at inlet states, as all mole fractions should be 
             # defined in the inlet stream
             self.sum_mole_frac_out = Constraint(expr= 1e3 == 1e3*sum(self.mole_frac_comp[i]
                                                 for i in self.params.component_list))

        if len(self.params.phase_list) == 1:
           # only one phase
           def rule_total_mass_balance(b):
               return b.flow_mol_phase[b.params.phase_list[1]] == b.flow_mol
           self.total_flow_balance = Constraint(rule=rule_total_mass_balance)

           def rule_comp_mass_balance(b, i):
               return 1e3*b.mole_frac_comp[i] == \
                      1e3*b.mole_frac_phase_comp[b.params.phase_list[1], i]
           self.component_flow_balances = Constraint(self.params.component_list, 
                                                     rule=rule_comp_mass_balance)
           def rule_phase_frac(b, p):
               return self.phase_frac[p] == 1
           self.phase_fraction_constraint = Constraint(self.params.phase_list, 
                                                       rule=rule_phase_frac)

        elif len(self.params.phase_list) == 2:
             # two phase, use Rachford-Rice formulation
             def rule_total_mass_balance(b):
                 return sum(b.flow_mol_phase[p] for p in b.params.phase_list) == \
                        b.flow_mol
             self.total_flow_balance = Constraint(rule=rule_total_mass_balance)

             def rule_comp_mass_balance(b, i):
                 return b.flow_mol*b.mole_frac_comp[i] == sum(
                        b.flow_mol_phase[p]*b.mole_frac_phase_comp[p, i]
                        for p in b.params.phase_list
                        if (p, i) in b.params._phase_component_set)
             self.component_flow_balances = Constraint(self.params.component_list,
                                                     rule=rule_comp_mass_balance)
             
             def rule_mole_frac(b):
                 return 1e3*sum(b.mole_frac_phase_comp[b.params.phase_list[1], i]
                                for i in b.params.component_list
                                if (b.params.phase_list[1], i)
                                in b.params._phase_component_set) -\
                        1e3*sum(b.mole_frac_phase_comp[b.params.phase_list[2], i]
                                for i in b.params.component_list
                                if (b.params.phase_list[2], i)
                                in b.params._phase_component_set) == 0
             self.sum_mole_frac = Constraint(rule=rule_mole_frac)
   
             def rule_phase_frac(b, p):
                 return b.phase_frac[p]*b.flow_mol == b.flow_mol_phase[p]
             self.phase_fraction_constraint = Constraint(self.params.phase_list,
                                                         rule=rule_phase_frac)

    # -----------------------------------------------------------------------------
    # General Methods: these methods are requied as they are used in the 
    # framework for determining the formulation of the higher level models

    def get_material_flow_basis(self):
        return MaterialFlowBasis.molar

    def get_material_flow_terms(self, p, j):
        """Create material flow terms for control volume."""
        if j in self.params.component_list:
            return self.flow_mol_phase[p] * self.mole_frac_phase_comp[p, j]
        else:
            return 0

    def get_enthalpy_flow_terms(self, p):
        """Create enthalpy flow terms."""
        return self.flow_mol_phase[p] * self.enth_mol_phase[p]

    def get_material_density_terms(self, p, j):
        """Create material density terms."""
        if j in self.params.component_list:
            return self.dens_mol_phase[p] * self.mole_frac_phase_comp[p, j]
        else:
            return 0

    def get_energy_density_terms(self, p):
        """Create energy density terms."""
        return self.dens_mol_phase[p] * self.enth_mol_phase[p]

    def default_material_balance_type(self):
        return MaterialBalanceType.componentTotal

    def default_energy_balance_type(self):
        return EnergyBalanceType.enthalpyTotal

    def define_state_vars(self):
        """Define state vars."""
        return {"flow_mol": self.flow_mol,
                "mole_frac_comp": self.mole_frac_comp,
                "temperature": self.temperature,
                "pressure": self.pressure}

    def define_display_vars(self):
        """Define display vars."""
        return {"Total Molar Flowrate": self.flow_mol,
                "Total Mole Fraction": self.mole_frac_comp,
                "Temperature": self.temperature,
                "Pressure": self.pressure,
                "Flow_mol_phase": self.flow_mol_phase}

    # -----------------------------------------------------------------------------
    # Check methdod to verify that the pressure and temperature are whithin bounds
    def model_check(blk):
        """Model checks for property block."""
        
        # Check temperature bounds
        if value(blk.temperature) < blk.temperature.lb:
            _log.error('{} Temperature set below lower bound.'.format(blk.name))
        if value(blk.temperature) > blk.temperature.ub:
            _log.error('{} Temperature set above upper bound.'.format(blk.name))

        # Check pressure bounds
        if value(blk.pressure) < blk.pressure.lb:
            _log.error('{} Pressure set below lower bound.'.format(blk.name))
        if value(blk.pressure) > blk.pressure.ub:
            _log.error('{} Pressure set above upper bound.'.format(blk.name))

    # -----------------------------------------------------------------------------
    # Property Methods

    def _mw_phase(self):
        def rule_mw_phase(b, p):
            return sum(b.mole_frac_phase_comp[p, j]*b.params.mw_comp[j]
                       for j in b.params.component_list)
        self.mw_phase = Expression(self.params.phase_list,
                                   rule=rule_mw_phase)

    def _mw(self):
        def rule_mw(b):
            return sum(b.mw_phase[p] for p in b.params.phase_list)
        self.mw = Expression(rule=rule_mw)

    def _dens_mol_phase(self): # Initialize this var
        self.dens_mol_phase = Var(self.params.phase_list,
                                  units=pyunits.mol/pyunits.m**3,
                                  doc="Molar density [mol/m^3]")

        def rule_dens_mol_phase(b, p):
            if p == 'Vap':
                return b._dens_mol_vap()
            else:
                return b._dens_mol_liq()
        self.eq_dens_mol_phase = Constraint(self.params.phase_list,
                                            rule=rule_dens_mol_phase)

    def _dens_mol(self):
        def rule_dens_mol(b):
            return sum(b.dens_mol_phase[p]*b.phase_frac[p]
                       for p in b.params.phase_list)
        self.dens_mol = Expression(rule=rule_dens_mol,
                                   doc="Mixture molar density")

    def _dens_mass_phase(self): # Initialize this var
        self.dens_mass_phase = Var(self.params.phase_list,
                                   units=pyunits.kg/pyunits.m**3,
                                   doc="Mass density [kg/m^3]")

        def rule_dens_mass_phase(b, p):
            return b.dens_mass_phase[p] == b.dens_mol_phase[p]*b.mw_phase[p]
        self.eq_dens_mass_phase = Constraint(self.params.phase_list,
                                             rule=rule_dens_mass_phase)

    def _dens_mass(self):
        def rule_dens_mass(b):
            return sum(b.dens_mass_phase[p]*b.phase_frac[p]
                       for p in b.params.phase_list)
        self.dens_mass = Expression(rule=rule_dens_mass,
                                    doc="Mixture mass density")

    def _enth_mol_phase_comp(self):

        self.enth_mol_phase_comp = Var(self.params.phase_list,
                                       self.params.component_list,
                                       initialize=7e5,
                                       doc='Phase-component molar specific enthalpies [J/mol]')

        def rule_enth_mol_phase_comp(b, p, j):
            if p == 'Vap':
                return b._enth_mol_comp_vap(j)
            else:
                return b._enth_mol_comp_liq(j)

        self.eq_enth_mol_phase_comp = Constraint(self.params.phase_list,
                                                 self.params.component_list,
                                                 rule=rule_enth_mol_phase_comp)

    def _enth_mol_phase(self):

        self.enth_mol_phase = Var(self.params.phase_list,
                                  initialize=7e5,
                                  doc='Phase molar specific enthalpies [J/mol]')

        def rule_enth_mol_phase(b, p):
            return b.enth_mol_phase[p] == sum(b.enth_mol_phase_comp[p, i] *
                                              b.mole_frac_phase_comp[p, i]
                                              for i in b.params.component_list)

        self.eq_enth_mol_phase = Constraint(self.params.phase_list,
                                            rule=rule_enth_mol_phase)

    def _enth_mol(self):
        def rule_enth_mol(b):
            return sum(b.enth_mol_phase[p]*b.phase_frac[p]
                       for p in b.params.phase_list)
        self.enth_mol = Expression(rule=rule_enth_mol,
                                   doc="Mixture molar enthalpy")

    def _entr_mol_phase_comp(self): # initialize this var

        self.entr_mol_phase_comp = Var(self.params.phase_list,
                                       self.params.component_list,
                                       doc='Phase-component molar specific entropies [J/mol.K]')

        def rule_entr_mol_phase_comp(b, p, j):
            if p == 'Vap':
                return b._entr_mol_comp_vap(j)
            else:
                return b._entr_mol_comp_liq(j)

        self.eq_entr_mol_phase_comp = Constraint(self.params.phase_list,
                                                 self.params.component_list,
                                                 rule=rule_entr_mol_phase_comp)

    def _entr_mol_phase(self): # initialize this var

        self.entr_mol_phase = Var(self.params.phase_list,
                                  doc='Phase molar specific enthropies [J/mol.K]')

        def rule_entr_mol_phase(b, p):
            return b.entr_mol_phase[p] == sum(b.entr_mol_phase_comp[p, i] *
                                              b.mole_frac_phase_comp[p, i]
                                              for i in b.params.component_list)

        self.eq_entr_mol_phase = Constraint(self.params.phase_list,
                                            rule=rule_entr_mol_phase)

    def _entr_mol(self):
        def rule_entr_mol(b):
            return sum(b.entr_mol_phase[p]*b.phase_frac[p]
                       for p in b.params.phase_list)
        self.entr_mol = Expression(rule=rule_entr_mol,
                                   doc="Mixture molar entropy")

    def _gibbs_mol_phase_comp(self): # initialize this var

        self.gibbs_mol_phase_comp = Var(self.params.phase_list,
                                        self.params.component_list,
                                        initialize=7e5,  # NOTE: check this out 
                                        doc='Phase-component molar gibbs energies [J/mol]')

        def rule_gibbs_mol_phase_comp(b, p, j):
            return b.gibbs_mol_phase_comp[p, j] == (b.enth_mol_phase_comp[p, j] -
                                                    b.entr_mol_phase_comp[p, j] *
                                                    b.temperature)
        self.eq_gibbs_mol_phase_comp = Constraint(self.params.phase_list,
                                                  self.params.component_list,
                                                  rule=rule_gibbs_mol_phase_comp)

    def _gibbs_mol_phase(self): # initialize this var

        self.gibbs_mol_phase = Var(self.params.phase_list,
                                   initialize=7e5, # NOTE: check this out 
                                   doc='Phase molar gibbs energies [J/mol]')

        def rule_gibbs_mol_phase(b, p):
            #return b.gibbs_mol_phase[p] == (b.enth_mol_phase[p] - b.entr_mol_phase[p]*b.temperature)
            return b.gibbs_mol_phase[p] == sum(b.gibbs_mol_phase_comp[p, i] *
                                               b.mole_frac_phase_comp[p, i]
                                               for i in b.params.component_list)
        self.eq_gibbs_mol_phase = Constraint(self.params.phase_list,
                                            rule=rule_gibbs_mol_phase)

    def _gibbs_mol(self):
        def rule_gibbs_mol(b):
            return sum(b.gibbs_mol_phase[p]*b.phase_frac[p]
                       for p in b.params.phase_list)
        self.gibbs_mol = Expression(rule=rule_gibbs_mol,
                                    doc="Mixture molar enthalpy")

    def _fug_phase_comp(self):

        def rule_fug_phase_comp(b, p, j):
            pobj = b.params.get_phase(p)
            if pobj.is_vapor_phase():
                return b.mole_frac_phase_comp[p, j] * b.pressure
            elif pobj.is_liquid_phase():
                return b.mole_frac_phase_comp[p, j] * b.pressure_sat[j]

        self.fug_phase_comp = Expression(self.params.phase_list,
                                         self.params.component_list,
                                         rule=rule_fug_phase_comp)

    # -----------------------------------------------------------------------------
    # Liquid phase properties
    # Liquid Molar Density Perry's Equation
    def _dens_mol_liq(b):

        return b.dens_mol_phase['Liq'] == 1e3*sum(
                b.mole_frac_phase_comp['Liq', j] *
                b.params.dens_mol_liq_comp_coeff_1[j] /
                b.params.dens_mol_liq_comp_coeff_2[j] **
                (1 + (1-b.temperature /
                      b.params.dens_mol_liq_comp_coeff_3[j]) **
                 b.params.dens_mol_liq_comp_coeff_4[j])
                for j in ['water', 'ethanol'])         # NOTE: add component list here                   

    # Ideal Liquid Molar Enthalpy Perry's Equation
    def _enth_mol_comp_liq(b, j):
        return b.enth_mol_phase_comp['Liq', j] * 1E3 == \
               (b.params.cp_mol_liq_comp_coeff_5[j]/5)* \
               (b.temperature**5-b.params.temperature_ref**5) + \
               (b.params.cp_mol_liq_comp_coeff_4[j]/4)* \
               (b.temperature**4-b.params.temperature_ref**4) + \
               (b.params.cp_mol_liq_comp_coeff_3[j]/3)* \
               (b.temperature**3-b.params.temperature_ref**3) + \
               (b.params.cp_mol_liq_comp_coeff_2[j]/2)* \
               (b.temperature**2-b.params.temperature_ref**2) + \
                b.params.cp_mol_liq_comp_coeff_1[j]* \
               (b.temperature-b.params.temperature_ref) + \
                b.params.enth_mol_form_liq_comp_ref[j]

    # Ideal Liquid Molar Entropy Perry's Equation
    def _entr_mol_comp_liq(b, j):
        return b.entr_mol_phase_comp['Liq', j] * 1E3 == \
               (b.params.cp_mol_liq_comp_coeff_5[j]/4)* \
               (b.temperature**4-b.params.temperature_ref**4) + \
               (b.params.cp_mol_liq_comp_coeff_4[j]/3)* \
               (b.temperature**3-b.params.temperature_ref**3) + \
               (b.params.cp_mol_liq_comp_coeff_3[j]/2)* \
               (b.temperature**2-b.params.temperature_ref**2) + \
                b.params.cp_mol_liq_comp_coeff_2[j]* \
               (b.temperature-b.params.temperature_ref) + \
                b.params.cp_mol_liq_comp_coeff_1[j]* \
                log(b.temperature/b.params.temperature_ref) + \
                b.params.entr_mol_form_liq_comp_ref[j]

    # Saturation (Vapor) Pressure NIST Equation
    def pressure_saturation(self, j, T):
        return (exp((1-(1 - T/self.params.temperature_crit[j]))**-1 * \
               (self.params.pressure_sat_comp_coeff_A[j]*(1 - \
                T/self.params.temperature_crit[j]) + \
                self.params.pressure_sat_comp_coeff_B[j]*(1 - \
                T/self.params.temperature_crit[j])**1.5 + \
                self.params.pressure_sat_comp_coeff_C[j]*(1 - \
                T/self.params.temperature_crit[j])**3 + \
                self.params.pressure_sat_comp_coeff_D[j]*(1 - \
                T/self.params.temperature_crit[j])**6)) * \
                self.params.pressure_crit[j])

    def der_pressure_saturation(self, j, T):
        return -self.pressure_saturation(j, T) * \
               ((self.params.pressure_sat_comp_coeff_A[j] + \
                  1.5*self.params.pressure_sat_comp_coeff_B[j]*(1-T/self.params.temperature_crit[j])**0.5 + \
                  3*self.params.pressure_sat_comp_coeff_C[j]*(1-T/self.params.temperature_crit[j])**2 + \
                  6*self.params.pressure_sat_comp_coeff_D[j]*(1-T/self.params.temperature_crit[j])**5)/T + \
                 (self.params.temperature_crit[j]/T**2) * \
                 (self.params.pressure_sat_comp_coeff_A[j]*(1-T/self.params.temperature_crit[j]) + \
                  self.params.pressure_sat_comp_coeff_B[j]*(1-T/self.params.temperature_crit[j])**1.5 + \
                  self.params.pressure_sat_comp_coeff_C[j]*(1-T/self.params.temperature_crit[j])**3 + \
                  self.params.pressure_sat_comp_coeff_D[j]*(1-T/self.params.temperature_crit[j])**6))

    def _pressure_sat(self):

        self.pressure_sat = Var(self.params.component_list,
                                initialize=101325,
                                doc="Vapor pressure [Pa]")

        def rule_P_sat(b, j):
            return b.pressure_sat[j] == b.pressure_saturation(j, b._teq)
        self.eq_pressure_sat = Constraint(self.params.component_list,
                                          rule=rule_P_sat)


    # -----------------------------------------------------------------------------
    # Vapor phase properties
    # Ideal Gas law equation
    def _dens_mol_vap(b):
        return b.pressure == (b.dens_mol_phase['Vap'] *
                              b.params.gas_const *
                              b.temperature)

    # Ideal Gas Molar Enthalpy RPP Equation
    def _enth_mol_comp_vap(b, j):
        return b.enth_mol_phase_comp['Vap', j] == ( \
               (b.params.cp_mol_ig_comp_coeff_D[j]/4)* \
               (b.temperature**4-b.params.temperature_ref**4) + \
               (b.params.cp_mol_ig_comp_coeff_C[j]/3)* \
               (b.temperature**3-b.params.temperature_ref**3) + \
               (b.params.cp_mol_ig_comp_coeff_B[j]/2)* \
               (b.temperature**2-b.params.temperature_ref**2) + \
                b.params.cp_mol_ig_comp_coeff_A[j]* \
               (b.temperature-b.params.temperature_ref) ) + \
                b.params.enth_mol_form_vap_comp_ref[j]

    # Ideal Gas Molar Entropy RPP Equation
    def _entr_mol_comp_vap(b, j):
        return b.entr_mol_phase_comp['Vap', j] == \
               (b.params.cp_mol_ig_comp_coeff_D[j]/3)* \
               (b.temperature**3-b.params.temperature_ref**3) + \
               (b.params.cp_mol_ig_comp_coeff_C[j]/2)* \
               (b.temperature**2-b.params.temperature_ref**2) + \
                b.params.cp_mol_ig_comp_coeff_B[j]* \
               (b.temperature-b.params.temperature_ref) + \
                b.params.cp_mol_ig_comp_coeff_A[j]* \
                log(b.temperature/b.params.temperature_ref) + \
                b.params.entr_mol_form_vap_comp_ref[j]

    # -------------------------------------------------------------------------
    # Bubble and Dew Points

    def _temperature_bubble(self):
        self.temperature_bubble = Var(initialize=298.15,
                                      bounds=(200, 500),
                                      units=pyunits.K,
                                      doc="Bubble point temperature (K)")
            
        self._mole_frac_tbub = Var(self.params.component_list,
                                   initialize=1/len(self.params.component_list),
                                   bounds=(0, None),
                                   units=None,
                                   doc="Vapor mole fractions at bubble point")

        def rule_psat_tbub(b, j):
            return b.pressure_saturation(j, b.temperature_bubble)
        self._p_sat_tbub = Expression(self.params.component_list,
                                      rule=rule_psat_tbub)

        def rule_bubble_temp(b):
            return (sum(b.mole_frac_comp[j] * b._p_sat_tbub[j] \
                    for j in b.params.component_list) - b.pressure) == 0
        self.eq_temperature_bubble = Constraint(rule=rule_bubble_temp)

        def rule_mole_frac_bubble_temp(b, j):
            return b._mole_frac_tbub[j]*b.pressure == b.mole_frac_comp[j] * \
                                                      b._p_sat_tbub[j]
        self.eq_mole_frac_tbub = Constraint(self.params.component_list,
                                            rule=rule_mole_frac_bubble_temp)

    def _temperature_dew(self):
        self.temperature_dew = Var(initialize=298.15,
                                   bounds=(200, 500),
                                   units=pyunits.K,
                                   doc="Dew point temperature (K)")

        self._mole_frac_tdew = Var(self.params.component_list,
                                   initialize=1/len(self.params.component_list),
                                   bounds=(0, None),
                                   units=None,
                                   doc="Liquid mole fractions at dew point")

        def rule_psat_tdew(b, j):
            return b.pressure_saturation(j, b.temperature_dew)
        self._p_sat_tdew = Expression(self.params.component_list,
                                       rule=rule_psat_tdew)

        def rule_dew_temp(b):
            return b.pressure*sum(b.mole_frac_comp[j] / \
                   b._p_sat_tdew[j] for j in b.params.component_list) - 1 == 0
        self.eq_temperature_dew = Constraint(rule=rule_dew_temp)

        def rule_mole_frac_dew_temp(b, j):
            return b._mole_frac_tdew[j] * b._p_sat_tdew[j] == b.mole_frac_comp[j] * b.pressure
        self.eq_mole_frac_tdew = Constraint(self.params.component_list,
                                            rule=rule_mole_frac_dew_temp)

    def _pressure_bubble(self):
        self.pressure_bubble = Var(initialize=1e5,
                                   domain=NonNegativeReals,
                                   units=pyunits.Pa,
                                   doc="Bubble point pressure (Pa)")

        self._mole_frac_pbub = Var(self.params.component_list,
                                   initialize=1/len(self.params.component_list),
                                   bounds=(0, None),
                                   doc="Vapor mole fractions at bubble point")

        def rule_psat_pbub(b, j):
            return b.pressure_saturation(j, b.temperature)
        self._p_sat_pbub = Expression(self.params.component_list,
                                       rule=rule_psat_pbub)

        def rule_bubble_press(b):
            return b.pressure_bubble == sum(b.mole_frac_comp[j] * b._p_sat_pbub[j] \
                                            for j in b.params.component_list)
        self.eq_pressure_bubble = Constraint(rule=rule_bubble_press)

        def rule_mole_frac_bubble_press(b, j):
            return b._mole_frac_pbub[j] * b.pressure_bubble == b.mole_frac_comp[j] * \
                                                               b._p_sat_pbub[j]
        self.eq_mole_frac_pbub = Constraint(self.params.component_list,
                                            rule=rule_mole_frac_bubble_press)

    def _pressure_dew(self):
        self.pressure_dew = Var(initialize=1e5,
                                domain=NonNegativeReals,
                                units=pyunits.Pa,
                                doc="Dew point pressure (Pa)")

        self._mole_frac_pdew = Var(self.params.component_list,
                                   initialize=1/len(self.params.component_list),
                                   bounds=(0, None),
                                   doc="Liquid mole fractions at dew point")

        def rule_psat_pdew(b, j):
            return b.pressure_saturation(j, b.temperature)
        self._p_sat_pdew = Expression(self.params.component_list,
                                       rule=rule_psat_pdew)

        def rule_dew_press(b,):
            return 0 == 1 - b.pressure_dew*sum(b.mole_frac_comp[j] / \
                        b._p_sat_pdew[j] for j in b.params.component_list)
        self.eq_pressure_dew = Constraint(rule=rule_dew_press)

        def rule_mole_frac_dew_press(b, j):
            return b._mole_frac_pdew[j] * b._p_sat_pdew[j] == b.mole_frac_comp[j] * \
                                                              b.pressure_dew
        self.eq_mole_frac_pdew = Constraint(self.params.component_list,
                                            rule=rule_mole_frac_dew_press)