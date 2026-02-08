# State Definitions Map

Choose one state definition and keep all bounds consistent.

## FTPx
State variables:
1. `flow_mol`
2. `temperature`
3. `pressure`
4. `mole_frac_comp`

Use for:
1. common process modeling interfaces
2. straightforward feed/product specification

## FpcTP
State variables:
1. `flow_mol_phase_comp`
2. `temperature`
3. `pressure`

Use for:
1. explicit phase-component flow specification
2. phase-partitioned inlet specification

## FcTP
State variables:
1. `flow_mol_comp`
2. `temperature`
3. `pressure`

Use for:
1. explicit component flow specification without direct phase split

## FPhx
State variables:
1. `flow_mol`
2. `pressure`
3. `enth_mol`
4. composition variable set by package

Use for:
1. energy-specified calculations
2. flashes and energy-coupled calculations

## FcPh
State variables:
1. `flow_mol_comp`
2. `pressure`
3. `enth_mol`

Use for:
1. component-flow + enthalpy-specified calculations

## Bound Guidance
Always provide:
1. lower bound
2. nominal value
3. upper bound
4. units

Set physically realistic bounds and avoid extreme defaults.
