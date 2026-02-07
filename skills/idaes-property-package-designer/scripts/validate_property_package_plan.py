#!/usr/bin/env python3
"""Validate that a property-package design plan is decision-complete."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


COMMON_REQUIRED = [
    "approach",
    "state",
    "component",
    "phase",
    "initialization",
    "scaling",
    "validation",
    "assumption",
]

GENERIC_REQUIRED = [
    "configuration",
    "state_definition",
    "state_bounds",
    "pressure_ref",
    "temperature_ref",
]

CUSTOM_REQUIRED = [
    "physicalparameterblock",
    "stateblockdata",
    "initialize",
    "release_state",
    "define_metadata",
]



def _missing_terms(text: str, required_terms: list[str]) -> list[str]:
    return [term for term in required_terms if term not in text]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-file", required=True)
    parser.add_argument("--approach", required=True, choices=["generic", "custom"])
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    path = Path(args.plan_file)
    text = path.read_text(encoding="utf-8").lower()

    missing = _missing_terms(text, COMMON_REQUIRED)
    if args.approach == "generic":
        missing.extend(_missing_terms(text, GENERIC_REQUIRED))
    else:
        missing.extend(_missing_terms(text, CUSTOM_REQUIRED))

    if args.strict and "default" not in text:
        missing.append("default")

    if missing:
        unique_missing = sorted(set(missing))
        print("Plan validation failed. Missing required terms:")
        for term in unique_missing:
            print(f"- {term}")
        return 1

    print("Plan validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
