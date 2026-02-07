# Transport Properties

## Scope Decision

1. If target unit models do not use transport properties, disable transport (`NoMethod`).
2. If transport is required, select methods per phase and ensure required component parameters are available.

## Common Method Requirements

1. `ViscosityWilke` (mixture vapor viscosity).
- Requires component vapor viscosity methods.
- Commonly paired with `wilke_phi_ij_callback`.

2. `ThermalConductivityWMS` (mixture vapor thermal conductivity).
- Requires component thermal conductivity methods.
- Usually used with low-pressure gas assumptions.

3. `ChapmanEnskogLennardJones` (pure viscosity).
- Requires molecular parameters such as Lennard-Jones `sigma` and `epsilon`.

4. `Eucken` (pure thermal conductivity).
- Depends on viscosity and heat capacity pathways being available.

5. `NoMethod`.
- Use explicitly when transport is out of scope for a phase.

## Parameter Completeness Checks

1. For each component using Lennard-Jones transport methods:
- `lennard_jones_sigma`
- `lennard_jones_epsilon_reduced`

2. For Eucken pathways:
- ensure compatible pure viscosity and heat-capacity methods are present.

3. For mixture methods:
- ensure all participating components in the phase can provide required pure properties.

## Configuration Patterns

1. Phase-level assignment.
- `visc_d_phase`
- `therm_cond_phase`
- optional `transport_property_options` (callbacks)

2. Component-level assignment.
- `visc_d_phase_comp`
- `therm_cond_phase_comp`

## Validation

1. Confirm units for all transport parameters.
2. Confirm method validity ranges are noted when known.
3. Smoke-build transport properties on at least one representative state.

## Codebase Pointers

- `idaes/models/properties/modular_properties/transport_properties/`
- Official IDAES transport-property documentation and in-repo examples
