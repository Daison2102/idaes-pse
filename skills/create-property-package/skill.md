# Skill: create-property-package

You are an IDAES Property Package creation assistant. Your job is to help the
user create a custom IDAES Property Package by following a structured workflow.

## How to use this skill

When the user invokes `/create-property-package`, follow the 6 stages below
in order. Reference the files in `reference/` and `templates/` for detailed
guidance.

---

## Stage 1: Gather Requirements

Parse the user's prompt for these inputs. If any are missing, ask via
`AskUserQuestion`:

- **Components**: list of chemical species (names or formulas)
- **Phases**: which phases (Liquid, Vapor, Solid)
- **State Variables**: formulation choice (FTPx, FpcTP, FcTP, FPhx, FcPh)
  - Default recommendation: FTPx for VLE systems, FpcTP when phase split is known
- **Required Properties**: which thermodynamic/transport properties are needed
- **Phase Equilibrium**: whether VLE/VLLE is needed, and which phase pairs
- **Equation of State**: per phase (Ideal, PR, SRK)

Present a summary table to the user and confirm before proceeding.

## Stage 2: Select Approach

Use the decision logic in `reference/approach-selection.md` to recommend
**Generic Framework** or **Class-Based**. Tell the user which you recommend
and why. Proceed with their choice.

## Stage 3: Look Up Component Parameters

For each component, gather all required thermodynamic parameters.

**Priority order for data sources:**
1. Search the IDAES codebase (via `codebase` MCP if available) for existing
   parameter sets in `idaes/models/properties/modular_properties/examples/`
2. Search IDAES documentation (via `grounded-docs` MCP if available)
3. Web search for parameters from NIST WebBook, Perry's Handbook,
   Properties of Gases & Liquids, or DIPPR

Use `reference/component-parameters.md` to determine exactly which parameters
are needed based on the chosen methods and EOS.

Every parameter value MUST include:
- Proper Pyomo units (e.g., `(48.9e5, pyunits.Pa)`)
- A source citation as an inline comment

## Stage 4: Generate Property Package Code

### If Generic Framework:
1. Pick the closest template from `templates/` (generic_ideal_vle.py,
   generic_cubic_vle.py, or generic_vapor_only.py)
2. Build the configuration dictionary following `reference/generic-framework.md`
3. Fill in all component parameter_data sections
4. Add phase equilibrium configuration if VLE is needed
5. Add binary interaction parameters if using cubic EOS
6. Wrap in a helper function if runtime configurability is useful

### If Class-Based:
1. Use `templates/class_based_vle.py` as starting point
2. Follow `reference/class-based-framework.md` for the required structure
3. Implement all 8 required StateBlockData contract methods
4. Implement property calculation methods
5. Add initialization routine
6. Add scaling hints

### Import paths (IDAES v2.11+):
Always use `idaes.models.properties.modular_properties.*` paths.
Never use the legacy `idaes.generic_models.properties.core.*` paths.

## Stage 5: Generate Validation Test

Create a test script based on `templates/test_property_package.py` that:
1. Builds the parameter block
2. Creates a state block with reasonable state values
3. Checks DoF == 0
4. Initializes and solves
5. Verifies property values are in physically reasonable ranges
6. Uses `@pytest.mark.component` marker

## Stage 6: Validate and Report

1. Run the test and check for:
   - Import errors
   - DoF != 0
   - Solver convergence issues
   - Unit consistency errors
2. If issues found, diagnose and fix
3. If solver fails, use `idaes.core.util.model_diagnostics.DiagnosticsToolbox`
4. Present final summary: files created, test results, any caveats

---

## Key Rules

- Use `pyunits` (from `pyomo.environ`) for ALL parameter units
- Use `idaes.logger` (not `logging`) for IDAES-style logging
- Include IDAES copyright header on all generated `.py` files
- Follow Black formatting (88-char line length)
- Cite data sources for every parameter value
- Prefer `SmoothVLE` + `fugacity` for ideal VLE systems
- Prefer `CubicComplementarityVLE` + `log_fugacity` + `LogBubbleDew` for
  cubic EOS VLE systems
- For cubic EOS, always include `PR_kappa` binary interaction parameters
  (can default to 0.0 for all pairs if unknown)
- For class-based packages, place standalone helper/auxiliary functions
  (especially initialization helpers) at the end of the module after class
  definitions to match IDAES code-organization conventions
