# Parameter Sourcing

Follow strict source priority.

## Priority
1. `codebase` MCP indexed IDAES source
2. `grounded-docs` MCP indexed IDAES documentation
3. external sources only if missing above
4. web search specifically for missing parameter placeholders

## External Preferred Sources
1. NIST WebBook
2. Perry's Chemical Engineers' Handbook
3. Poling, Prausnitz, O'Connell
4. DIPPR (if accessible)

## Ledger Requirements
Track each parameter with:
1. name
2. value
3. units
4. applies_to (component/phase/package)
5. source
6. retrieved_on (YYYY-MM-DD)
7. confidence (`high`, `medium`, `low`)
8. notes

Use `scripts/build_parameter_ledger.py` to create or update ledger files.

## Placeholders
If a parameter is unresolved:
1. add placeholder value or TODO marker
2. set confidence to `low`
3. explain impact on validation
4. keep unresolved items in delivery summary
