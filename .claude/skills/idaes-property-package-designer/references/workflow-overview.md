# Workflow Overview

Execute these stages in order.

1. Preflight: detect MCP/tool availability and fallback mode.
2. Requirements normalization: parse components, phases, state definition, properties, equilibrium, EOS.
3. Property profile resolution: apply `minimum` or `comprehensive` and user overrides.
4. Approach selection: choose Generic or class-based path.
5. Parameter plan: enumerate required parameters and sources.
6. Code generation: scaffold package modules from templates/scripts.
7. Validation generation: scaffold pytest and smoke checks.
8. Repair loop: patch until checks pass or blockers are explicit.
9. Delivery: return package, tests, parameter ledger, assumptions, and commands.

Load only the detailed reference files needed for the current stage.
