#!/usr/bin/env python3
"""Generate a checklist markdown file for generic or custom package design."""

from __future__ import annotations

import argparse
from pathlib import Path


GENERIC_ITEMS = [
    "Approach rationale documented as Generic.",
    "Components and phases defined with required methods.",
    "State definition and bounds documented.",
    "Reference state defined.",
    "Phase equilibrium configuration documented where needed.",
    "Initialization path documented.",
    "Scaling plan documented.",
    "Validation matrix documented.",
    "Source traceability table complete.",
]

CUSTOM_ITEMS = [
    "Approach rationale documented as Custom.",
    "Parameter block responsibilities documented.",
    "StateBlock methods class responsibilities documented.",
    "StateBlockData required methods documented.",
    "State variable definitions documented.",
    "Initialization and release-state logic documented.",
    "Scaling strategy documented.",
    "Validation matrix documented.",
    "Source traceability table complete.",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approach", required=True, choices=["generic", "custom"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    items = GENERIC_ITEMS if args.approach == "generic" else CUSTOM_ITEMS

    lines = [f"# {args.approach.capitalize()} Property Package Checklist", ""]
    lines.extend([f"- [ ] {item}" for item in items])
    lines.append("")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote checklist: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
