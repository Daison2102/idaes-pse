"""Template pytest for class-based property packages."""

import pytest
from pyomo.environ import ConcreteModel
from pyomo.util.check_units import assert_units_consistent
from idaes.core.util.model_statistics import degrees_of_freedom

from YOUR_CLASS_MODULE import TemplateParameterBlock


@pytest.mark.component
def test_class_based_property_package_smoke():
    m = ConcreteModel()
    m.params = TemplateParameterBlock()
    m.props = m.params.build_state_block([1], defined_state=True)

    assert_units_consistent(m)
    assert degrees_of_freedom(m.props[1]) == 0
