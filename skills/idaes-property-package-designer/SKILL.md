---
name: idaes-property-package-designer
description: Design systematic, reusable workflows for creating custom IDAES property packages. Use when users need to plan, scaffold, review, or validate thermophysical property packages in IDAES, including both (1) Generic Property Package framework workflows and (2) fully custom class-based property package workflows.
---

# IDAES Property Package Designer

## Overview
Design decision-complete plans and scaffolds for IDAES property packages using either the Generic framework or explicit custom classes, with source-grounded reasoning and validation-first outputs.

## Source Priority Protocol
Use sources in this order for every design decision:

1. `codebase` MCP (or `repobase` when `codebase` is unavailable): official repository patterns, examples, and tests.
2. `grounded-docs` MCP: official IDAES documentation and API guidance.
3. External web sources only if required details are missing from 1 and 2.

For each major decision, record the source and why it was selected.

## Workflow Stages
Follow the stage map in `references/workflow-overview.md`:

1. Stage 0: scope and constraints capture.
2. Stage 1: approach selection.
3. Stage 2: source-grounded evidence collection.
4. Stage 3: thermodynamic architecture definition.
5. Stage 4A: generic framework construction path.
6. Stage 4B: custom class construction path.
7. Stage 5: initialization and scaling design.
8. Stage 6: validation and test design.
9. Stage 7: packaging, review, and handoff.

## Approach Decision Gateway
Use `references/approach-selection.md` to choose between:

- Generic framework path: `references/generic-framework-playbook.md`
- Custom class path: `references/custom-class-playbook.md`

Always include explicit rationale for the selected path.

## Required Design Coverage
For either approach, cover all of the following:

- Phases, components, and parameterization strategy.
- State variable set, bounds, and reference state.
- Property methods and metadata registration.
- Core constraints and optional phase equilibrium.
- Initialization and state release sequence.
- Scaling strategy for variables and constraints.
- Validation tests and acceptance criteria.

Use:

- `references/property-method-catalog.md`
- `references/initialization-scaling-validation.md`
- `references/source-priority-and-citation.md`

## Local Legacy Example Policy
Use local examples as structural references, not canonical authority:

- `custom_example_pro_pack/WE_ideal_FTPx_class.py`
- `custom_example_pro_pack/WE_ideal_FTPx.py`
- `custom_example_pro_pack/WE_ideal_FpcTP.py`
- `custom_example_pro_pack/methanol_ceos.py` (preferred local style reference for generic setup)

If these conflict with official IDAES sources, follow official sources.

## Scripts and Templates
Use bundled scripts for deterministic output:

- `scripts/scaffold_generic_package.py`
- `scripts/scaffold_custom_package.py`
- `scripts/generate_property_package_checklist.py`
- `scripts/validate_property_package_plan.py`

Use templates and checklists:

- `references/checklists/generic-checklist.md`
- `references/checklists/custom-checklist.md`
- `references/checklists/review-checklist.md`
- `references/templates/*.md`
- `assets/stubs/*.j2`

## Output Contract
When producing a design output, provide:

1. Selected approach and rationale.
2. Stage-by-stage plan with explicit deliverables.
3. Proposed public interfaces and data structures.
4. Initialization/scaling/validation strategy.
5. Assumptions, defaults, and open risks.
6. Traceability notes linking decisions to sources.
