# Build with Generic Property Package Framework

Use this when standard IDAES modular methods and EOS cover the needed properties.

## Required Structure (Default)

The generic path must use the enforced module pattern:

1. Module skeleton.
- `# pylint: disable=all`
- import order: Python stdlib -> Pyomo units -> IDAES modules
- logger setup (`_log = logging.getLogger(__name__)`)
- `EosType` enum for EOS routing

2. Master dictionaries.
- `_phase_dicts_pr` and `_phase_dicts_ideal`
- `_component_params`
- optional helper dicts for transport callbacks and phase-scoped methods

3. Factory builder.
- `get_prop(components=None, phases=..., eos=..., scaled=False, ...)`
- assemble top-level keys:
  - `components`
  - `phases`
  - `base_units`
  - `state_definition`
  - `state_bounds`
  - `pressure_ref`
  - `temperature_ref`

4. Module export.
- `configuration = get_prop(...)`

## Alternate Structure (On Explicit User Request Only)

Use this only if user asks for "generic framework using class definitions":

1. Class declaration.
- `@declare_process_block_class("UserParameterBlock")`
- subclass `GenericParameterData`

2. `configure(self)` method.
- set configuration choices using `self.config.<option> = <value>`
- set/confirm default units metadata if needed by selected methods
- keep all required generic config keys (components, phases, state refs, units)

3. `parameters(self)` method.
- define parameters required by selected methods
- include units and physically sensible initial values/placeholders
- use this for extra user parameters only; do not replace modular method internals

## Generic Build Sequence

1. Copy the template.
- Start from `assets/templates/generic_property_package.py`.
- Preserve section order.

2. Build phase dictionaries.
- Assign `type` and `equation_of_state` for each phase.
- Add `equation_of_state_options` where needed.
- Add transport methods only if requested.

3. Build component dictionary.
- Define `type`, `valid_phase_types`, pure methods, and `parameter_data`.
- Include phase-equilibrium form only for components shared across equilibrium phase pairs.
- Include explicit units (or explicit unitless marker).

4. Wire phase equilibrium (only when requested).
- Add `phases_in_equilibrium`.
- Add `phase_equilibrium_state` matching each phase pair.
- Ensure shared components provide `phase_equilibrium_form` entries.
- For ideal two-phase bubble/dew usage, set bubble/dew method explicitly.

5. Add global options.
- Set `include_enthalpy_of_formation` explicitly when user preference is known.

6. Add package-level parameter data.
- Add binary interaction matrices (e.g., PR/SRK `kappa`) when required by EOS choice.

7. Add guard checks.
- Validate compatibility before returning configuration.
- Raise `ConfigurationError` for incompatible EOS/equilibrium combinations.

8. Export `configuration`.
- Provide representative default call for expected usage.

9. If class-definition option is selected.
- implement `GenericParameterData` subclass instead of factory dict export
- ensure `configure` and `parameters` cover all selected methods
- if custom state equations/interfaces are required, switch to
  `workflow/30_class_build.md` instead

## Hard Validation Gates (Must Pass Before Output)

1. Required key presence.
- All top-level required keys are present.

2. Compatibility checks.
- EOS is compatible with selected equilibrium state method.
- Bubble/dew method is compatible with selected phases and assumptions.

3. Equilibrium consistency.
- Every pair in `phases_in_equilibrium` has a matching entry in `phase_equilibrium_state`.
- Shared components across phase pairs define `phase_equilibrium_form`.

4. Method parameter completeness.
- Every selected pure/transport method has required parameter placeholders or values.

5. IDAES smoke checks.
- `GenericParameterBlock(**configuration)` constructs.
- Unit consistency check passes.
- Minimal unit-model smoke solve is feasible for in-scope behavior.

6. Class-definition option checks (if used).
- class inherits from `GenericParameterData`
- `configure` method sets all needed config options
- `parameters` method defines required parameters for chosen methods

## Useful References

- `references/generic_patterns.md`
- `references/eos_phase_equil.md`
- `references/state_definitions.md`
- `references/transport_props.md`
- `references/scaling_init.md`
- `references/mcp_search_tips.md`

## Template

- Default: `assets/templates/generic_property_package.py`
- On explicit class-definition request: `assets/templates/generic_property_package_class.py`
