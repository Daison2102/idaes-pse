# Generic Framework Playbook

Use this playbook when the selected approach is Generic Property Framework.

## Target Imports

Use current import paths:
1. `idaes.models.properties.modular_properties.base.generic_property import GenericParameterBlock`
2. `idaes.models.properties.modular_properties.state_definitions import FTPx, FpcTP, FcTP, FPhx, FcPh`
3. EOS modules from `idaes.models.properties.modular_properties.eos`
4. Equilibrium modules from `idaes.models.properties.modular_properties.phase_equil`
5. Pure/transport methods from modular method libraries

Do not use legacy `idaes.generic_models...` imports in new outputs.

## Build Sequence

1. Build component dictionary.
2. Build phase dictionary.
3. Define base units.
4. Assign state definition and bounds.
5. Add reference state.
6. Add equilibrium configuration when needed.
7. Add package-wide parameters (for example binary interactions).
8. Instantiate: `GenericParameterBlock(**configuration)`.

## Minimum Configuration Keys

1. `components`
2. `phases`
3. `base_units`
4. `state_definition`
5. `state_bounds`
6. `pressure_ref`
7. `temperature_ref`

Optional but common:
1. `phases_in_equilibrium`
2. `phase_equilibrium_state`
3. `bubble_dew_method`
4. package `parameter_data`

## Generic Skeleton Pattern

```python
configuration = {
    "components": {...},
    "phases": {...},
    "base_units": {
        "time": pyunits.s,
        "length": pyunits.m,
        "mass": pyunits.kg,
        "amount": pyunits.mol,
        "temperature": pyunits.K,
    },
    "state_definition": FTPx,
    "state_bounds": {...},
    "pressure_ref": (101325, pyunits.Pa),
    "temperature_ref": (298.15, pyunits.K),
}
```

## Optional Factory Function Pattern

Use a factory function when users need configurable subsets/components/phases:
1. start from reusable component/phase templates;
2. subset based on user input;
3. patch equilibrium and package parameters based on selected phases/eos;
4. return final config dict.

## Equilibrium Notes

1. `phase_equilibrium_form` is usually defined per component.
2. `phases_in_equilibrium` and `phase_equilibrium_state` are package-level.
3. Choose form and state method consistent with EOS:
1. Ideal patterns often use fugacity-based forms and smooth VLE methods.
2. Cubic EOS patterns often use log-fugacity and cubic-appropriate equilibrium methods.

## Cubic EOS Notes

1. Include `equation_of_state_options` with `CubicType`.
2. Include package-level interaction parameter map (for example `PR_kappa`).
3. Ensure all component pairs are present.

## Output Expectations

The generated Generic package should include:
1. clean config dict.
2. method-parameter coverage comments.
3. source comments for parameter provenance.
4. compatibility with `GenericParameterBlock(**configuration)`.
