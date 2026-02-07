#!/usr/bin/env python3
"""Scaffold a generic IDAES property package module from a local template."""

from __future__ import annotations

import argparse
from pathlib import Path


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _component_block(components: list[str]) -> str:
    lines = []
    for comp in components:
        lines.extend(
            [
                f'        "{comp}": {{',
                '            "type": Component,',
                '            "elemental_composition": {},  # TODO',
                '            "parameter_data": {},  # TODO',
                "        },",
            ]
        )
    return "\n".join(lines)


def _phase_block(phases: list[str]) -> str:
    lines = []
    for phase in phases:
        phase_type = "VaporPhase" if phase.lower().startswith("vap") else "LiquidPhase"
        lines.append(
            f'        "{phase}": {{"type": {phase_type}, "equation_of_state": Ideal}},'
        )
    return "\n".join(lines)


def _equilibrium_block(phases: list[str], include_equilibrium: bool) -> str:
    if not include_equilibrium or len(phases) < 2:
        return ""
    pair = f'("{phases[0]}", "{phases[1]}")'
    return (
        "\n"
        "    # Optional phase equilibrium\n"
        f"    \"phases_in_equilibrium\": [{pair}],\n"
        f"    \"phase_equilibrium_state\": {{{pair}: SmoothVLE}},\n"
        "    # \"bubble_dew_method\": IdealBubbleDew,\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Property package name")
    parser.add_argument("--components", required=True, help="Comma-separated component names")
    parser.add_argument("--phases", default="Vap,Liq", help="Comma-separated phase names")
    parser.add_argument("--state-def", default="FTPx", help="State definition symbol")
    parser.add_argument("--include-equilibrium", action="store_true")
    parser.add_argument("--output", required=True, help="Output python file path")
    args = parser.parse_args()

    components = _split_csv(args.components)
    phases = _split_csv(args.phases)

    if not components:
        raise ValueError("At least one component is required.")
    if not phases:
        raise ValueError("At least one phase is required.")

    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "assets" / "stubs" / "generic_property_package_stub.py.j2"
    template = template_path.read_text(encoding="utf-8")

    rendered = (
        template.replace("{{PACKAGE_NAME}}", args.name)
        .replace("{{COMPONENT_BLOCK}}", _component_block(components))
        .replace("{{PHASE_BLOCK}}", _phase_block(phases))
        .replace("{{STATE_DEFINITION}}", args.state_def)
        .replace(
            "{{EQUILIBRIUM_BLOCK}}",
            _equilibrium_block(phases, args.include_equilibrium),
        )
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")

    print(f"Wrote generic scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
