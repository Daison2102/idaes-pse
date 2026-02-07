# Intake: Property Package Spec Sheet

Goal: produce a complete spec for the property package before building anything.

## Step-by-step checklist

1. Identify the scope.
- Name the package.
- Note the intended unit models (flash, column, reactor, etc.).
- Decide if reactions are in-scope.

2. List components.
- Component IDs.
- Valid phase types per component.
- Elemental composition for each component.

3. Define phases.
- Phase names.
- Phase types (liquid, vapor, solid).

4. Choose state definition and basis.
- State definition (FTPx, FpcTP, etc.).
- Basis (mole, mass, volumetric).
- Expected degrees of freedom for a defined state.
- Why this state definition is preferred for target unit models.

5. Define required properties.
- Properties needed for material balances.
- Properties needed for energy balances.
- Properties needed by transport or unit operations.
- Properties needed for equilibrium calculations.

6. Define phase equilibrium requirements.
- Equilibrium types (VLE, LLE, SLE).
- Phase pairs that equilibrate.
- Equilibrium formulation (fugacity, K-value, etc.).
- Equilibrium state method (e.g., `SmoothVLE`, cubic complementarity).
- Bubble/dew method requirements (if any).

7. Choose EOS per phase.
- EOS for each phase (Ideal, PR, SRK, or other).
- Any EOS options needed (e.g., PR alpha model).

8. Decide transport properties.
- Viscosity model.
- Thermal conductivity model.
- Diffusivity model (if required).
- Whether transport can be disabled (`NoMethod`) for this use case.

9. Define operating ranges.
- Temperature range.
- Pressure range.
- Composition range or expected bounds.

10. Reference states and units.
- Enthalpy and entropy reference states.
- Base unit system.
- Whether `include_enthalpy_of_formation` should be True/False.

11. Generic framework contract requirements (mandatory when generic path is selected).
- Confirm all required top-level config keys.
- Confirm EOS/phase-equilibrium compatibility.
- Confirm method-specific parameter requirements are available (or placeholders are acceptable).
- Confirm per-component phase equilibrium forms for shared components.

12. Class-based contract requirements (mandatory when class path is selected).
- State block class name and pointer plan (`state_block_class` / `_state_block_class`).
- Supported properties to expose via metadata (`add_properties` list).
- Whether elemental balances are required in downstream models.
- If elemental balances are required, define `element_list` and `element_comp` explicitly.

## Decision Rules

- If multiphase + FTPx + effectively single-component behavior is expected,
  flag state-definition risk and consider alternative state definitions.
- If VLE is requested and EOS is non-cubic, default to `SmoothVLE`.
- If cubic-specific smooth equilibrium is requested, require cubic EOS.
- If ideal bubble/dew method is requested, require a two-phase ideal setup.
- If user requests elemental balances, atom balances, or reaction coupling,
  `element_list` and `element_comp` are required.
- If user selects class-based implementation, metadata requirements must be
  specified at intake (not deferred).

Deliverable: a concise spec sheet (flat list) that includes all items above.
