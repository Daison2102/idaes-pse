#!/usr/bin/env python
"""Scaffold class-based IDAES property package files from templates."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


CLASS_TEMPLATES = {
    "parameter": "parameter_block_template.py",
    "state-methods": "state_block_methods_template.py",
    "state-data": "state_block_data_template.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest-dir",
        required=True,
        help="Destination directory for generated files.",
    )
    parser.add_argument(
        "--parts",
        nargs="+",
        choices=sorted(CLASS_TEMPLATES.keys()),
        default=sorted(CLASS_TEMPLATES.keys()),
        help="Class-based template parts to generate.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    script_dir = Path(__file__).resolve().parent
    src_dir = script_dir.parent / "templates" / "class_based"
    dst_dir = Path(args.dest_dir).resolve()
    dst_dir.mkdir(parents=True, exist_ok=True)

    for part in args.parts:
        src = src_dir / CLASS_TEMPLATES[part]
        dst = dst_dir / CLASS_TEMPLATES[part]

        if not src.exists():
            raise FileNotFoundError(f"Template not found: {src}")

        if dst.exists() and not args.force:
            raise FileExistsError(f"Output exists: {dst}. Use --force to overwrite.")

        shutil.copyfile(src, dst)
        print(f"Wrote class-based scaffold: {dst}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
