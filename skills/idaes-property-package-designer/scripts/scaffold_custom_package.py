#!/usr/bin/env python3
"""Scaffold a custom class-based IDAES property package module from a local template."""

from __future__ import annotations

import argparse
from pathlib import Path


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _phase_declarations(phases: list[str]) -> str:
    lines = []
    for phase in phases:
        cls_name = "VaporPhase" if phase.lower().startswith("vap") else "LiquidPhase"
        lines.append(f"        self.{phase} = {cls_name}()")
    return "\n".join(lines)


def _component_declarations(components: list[str]) -> str:
    return "\n".join([f"        self.{comp} = Component()" for comp in components])


def _state_var_map(state_vars: list[str]) -> str:
    lines = ["        return {"]
    for name in state_vars:
        lines.append(f'            "{name}": self.{name},')
    lines.append("        }")
    return "\n".join(lines)


def _initialize_body(include_initialize: bool) -> str:
    if not include_initialize:
        return "        return None"
    return "\n".join(
        [
            "        # TODO: add custom initialization sequence",
            "        return None",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Property package name stem")
    parser.add_argument("--components", required=True, help="Comma-separated component names")
    parser.add_argument("--phases", default="Liq,Vap", help="Comma-separated phase names")
    parser.add_argument(
        "--state-vars",
        default="flow_mol,mole_frac_comp,temperature,pressure",
        help="Comma-separated state variable names",
    )
    parser.add_argument("--include-initialize", action="store_true")
    parser.add_argument("--output", required=True, help="Output python file path")
    args = parser.parse_args()

    components = _split_csv(args.components)
    phases = _split_csv(args.phases)
    state_vars = _split_csv(args.state_vars)

    if not components:
        raise ValueError("At least one component is required.")
    if not phases:
        raise ValueError("At least one phase is required.")

    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "assets" / "stubs" / "custom_property_package_stub.py.j2"
    template = template_path.read_text(encoding="utf-8")

    class_stem = "".join(part.capitalize() for part in args.name.replace("-", "_").split("_"))
    rendered = (
        template.replace("{{CLASS_STEM}}", class_stem)
        .replace("{{PHASE_DECLARATIONS}}", _phase_declarations(phases))
        .replace("{{COMPONENT_DECLARATIONS}}", _component_declarations(components))
        .replace("{{STATE_VARS_MAP}}", _state_var_map(state_vars))
        .replace("{{INITIALIZE_BODY}}", _initialize_body(args.include_initialize))
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")

    print(f"Wrote custom scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
