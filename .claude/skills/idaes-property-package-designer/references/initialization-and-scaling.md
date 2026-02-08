# Initialization and Scaling

Treat initialization and scaling as required, not optional.

## Initialization
### Generic
1. set realistic `state_bounds`
2. provide good nominal values
3. call package/state initializer before solve checks

### Class-Based
1. implement `initialize` and `release_state`
2. preserve DOF during fix/unfix operations
3. separate defined-state and non-defined-state logic

## Scaling
1. assign scaling factors for state variables
2. add scaling for difficult constraints (equilibrium, phase split, bubble/dew)
3. for class-based path, use `CustomScalerBase` when needed

## Minimum Checks
1. no singular Jacobian error at initial state
2. bounded variables remain inside physical range
3. scaled model solves where unscaled model is unstable
