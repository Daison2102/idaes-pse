# State Definitions

## Decision Table

1. `FTPx`.
- Use when total flow, temperature, pressure, and composition are natural user inputs.
- Good for simple flash-oriented interfaces.
- Watch for extra equilibrium burden at inlets in multiphase systems.

2. `FcTP`.
- Use when component molar flows are primary known quantities.
- Reduces dependence on composition constraints from mole fractions.

3. `FpcTP`.
- Use when phase-component flow detail is needed directly.
- Useful when phase split variables are central to model structure.

4. `FPhx` / `FcPh`.
- Use for enthalpy-driven formulations where pressure/enthalpy pairing is required.

## Selection Rules

1. Match state definition to unit model interfaces first.
2. Confirm a defined state yields DOF = 0 for intended block type.
3. For multiphase inlet-heavy models, avoid choices that force unnecessary flash effort when possible.

## Required Configuration Hooks

1. `state_definition`
2. `state_bounds` for all state variables exposed by the chosen definition
3. `pressure_ref`
4. `temperature_ref`

## Initialization and Constraint Notes

1. Respect `defined_state` behavior for inlet vs outlet constraints.
2. Ensure sum constraints are only added where appropriate for the chosen state definition behavior.
3. If custom state definition development is needed, include `always_flash` behavior per developer guidance.

## Codebase Pointers

- `idaes/models/properties/modular_properties/state_definitions/`
- Official IDAES state-definition documentation and in-repo modular examples
