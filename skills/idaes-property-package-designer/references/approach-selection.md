# Approach Selection

## Decision Rules

1. Select `Generic` if all required thermodynamic behavior can be represented using standard IDAES modular property components and existing state definitions.
2. Select `Custom` if you need non-standard state variables, custom balance term expressions, or property equations not cleanly expressible through the Generic framework configuration.
3. Select `Generic` when schedule risk is high and a reliable first implementation is needed quickly.
4. Select `Custom` when extensibility and mathematical control outweigh implementation speed.

## Required Decision Record
Document all fields:

- `chosen_approach`: `generic` or `custom`
- `justification`: 3-5 bullets
- `rejected_alternative`: short reason
- `migration_path`: how to pivot later if requirements grow

## Heuristic Signals

### Signals for Generic
- Standard VLE/LLE/VLLE relationships with built-in formulations.
- Existing EOS and pure-component methods cover required outputs.
- Need rapid integration with existing unit models.

### Signals for Custom
- Special constitutive equations and custom closure constraints.
- Need direct control of `StateBlockData` internals.
- Requirement for custom initialization sequence across unique constraints.
