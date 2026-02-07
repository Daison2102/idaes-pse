# EOS and Phase Equilibrium

## Step-by-step checklist

1. Select EOS per phase.
- Ideal for dilute or low-pressure systems.
- Cubic (PR/SRK) for non-ideal VLE.

2. Select equilibrium formulation.
- Fugacity-based is standard for VLE.
- Confirm compatibility with EOS choice.

3. Define phase pairs.
- Identify which phase pairs equilibrate (e.g., Vap-Liq).

4. Configure options.
- Add EOS options if required.
- Add equilibrium options if formulation requires.

## EOS Options

- Ideal: simplest, use for dilute or low-pressure assumptions.
- Cubic (PR, SRK): use for non-ideal vapor-liquid behavior.

## Phase Equilibrium

- Fugacity-based VLE is the standard pattern.
- Use IDAES phase equilibrium forms for consistent formulation.

## Codebase pointers

- EOS: `idaes/models/properties/modular_properties/eos/`
- Phase equilibrium: `idaes/models/properties/modular_properties/phase_equil/`

Use the EOS per phase defined in the intake spec and match the phase equilibrium forms accordingly.
