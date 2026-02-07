# State Definitions

## Step-by-step checklist

1. Identify required variables from unit models.
- Do unit models require T/P or component flows?

2. Choose a standard definition.
- FTPx: T, P, phase/component mole fractions.
- FpcTP: component flow, T, P.

3. Confirm degrees of freedom.
- Ensure a defined state has DOF = 0.

4. Set bounds and scaling.
- Add reasonable bounds for state variables.
- Apply scaling to avoid ill-conditioning.

## Guidance

- Use FTPx for flash and VLE-heavy workflows.
- Use FpcTP for component flow-based state equations.

## Codebase pointers

- `idaes/models/properties/modular_properties/state_definitions/`

Pick the state definition that matches the unit model requirements and expected DOF.
