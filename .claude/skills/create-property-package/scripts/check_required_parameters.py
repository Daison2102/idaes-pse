#!/usr/bin/env python3
"""Check required property coverage and parameter completeness from a spec file.

Usage:
    python check_required_parameters.py --spec spec.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


METHOD_REQUIREMENTS: Dict[str, Set[str]] = {
    "NIST": {"cp_mol_ig_comp_coeff", "enth_mol_form_vap_comp_ref", "entr_mol_form_vap_comp_ref"},
    "RPP4": {"cp_mol_ig_comp_coeff", "enth_mol_form_vap_comp_ref", "entr_mol_form_vap_comp_ref"},
    "RPP5": {"cp_mol_ig_comp_coeff", "enth_mol_form_vap_comp_ref", "entr_mol_form_vap_comp_ref"},
    "Perrys": {
        "dens_mol_liq_comp_coeff",
        "cp_mol_liq_comp_coeff",
        "enth_mol_form_liq_comp_ref",
        "entr_mol_form_liq_comp_ref",
    },
    "ConstantProperties": set(),
    "ChapmanEnskogLennardJones": {"lennard_jones_sigma", "lennard_jones_epsilon_reduced"},
    "Eucken": {"f_int_eucken"},
}

CORE_COMPONENT_KEYS = {"mw", "pressure_crit", "temperature_crit"}
CUBIC_EXTRA_KEYS = {"omega"}

MIN_CLASS_CONTRACT = {
    "get_material_flow_terms",
    "get_enthalpy_flow_terms",
    "get_material_density_terms",
    "get_energy_density_terms",
    "default_material_balance_type",
    "default_energy_balance_type",
    "get_material_flow_basis",
    "define_state_vars",
    "define_display_vars",
    "initialize",
    "release_state",
}

MIN_EQ_REQUIRED = {"phase_equilibrium_form", "phases_in_equilibrium", "phase_equilibrium_state"}

COMPREHENSIVE_ADDITIONS = {
    "enth_mol",
    "enth_mol_phase",
    "entr_mol",
    "entr_mol_phase",
    "dens_mol",
    "dens_mol_phase",
    "mw",
    "mw_phase",
    "pressure_sat_comp",
    "temperature_bubble",
    "temperature_dew",
    "pressure_bubble",
    "pressure_dew",
}


def _component_entries(raw_components: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(raw_components, list):
        return out
    for c in raw_components:
        if isinstance(c, str):
            out.append({"id": c, "parameter_data": {}, "methods": []})
        elif isinstance(c, dict):
            cid = c.get("id") or c.get("name") or "component"
            out.append(
                {
                    "id": str(cid),
                    "parameter_data": c.get("parameter_data", {})
                    if isinstance(c.get("parameter_data", {}), dict)
                    else {},
                    "methods": _collect_methods(c),
                }
            )
    return out


def _collect_methods(comp: Dict[str, Any]) -> List[str]:
    methods: List[str] = []

    for key in ("methods", "selected_methods"):
        vals = comp.get(key, [])
        if isinstance(vals, list):
            for m in vals:
                if isinstance(m, str):
                    methods.append(m)

    method_map = comp.get("method_map", {})
    if isinstance(method_map, dict):
        for m in method_map.values():
            if isinstance(m, str):
                methods.append(m)

    return sorted(set(methods))


def _phase_ids(spec: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    phases = spec.get("phases", [])
    if isinstance(phases, list):
        for p in phases:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict):
                pid = p.get("id") or p.get("name")
                if pid:
                    out.append(str(pid))
    return out


def _eos_map(spec: Dict[str, Any], phase_ids: List[str]) -> Dict[str, str]:
    eos = spec.get("eos", {})
    phase_to_eos = eos.get("phase_to_eos", {}) if isinstance(eos, dict) else {}
    out: Dict[str, str] = {}
    for ph in phase_ids:
        val = str(phase_to_eos.get(ph, "IDEAL")).upper()
        if val not in {"IDEAL", "PR", "SRK"}:
            val = "IDEAL"
        out[ph] = val
    return out


def _state_vars_for(state_def: str) -> Set[str]:
    if state_def == "FTPx":
        return {"flow_mol", "temperature", "pressure", "mole_frac_comp"}
    if state_def == "FpcTP":
        return {"flow_mol_phase_comp", "temperature", "pressure"}
    if state_def == "FcTP":
        return {"flow_mol_comp", "temperature", "pressure"}
    if state_def == "FPhx":
        return {"flow_mol", "temperature", "pressure", "mole_frac_comp", "enth_mol"}
    if state_def == "FcPh":
        return {"flow_mol_comp", "temperature", "pressure", "enth_mol"}
    return {"flow_mol", "temperature", "pressure", "mole_frac_comp"}


def _required_properties(spec: Dict[str, Any]) -> Tuple[Set[str], List[Tuple[str, str, str]]]:
    coverage_mode = str(spec.get("coverage_mode", "minimum")).lower()
    approach = str(spec.get("approach", "generic")).lower()
    state_def = str(spec.get("state_definition", "FTPx"))

    requested = set()
    req = spec.get("required_properties", [])
    if isinstance(req, list):
        requested = {str(x) for x in req}

    provided = set()
    prv = spec.get("provided_properties", [])
    if isinstance(prv, list):
        provided = {str(x) for x in prv}

    auto_covered: Set[str] = set(_state_vars_for(state_def))
    required: Set[str] = set(auto_covered)
    required.update({"temperature", "pressure"})
    auto_covered.update({"temperature", "pressure"})

    eq = spec.get("equilibrium", {})
    eq_required = bool(eq.get("required", False)) if isinstance(eq, dict) else False
    auto_obligations: Set[str] = set()
    if eq_required:
        required.update(MIN_EQ_REQUIRED)
        auto_obligations.update(MIN_EQ_REQUIRED)

    if approach == "class":
        required.update(MIN_CLASS_CONTRACT)
        auto_obligations.update(MIN_CLASS_CONTRACT)

    if coverage_mode == "comprehensive":
        required.update(COMPREHENSIVE_ADDITIONS)
        auto_obligations.update(COMPREHENSIVE_ADDITIONS)

    rows: List[Tuple[str, str, str]] = []
    for item in sorted(required):
        if item in provided:
            status = "covered"
        elif item in auto_covered:
            status = "covered"
        elif item in auto_obligations:
            status = "custom-implementation-needed"
        elif item in requested:
            status = "custom-implementation-needed"
        else:
            status = "missing"
        rows.append((item, "minimum" if item not in COMPREHENSIVE_ADDITIONS else "comprehensive", status))

    return required, rows


def _parameter_gaps(spec: Dict[str, Any]) -> Tuple[List[str], Dict[str, List[str]], List[str]]:
    components = _component_entries(spec.get("components", []))
    phase_ids = _phase_ids(spec)
    eos_map = _eos_map(spec, phase_ids)
    package_data = spec.get("parameter_data", {})
    if not isinstance(package_data, dict):
        package_data = {}

    global_gaps: List[str] = []
    component_gaps: Dict[str, List[str]] = {}
    package_gaps: List[str] = []

    uses_cubic = any(v in {"PR", "SRK"} for v in eos_map.values())

    for comp in components:
        cid = comp["id"]
        pdata = comp.get("parameter_data", {})
        if not isinstance(pdata, dict):
            pdata = {}
        missing: Set[str] = set()

        missing.update(k for k in CORE_COMPONENT_KEYS if k not in pdata)
        if uses_cubic:
            missing.update(k for k in CUBIC_EXTRA_KEYS if k not in pdata)

        for m in comp.get("methods", []):
            missing.update(k for k in METHOD_REQUIREMENTS.get(m, set()) if k not in pdata)

        component_gaps[cid] = sorted(missing)

    if uses_cubic:
        cubic_labels = sorted({v for v in eos_map.values() if v in {"PR", "SRK"}})
        for lbl in cubic_labels:
            key = f"{lbl}_kappa"
            if key not in package_data:
                package_gaps.append(key)

    for cid, missing in component_gaps.items():
        if missing:
            global_gaps.append(f"{cid}: {', '.join(missing)}")

    return global_gaps, component_gaps, package_gaps


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Path to normalized spec JSON")
    parser.add_argument("--report", help="Optional JSON report output path")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 when minimum gates are not satisfied",
    )
    args = parser.parse_args()

    with Path(args.spec).open("r", encoding="utf-8") as f:
        spec = json.load(f)

    _, coverage_rows = _required_properties(spec)
    global_gaps, component_gaps, package_gaps = _parameter_gaps(spec)

    print("== Required Properties Coverage ==")
    for item, mode, status in coverage_rows:
        print(f"- {item}: mode={mode}, status={status}")

    print("\n== Parameter Gaps by Component ==")
    for comp, gaps in component_gaps.items():
        if gaps:
            print(f"- {comp}: MISSING -> {', '.join(gaps)}")
        else:
            print(f"- {comp}: OK")

    print("\n== Package-Level Parameter Gaps ==")
    if package_gaps:
        for g in package_gaps:
            print(f"- MISSING -> {g}")
    else:
        print("- OK")

    report = {
        "required_property_coverage": [
            {"item": i, "mode": m, "status": s} for i, m, s in coverage_rows
        ],
        "parameter_gaps_by_component": component_gaps,
        "package_parameter_gaps": package_gaps,
    }

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nWrote report: {out}")

    strict_fail = False
    if args.strict:
        strict_fail = any(status == "missing" for _, mode, status in coverage_rows if mode == "minimum")
        strict_fail = strict_fail or bool(global_gaps) or bool(package_gaps)

    if strict_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
