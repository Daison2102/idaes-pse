#!/usr/bin/env python3
"""Generate pytest scaffolding for an IDAES property package.

Usage:
    python generate_property_package_tests.py \
        --spec spec.json --approach generic --output test_props.py --module my_props
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", text).strip("_").lower() or "custom_props"


def _state_definition(spec: Dict[str, Any]) -> str:
    sd = str(spec.get("state_definition", "FTPx"))
    return sd if sd in {"FTPx", "FpcTP", "FcTP", "FPhx", "FcPh"} else "FTPx"


def _render_fix_state_block(state_def: str) -> str:
    if state_def == "FTPx":
        return """
    s.flow_mol.fix(1.0)
    s.temperature.fix(300.0)
    s.pressure.fix(101325.0)
    n = len(list(s.params.component_list))
    for j in s.params.component_list:
        s.mole_frac_comp[j].fix(1.0 / n)
"""
    if state_def == "FpcTP":
        return """
    s.temperature.fix(300.0)
    s.pressure.fix(101325.0)
    nph = len(list(s.params.phase_list))
    ncp = len(list(s.params.component_list))
    val = 1.0 / max(nph * ncp, 1)
    for p in s.params.phase_list:
        for j in s.params.component_list:
            s.flow_mol_phase_comp[p, j].fix(val)
"""
    if state_def == "FcTP":
        return """
    s.temperature.fix(300.0)
    s.pressure.fix(101325.0)
    ncp = len(list(s.params.component_list))
    val = 1.0 / max(ncp, 1)
    for j in s.params.component_list:
        s.flow_mol_comp[j].fix(val)
"""
    if state_def == "FPhx":
        return """
    s.flow_mol.fix(1.0)
    s.enth_mol.fix(0.0)
    s.pressure.fix(101325.0)
    n = len(list(s.params.component_list))
    for j in s.params.component_list:
        s.mole_frac_comp[j].fix(1.0 / n)
"""
    return """
    s.enth_mol.fix(0.0)
    s.pressure.fix(101325.0)
    ncp = len(list(s.params.component_list))
    val = 1.0 / max(ncp, 1)
    for j in s.params.component_list:
        s.flow_mol_comp[j].fix(val)
"""


def _render(
    spec: Dict[str, Any],
    approach: str,
    module_name: str,
    marker: str,
    param_block_class: str,
) -> str:
    state_def = _state_definition(spec)

    lines = []
    lines.append('"""Generated tests for IDAES property package scaffolding."""')
    lines.append("")
    lines.append("import pytest")
    lines.append("from pyomo.environ import ConcreteModel")
    lines.append("from pyomo.util.check_units import assert_units_consistent")
    lines.append("from idaes.core import FlowsheetBlock")
    lines.append("from idaes.core.solvers import get_solver")
    lines.append("from idaes.core.util.model_statistics import degrees_of_freedom")
    lines.append("")

    if approach == "generic":
        lines.append(f"from {module_name} import configuration")
        lines.append(
            "from idaes.models.properties.modular_properties.base.generic_property import GenericParameterBlock"
        )
    else:
        lines.append(f"from {module_name} import {param_block_class}")

    lines.append("")
    lines.append("solver = get_solver(\"ipopt_v2\")")
    lines.append("")
    lines.append("@pytest.fixture()")
    lines.append("def m():")
    lines.append("    m = ConcreteModel()")
    lines.append("    m.fs = FlowsheetBlock(dynamic=False)")
    if approach == "generic":
        lines.append("    m.fs.params = GenericParameterBlock(**configuration)")
    else:
        lines.append(f"    m.fs.params = {param_block_class}()")
    lines.append("    m.fs.state = m.fs.params.build_state_block([0], defined_state=True)")
    lines.append("    return m")
    lines.append("")

    lines.append(f"@pytest.mark.{marker}")
    lines.append("def test_build(m):")
    lines.append("    assert m.fs.params is not None")
    lines.append("    assert m.fs.state[0] is not None")
    lines.append("")

    lines.append(f"@pytest.mark.{marker}")
    lines.append("def test_units(m):")
    lines.append("    assert_units_consistent(m)")
    lines.append("")

    lines.append(f"@pytest.mark.{marker}")
    lines.append("def test_initialize_and_solve(m):")
    lines.append("    s = m.fs.state[0]")
    lines.append(_render_fix_state_block(state_def).rstrip("\n"))
    lines.append("    assert degrees_of_freedom(s) == 0")
    lines.append("    s.initialize()")
    lines.append("    results = solver.solve(m)")
    lines.append("    assert results.solver.termination_condition is not None")
    lines.append("")

    lines.append(f"@pytest.mark.{marker}")
    lines.append("def test_required_properties_smoke(m):")
    lines.append("    s = m.fs.state[0]")
    lines.append("    # TODO: Replace with concrete, package-specific property checks.")
    req = spec.get("required_properties", [])
    if isinstance(req, list) and req:
        for p in req:
            pname = str(p)
            lines.append(f"    _ = getattr(s, \"{pname}\", None)")
        lines.append("    assert True")
    else:
        lines.append("    assert s is not None")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Path to normalized JSON spec")
    parser.add_argument("--approach", choices=["generic", "class"], required=True)
    parser.add_argument("--output", required=True, help="Output pytest file")
    parser.add_argument("--module", help="Python module path for generated property package")
    parser.add_argument(
        "--parameter-block-class",
        help="Class name for class-based parameter block",
    )
    parser.add_argument(
        "--marker",
        default="component",
        choices=["unit", "component", "integration", "performance"],
        help="Primary pytest marker",
    )
    args = parser.parse_args()

    with Path(args.spec).open("r", encoding="utf-8") as f:
        spec = json.load(f)

    module_name = args.module or _slug(str(spec.get("name", "custom_props")))
    if args.approach == "class":
        default_class = _slug(str(spec.get("name", "custom"))).title().replace("_", "") + "ParameterBlock"
        param_block_class = args.parameter_block_class or default_class
    else:
        param_block_class = ""

    text = _render(
        spec=spec,
        approach=args.approach,
        module_name=module_name,
        marker=args.marker,
        param_block_class=param_block_class,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
