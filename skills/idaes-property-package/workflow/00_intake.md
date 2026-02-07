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

5. Define required properties.
- Properties needed for material balances.
- Properties needed for energy balances.
- Properties needed by transport or unit operations.
- Properties needed for equilibrium calculations.

6. Define phase equilibrium requirements.
- Equilibrium types (VLE, LLE, SLE).
- Phase pairs that equilibrate.
- Equilibrium formulation (fugacity, K-value, etc.).

7. Choose EOS per phase.
- EOS for each phase (Ideal, PR, SRK, or other).
- Any EOS options needed (e.g., PR alpha model).

8. Decide transport properties.
- Viscosity model.
- Thermal conductivity model.
- Diffusivity model (if required).

9. Define operating ranges.
- Temperature range.
- Pressure range.
- Composition range or expected bounds.

10. Reference states and units.
- Enthalpy and entropy reference states.
- Base unit system.

Deliverable: a concise spec sheet (flat list) that includes all items above.
