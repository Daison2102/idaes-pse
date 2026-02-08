# Source Priority and Citation Rules

This skill must gather knowledge with strict precedence.

## Priority Order

1. Indexed IDAES repository (codebase MCP / repobase).
2. Indexed IDAES docs and examples (grounded-docs MCP).
3. External sources only when information is missing from 1-2.
4. For missing parameter placeholders, perform targeted web search from trusted references.

## Canonical vs Informational Sources

1. Canonical for APIs and patterns: official IDAES code/docs.
2. Informational for missing numerical parameters: trusted thermodynamic references.

## Trusted External Parameter Sources

1. NIST WebBook.
2. Perry's Chemical Engineers' Handbook.
3. Poling/Prausnitz/O'Connell (Properties of Gases and Liquids).
4. DIPPR (if available).

## Citation Requirements

Every parameter should have provenance metadata, minimally:
1. Source name.
2. Data location (table/section/page or URL).
3. Retrieval date for web sources.
4. Unit basis before/after conversion.

Recommended inline style:

```python
"mw": (0.01801528, pyunits.kg/pyunits.mol),  # NIST WebBook, retrieved 2026-02-08
```

## Gap Policy

If parameter values are unavailable:
1. Mark placeholder explicitly with TODO.
2. Include target source suggestion.
3. Do not silently fabricate values.

## Conflict Resolution

If sources disagree:
1. Prefer official IDAES example values when reproducing known methods.
2. Otherwise prefer source with clearer units and traceability.
3. Record resolution rationale in comments or summary.
