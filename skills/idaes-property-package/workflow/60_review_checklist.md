# Final Review Checklist (Class-Based Packages)

Use this checklist right before returning a class-based property package.

## PhysicalParameterBlock contract

1. `PhysicalParameterBlock` subclass exists.
2. `component_list` is defined.
3. `phase_list` is defined.
4. State block linkage is set (`state_block_class` or `_state_block_class`).
5. If elemental balances/reactions are in scope:
- `element_list` exists.
- `element_comp` exists and covers all components.

## State block contract

1. `StateBlock`/`StateBlockData` classes are defined and linked correctly.
2. State variables are declared with units and sensible defaults/bounds.
3. Required interface methods are implemented:
- `get_material_flow_terms`
- `get_enthalpy_flow_terms`
4. Optional density interface methods are implemented when required by target unit models.

## Metadata contract

1. `define_metadata` is implemented in the parameter block.
2. `add_default_units(...)` is present.
3. `add_properties(...)` is present.
4. Every metadata-registered property has a valid construction path
   (`method=None` for direct vars, or a valid method/expression name).

## Validation gates

1. Units consistency check passes.
2. Defined-state DOF check is satisfied.
3. Initialization path runs without errors.
4. Minimal smoke test builds a state block and touches metadata-registered properties.

## Return-quality checks

1. Code/comments match requested style and naming.
2. Assumptions and placeholders are explicitly documented.
3. External parameter sources are cited when placeholders were used.
