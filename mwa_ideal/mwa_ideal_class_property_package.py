# pylint: disable=all
"""
Compatibility class package for MWA.

This module preserves the original class-package entrypoint name
(`MWAIdealParameterBlock`) while delegating implementation to the generic
framework class-definition package so flash results are consistent across:

- test_flash_example.py
- test_generic_flash_example.py
- test_generic_class_flash_example.py
"""

try:
    from mwa_ideal.mwa_ideal_generic_property_package_class import (  # noqa: F401
        MWAClassGenericParameterBlock as MWAIdealParameterBlock,
    )
except ModuleNotFoundError:
    from mwa_ideal_generic_property_package_class import (  # noqa: F401
        MWAClassGenericParameterBlock as MWAIdealParameterBlock,
    )
