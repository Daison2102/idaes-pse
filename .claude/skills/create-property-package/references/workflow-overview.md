# Workflow Overview

This reference defines the default end-to-end process used by the skill.

## Stage Sequence

1. Input normalization.
2. Coverage mode and required-properties gate.
3. Approach selection.
4. Canonical pattern mining.
5. Method/parameter mapping.
6. Branch-specific scaffolding.
7. Initialization/scaling design.
8. Validation/test generation.
9. Delivery summary.

## Stage Details

### 1) Input Normalization

Convert user intent into a strict internal spec. The skill should not proceed with free-form assumptions for components, phases, EOS, or state definition.

Expected minimum fields:
1. Components list.
2. Phases list.
3. State-variable definition.
4. Required properties.
5. Equilibrium requirement and phase pairs.
6. EOS by phase.

### 2) Coverage Mode Gate

Choose:
1. `minimum`: fast, viable package for standard unit-model coupling.
2. `comprehensive`: broader property surface for production studies.

Apply `required-properties-catalog.md` to generate a coverage table.

Coverage status values:
1. `covered`
2. `missing`
3. `custom-implementation-needed`

### 3) Approach Selection

Use `approach-selection.md`.

Decision output includes:
1. Selected approach (`generic` or `class`).
2. Reasoning.
3. Risk flags (unsupported methods, likely custom equations, difficult initialization path).

### 4) Canonical Pattern Mining

Gather patterns from official IDAES code and docs before generating code.

Required artifacts:
1. At least one official property package example with similar phase/EOS profile.
2. At least one official test file with relevant validation patterns.

### 5) Method and Parameter Mapping

For each required property, map:
1. Candidate method.
2. Required parameter keys.
3. Parameter source and units.
4. Gaps.

No scaffolding starts until minimum coverage is feasible.

### 6) Branch-Specific Scaffolding

Generic branch:
1. Build a complete `configuration` dictionary.
2. Include phase equilibrium entries when needed.
3. Include package-wide binary parameters when required (for cubic EOS).
4. Optionally provide `get_prop(...)` factory.

Class branch:
1. Build ParameterBlock class.
2. Build StateBlock methods class with `initialize` and `release_state`.
3. Build StateBlockData with required contracts and build-on-demand property methods.

### 7) Initialization and Scaling

Provide:
1. Initial guess strategy.
2. State-fixing/unfixing flow.
3. Default scaling factors for key variables/constraints.

### 8) Validation and Testing

Generate tests for:
1. Build and metadata sanity.
2. Units consistency.
3. Degrees of freedom.
4. Initialization behavior.
5. Solve success.
6. Representative property checks.

### 9) Delivery Summary

Deliverables must include:
1. Produced files list.
2. Coverage report.
3. Parameter provenance report.
4. Remaining assumptions and limitations.

## Hard Stops

Do not continue to code generation when:
1. Minimum required properties are unresolved.
2. EOS/phase pair combination is unsupported by selected method.
3. Critical parameters are missing with no placeholder strategy.

## Default Choices

When not specified by user:
1. Coverage mode defaults to `minimum`.
2. Approach defaults to `generic` if feasible.
3. Base units default to SI set (s, m, kg, mol, K).
