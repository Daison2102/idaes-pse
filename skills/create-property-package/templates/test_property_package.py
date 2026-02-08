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
Validation tests for {{SYSTEM_NAME}} property package.

Tests verify:
- Parameter block builds correctly
- State block creates and fixes without error
- Degrees of freedom are correct
- Initialization converges
- Solver reaches optimal solution
- Key property values are physically reasonable
- (Optional) Integration with a simple Heater unit model
"""
import pytest
import pyomo.environ as pyo
from pyomo.environ import TerminationCondition, value

from idaes.core import FlowsheetBlock
from idaes.core.solvers import get_solver
from idaes.core.util.model_statistics import degrees_of_freedom
import idaes.logger as idaeslog

# ---------------------------------------------------------------------------
# Import the property package under test.
#
# For Generic Framework:
from idaes.models.properties.modular_properties.base.generic_property import (
    GenericParameterBlock,
)

# from {{MODULE}} import configuration
#
# For Class-Based:
# from {{MODULE}} import {{PARAM_BLOCK_NAME}}
# ---------------------------------------------------------------------------


solver = get_solver()


# ===========================================================================
# Test class: Generic Framework property package
# ===========================================================================


@pytest.mark.component
class TestGenericPropertyPackage:
    """Tests for the Generic Framework property package."""

    @pytest.fixture(scope="class")
    def model(self):
        """Build the model once for all tests in this class."""
        m = pyo.ConcreteModel()
        m.fs = FlowsheetBlock(dynamic=False)

        # --- Replace with actual configuration import ---
        # m.fs.params = GenericParameterBlock(**configuration)
        raise NotImplementedError(
            "Replace this fixture with your actual configuration import"
        )

        m.fs.state = m.fs.params.build_state_block(
            [0],
            defined_state=True,
            has_phase_equilibrium={{HAS_VLE}},
        )

        # Fix state variables to physically reasonable values
        m.fs.state[0].flow_mol.fix({{FLOW_MOL}})
        m.fs.state[0].temperature.fix({{TEMPERATURE}})
        m.fs.state[0].pressure.fix({{PRESSURE}})
        # Fix mole fractions (must sum to 1.0)
        # m.fs.state[0].mole_frac_comp["{{COMP_A}}"].fix({{XA}})
        # m.fs.state[0].mole_frac_comp["{{COMP_B}}"].fix({{XB}})

        return m

    def test_build(self, model):
        """Test that the parameter block builds correctly."""
        assert hasattr(model.fs, "params")
        assert hasattr(model.fs, "state")

    def test_components(self, model):
        """Test that components are defined."""
        comp_list = [c for c in model.fs.params.component_list]
        assert len(comp_list) >= 2
        # assert "{{COMP_A}}" in comp_list
        # assert "{{COMP_B}}" in comp_list

    def test_phases(self, model):
        """Test that phases are defined."""
        phase_list = [p for p in model.fs.params.phase_list]
        # Adjust assertions based on expected phases
        assert len(phase_list) >= 1
        # assert "Vap" in phase_list
        # assert "Liq" in phase_list

    def test_dof(self, model):
        """Degrees of freedom should be 0 after fixing state variables."""
        assert degrees_of_freedom(model.fs.state[0]) == 0

    def test_initialize(self, model):
        """Initialization should converge without errors."""
        model.fs.state.initialize(outlvl=idaeslog.WARNING)

    def test_solve(self, model):
        """Solver should find an optimal solution."""
        results = solver.solve(model.fs.state, tee=False)
        assert results.solver.termination_condition == TerminationCondition.optimal

    def test_density_positive(self, model):
        """Molar densities should be positive for all phases."""
        if hasattr(model.fs.state[0], "dens_mol_phase"):
            for p in model.fs.params.phase_list:
                rho = value(model.fs.state[0].dens_mol_phase[p])
                assert rho > 0, f"Density of phase {p} is non-positive: {rho}"

    def test_enthalpy_reasonable(self, model):
        """Molar enthalpies should be finite and not NaN."""
        if hasattr(model.fs.state[0], "enth_mol_phase"):
            for p in model.fs.params.phase_list:
                h = value(model.fs.state[0].enth_mol_phase[p])
                assert h == h, f"Enthalpy of phase {p} is NaN"
                assert abs(h) < 1e9, f"Enthalpy of phase {p} seems unreasonable: {h}"

    def test_phase_fractions_sum_to_one(self, model):
        """Phase fractions should sum to 1.0."""
        if hasattr(model.fs.state[0], "phase_frac"):
            pf_sum = sum(
                value(model.fs.state[0].phase_frac[p])
                for p in model.fs.params.phase_list
            )
            assert abs(pf_sum - 1.0) < 1e-6, (
                f"Phase fractions sum to {pf_sum}, expected 1.0"
            )

    def test_mole_fractions_in_range(self, model):
        """Phase mole fractions should be between 0 and 1."""
        if hasattr(model.fs.state[0], "mole_frac_phase_comp"):
            for p in model.fs.params.phase_list:
                for j in model.fs.params.component_list:
                    if (p, j) in model.fs.params._phase_component_set:
                        x = value(
                            model.fs.state[0].mole_frac_phase_comp[p, j]
                        )
                        assert -1e-6 <= x <= 1.0 + 1e-6, (
                            f"Mole frac ({p}, {j}) = {x} out of range"
                        )


# ===========================================================================
# (Optional) Integration test with a Heater unit model
# ===========================================================================


@pytest.mark.component
class TestHeaterIntegration:
    """Test the property package with a simple Heater unit."""

    @pytest.fixture(scope="class")
    def model(self):
        from idaes.models.unit_models import Heater

        m = pyo.ConcreteModel()
        m.fs = FlowsheetBlock(dynamic=False)

        # --- Replace with actual configuration import ---
        # m.fs.params = GenericParameterBlock(**configuration)
        raise NotImplementedError(
            "Replace this fixture with your actual configuration import"
        )

        m.fs.heater = Heater(property_package=m.fs.params)

        # Fix inlet conditions
        m.fs.heater.inlet.flow_mol[0].fix({{FLOW_MOL}})
        m.fs.heater.inlet.temperature[0].fix({{TEMPERATURE}})
        m.fs.heater.inlet.pressure[0].fix({{PRESSURE}})
        # m.fs.heater.inlet.mole_frac_comp[0, "{{COMP_A}}"].fix({{XA}})
        # m.fs.heater.inlet.mole_frac_comp[0, "{{COMP_B}}"].fix({{XB}})

        # Fix heater duty
        m.fs.heater.heat_duty[0].fix(1000)  # W

        return m

    def test_dof(self, model):
        assert degrees_of_freedom(model) == 0

    def test_initialize_and_solve(self, model):
        model.fs.heater.initialize(outlvl=idaeslog.WARNING)
        results = solver.solve(model, tee=False)
        assert results.solver.termination_condition == TerminationCondition.optimal

    def test_outlet_temperature_increased(self, model):
        """Adding heat should increase the outlet temperature."""
        T_in = value(model.fs.heater.inlet.temperature[0])
        T_out = value(model.fs.heater.outlet.temperature[0])
        assert T_out > T_in, (
            f"Outlet T ({T_out}) should be > inlet T ({T_in})"
        )
