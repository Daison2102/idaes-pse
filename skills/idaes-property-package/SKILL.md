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

If the user already provided these, use them. Otherwise, prompt for them using the intake checklist.

## Approach Selection Summary

- Default to the Generic framework unless the package needs:
  - Custom state variables or constraints
  - Non-standard property definitions not supported by modular methods
  - Highly bespoke initialization logic
- For custom constraints or novel property equations, use the class-based approach.

For full decision logic, see `workflow/10_select_approach.md`.

## Output Expectations

- Provide a clear step-by-step plan and a minimal code skeleton.
- Use templates in `assets/templates/` instead of writing code from scratch.
- Include validation steps using the property harness.
- Keep documentation modular and navigable.
