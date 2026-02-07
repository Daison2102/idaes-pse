# MCP Search Tips for IDAES Modules and Patterns

Use these tips with the `codebase` MCP (repo search) and `grounded-docs` MCP (official docs/examples).

## General patterns to search

- "modular_properties" for generic property framework
- "PhysicalParameterBlock" for class-based parameter blocks
- "StateBlockData" for custom state blocks
- "phase_equil" for equilibrium formulations
- "transport_properties" for viscosity/thermal conductivity

## Codebase MCP: high-signal paths

- `idaes/models/properties/modular_properties/`
- `idaes/models/properties/modular_properties/state_definitions/`
- `idaes/models/properties/modular_properties/eos/`
- `idaes/models/properties/modular_properties/phase_equil/`
- `idaes/models/properties/modular_properties/pure/`
- `idaes/models/properties/modular_properties/transport_properties/`
- `idaes/models/properties/tests/test_harness.py`

## Suggested MCP search queries

- "configuration = {" to find generic configuration dicts
- "get_prop(" for factory-style generic package builders
- "_phase_dicts_ideal" and "_phase_dicts_pr" for standard phase layout
- "_component_params" for component master dictionaries
- "phase_equilibrium_form" for VLE/LLE patterns
- "phases_in_equilibrium" and "phase_equilibrium_state" for phase-state wiring
- "equation_of_state_options" for EOS-specific options
- "visc_d_phase" and "therm_cond_phase" for transport wiring
- "viscosity_phi_ij_callback" for Wilke transport options
- "define_metadata" for property metadata patterns
- "get_material_flow_terms" for required interface methods

## Grounded-docs MCP hints

- Search for "Generic Property Package" and "modular properties" pages
- Search for "Property Package" + "state definition"
- Search for "phase equilibrium" + "fugacity"

## When to use external sources

- Only when required data or examples are missing from codebase and grounded-docs
- Use web search for placeholder parameter values and record sources

## Compare-Against Pattern

Before finalizing a generic package, compare your output against:

- IDAES modular examples under `idaes/models/properties/modular_properties/examples/`
- the enforced pattern in `assets/templates/generic_property_package.py`
