# Validation Checklist

Use this checklist before final delivery.

## Build Checks
1. package module imports
2. parameter block constructs
3. state block constructs
4. units are consistent

## Model Checks
1. DOF is correct for tested states
2. state bounds are present and sensible
3. required properties are constructible

## Initialization Checks
1. initialization runs without structural failure
2. release_state behavior is correct

## Solve Checks
1. solver termination is optimal (if solver available)
2. key property values are finite and physically plausible

## Test Checks
1. pytest file exists
2. each test has exactly one required marker (`unit`, `component`, `integration`, `performance`)
3. smoke tests pass

## Delivery Checks
1. parameter ledger includes source and units for each value
2. unresolved placeholders are explicitly listed
3. commands used for validation are reported
