# Generic Property Package Patterns

## Step-by-step checklist

1. Locate a close example in the codebase.
- Start with `idaes/models/properties/modular_properties/`.
- Prefer examples that match your phases and EOS.

2. Copy the configuration dict structure.
- Components, phases, equilibrium, transport, base units.

3. Verify method availability.
- Check that required pure component and transport methods exist.
- Confirm compatible EOS and phase equilibrium forms.

4. Populate parameter data.
- Add `mw`, `pressure_crit`, `temperature_crit`, and method-specific coeffs.
- Include units and sources.

5. Validate the dict keys.
- Ensure key names match IDAES expectations.
- Ensure phase and component IDs are consistent.

## Codebase Pointers

- Modular properties: `idaes/models/properties/modular_properties/`
- Example usages: `idaes/models/properties/modular_properties/examples/` (if present)
- Phase equilibrium forms: `idaes/models/properties/modular_properties/phase_equil/`
- Pure component methods: `idaes/models/properties/modular_properties/pure/`

## Common Configuration Keys

- `components` with `type`, `valid_phase_types`, method assignments, and `parameter_data`
- `phases` with `type`, `equation_of_state`, and phase options
- `phase_equilibrium_form` for VLE/LLE
- `state_definition` and `state_bounds`

Use methanol_ceos.py structure as the primary layout pattern.
