# Equilibrium Patterns

Use these patterns when phase equilibrium is requested.

## No Equilibrium
Do not set:
1. `phases_in_equilibrium`
2. `phase_equilibrium_state`
3. `bubble_dew_method`

## Ideal VLE Pattern
Recommended settings:
1. `phases_in_equilibrium = [("Vap", "Liq")]`
2. `phase_equilibrium_state = {("Vap", "Liq"): SmoothVLE}`
3. `bubble_dew_method = IdealBubbleDew`
4. component `phase_equilibrium_form = {("Vap", "Liq"): fugacity}`

## Cubic VLE Pattern (PR/SRK)
Recommended settings:
1. both phases use `Cubic` EOS with `CubicType.PR` or `CubicType.SRK`
2. `phase_equilibrium_state = {("Vap", "Liq"): CubicComplementarityVLE}`
3. `bubble_dew_method = LogBubbleDew`
4. component `phase_equilibrium_form = {("Vap", "Liq"): log_fugacity}`
5. define package `parameter_data` binary interaction map (e.g., `PR_kappa`)

## Validations
Check:
1. phase pair keys match declared phases
2. components participating in both phases have equilibrium form
3. required bubble/dew dependencies exist
