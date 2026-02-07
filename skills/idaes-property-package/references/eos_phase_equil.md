# EOS and Phase Equilibrium

## EOS Selection Guidance

1. Ideal EOS.
- Best for ideal-gas/ideal-liquid assumptions and simpler problems.
- Not suitable for all critical-property workflows.

2. Cubic EOS (PR/SRK).
- Use for non-ideal VLE where fugacity behavior is important.
- Requires package-level binary interaction parameters when applicable.

## Equilibrium Configuration Triad (Required)

When equilibrium is enabled, configure all three:

1. `phases_in_equilibrium`
2. `phase_equilibrium_state`
3. per-component `phase_equilibrium_form`

Missing any part leads to incomplete or inconsistent equilibrium setup.

## Compatibility Matrix

1. Non-cubic EOS + VLE.
- Recommended equilibrium-state method: `SmoothVLE`.

2. Cubic EOS + VLE.
- `SmoothVLE` is valid.
- Cubic smooth/complementarity methods are valid only with cubic EOS.

3. Ideal bubble/dew methods.
- Use for two-phase ideal assumptions only.
- For more complex multiphase behavior, use log-form/smooth formulations.

## Required Package-Level Parameters

1. Cubic EOS.
- Include binary interaction matrix in top-level `parameter_data`
  (e.g., `PR_kappa`/`SRK_kappa` style dict over component pairs).

2. Any method with package-scoped options.
- Keep package-level options in top-level config, not inside components.

## Implementation Checks

1. Each phase pair in `phases_in_equilibrium` has an entry in `phase_equilibrium_state`.
2. Every component present in both phases of a pair defines the needed `phase_equilibrium_form`.
3. EOS method supports fugacity behavior required by selected equilibrium form.

## Codebase Pointers

- EOS modules: `idaes/models/properties/modular_properties/eos/`
- Phase-equilibrium forms/state methods: `idaes/models/properties/modular_properties/phase_equil/`
- Bubble/dew methods: `idaes/models/properties/modular_properties/phase_equil/bubble_dew.py`
