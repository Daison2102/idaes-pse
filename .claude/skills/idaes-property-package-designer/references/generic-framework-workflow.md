# Generic Framework Workflow

Use this path for modular property packages.

## Imports (modern paths)
Use:
1. `idaes.models.properties.modular_properties.base.generic_property.GenericParameterBlock`
2. `idaes.models.properties.modular_properties.state_definitions.*`
3. `idaes.models.properties.modular_properties.eos.ideal.Ideal`
4. `idaes.models.properties.modular_properties.eos.ceos.Cubic, CubicType`
5. `idaes.models.properties.modular_properties.phase_equil.*`
6. `idaes.models.properties.modular_properties.pure.*`

## Build Configuration Sections
Define these top-level keys in order:
1. `components`
2. `phases`
3. `base_units`
4. `state_definition`
5. `state_bounds`
6. `pressure_ref`
7. `temperature_ref`
8. optional equilibrium keys
9. package `parameter_data` (for binary params such as `PR_kappa`)

## Component Definition Pattern
For each component, include:
1. `type`
2. optional `elemental_composition`
3. method pointers for required properties
4. `parameter_data` values with units
5. optional `phase_equilibrium_form`

## Phase Definition Pattern
For each phase, include:
1. `type`
2. `equation_of_state`
3. optional `equation_of_state_options`
4. optional phase `component_list`

## Equilibrium Configuration
If equilibrium is enabled:
1. set `phases_in_equilibrium`
2. set `phase_equilibrium_state` by pair
3. set `bubble_dew_method` when needed
4. ensure component `phase_equilibrium_form` is present for participating species

## Optional Builder Style
For reusable family packages, follow `get_prop()` style:
1. static component/phase dictionaries
2. runtime subset selection for components/phases
3. EOS switching enum

## Templates
Start from one template:
1. `templates/generic/config_minimal_single_phase.py`
2. `templates/generic/config_ideal_vle_ftpx.py`
3. `templates/generic/config_cubic_vle.py`
4. `templates/generic/config_builder_get_prop_style.py`
