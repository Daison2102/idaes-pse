---
name: idaes-property-package
description: Design a systematic, reusable workflow for creating IDAES Property Packages using either the generic framework or custom class-based definitions, with best-practice guidance, templates, and validation steps.
metadata:
  short-description: Design IDAES Property Packages
---

# IDAES Property Package Skill

Use this skill when the user needs to design or create an IDAES Property Package, either via the Generic Property Package framework or via fully custom class-based definitions. The goal is to guide them through a complete, reusable workflow that produces a correct and maintainable property package.

## Core Principles

- Prefer official IDAES patterns. Use this repo and official docs as the source of truth.
- Keep SKILL.md lean; load references only when needed.
- Support both approaches and select based on requirements.
- Use web search only when parameter values are missing and placeholders are needed.
- Generic framework outputs must follow the enforced module and factory pattern in
  `workflow/20_generic_build.md` and `assets/templates/generic_property_package.py`,
  unless the user explicitly requests a different style.
- If the user explicitly requests "generic property package using class definitions",
  use a `GenericParameterData` subclass with `configure` and `parameters` methods.
- Class-based outputs must satisfy the `PhysicalParameterBlock` contract:
  explicit `state_block_class`, required indexing sets, optional elemental
  definitions where relevant, and complete metadata registration.

## Source Priority (Strict)

1. Use the indexed IDAES codebase MCP to find patterns in the repo.
2. Use grounded-docs MCP for official docs/examples.
3. Use external sources only if required information is missing in 1 and 2.
4. Use web search to source parameter placeholders when missing.

## Workflow Map

Start here and follow the workflow in order:

- `workflow/00_intake.md` for the property package spec sheet
- `workflow/10_select_approach.md` to decide Generic vs Class-based
- `workflow/20_generic_build.md` for the Generic framework path
- `workflow/30_class_build.md` for the Class-based path
- `workflow/40_validation.md` for testing and validation
- `workflow/50_parameters.md` for parameter sourcing
- `workflow/60_review_checklist.md` for final pre-delivery checks

Reference material (load as needed):

- `references/generic_patterns.md`
- `references/class_patterns.md`
- `references/state_definitions.md`
- `references/eos_phase_equil.md`
- `references/transport_props.md`
- `references/scaling_init.md`
- `references/test_harness.md`
- `references/legacy_examples_summary.md`
- `references/mcp_search_tips.md`

Templates (copy and edit as needed):

- `assets/templates/generic_property_package.py`
- `assets/templates/generic_property_package_class.py`
- `assets/templates/class_property_package.py`
- `assets/templates/test_property_package.py`

## What the Skill Must Capture

The skill must ensure the workflow captures and documents:

- Components list
- Phases list
- State variables and basis
- Required properties (and which are phase- or mixture-specific)
- Equilibrium requirements and phase pairs
- EOS for each phase
- For class-based packages:
  - explicit `state_block_class` linkage
  - `phase_list` and `component_list`
  - `element_list` and `element_comp` when elemental balances/reactions require it
  - `define_metadata` with `add_default_units` and `add_properties`

If the user already provided these, use them. Otherwise, prompt for them using the intake checklist.

## Approach Selection Summary

- Default to the Generic framework unless the package needs:
  - Custom state variables or constraints
  - Non-standard property definitions not supported by modular methods
  - Highly bespoke initialization logic
- If user explicitly asks for "generic with class definitions", use the
  Generic class-definition option (`GenericParameterData` with
  `configure/parameters`).
- For custom constraints or novel property equations, use the class-based approach.

For full decision logic, see `workflow/10_select_approach.md`.

## Avoid Confusion: Two Different "Class" Paths

- Generic framework with class definitions:
  - subclass `GenericParameterData`
  - implement `configure(self)` and `parameters(self)`
  - still uses modular generic methods and configuration model
- Fully custom class-based package:
  - subclass `PhysicalParameterBlock` and custom `StateBlockData`
  - implement custom interfaces and equations directly

## Output Expectations

- Provide a clear step-by-step plan and a minimal code skeleton.
- Use templates in `assets/templates/` instead of writing code from scratch.
- Include validation steps using the property harness.
- Run `workflow/60_review_checklist.md` before returning class-based package outputs.
- Keep documentation modular and navigable.

## Class Output Standard

For the Class-based path, the default required format is:

- `PhysicalParameterBlock` with explicit state block pointer assignment
- `component_list` and `phase_list` declared in the parameter block
- optional `element_list` and `element_comp` block when requested or required
- `define_metadata` that includes:
  - `add_default_units(...)`
  - `add_properties(...)` entries for all expected constructed properties
- required interface methods implemented in the state block

If a user asks for a different style, document the deviation and proceed.

## Generic Output Standard

For the Generic framework path, the default required format is:

- module header with `# pylint: disable=all`
- grouped imports in this order: Python stdlib, Pyomo units, IDAES cores/modules
- logger setup and `EosType` enum
- phase dictionaries (`_phase_dicts_pr`, `_phase_dicts_ideal`)
- component master dictionary (`_component_params`)
- factory builder function `get_prop(...)`
- exported `configuration = get_prop(...)`

If a user asks for a different style, document the deviation and proceed.

## Generic Class-Definition Option

If and only if the user explicitly asks for generic framework class definitions,
use this alternate pattern:

- `@declare_process_block_class("...")`
- subclass `GenericParameterData`
- implement `configure(self)` to set selected config options
- implement `parameters(self)` to define required parameters and values
- keep metadata units consistent with selected methods

For this option, start from `assets/templates/generic_property_package_class.py`.

## Generic Contract (Required)

Any Generic framework output must include and validate:

- Top-level keys: `components`, `phases`, `base_units`, `state_definition`,
  `state_bounds`, `pressure_ref`, `temperature_ref`
- Phase/component compatibility:
  - each component has valid `valid_phase_types`
  - optional phase `component_list` is a subset of package components
- Equilibrium triad consistency when equilibrium is enabled:
  - `phases_in_equilibrium`
  - `phase_equilibrium_state`
  - per-component `phase_equilibrium_form` for shared components
- Method-parameter completeness:
  - each chosen pure/transport/EOS method has required `parameter_data` keys
  - units are explicit where expected

Compatibility defaults:

- Use `SmoothVLE` by default for non-cubic VLE.
- Use cubic-only smooth equilibrium methods only when cubic EOS is selected.
- Use `IdealBubbleDew` only for 2-phase ideal assumptions.
- Default `include_enthalpy_of_formation=True` unless user requests otherwise.
