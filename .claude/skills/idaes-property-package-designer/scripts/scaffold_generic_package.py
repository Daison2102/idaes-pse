#!/usr/bin/env python
"""Scaffold a generic IDAES property package file from a template."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


TEMPLATES = {
    "minimal-single-phase": "config_minimal_single_phase.py",
    "ideal-vle-ftpx": "config_ideal_vle_ftpx.py",
    "cubic-vle": "config_cubic_vle.py",
    "builder-get-prop": "config_builder_get_prop_style.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template",
        choices=sorted(TEMPLATES.keys()),
        default="ideal-vle-ftpx",
        help="Template key to use.",
    )
    parser.add_argument("--output", required=True, help="Output Python file path.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    script_dir = Path(__file__).resolve().parent
    src = script_dir.parent / "templates" / "generic" / TEMPLATES[args.template]
    dst = Path(args.output).resolve()

    if not src.exists():
        raise FileNotFoundError(f"Template not found: {src}")

    if dst.exists() and not args.force:
        raise FileExistsError(f"Output exists: {dst}. Use --force to overwrite.")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    print(f"Wrote generic scaffold: {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
