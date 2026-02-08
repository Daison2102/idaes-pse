"""Template pytest for generic property packages."""

import pytest
from pyomo.environ import ConcreteModel
from pyomo.util.check_units import assert_units_consistent
from idaes.core.util.model_statistics import degrees_of_freedom
from idaes.models.properties.modular_properties.base.generic_property import GenericParameterBlock

from YOUR_GENERIC_MODULE import configuration


@pytest.mark.component
def test_generic_property_package_smoke():
    m = ConcreteModel()
    m.params = GenericParameterBlock(**configuration)
    m.props = m.params.build_state_block([1], defined_state=True)

    assert_units_consistent(m)
    assert degrees_of_freedom(m.props[1]) == 0
