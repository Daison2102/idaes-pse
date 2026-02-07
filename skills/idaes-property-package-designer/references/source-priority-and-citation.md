# Source Priority and Citation

## Source Order

1. Official IDAES code patterns from repository indexes (`codebase` MCP first; `repobase` fallback).
2. Official IDAES documentation from `grounded-docs` MCP.
3. External sources only if information is not present in 1 or 2.

## Decision Traceability Format
For each major technical choice, record:

- decision
- selected option
- primary source
- fallback source (if used)
- reason this source was authoritative

## Conflict Resolution

1. If local legacy examples conflict with official patterns, follow official patterns.
2. If docs and code diverge, prioritize current repository implementations, then note discrepancy.
3. If external references are used, mark them as supplemental.
