---
name: create-property-package
description: Design and implement IDAES thermophysical property packages using either the Generic Property Package framework or fully custom class-based definitions. Use this when users ask to build, refactor, validate, or template property packages, including method selection, parameter requirements, initialization/scaling, and tests.
metadata:
  short-description: Build IDAES property packages
---

# Create Property Package

Use this skill when the user needs to create or update an IDAES property package.

## Scope

This skill supports both official approaches:
1. Generic framework: `GenericParameterBlock` with a configuration dictionary.
2. Class-based framework: `PhysicalParameterBlock` + `StateBlock` + `StateBlockData`.

This skill is workflow-first: it does not jump directly to code. It enforces feasibility, property coverage, and validation requirements before scaffolding code.

## Source Priority (mandatory)

Always gather information in this order:
1. Indexed IDAES codebase (codebase MCP / repobase).
2. Indexed IDAES docs and examples (grounded-docs MCP for `idaes` and `idaes-examples`).
3. External sources only when required info is missing from 1-2.
4. For parameter placeholders/missing values, perform web lookup from reputable sources.

Follow detailed rules in `references/source-priority-and-citation-rules.md`.

## Required User Inputs

The user prompt should provide:
1. `components` list.
2. `phases` list.
3. `state_variables` (`FTPx`, `FpcTP`, `FcTP`, `FPhx`, `FcPh`).
4. `required_properties`.
5. `equilibrium_required` and phase pairs.
6. `equation_of_state` per phase (for example `Ideal`, `PR`, `SRK`).

If critical fields are missing, ask only for missing high-impact fields.

## Workflow

### Stage 0: Normalize Inputs

Build a structured spec with this shape:

```yaml
name: string
approach: auto|generic|class
coverage_mode: minimum|comprehensive
components:
  - id: string
    elemental_composition: {element: number}
phases:
  - id: string
    type: LiquidPhase|VaporPhase|SolidPhase
state_definition: FTPx|FpcTP|FcTP|FPhx|FcPh
required_properties: [string]
equilibrium:
  required: bool
  pairs: [[phase_1, phase_2]]
  form: fugacity|log_fugacity
eos:
  phase_to_eos:
    Liq: Ideal|PR|SRK
    Vap: Ideal|PR|SRK
transport:
  include: bool
```

### Stage 1: Coverage Mode Gate

Select coverage mode:
1. `minimum`: smallest viable package for unit-model compatibility.
2. `comprehensive`: production-ready package with wider property surface.

Use `references/required-properties-catalog.md` and generate a coverage table with each property marked as:
1. `covered`
2. `missing`
3. `custom-implementation-needed`

Never scaffold code while minimum-required properties are unresolved.

### Stage 2: Approach Selection

Use `references/approach-selection.md`.

Default to Generic unless unsupported requirements force class-based implementation.

### Stage 3: Canonical Pattern Mining

Before creating code, mine canonical patterns from IDAES repository/docs:
1. Generic examples under `idaes/models/properties/modular_properties/examples/`.
2. Class-based examples such as `idaes/models/properties/examples/saponification_thermo.py`.
3. Associated tests in the matching `tests/` folders.

Use `references/examples-map.md`.

### Stage 4: Method and Parameter Mapping

1. Select property methods for each required property.
2. Identify required parameter keys.
3. Build a parameter completeness matrix by component/phase/package-wide values.

Use:
1. `references/property-method-selection-matrix.md`
2. `references/parameter-requirements-by-method.md`

### Stage 5A: Generic Framework Branch

Follow `references/generic-framework-playbook.md`.

Primary output is a clean configuration dictionary and optional helper factory (`get_prop`) when configurability is needed.

Use script:
`python .claude/skills/create-property-package/scripts/build_generic_config_template.py --spec spec.json --output my_props.py`

### Stage 5B: Class-Based Branch

Follow `references/class-based-playbook.md` and `references/state-vars-and-required-contracts.md`.

Primary output is skeleton classes for:
1. Parameter block (`PhysicalParameterBlock`).
2. State block methods (`StateBlock`) with `initialize` and `release_state`.
3. State block data (`StateBlockData`) including required contracts and build-on-demand properties.

Use script:
`python .claude/skills/create-property-package/scripts/build_class_package_template.py --spec spec.json --output my_props.py`

### Stage 6: Initialization and Scaling

Apply staged initialization and explicit scaling-factor strategy.

Use `references/initialization-and-scaling.md`.

### Stage 7: Validation and Tests

Generate test scaffold and run checks:
1. Construction checks.
2. Unit consistency.
3. Degrees of freedom.
4. Initialization and solve.
5. Property sanity checks.
6. Optional unit-model integration check.

Use `references/validation-and-testing.md`.

Use script:
`python .claude/skills/create-property-package/scripts/generate_property_package_tests.py --spec spec.json --approach generic --output test_my_props.py`

### Stage 8: Delivery Package

Deliver:
1. Final package code.
2. Validation tests.
3. Coverage report.
4. Parameter provenance report with source references.

## Required-Properties Policy

Use the full catalog in `references/required-properties-catalog.md`.

Hard rules:
1. Minimum mode is default.
2. If equilibrium is requested, equilibrium subset becomes mandatory even in minimum mode.
3. Comprehensive mode must include all comprehensive entries or provide explicit exclusions with rationale.

## Legacy/Reference Handling

If local legacy examples are available, use them as structural inspiration only, not canonical authority.

Prioritize modern IDAES conventions and import paths:
1. `idaes.models.properties.modular_properties...` (preferred)
2. Do not use legacy `idaes.generic_models...` imports in new package outputs.

## Scripts and References to Load

1. Always read:
1. `references/workflow-overview.md`
2. `references/required-properties-catalog.md`
3. `references/source-priority-and-citation-rules.md`
2. Read conditionally:
1. Generic branch: `references/generic-framework-playbook.md`
2. Class branch: `references/class-based-playbook.md` + `references/state-vars-and-required-contracts.md`
3. Equilibrium-heavy work: `references/property-method-selection-matrix.md`
4. Validation phase: `references/validation-and-testing.md`

## Output Contract

For every run, produce a concise, implementation-ready result containing:
1. Approach decision and rationale.
2. Coverage mode and coverage status table.
3. Selected methods and required parameters.
4. File plan (package + tests).
5. Initialization/scaling plan.
6. Validation checklist and expected pass criteria.
7. Parameter provenance table.
