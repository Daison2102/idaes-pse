# Build with Generic Property Package Framework

Use this when standard IDAES modular methods and EOS cover the needed properties.

## Required Structure (Default)

The generic path must use the enforced module pattern:

1. Module skeleton:
- start with `# pylint: disable=all`
- import order: Python stdlib -> Pyomo units -> IDAES modules
- define `_log = logging.getLogger(__name__)`

2. EOS selection primitive:
- define `EosType` enum with `PR` and `IDEAL`

3. Phase dictionaries:
- define `_phase_dicts_pr`
- define `_phase_dicts_ideal`

4. Component dictionary:
- define `_component_params` with component methods and `parameter_data`
- each parameter group must include source comments and units (or explicit unitless marker)

5. Factory builder:
- define `get_prop(components=None, phases=..., eos=..., scaled=False)`
- builder must assemble `components`, `phases`, base units, state definition, bounds, references
- if multiple phases selected, include equilibrium state mapping

6. Export:
- define module-level `configuration = get_prop(...)`

## Step-by-step checklist

1. Copy the standards template.
- Start from `assets/templates/generic_property_package.py` and keep section order.

2. Populate `_component_params`.
- Add each component with `type`, `valid_phase_types`, composition, methods, and `parameter_data`.
- For each parameter group, include source comment and validity range note where relevant.

3. Populate phase dicts.
- Add EOS and transport choices in `_phase_dicts_pr` / `_phase_dicts_ideal`.
- Add `transport_property_options` where needed (e.g. Wilke callback).

4. Implement `get_prop(...)`.
- Select components/phases from master dicts via `copy.deepcopy`.
- Add phase equilibrium entries when two-phase system is selected.
- Add optional PR binary parameter defaults when `eos == EosType.PR`.

5. Add module-level `configuration`.
- Build a default configuration representative of intended use.

6. Validate structure and physics.
- Construct `GenericParameterBlock(**configuration)`.
- Run `assert_units_consistent` on a minimal model.
- Run at least one minimal unit-model solve (Flash for VLE packages).

## Useful References

- `references/generic_patterns.md`
- `references/eos_phase_equil.md`
- `references/transport_props.md`
- `references/scaling_init.md`
- `references/mcp_search_tips.md`

## Template

Start from `assets/templates/generic_property_package.py` and preserve its section order.
