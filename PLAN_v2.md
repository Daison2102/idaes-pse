# PLAN_v2: Skill Design for IDAES Property Package Creation

## 1. Goal
Design a Claude CLI skill that guides users through a robust, repeatable workflow to create IDAES property packages using either:
1. Generic Property Package Framework (`GenericParameterBlock`)
2. Fully custom class-based implementation (`PhysicalParameterBlock` + `StateBlock` + `StateBlockData`)

This plan defines the skill structure, internal workflow, references, templates, scripts, and validation strategy.
It does **not** implement the skill yet.

## 2. Scope and Constraints

### In scope
1. Workflow design for both official IDAES approaches
2. Prompt-to-code guidance logic (requirements parsing, approach selection, generation steps)
3. Parameter sourcing protocol with traceability
4. Test and validation expectations
5. File/folder layout compatible with Codex `skill-creator`

### Out of scope
1. Final skill implementation (`SKILL.md`, templates, scripts) in this step
2. Final property package generation for a specific chemical system

### Source priority (must be encoded in skill behavior)
1. `codebase` MCP (indexed IDAES source)
2. `grounded-docs` MCP (indexed IDAES docs/examples)
3. External sources only when 1-2 are insufficient
4. Web search specifically for missing parameter placeholders

### Current environment note
In this workspace, MCP servers `codebase` and `grounded-docs` are not currently available. The skill design should include a preflight check and graceful fallback instructions.

## 3. Primary Design Principles
1. Prefer Generic framework by default for maintainability and consistency.
2. Switch to class-based approach when requirements exceed Generic framework capabilities.
3. Keep `SKILL.md` concise and route detail into `references/` (progressive disclosure).
4. Use modern IDAES import paths (`idaes.models.properties.modular_properties.*`), not legacy `idaes.generic_models.*`.
5. Require units, references, and source provenance for every parameter.
6. Generate validation artifacts by default (tests + checks), not as optional afterthoughts.
7. Keep templates modular and reusable; avoid monolithic examples.

## 4. Planned Skill Name and Location

## Proposed skill name
`idaes-property-package-designer`

Reason: verb-like intent + domain specificity, lowercase hyphen-case, Codex naming compliant.

## Proposed folder (for implementation phase)
`.claude/skills/idaes-property-package-designer/`

(If your local Claude/Codex setup expects a different root, only the root changes; inner layout remains the same.)

## 5. Planned Skill File Layout (Multi-file, Non-monolithic)

```text
.claude/skills/idaes-property-package-designer/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   |-- workflow-overview.md
|   |-- approach-selection.md
|   |-- requirements-schema.md
|   |-- required-properties-profiles.md
|   |-- generic-framework-workflow.md
|   |-- class-based-workflow.md
|   |-- parameter-sourcing.md
|   |-- state-definitions-map.md
|   |-- equilibrium-patterns.md
|   |-- initialization-and-scaling.md
|   |-- validation-checklist.md
|   `-- source-priority-and-fallback.md
|-- templates/
|   |-- generic/
|   |   |-- config_minimal_single_phase.py
|   |   |-- config_ideal_vle_ftpx.py
|   |   |-- config_cubic_vle.py
|   |   `-- config_builder_get_prop_style.py
|   |-- class_based/
|   |   |-- parameter_block_template.py
|   |   |-- state_block_methods_template.py
|   |   `-- state_block_data_template.py
|   `-- tests/
|       |-- test_property_package_generic.py
|       `-- test_property_package_class_based.py
`-- scripts/
    |-- scaffold_generic_package.py
    |-- scaffold_class_package.py
    |-- build_parameter_ledger.py
    `-- smoke_validate_property_package.py
