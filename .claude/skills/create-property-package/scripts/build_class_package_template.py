#!/usr/bin/env python3
"""Generate a class-based IDAES property package template from a JSON spec.

Usage:
    python build_class_package_template.py --spec spec.json --output my_class_props.py
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


def _title_slug(text: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", text)
    cleaned = [p for p in parts if p]
    if not cleaned:
        return "Custom"
    return "".join(p[0].upper() + p[1:] for p in cleaned)


def _normalize_components(raw_components: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(raw_components, list):
        return out
    for item in raw_components:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            cid = item.get("id") or item.get("name")
            if cid:
                out.append(str(cid))
    return out


def _normalize_phases(raw_phases: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(raw_phases, list):
        return out
    for item in raw_phases:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            pid = item.get("id") or item.get("name")
            if pid:
                out.append(str(pid))
    return out


def _state_definition(spec: Dict[str, Any]) -> str:
    sd = str(spec.get("state_definition", "FTPx"))
    return sd if sd in {"FTPx", "FpcTP", "FcTP", "FPhx", "FcPh"} else "FTPx"


def _state_var_code(state_def: str) -> List[str]:
    lines: List[str] = []
    if state_def == "FTPx":
        lines.extend(
            [
                "        self.flow_mol = Var(initialize=1.0, bounds=(0, None), units=pyunits.mol/pyunits.s)",
                "        self.mole_frac_comp = Var(self.params.component_list, initialize=0.5, bounds=(0, 1), units=pyunits.dimensionless)",
                "        self.temperature = Var(initialize=298.15, bounds=(200, 2000), units=pyunits.K)",
                "        self.pressure = Var(initialize=101325, bounds=(1e3, 1e8), units=pyunits.Pa)",
                "",
                "        self.sum_mole_frac = Constraint(expr=sum(self.mole_frac_comp[j] for j in self.params.component_list) == 1)",
            ]
        )
    elif state_def == "FpcTP":
        lines.extend(
            [
                "        self.flow_mol_phase_comp = Var(",
                "            self.params.phase_list, self.params.component_list,",
                "            initialize=0.1, bounds=(0, None), units=pyunits.mol/pyunits.s",
                "        )",
                "        self.temperature = Var(initialize=298.15, bounds=(200, 2000), units=pyunits.K)",
                "        self.pressure = Var(initialize=101325, bounds=(1e3, 1e8), units=pyunits.Pa)",
            ]
        )
    elif state_def == "FcTP":
        lines.extend(
            [
                "        self.flow_mol_comp = Var(self.params.component_list, initialize=0.1, bounds=(0, None), units=pyunits.mol/pyunits.s)",
                "        self.temperature = Var(initialize=298.15, bounds=(200, 2000), units=pyunits.K)",
                "        self.pressure = Var(initialize=101325, bounds=(1e3, 1e8), units=pyunits.Pa)",
            ]
        )
    elif state_def == "FPhx":
        lines.extend(
            [
                "        self.flow_mol = Var(initialize=1.0, bounds=(0, None), units=pyunits.mol/pyunits.s)",
                "        self.mole_frac_comp = Var(self.params.component_list, initialize=0.5, bounds=(0, 1), units=pyunits.dimensionless)",
                "        self.enth_mol = Var(initialize=0.0, units=pyunits.J/pyunits.mol)",
                "        self.pressure = Var(initialize=101325, bounds=(1e3, 1e8), units=pyunits.Pa)",
                "",
                "        self.sum_mole_frac = Constraint(expr=sum(self.mole_frac_comp[j] for j in self.params.component_list) == 1)",
            ]
        )
    else:  # FcPh
        lines.extend(
            [
                "        self.flow_mol_comp = Var(self.params.component_list, initialize=0.1, bounds=(0, None), units=pyunits.mol/pyunits.s)",
                "        self.enth_mol = Var(initialize=0.0, units=pyunits.J/pyunits.mol)",
                "        self.pressure = Var(initialize=101325, bounds=(1e3, 1e8), units=pyunits.Pa)",
            ]
        )
    return lines


def _render(spec: Dict[str, Any]) -> str:
    name = _title_slug(str(spec.get("name", "CustomProperty")))
    state_def = _state_definition(spec)
    components = _normalize_components(spec.get("components", []))
    phases = _normalize_phases(spec.get("phases", []))
    required_props = spec.get("required_properties", [])
    if not isinstance(required_props, list):
        required_props = []

    if not components:
        components = ["component_1", "component_2"]
    if not phases:
        phases = ["Vap"]

    pb_name = f"{name}ParameterBlock"
    pb_data = f"{name}ParameterBlockData"
    sb_name = f"{name}StateBlock"
    sb_data = f"{name}StateBlockData"
    sb_methods = f"_{name}StateBlock"

    lines: List[str] = []
    lines.append('"""')
    lines.append(f"Class-based property package template for: {name}")
    lines.append("Generated by create-property-package skill scaffolder.")
    lines.append('"""')
    lines.append("")
    lines.append("from pyomo.environ import Constraint, Param, Set, Var")
    lines.append("from pyomo.environ import units as pyunits")
    lines.append("from idaes.core import (")
    lines.append("    Component,")
    lines.append("    EnergyBalanceType,")
    lines.append("    LiquidPhase,")
    lines.append("    MaterialBalanceType,")
    lines.append("    MaterialFlowBasis,")
    lines.append("    PhysicalParameterBlock,")
    lines.append("    SolidPhase,")
    lines.append("    StateBlock,")
    lines.append("    StateBlockData,")
    lines.append("    VaporPhase,")
    lines.append("    declare_process_block_class,")
    lines.append(")")
    lines.append("from idaes.core.util.initialization import fix_state_vars, revert_state_vars")
    lines.append("import idaes.logger as idaeslog")
    lines.append("")
    lines.append("_log = idaeslog.getLogger(__name__)")
    lines.append("")
    lines.append("")
    lines.append(f"@declare_process_block_class(\"{pb_name}\")")
    lines.append(f"class {pb_data}(PhysicalParameterBlock):")
    lines.append("    \"\"\"Parameter block for custom class-based property package.\"\"\"")
    lines.append("")
    lines.append("    def build(self):")
    lines.append(f"        super({pb_data}, self).build()")
    lines.append(f"        self._state_block_class = {sb_name}")
    lines.append("")
    for ph in phases:
        pid = ph.lower()
        if "liq" in pid:
            ptype = "LiquidPhase"
        elif "sol" in pid:
            ptype = "SolidPhase"
        else:
            ptype = "VaporPhase"
        lines.append(f"        self.{ph} = {ptype}()")
    for comp in components:
        lines.append(f"        self.{comp} = Component()")
    lines.append("")
    lines.append("        self.pressure_ref = Param(initialize=101325, mutable=True, units=pyunits.Pa)")
    lines.append("        self.temperature_ref = Param(initialize=298.15, mutable=True, units=pyunits.K)")
    lines.append("        self.mw_comp = Param(")
    lines.append("            self.component_list,")
    lines.append("            initialize={k: 0.0 for k in self.component_list},")
    lines.append("            mutable=True,")
    lines.append("            units=pyunits.kg/pyunits.mol,")
    lines.append("        )")
    lines.append("")
    lines.append("    @classmethod")
    lines.append("    def define_metadata(cls, obj):")
    lines.append("        obj.add_properties({")

    always_props = ["temperature", "pressure"]
    if state_def in {"FTPx", "FPhx"}:
        always_props.extend(["flow_mol", "mole_frac_comp"])
    if state_def in {"FcTP", "FcPh"}:
        always_props.append("flow_mol_comp")
    if state_def == "FpcTP":
        always_props.append("flow_mol_phase_comp")
    if state_def in {"FPhx", "FcPh"}:
        always_props.append("enth_mol")

    for p in always_props:
        lines.append(f"            \"{p}\": {{\"method\": None}},")

    for p in required_props:
        if p in always_props:
            continue
        p_clean = str(p)
        method_name = f"_build_{p_clean}"
        lines.append(f"            \"{p_clean}\": {{\"method\": \"{method_name}\"}},")

    lines.append("        })")
    lines.append("        obj.add_default_units({")
    lines.append("            \"time\": pyunits.s,")
    lines.append("            \"length\": pyunits.m,")
    lines.append("            \"mass\": pyunits.kg,")
    lines.append("            \"amount\": pyunits.mol,")
    lines.append("            \"temperature\": pyunits.K,")
    lines.append("        })")
    lines.append("")
    lines.append("")
    lines.append(f"class {sb_methods}(StateBlock):")
    lines.append("    \"\"\"Methods applied to an indexed set of state blocks.\"\"\"")
    lines.append("")
    lines.append("    def initialize(")
    lines.append("        blk,")
    lines.append("        state_args=None,")
    lines.append("        state_vars_fixed=False,")
    lines.append("        hold_state=False,")
    lines.append("        outlvl=idaeslog.NOTSET,")
    lines.append("        solver=None,")
    lines.append("        optarg=None,")
    lines.append("    ):")
    lines.append("        \"\"\"Initialization routine template.\"\"\"")
    lines.append("        if state_args is None:")
    lines.append("            state_args = {}")
    lines.append("        flags = None")
    lines.append("        if not state_vars_fixed:")
    lines.append("            flags = fix_state_vars(blk, state_args)")
    lines.append("")
    lines.append("        # TODO: Add staged initialization and solve logic.")
    lines.append("")
    lines.append("        if hold_state:")
    lines.append("            return flags")
    lines.append("        if flags is not None:")
    lines.append("            blk.release_state(flags)")
    lines.append("        return None")
    lines.append("")
    lines.append("    def release_state(blk, flags, outlvl=idaeslog.NOTSET):")
    lines.append("        \"\"\"Release states fixed during initialize.\"\"\"")
    lines.append("        revert_state_vars(blk, flags)")
    lines.append("")
    lines.append("")
    lines.append(f"@declare_process_block_class(\"{sb_name}\", block_class={sb_methods})")
    lines.append(f"class {sb_data}(StateBlockData):")
    lines.append("    \"\"\"State block data class template.\"\"\"")
    lines.append("")
    lines.append("    def build(self):")
    lines.append(f"        super({sb_data}, self).build()")
    lines.append("")
    lines.extend(_state_var_code(state_def))
    lines.append("")
    lines.append("    # --- Required IDAES state-block contract methods ---")
    lines.append("    def get_material_flow_terms(self, p, j):")
    if state_def == "FpcTP":
        lines.append("        return self.flow_mol_phase_comp[p, j]")
    elif state_def in {"FcTP", "FcPh"}:
        lines.append("        return self.flow_mol_comp[j]")
    else:
        lines.append("        return self.flow_mol * self.mole_frac_comp[j]")
    lines.append("")
    lines.append("    def get_enthalpy_flow_terms(self, p):")
    if state_def in {"FPhx", "FcPh"}:
        if state_def == "FcPh":
            lines.append("        return sum(self.flow_mol_comp[j] for j in self.params.component_list) * self.enth_mol")
        else:
            lines.append("        return self.flow_mol * self.enth_mol")
    else:
        lines.append("        raise NotImplementedError(\"TODO: Implement phase enthalpy flow terms.\")")
    lines.append("")
    lines.append("    def get_material_density_terms(self, p, j):")
    lines.append("        raise NotImplementedError(\"TODO: Implement material density terms.\")")
    lines.append("")
    lines.append("    def get_energy_density_terms(self, p):")
    lines.append("        raise NotImplementedError(\"TODO: Implement energy density terms.\")")
    lines.append("")
    lines.append("    def default_material_balance_type(self):")
    lines.append("        return MaterialBalanceType.componentPhase")
    lines.append("")
    lines.append("    def default_energy_balance_type(self):")
    lines.append("        return EnergyBalanceType.enthalpyTotal")
    lines.append("")
    lines.append("    def get_material_flow_basis(self):")
    lines.append("        return MaterialFlowBasis.molar")
    lines.append("")
    lines.append("    def define_state_vars(self):")
    if state_def == "FTPx":
        lines.append("        return {\"flow_mol\": self.flow_mol, \"mole_frac_comp\": self.mole_frac_comp, \"temperature\": self.temperature, \"pressure\": self.pressure}")
    elif state_def == "FpcTP":
        lines.append("        return {\"flow_mol_phase_comp\": self.flow_mol_phase_comp, \"temperature\": self.temperature, \"pressure\": self.pressure}")
    elif state_def == "FcTP":
        lines.append("        return {\"flow_mol_comp\": self.flow_mol_comp, \"temperature\": self.temperature, \"pressure\": self.pressure}")
    elif state_def == "FPhx":
        lines.append("        return {\"flow_mol\": self.flow_mol, \"mole_frac_comp\": self.mole_frac_comp, \"enth_mol\": self.enth_mol, \"pressure\": self.pressure}")
    else:
        lines.append("        return {\"flow_mol_comp\": self.flow_mol_comp, \"enth_mol\": self.enth_mol, \"pressure\": self.pressure}")
    lines.append("")
    lines.append("    def define_display_vars(self):")
    lines.append("        # TODO: customize report-facing labels")
    lines.append("        return self.define_state_vars()")
    lines.append("")

    for p in required_props:
        if p in always_props:
            continue
        p_clean = str(p)
        lines.append(f"    def _build_{p_clean}(self):")
        lines.append(f"        raise NotImplementedError(\"TODO: Implement property method for '{p_clean}'.\")")
        lines.append("")

    lines.append("    def model_check(self):")
    lines.append("        # TODO: Add bounds/sanity checks")
    lines.append("        return None")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Path to normalized JSON spec")
    parser.add_argument("--output", required=True, help="Output Python module path")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    out_path = Path(args.output)

    with spec_path.open("r", encoding="utf-8") as f:
        spec = json.load(f)

    text = _render(spec)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
