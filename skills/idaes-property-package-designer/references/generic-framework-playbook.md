# Generic Framework Playbook

## Objective
Design a complete Generic property package configuration compatible with current IDAES APIs.

## Required Sections in Configuration

1. `components`
2. `phases`
3. `base_units`
4. `state_definition`
5. `state_bounds`
6. `pressure_ref`
7. `temperature_ref`
8. Optional equilibrium keys:
   - `phases_in_equilibrium`
   - `phase_equilibrium_state`
   - `bubble_dew_method`
9. Optional package-level `parameter_data`

## Procedure

### 1) Build Component Definitions
- Set `type` and `elemental_composition`.
- Assign pure-component property methods.
- Provide `parameter_data` with units.
- Add `phase_equilibrium_form` for shared-phase components when needed.

### 2) Build Phase Definitions
- Declare phase `type`.
- Assign `equation_of_state` and options when needed.
- Add transport configuration only when in scope.

### 3) Select State Definition
- Choose from official state definition modules (for example `FTPx`, `FpcTP`, `FcTP`, `FcPh`, `FPhx`).
- Set robust bounds using `(lower, nominal, upper, units)` tuples.
- Ensure reference pressure and temperature are explicit.

### 4) Add Equilibrium Model (Optional)
- Set `phases_in_equilibrium` pairs.
- Set `phase_equilibrium_state` mapping for each pair.
- Define per-component `phase_equilibrium_form` entries.
- Add bubble/dew method when required by selected formulation.

### 5) Add Global Parameters
- Add package-wide parameters (for example interaction coefficients) in top-level `parameter_data`.

### 6) Plan Initialization and Scaling
- Define initial state guesses and fixed variables.
- Define scaling expectations for key state/property variables.

### 7) Plan Validation
- Structure tests for:
  - parameter block construction,
  - state block construction,
  - required property availability,
  - unit consistency,
  - solve behavior at representative states.

## Local Style Reference
For local style inspiration only, prefer `custom_example_pro_pack/methanol_ceos.py` conventions over older local examples.
