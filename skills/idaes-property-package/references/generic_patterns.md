# Generic Property Package Patterns

## Canonical Module Pattern (Required)

1. Header and imports.
- `# pylint: disable=all`
- import order: stdlib -> pyomo units -> idaes modules
- logger + `EosType` enum

2. Master dictionaries.
- `_phase_dicts_pr`
- `_phase_dicts_ideal`
- `_component_params`

3. Factory and export.
- `get_prop(...)`
- exported `configuration = get_prop(...)`

## Optional Class-Definition Pattern (Only On Explicit Request)

1. Class definition.
- `@declare_process_block_class("UserParameterBlock")`
- subclass `GenericParameterData`

2. `configure(self)`.
- assign selected options via `self.config.option = value`

3. `parameters(self)`.
- define only parameters required by selected methods
- add units and sensible defaults/placeholders

## Intent Mapping

- "generic property package" -> Generic dict/factory pattern (default)
- "generic using classes" -> Generic class-definition pattern
- "custom equations/state block" -> Full class-based package (not generic)

## Canonical Configuration Keys

- `components`
- `phases`
- `base_units`
- `state_definition`
- `state_bounds`
- `pressure_ref`
- `temperature_ref`
- optional: `phases_in_equilibrium`, `phase_equilibrium_state`, `bubble_dew_method`
- optional: top-level `parameter_data` for package-wide parameters (e.g., EOS binary interactions)

## Pattern Variants

1. Single-phase non-equilibrium.
- no `phases_in_equilibrium`
- no `phase_equilibrium_state`
- no per-component `phase_equilibrium_form`

2. Ideal/non-cubic VLE.
- `phases_in_equilibrium` + `phase_equilibrium_state`
- per-component `phase_equilibrium_form`
- default equilibrium-state method: `SmoothVLE`

3. Cubic VLE.
- cubic EOS in relevant phases
- cubic-compatible equilibrium-state method if requested
- package-level binary interactions (`PR_kappa`/`SRK_kappa` style)

4. Vapor transport enabled.
- phase uses `ViscosityWilke` and/or `ThermalConductivityWMS`
- component methods provide required transport parameter keys
- callback options set where needed (e.g., Wilke phi callback)

## Compatibility and Completeness Checklist

1. Equilibrium triad consistency.
- each equilibrium pair appears in both `phases_in_equilibrium` and `phase_equilibrium_state`
- each shared component has matching `phase_equilibrium_form`

2. Method-parameter completeness.
- pure method coefficients are present
- transport parameters are present when transport is enabled
- EOS-level package parameters are present when EOS requires them

3. Phase/component consistency.
- phase `component_list` (if used) is subset of package components
- component `valid_phase_types` are compatible with included phases

## Common Errors

- Over-defining phase-equilibrium pairs in multi-equilibrium systems.
- Missing per-component `phase_equilibrium_form` for shared components.
- Enabling transport methods without required molecular parameters.
- Choosing cubic-only equilibrium formulations with non-cubic EOS.
- Omitting required top-level keys (`state_bounds`, references, units).
- Using class-definition pattern without implementing both `configure` and `parameters`.
- Trying to add full custom state equations in generic-class mode.
