#!/usr/bin/env python
"""Run smoke checks for generated property-package modules."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module-file", required=True, help="Path to module file.")
    return parser.parse_args()


def load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location("_skill_smoke_module", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to create import spec for {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_generic(module) -> None:
    from pyomo.environ import ConcreteModel
    from pyomo.util.check_units import assert_units_consistent
    from idaes.models.properties.modular_properties.base.generic_property import (
        GenericParameterBlock,
    )

    if not hasattr(module, "configuration"):
        return

    m = ConcreteModel()
    m.params = GenericParameterBlock(**module.configuration)
    m.props = m.params.build_state_block([1], defined_state=True)
    assert_units_consistent(m)


def check_class_based(module) -> None:
    from pyomo.environ import ConcreteModel
    from pyomo.util.check_units import assert_units_consistent

    parameter_cls = None
    for name in dir(module):
        if name.endswith("ParameterBlock"):
            parameter_cls = getattr(module, name)
            break

    if parameter_cls is None:
        return

    m = ConcreteModel()
    m.params = parameter_cls()
    m.props = m.params.build_state_block([1], defined_state=True)
    assert_units_consistent(m)


def main() -> int:
    args = parse_args()
    module_path = Path(args.module_file).resolve()

    if not module_path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")

    module = load_module(module_path)

    generic_checked = hasattr(module, "configuration")
    check_generic(module)

    class_checked = any(name.endswith("ParameterBlock") for name in dir(module))
    check_class_based(module)

    if not generic_checked and not class_checked:
        print("No known smoke target found (no `configuration` and no `*ParameterBlock`).")
    else:
        print(f"Smoke validation passed for: {module_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
