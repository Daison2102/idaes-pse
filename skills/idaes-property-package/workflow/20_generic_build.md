# Build with Generic Property Package Framework

Use this when standard IDAES modular methods and EOS cover the needed properties.

## Step-by-step checklist

1. Create the configuration dict skeleton.
- Use the template in `assets/templates/generic_property_package.py`.

2. Define components.
- Add each component under `components`.
- Set `type`, `valid_phase_types`, and `elemental_composition`.
- Assign pure-component property methods.

3. Define phases.
- Add each phase under `phases`.
- Set phase `type`.
- Set `equation_of_state` per phase.
- Add EOS options if required.

4. Configure phase equilibrium.
- Set `phase_equilibrium` mapping.
- Add `phase_equilibrium_form` for components.
- Add `phase_equilibrium_options` if needed.

5. Add parameter data.
- Populate `parameter_data` for each component.
- Include units and validity ranges.
- Record sources for each parameter.

6. Add transport properties.
- Set `visc_d_phase` and `therm_cond_phase` per phase.
- Add transport options and mixing rules.

7. Choose and set the state definition.
- Set `state_definition` to FTPx, FpcTP, etc.
- Add any `state_bounds` if needed.

8. Set base units.
- Confirm unit consistency across all parameters.

9. Add scaling.
- Use default scaling where available.
- Add custom scaling for key vars/constraints.

10. Add initialization guidance.
- Use IDAES initializer where possible.
- Document any required initial guesses.

11. Validate.
- Run the harness tests and unit consistency checks.

## Useful References

- `references/generic_patterns.md`
- `references/eos_phase_equil.md`
- `references/transport_props.md`
- `references/scaling_init.md`
- `references/mcp_search_tips.md`

## Template

Start from `assets/templates/generic_property_package.py`.
