# Approach Selection

Use this decision policy to choose between Generic and Class-based property package implementations.

## Decision Priority

1. Feasibility.
2. Maintainability.
3. User preference.

## Default

Use the Generic framework unless there is a concrete reason it cannot satisfy requirements.

## Choose Generic Framework When

1. Required properties are available through modular property methods.
2. EOS and equilibrium forms are supported by modular framework options.
3. State definition is one of: `FTPx`, `FpcTP`, `FcTP`, `FPhx`, `FcPh`.
4. The package does not require bespoke constitutive equations outside available method libraries.
5. User prioritizes speed and reuse.

## Choose Class-Based When

1. Any required property requires custom equations not available in modular method libraries.
2. Non-standard state-variable definitions are required.
3. Custom coupling constraints are required between properties beyond generic framework capabilities.
4. Specialized initialization behavior is needed that is awkward or impossible in generic config only.
5. User explicitly requests full control and accepts greater implementation/test burden.

## Tie-Breaker Rules

1. If both are feasible, choose Generic.
2. If user explicitly asks for Class-based and no hard blocker exists, honor user choice.
3. If user asks for Generic but feasibility fails, report blocker and switch to Class-based with clear rationale.

## Evidence to Collect Before Finalizing Decision

1. Similar official example package from `idaes/models/properties/modular_properties/examples/` or class-based examples.
2. Confirmed method/EOS compatibility from docs and code.
3. Required-properties coverage table showing no unresolved minimum entries.

## Generic Conventions to Prefer

For Generic branch structure and style, prioritize patterns similar to modern `get_prop(...)` dictionary assembly style:
1. Separate reusable component/phase dictionaries.
2. Assemble final config from user-selected components/phases.
3. Add package-wide interaction parameters centrally.
4. Keep imports and APIs aligned with current `idaes.models.properties.modular_properties` paths.
