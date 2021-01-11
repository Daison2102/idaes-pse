##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2019, by the
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
Test for plate heat exchanger model

Author: Paul Akula
"""
# Import Python libraries
import pytest
import sys
import os

# Import Pyomo libraries
from pyomo.environ import ConcreteModel, value, TerminationCondition

# Import IDAES Libraries
from idaes.core import FlowsheetBlock
from idaes.core.util.testing import get_default_solver
from idaes.core.util.model_statistics import degrees_of_freedom
# Access mea_column_files dir from the current dir (tests dir)
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from unit_models.phe import PHE
from properties.liquid_prop import LiquidParameterBlock

solver = get_default_solver()

class TestPlateHeatExchanger:
    '''
    Tests for the plate heat exchange (PHE) model
    '''

    @pytest.fixture(scope="module")
    def measurement(self):
      nccc_data = {'dataset1':
                   {'input':
                    {'hotside':
                     {'flowrate': 60.54879,
                      'temperature': 392.23,
                      'pressure': 202650,
                      'mole_fraction':
                      {'CO2': 0.0158,
                       'MEA': 0.1095,
                       'H2O': 0.8747}},
                     'coldside':
                     {'flowrate': 63.01910,
                      'temperature': 326.36,
                      'pressure': 202650,
                      'mole_fraction':
                      {'CO2': 0.0414,
                       'MEA': 0.1077,
                       'H2O': 0.8509}}},
                    'output':
                        {'hotside':
                            {'temperature': 330.42},
                         'coldside':
                            {'temperature': 384.91}}},
                   'dataset2':
                   {"input":
                        {'hotside':
                            {'flowrate': 102.07830,
                             'temperature': 389.57,
                             'pressure': 202650,
                             'mole_fraction':
                             {'CO2': 0.0284,
                              'MEA': 0.1148,
                              'H2O': 0.8569}},
                         'coldside':
                            {'flowrate': 104.99350,
                             'temperature': 332.26,
                             'pressure': 202650,
                             'mole_fraction':
                             {'CO2': 0.0438,
                              'MEA': 0.1137,
                              'H2O': 0.8426}}},
                    'output':
                        {'hotside':
                            {'temperature': 336.70},
                         'coldside':
                            {'temperature': 383.21}}}}

      return nccc_data

    @pytest.fixture(scope="module")
    def phe_model(self):
        m = ConcreteModel()
        m.fs = FlowsheetBlock(default={"dynamic": False})
        # Set up property package
        m.fs.hotside_properties = LiquidParameterBlock()
        m.fs.coldside_properties = LiquidParameterBlock()

        # create instance of plate heat exchanger  on flowsheet
        m.fs.hx = PHE(default={'passes': 4,
                               'channel_list': [12, 12, 12, 12],
                               "hot_side": {
                                   "property_package": m.fs.hotside_properties
                               },
                               "cold_side":
                               {
                                   "property_package": m.fs.coldside_properties
                               }})
        return m


    @pytest.fixture(scope="module", params=['dataset1', 'dataset2'])
    def set_input_output(self, phe_model, measurement, request):
        for t in phe_model.fs.time:
            # hot fluid
            Th_out = measurement[request.param]['output']['hotside']['temperature']
            Th = measurement[request.param]['input']['hotside']['temperature']
            Fh = measurement[request.param]['input']['hotside']['flowrate']
            Ph = measurement[request.param]['input']['hotside']['pressure']
            xh_CO2 = measurement[request.param]['input']['hotside']['mole_fraction']['CO2']
            xh_MEA = measurement[request.param]['input']['hotside']['mole_fraction']['MEA']
            xh_H2O = measurement[request.param]['input']['hotside']['mole_fraction']['H2O']

            phe_model.fs.hx.hot_inlet.flow_mol[t].fix(Fh)
            phe_model.fs.hx.hot_inlet.temperature[t].fix(Th)
            phe_model.fs.hx.hot_inlet.pressure[t].fix(Ph)
            phe_model.fs.hx.hot_inlet.mole_frac_comp[t, "CO2"].fix(xh_CO2)
            phe_model.fs.hx.hot_inlet.mole_frac_comp[t, "H2O"].fix(xh_H2O)
            phe_model.fs.hx.hot_inlet.mole_frac_comp[t, "MEA"].fix(xh_MEA)

            # cold fluid
            Tc_out = measurement[request.param]['output']['coldside']['temperature']
            Tc = measurement[request.param]['input']['coldside']['temperature']
            Fc = measurement[request.param]['input']['coldside']['flowrate']
            Pc = measurement[request.param]['input']['coldside']['pressure']
            xc_CO2 = measurement[request.param]['input']['coldside']['mole_fraction']['CO2']
            xc_MEA = measurement[request.param]['input']['coldside']['mole_fraction']['MEA']
            xc_H2O = measurement[request.param]['input']['coldside']['mole_fraction']['H2O']
            phe_model.fs.hx.cold_inlet.flow_mol[t].fix(Fc)
            phe_model.fs.hx.cold_inlet.temperature[t].fix(Tc)
            phe_model.fs.hx.cold_inlet.pressure[t].fix(Pc)
            phe_model.fs.hx.cold_inlet.mole_frac_comp[t, "CO2"].fix(xc_CO2)
            phe_model.fs.hx.cold_inlet.mole_frac_comp[t, "H2O"].fix(xc_H2O)
            phe_model.fs.hx.cold_inlet.mole_frac_comp[t, "MEA"].fix(xc_MEA)

            output = {'hotside_temperature_expectation': Th_out,
                      'coldside_temperature_expectation': Tc_out}
            return output


    @pytest.mark.unit
    def test_phe_build(self, phe_model):
        assert phe_model.fs.hx.config.dynamic is False
        assert degrees_of_freedom(phe_model) == 12

    @pytest.mark.skipif(solver is None, reason="Solver not available")
    @pytest.mark.integration
    def test_phe_validation(self, phe_model, set_input_output):

        optarg = {"tol": 1e-7,
                  "linear_solver": "mumps",
                  "max_iter": 40}
        solver.options = optarg

        phe_model.fs.hx.initialize()
        res = solver.solve(phe_model)

        assert res.solver.termination_condition == TerminationCondition.optimal

        assert value(phe_model.fs.hx.QH[0]) == value(phe_model.fs.hx.QC[0])

        assert value(phe_model.fs.hx.hot_outlet.temperature[0]) == \
            pytest.approx(
            set_input_output['hotside_temperature_expectation'], abs=1.5)

        assert value(phe_model.fs.hx.cold_outlet.temperature[0]) == \
            pytest.approx(
            set_input_output['coldside_temperature_expectation'], abs=1.5)
