# Skill Plan v2: `create-property-package`

## Purpose

Create a Codex/Claude CLI skill that provides a systematic, reusable workflow for building IDAES thermophysical property packages using:
1. Generic framework (`GenericParameterBlock` + configuration dictionary).
2. Class-based framework (`PhysicalParameterBlock` + `StateBlock` + `StateBlockData`).

The skill must choose the right approach, enforce required-property coverage gates, and drive creation, validation, and provenance reporting.

## Skill Location

Repo-local path:

```text
.claude/skills/create-property-package/
```

## Implemented Skill Structure

```text
.claude/skills/create-property-package/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   |-- workflow-overview.md
|   |-- approach-selection.md
|   |-- required-properties-catalog.md
|   |-- generic-framework-playbook.md
|   |-- class-based-playbook.md
|   |-- state-vars-and-required-contracts.md
|   |-- property-method-selection-matrix.md
|   |-- parameter-requirements-by-method.md
|   |-- initialization-and-scaling.md
|   |-- validation-and-testing.md
|   |-- source-priority-and-citation-rules.md
|   `-- examples-map.md
`-- scripts/
    |-- build_generic_config_template.py
    |-- build_class_package_template.py
    |-- generate_property_package_tests.py
    `-- check_required_parameters.py
```

## Core Workflow Stages

1. Normalize inputs from user prompt into a strict spec.
2. Select coverage mode (`minimum` or `comprehensive`).
3. Build required-properties coverage table and enforce gate.
4. Select approach (Generic vs Class-based).
5. Mine canonical patterns from IDAES code/docs.
6. Map methods to required parameters and identify gaps.
7. Generate branch-specific scaffold.
8. Add initialization and scaling strategy.
9. Generate and run validation tests.
10. Deliver coverage and provenance report.

## Source Priority Policy

1. Indexed IDAES codebase MCP (repobase/codebase).
2. Indexed IDAES docs/examples MCP (grounded-docs).
3. External sources only if needed.
4. Web lookup specifically for missing parameter placeholders.

## Required Properties Gate

### Minimum Required

Mandatory baseline includes:
1. State-variable set from selected state definition.
2. `temperature` and `pressure`.
3. Composition representation.
4. `phase_frac` for multiphase systems.
5. Flow term representation by phase/component.
6. Class-based contract methods:
1. `get_material_flow_terms`
2. `get_enthalpy_flow_terms`
3. `get_material_density_terms`
4. `get_energy_density_terms`
5. `default_material_balance_type`
6. `default_energy_balance_type`
7. `get_material_flow_basis`
8. `define_state_vars`
9. `define_display_vars`
10. `initialize`
11. `release_state`
7. Equilibrium-required subset when equilibrium is requested:
1. `phase_equilibrium_form`
2. `phases_in_equilibrium`
3. `phase_equilibrium_state`

### Comprehensive Required

Includes all minimum items plus:
1. Mixture thermodynamic properties (`enth_mol`, `entr_mol`, `dens_mol`, `mw` and phase forms).
2. Pure-component thermo support (`cp_mol_ig_comp`, `enth_mol_ig_comp`, `entr_mol_ig_comp`, liquid analogs).
3. Phase-transition properties (`pressure_sat_comp`, bubble/dew temperature/pressure).
4. EOS interaction parameters for cubic EOS (`PR_kappa`/`SRK_kappa` style maps).
5. Optional transport properties and required transport parameters.
6. `model_check` and robust scaling support.

## Approach Selection Rules

1. Default to Generic framework.
2. Force Class-based if required behavior is unsupported in Generic method libraries.
3. Honor user override when feasible.
4. If user override is infeasible, report blocker and switch with rationale.

## Output Expectations

For each skill run, produce:
1. Approach decision and reason.
2. Coverage mode and coverage status table.
3. Method-to-parameter mapping.
4. Generated file plan/code scaffold.
5. Initialization/scaling plan.
6. Validation test plan/results.
7. Parameter provenance report.

## Notes on Local Legacy References

Local files in `custom_example_pro_pack` may be used as structural inspiration only. Official IDAES repository code and documentation remain canonical.

For Generic style when local legacy examples are available, prioritize newer methanol-style dictionary assembly patterns.
