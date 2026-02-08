---
name: idaes-property-package-designer
description: Systematic workflow for designing and generating IDAES thermophysical property packages using either the modular Generic Property Package Framework or fully custom class-based implementations. Use when creating or updating IDAES property packages, selecting state definitions (FTPx/FpcTP/FcTP/FPhx/FcPh), defining components/phases/EOS/equilibrium, sourcing thermodynamic parameters, scaffolding package code and tests, and validating initialization and scaling behavior.
---

# IDAES Property Package Designer
Execute this workflow to design and scaffold an IDAES property package from user requirements.

## Collect Inputs
Capture and normalize all of the following:
1. `components` list
2. `phases` list
3. `state_definition` (`FTPx`, `FpcTP`, `FcTP`, `FPhx`, or `FcPh`)
4. `required_properties` profile (`minimum` or `comprehensive`) plus user overrides
5. `equilibrium_required` and phase pairs
6. `equation_of_state` per phase (`Ideal`, `PR`, `SRK`)

If an input is missing, ask focused follow-up questions before generating code.

## Run Preflight
1. Check whether `codebase` MCP and `grounded-docs` MCP are available.
2. If unavailable, use local repository sources and state the fallback.
3. Continue only with explicit assumptions when data is incomplete.

Use `references/source-priority-and-fallback.md`.

## Choose Approach
1. Apply decision rules in `references/approach-selection.md`.
2. Default to Generic framework when supported.
3. Switch to class-based implementation when needed for unsupported/custom behavior.

## Resolve Required Properties
1. Load profiles in `references/required-properties-profiles.md`.
2. Start with profile defaults.
3. Add user-requested properties.
4. Mark each property as `supported`, `placeholder`, or `not_supported`.

## Build Package
If Generic path is selected:
1. Follow `references/generic-framework-workflow.md`.
2. Start from templates under `templates/generic/`.
3. Use `scripts/scaffold_generic_package.py` when appropriate.

If class-based path is selected:
1. Follow `references/class-based-workflow.md`.
2. Start from templates under `templates/class_based/`.
3. Use `scripts/scaffold_class_package.py` when appropriate.

## Source Parameters
1. Follow `references/parameter-sourcing.md`.
2. Record values and provenance with `scripts/build_parameter_ledger.py`.
3. Use web search only for missing parameter data after primary sources are exhausted.

## Validate
1. Follow `references/validation-checklist.md`.
2. Create tests from `templates/tests/`.
3. Run `scripts/smoke_validate_property_package.py` for quick checks.
4. Iterate until exit criteria are met or blockers are explicit.

## Output Contract
Always deliver:
1. Package module(s)
2. Test module(s)
3. Parameter ledger
4. Assumptions and unresolved risks
5. Exact commands used for validation

## Reference Navigation
Use these references only as needed:
1. `references/workflow-overview.md`
2. `references/requirements-schema.md`
3. `references/required-properties-profiles.md`
4. `references/approach-selection.md`
5. `references/generic-framework-workflow.md`
6. `references/class-based-workflow.md`
7. `references/state-definitions-map.md`
8. `references/equilibrium-patterns.md`
9. `references/parameter-sourcing.md`
10. `references/initialization-and-scaling.md`
11. `references/validation-checklist.md`
12. `references/source-priority-and-fallback.md`