```

Notes:
1. `scripts/` are included because boilerplate generation and validation are deterministic and repeated.
2. Templates are split by approach and complexity tier to reduce context load.
3. References are one level deep from `SKILL.md` to follow progressive disclosure.

## 6. Internal Skill Workflow (Execution Stages)

## Stage 0: Preflight and Context Discovery
1. Detect tool availability (`codebase`, `grounded-docs`, web search capability).
2. Load minimum required reference docs for selected path only.
3. Confirm user intent: design/package generation and target approach constraints.

Output:
- Preflight report with available sources and fallback mode.

## Stage 1: Requirements Normalization
The skill parses the user prompt into a normalized schema:
1. Component list
2. Phase list
3. State variable set (`FTPx`, `FpcTP`, `FcTP`, `FPhx`, `FcPh`)
4. Required properties (`minimum` or `comprehensive` profile, plus optional custom additions)
5. Equilibrium required? If yes, phase pairs
6. EOS per phase (`Ideal`, `PR`, `SRK`)

Output:
- Structured requirements object + selected property profile + gap list (if missing fields).

## Stage 1A: Required Properties Profile Resolution
The skill resolves `required properties` using canonical profile defaults and user overrides.

### Minimum profile (default)
This profile is intended for fast, robust package creation and common unit-model compatibility.
1. `temperature`
2. `pressure`
3. One total/partial flow representation consistent with state definition: `flow_mol` or `flow_mol_comp` or `flow_mol_phase_comp`
4. One composition representation consistent with state definition: `mole_frac_comp` or `mole_frac_phase_comp`
5. `phase_frac` (multiphase only)
6. `enth_mol` or `enth_mol_phase`
7. `dens_mol` or `dens_mol_phase`
8. `mw`
9. `cp_mol` or `cp_mol_phase`
10. `pressure_sat_comp` (only when VLE/bubble/dew is requested)
11. `fug_phase_comp` (only when fugacity/log-fugacity equilibrium forms are requested)

### Comprehensive profile
This profile targets broad thermodynamic and transport coverage. The skill should include these when methods/data are available.
1. `flow_mol`
2. `flow_mol_comp`
3. `flow_mol_phase`
4. `flow_mol_phase_comp`
5. `mole_frac_comp`
6. `mole_frac_phase_comp`
7. `phase_frac`
8. `mass_frac_phase_comp`
9. `mw`
10. `dens_mol`
11. `dens_mol_phase`
12. `dens_mass`
13. `dens_mass_phase`
14. `enth_mol`
15. `enth_mol_phase`
16. `enth_mol_phase_comp`
17. `entr_mol`
18. `entr_mol_phase`
19. `gibbs_mol`
20. `cp_mol`
21. `cp_mol_phase`
22. `cv_mol_phase`
23. `compress_fact_phase`
24. `fug_phase_comp`
25. `pressure_sat_comp`
26. `temperature_bubble`
27. `temperature_dew`
28. `pressure_bubble`
29. `pressure_dew`
30. `visc_d_phase`
31. `therm_cond_phase`
32. `diffus_phase_comp`
33. `prandtl_phase`

### Resolution rules
1. Start from selected profile (`minimum` default if user is silent).
2. Add any user-requested properties.
3. Remove properties incompatible with the selected approach/state definition/method libraries.
4. Emit an explicit "not supported" report for dropped properties and suggest alternatives.

Output:
- Final resolved required-properties list with status: `supported`, `placeholder`, or `not_supported`.

## Stage 2: Approach Selection
Use explicit decision logic (`references/approach-selection.md`):
1. If supported by modular methods/EOS/state definitions and no unusual custom constraints: Generic
2. If custom/non-library correlations, unusual thermodynamic forms, or unsupported behavior: class-based
3. If user explicitly requests one approach: honor request, but warn on risk if mismatch

Output:
- Chosen approach + rationale + risk notes.

## Stage 3: Parameter Strategy and Data Plan
1. Enumerate required parameters from selected methods/EOS.
2. Resolve from source priority order.
3. If unresolved, web search for parameter placeholders and canonical references.
4. Normalize units and attach provenance.

Output:
- Parameter ledger table (name, value, units, source, confidence, notes).

## Stage 4A: Generic Framework Build Path
1. Build `configuration` dictionary sections:
   - `components`
   - `phases`
   - `base_units`
   - `state_definition`, `state_bounds`
   - `pressure_ref`, `temperature_ref`
   - equilibrium blocks when required
   - package-level `parameter_data` (e.g., `PR_kappa`)
2. Apply methanol-style conventions where useful:
   - reusable component dictionary
   - reusable phase dictionary
   - configurable helper (`get_prop` style)
3. Bind property methods and EOS consistently with requested state variables.

Output:
- Draft generic property package module.

## Stage 4B: Class-Based Build Path
1. Create `PhysicalParameterBlock` data class:
   - phases/components
   - global parameters
   - `_state_block_class` link
   - `define_metadata`
2. Create `StateBlock` methods class:
   - `initialize`
   - `release_state`
   - optional `fix_initialization_states`
3. Create `StateBlockData` class:
   - state vars and constraints
   - required interface methods
   - on-demand property methods
   - optional equilibrium constraints and bubble/dew calculations
4. Add default scaler (`CustomScalerBase`) when needed.

Output:
- Draft class-based property package module(s).

## Stage 5: Validation Artifact Generation
Generate a pytest module with exactly one required marker per test.
Checks include:
1. build/import succeeds
2. units consistency
3. degrees of freedom
4. state var and bounds sanity
5. initialization and release behavior
6. solve termination (when solver available)
7. key property sanity/value checks

Output:
- Test module + expected run command.

## Stage 6: Validation and Repair Loop
1. Run smoke checks first (build + units + DOF).
2. Run component tests.
3. If failure, classify issue:
   - missing parameter
   - wrong units
   - bad state bounds
   - equilibrium inconsistency
   - initialization/scaling gap
4. Patch iteratively until pass criteria met.

Output:
- Validation summary and unresolved risks.

## Stage 7: Delivery Package
Deliver:
1. property package file(s)
2. test file(s)
3. parameter ledger
4. assumptions and source report
5. next-step guidance

## 7. Detailed Build Content by Major Component

## 7.1 Components
### Generic
1. Define each component with `type` and optional `elemental_composition`.
2. Attach pure property methods (`NIST`, `RPP4`, `RPP5`, `Perrys`, etc.).
3. Add component `parameter_data` with units.
4. Add `phase_equilibrium_form` per phase-pair if applicable.

### Class-based
1. Create `Component` objects in parameter block.
2. Define all required Params/Vars centrally in parameter block.
3. Expose component-dependent properties via state methods/expressions.

## 7.2 Phases and EOS
### Generic
1. Define phase objects (`LiquidPhase`, `VaporPhase`, `SolidPhase`).
2. Map EOS by phase (`Ideal`, `Cubic` with `CubicType.PR/SRK`).
3. Add EOS options and phase-specific parameters where needed.

### Class-based
1. Create phase objects directly.
2. Encode EOS relationships as explicit constraints/expressions.
3. Ensure critical property and phase-fraction logic is explicit.

## 7.3 State Variables
1. Enforce supported state-definition list from user prompt.
2. Generic path: select corresponding modular state definition.
3. Class path: declare state vars and composition constraints explicitly.
4. Always specify `state_bounds` and reference state.

## 7.4 Property Methods and Constraints
### Generic
1. Leverage modular method libraries and equilibrium forms.
2. Resolve the final property set from the selected profile (`minimum`/`comprehensive`) plus user overrides.
3. Include only resolved properties to reduce model size.

### Class-based
1. Implement on-demand property methods with consistent naming.
2. Resolve the final property set from the selected profile (`minimum`/`comprehensive`) plus user overrides.
3. Implement required framework interface methods.
4. Separate state constraints from derived-property constraints for clarity.

## 7.5 Initialization
### Generic
1. Use default initializer unless overridden.
2. Provide robust initial state bounds and nominal values.

### Class-based
1. Implement `initialize` and `release_state` explicitly.
2. Fix/unfix logic must preserve DOF and avoid over-specification.

## 7.6 Scaling
1. Add scaling factors for key state vars and difficult constraints.
2. Class path should include a `CustomScalerBase` subclass when nontrivial.
3. Validation must assert scaling exists for numerically sensitive equations.

## 7.7 Validation
1. Unit consistency (`assert_units_consistent`).
2. DOF checks at each state.
3. Initialization stability.
4. Solver convergence and physical sanity checks.
5. Include one required test marker per test (`unit`, `component`, etc.).

## 8. Generic vs Class-Based Decision Matrix (Skill Logic)

| Requirement Pattern | Preferred Approach | Reason |
|---|---|---|
| Standard components + standard EOS/method libraries | Generic | Fast, consistent, lower maintenance |
| Need custom correlation not represented in modular libraries | Class-based | Full control over equations |
| Nonstandard state representation beyond supported state definitions | Class-based | Requires explicit state equations |
| Multi-phase equilibrium supported by modular options | Generic | Built-in PE formulations |
| User explicitly wants class internals for research or custom init/scaling | Class-based | Maximum transparency/control |

## 9. Template Strategy (Improved from Legacy Examples)

## Generic templates
Incorporate strengths from `methanol_ceos.py`:
1. reusable component and phase dictionaries
2. EOS enum/config switch pattern
3. helper builder (`get_prop` style)
4. optional transport property hooks
5. package-level binary interaction defaults

## Class-based templates
Improve over older water-ethanol class file by:
1. splitting logic into cleaner sections/classes
2. reducing hardcoded component references
3. keeping property methods modular and testable
4. adding explicit scaling and diagnostics hooks
5. aligning with current IDAES naming/import conventions

## Legacy usage policy
Legacy files are used as structural references only, not canonical source-of-truth.
Official repository patterns/docs remain authoritative.

## 10. Parameter Sourcing and Placeholder Policy

For every required parameter:
1. Try `codebase` examples and existing property packages first.
2. Then `grounded-docs` method pages and examples.
3. If still missing, use web search (NIST, Perry, Poling/Prausnitz/O'Connell, DIPPR if available).
4. Record source, units, temperature range validity, and retrieval date.
5. If value remains uncertain, emit placeholder with explicit TODO and confidence tag.

Planned artifact format (`build_parameter_ledger.py`):
- `parameter_name`
- `value`
- `units`
- `applies_to`
- `source`
- `retrieved_on`
- `notes`

## 11. Validation Standards and Exit Criteria

A generated package is considered acceptable only if:
1. module imports without errors
2. parameter block and state block construct successfully
3. units are consistent
4. DOF target is met for tested states
5. initialization runs without structural errors
6. solver reports optimal termination for test case(s), if solver available
7. test suite has required marker and passes selected checks
8. parameter ledger is complete with provenance

## 12. Codex `skill-creator` Compatibility Plan

When implementing the skill from this plan:
1. Initialize scaffold using `scripts/init_skill.py`.
2. Keep `SKILL.md` short and procedural.
3. Place detailed material in `references/`.
4. Add deterministic scripts only where repetition/fragility justifies them.
5. Generate `agents/openai.yaml` with deterministic interface values.
6. Validate with `scripts/quick_validate.py`.

Required frontmatter in future `SKILL.md`:
1. `name`
2. `description`

No extra auxiliary docs beyond required skill resources.

## 13. Implementation Backlog (Next Step, Not Executed Now)

## Phase A
1. Create skill folder scaffold
2. Draft `SKILL.md` navigation and trigger description

## Phase B
1. Write `references/` documents from this plan
2. Encode source priority and fallback behavior

## Phase C
1. Build templates (generic + class-based + tests)
2. Build scripts for scaffolding and parameter ledger

## Phase D
1. Run skill validation (`quick_validate.py`)
2. Dry-run with at least two cases:
   - ideal VLE binary (generic)
   - custom state/property case (class-based)

## 14. Explicit Reference Anchors Used for this Plan

Official IDAES source/docs inspected:
1. `idaes/models/properties/modular_properties/examples/BT_ideal.py`
2. `idaes/models/properties/modular_properties/examples/BT_PR.py`
3. `idaes/models/properties/examples/saponification_thermo.py`
4. `idaes/models/properties/examples/tests/test_saponification_thermo.py`
5. `idaes/models/properties/modular_properties/examples/tests/test_BTIdeal.py`
6. `idaes/models/properties/modular_properties/examples/tests/test_BTIdeal_FcTP.py`
7. `docs/explanations/components/property_package/general/generic_definition.rst`
8. `docs/explanations/components/property_package/general/component_def.rst`
9. `docs/explanations/components/property_package/general/phase_def.rst`
10. `docs/explanations/components/property_package/general/state_definition.rst`
11. `docs/explanations/components/property_package/general/phase_equilibrium.rst`
12. `docs/how_to_guides/custom_models/property_package_development.rst`

Legacy structural references (non-canonical):
1. `custom_example_pro_pack/WE_ideal_FTPx_class.py`
2. `custom_example_pro_pack/WE_ideal_FTPx.py`
3. `custom_example_pro_pack/WE_ideal_FpcTP.py`
4. `custom_example_pro_pack/methanol_ceos.py`

## 15. Acceptance Criteria for PLAN_v2
1. Distinguishes Generic vs Class-based workflows clearly.
2. Defines both `minimum` and `comprehensive` required-properties profiles with explicit resolution rules.
3. Covers phases, components, state vars, properties, constraints, initialization, scaling, validation.
4. Defines non-monolithic multi-file skill layout with references/templates/scripts.
5. Encodes source-priority policy and parameter placeholder strategy.
6. Is directly usable as blueprint for Codex `skill-creator` implementation.

