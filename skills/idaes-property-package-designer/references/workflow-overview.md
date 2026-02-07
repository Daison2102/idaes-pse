# Workflow Overview

## Purpose
Provide a reproducible process for designing IDAES property packages with clear branch points for Generic and Custom approaches.

## Stage Outputs

### Stage 0: Scope and Constraints Capture
- Define components, phases, target operating range, and required properties.
- Capture solver, robustness, and integration constraints.
- Output: scope sheet with in-scope and out-of-scope items.

### Stage 1: Approach Selection
- Apply deterministic rules from `approach-selection.md`.
- Choose `generic` or `custom`.
- Output: approach decision with rationale.

### Stage 2: Source-Grounded Evidence Collection
- Collect official code patterns from the IDAES repository first.
- Collect official docs only for unresolved details.
- Output: evidence table (decision, source, rationale).

### Stage 3: Thermodynamic Architecture Definition
- Define component and phase model assumptions.
- Define state variable set, bounds, and reference state.
- Define required properties and optional advanced properties.
- Output: architecture spec.

### Stage 4A: Generic Framework Construction Path
- Build configuration dictionary structure.
- Define components, phases, state definition, and equilibrium blocks.
- Define package-wide parameters and optional transport methods.
- Output: generic config blueprint.

### Stage 4B: Custom Class Construction Path
- Define parameter block, state block methods, and state block data classes.
- Define metadata, state variables, and required framework methods.
- Output: class-based blueprint.

### Stage 5: Initialization and Scaling Design
- Define initialization sequence and failure handling.
- Define scaling factors for key variables and constraints.
- Output: initialization and scaling plan.

### Stage 6: Validation and Test Design
- Define structural, unit consistency, and solve tests.
- Include harness-style tests where applicable.
- Output: test matrix and acceptance criteria.

### Stage 7: Packaging, Review, and Handoff
- Assemble plan, scaffolds, and checklist results.
- Output: handoff bundle with assumptions, defaults, and residual risks.
