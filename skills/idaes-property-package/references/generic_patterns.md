# Generic Property Package Patterns

## Required Pattern (Default)

Use this as the canonical module layout unless user explicitly asks otherwise.

1. Module header and imports:
- `# pylint: disable=all`
- Python stdlib imports (`logging`, `copy`, `enum`)
- Pyomo units import
- IDAES imports grouped by role

2. Core module scaffolding:
- logger setup (`_log = logging.getLogger(__name__)`)
- `EosType` enum for EOS routing

3. Configuration architecture:
- `_phase_dicts_pr`
- `_phase_dicts_ideal`
- `_component_params`
- `get_prop(...)` builder
- module-level `configuration = get_prop(...)`

4. Data quality requirements:
- use unit-bearing tuples in `parameter_data`
- add source comments by parameter group
- note validity ranges for key correlations where available

5. Required equilibrium keys for two-phase systems:
- `phases_in_equilibrium`
- `phase_equilibrium_state`
- `phase_equilibrium_form` on relevant components

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

## Common Errors

- Missing units on numeric coefficients
- Building `configuration` directly without a reusable `get_prop(...)` factory
- Inconsistent import grouping/order
- Missing equilibrium keys in multi-phase setups
- EOS-specific keys mixed into wrong phase dictionary
