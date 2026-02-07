# Property Method Catalog

## Purpose
Guide selection of property methods and parameter requirements for package design.

## Selection Matrix

1. `Core thermodynamic methods`
- Ideal gas/liquid and cubic EOS methods.
- Pure-component correlations for heat capacity, enthalpy, entropy, and saturation pressure.

2. `Phase equilibrium methods`
- Equilibrium forms per component and phase pair.
- Equilibrium state formulation methods.
- Bubble/dew methods where required.

3. `Transport methods` (optional)
- Viscosity and thermal conductivity methods.
- Mixture rule methods when in scope.

## Method Selection Rules

1. Prefer official built-in methods available in the current IDAES repo.
2. Confirm parameter availability before method commitment.
3. Enforce consistent units and validity ranges.
4. Record each method decision and required parameters in the design table.

## Required Design Table Columns

- property name
- selected method
- required parameters
- data source
- validity range
- notes on scaling impact
