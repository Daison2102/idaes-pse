# Source Priority and Fallback

Enforce this order for information retrieval.

## Priority Order
1. `codebase` MCP
2. `grounded-docs` MCP
3. local repository fallback when MCP is unavailable
4. external sources only when required fields remain unresolved
5. web search for missing parameter placeholders

## Preflight Procedure
1. attempt MCP resource/template listing
2. if unavailable, record fallback mode
3. continue with local source files and documentation paths

## Fallback Paths in This Repository
1. `idaes/models/properties/modular_properties/examples/`
2. `idaes/models/properties/examples/`
3. `docs/explanations/components/property_package/general/`
4. `docs/how_to_guides/custom_models/property_package_development.rst`

## Reporting
Always include in output:
1. which source tiers were used
2. which tiers were unavailable
3. which parameters still require external confirmation
