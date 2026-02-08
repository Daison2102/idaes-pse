# Approach Selection

Select approach using these rules.

## Prefer Generic Framework
Use Generic when all of the following are true:
1. EOS and methods are supported by `idaes.models.properties.modular_properties`.
2. State definition is one of `FTPx`, `FpcTP`, `FcTP`, `FPhx`, `FcPh`.
3. Required properties can be expressed with available modular methods.
4. No custom residual forms or unusual coupling are required.

## Use Class-Based Implementation
Use class-based when any of the following is true:
1. Required property correlations are not in modular method libraries.
2. Nonstandard state representation is required.
3. Specialized initialization/scaling behavior is essential.
4. Custom algebraic forms are required for performance or research goals.

## User Override
1. If user explicitly requests one approach, honor it.
2. Emit risk notes when user choice conflicts with recommended approach.

## Output
Always report:
1. selected approach
2. reason
3. known risks
4. fallback plan if generation fails
