#!/usr/bin/env python
"""Create or update a parameter-ledger CSV for property-package development."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


FIELDNAMES = [
    "parameter_name",
    "value",
    "units",
    "applies_to",
    "source",
    "retrieved_on",
    "confidence",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Path to output CSV ledger.")
    parser.add_argument(
        "--from-json",
        help="Optional JSON file containing a list of parameter records.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing ledger instead of rewriting.",
    )
    return parser.parse_args()


def load_records(path: Path | None) -> Iterable[dict[str, str]]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("JSON root must be a list of records.")
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each JSON record must be an object.")
        yield {k: str(item.get(k, "")) for k in FIELDNAMES}


def main() -> int:
    args = parse_args()

    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    json_path = Path(args.from_json).resolve() if args.from_json else None
    records = list(load_records(json_path))

    mode = "a" if args.append and out.exists() else "w"
    needs_header = mode == "w" or (mode == "a" and out.stat().st_size == 0)

    with out.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        if needs_header:
            writer.writeheader()
        for row in records:
            writer.writerow(row)

    print(f"Ledger written: {out}")
    if not records:
        print("No rows provided. Header-only ledger created or preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
