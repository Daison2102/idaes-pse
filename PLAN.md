# Skill Plan: `create-property-package`

## Purpose

A Claude Code skill that guides users through the systematic creation of IDAES
Property Packages. The skill supports both official approaches:

1. **Generic Framework** - Configuration-dictionary-based approach using
   `GenericParameterBlock` (recommended for most use cases)
2. **Class-Based** - From-scratch implementation by subclassing
   `PhysicalParameterBlock` and `StateBlockData` (for maximum control)

## Skill Invocation

```
/create-property-package
```

The user's prompt provides the key inputs:
- Components list
- Phases list
- State variables (FTPx, FpcTP, FcTP, FPhx, FcPh)
- Required properties
- Whether equilibrium is required and phase pairs
- Equation of state per phase (Ideal, PR, SRK)

---

## Skill File Layout

```
.claude/skills/create-property-package/
├── PLAN.md                          # This file - master plan
├── skill.md                         # Skill prompt (entry point for Claude Code)
├── reference/
│   ├── approach-selection.md        # Decision logic for Generic vs Class-Based
│   ├── generic-framework.md         # Detailed guide for the generic approach
│   ├── class-based-framework.md     # Detailed guide for the class-based approach
│   ├── component-parameters.md      # Parameter data requirements per EOS/method
│   ├── available-methods.md         # Catalog of all available IDAES methods
│   └── validation-checklist.md      # Post-generation validation steps
└── templates/
    ├── generic_ideal_vle.py         # Template: Generic + Ideal EOS + VLE
    ├── generic_cubic_vle.py         # Template: Generic + Cubic EOS (PR/SRK) + VLE
    ├── generic_vapor_only.py        # Template: Generic + single vapor phase
    ├── class_based_vle.py           # Template: Class-based + VLE
    └── test_property_package.py     # Template: validation test script
```

---

## Workflow Stages

The skill executes in **6 sequential stages**. Each stage produces concrete
outputs and feeds into the next.

### Stage 1: Gather Requirements

**Input**: User prompt (components, phases, state vars, properties, EOS, equilibrium)

**Actions**:
1. Parse the user prompt for:
   - Component names and formulas
   - Phase types (Liquid, Vapor, Solid)
   - State variable formulation (FTPx, FpcTP, FcTP, FPhx, FcPh)
   - Required thermodynamic properties
   - Phase equilibrium requirements (VLE pairs, equilibrium form)
   - EOS choice per phase (Ideal, PR, SRK)
2. If any critical info is missing, ask the user via `AskUserQuestion`
3. Determine the recommended approach (see [approach-selection.md](reference/approach-selection.md))

**Output**: Structured requirements summary shown to the user for confirmation

### Stage 2: Select Approach

**Decision Logic**: See [approach-selection.md](reference/approach-selection.md)

| Condition | Recommended Approach |
|-----------|---------------------|
| Standard EOS (Ideal, PR, SRK) + standard property methods | Generic Framework |
| Custom correlations or non-standard equations | Class-Based |
| Electrolyte systems with standard IDAES support | Generic Framework |
| Unusual state definitions not in IDAES | Class-Based |
| User explicitly requests one approach | Honor user choice |

**Output**: Chosen approach communicated to the user with rationale

### Stage 3: Look Up Component Parameters

**Actions**:
1. Search IDAES documentation and codebase for existing parameter data
   (via `codebase` MCP and `grounded-docs` MCP)
2. Check `idaes/models/properties/modular_properties/examples/` for similar systems
3. For missing parameters, search the web for thermodynamic data from:
   - NIST WebBook
   - Perry's Chemical Engineers' Handbook
   - The Properties of Gases and Liquids (Poling, Prausnitz, O'Connell)
   - DIPPR Database
4. Record data sources as inline comments

**Required Parameters by Method**: See [component-parameters.md](reference/component-parameters.md)

**Output**: Complete parameter dataset for all components, with units and references

### Stage 4: Generate Property Package Code

**Actions** (approach-dependent):

#### Generic Framework Path
See [generic-framework.md](reference/generic-framework.md)

1. Build configuration dictionary with all sections:
   - `components` (with types, methods, parameter_data)
   - `phases` (with types, EOS, EOS options)
   - `base_units`
   - `state_definition` and `state_bounds`
   - `pressure_ref`, `temperature_ref`
   - Phase equilibrium config (if VLE)
   - `parameter_data` (binary interaction params if cubic EOS)
2. Select appropriate templates from `templates/`
3. Fill in all parameter values
4. Add optional helper function (like `get_prop()` in methanol example) if
   the package needs runtime configurability

#### Class-Based Path
See [class-based-framework.md](reference/class-based-framework.md)

1. Create `PhysicalParameterBlock` subclass:
   - `build()`: phases, components, all Params
   - `define_metadata()`: properties metadata + units
2. Create `StateBlock` container class:
   - `initialize()` method
   - `release_state()` method
3. Create `StateBlockData` subclass:
   - `build()`: state variables + supporting variables/constraints
   - Required contract methods (8 methods)
   - On-demand property methods
   - Phase equilibrium constraints (if VLE)
   - Bubble/dew point calculations (if VLE)
4. Add scaling hints

**Output**: Complete Python module(s) for the property package

### Stage 5: Generate Validation Test

**Actions**:
1. Generate a test script using the template in `templates/test_property_package.py`
2. The test should:
   - Build the parameter block
   - Create a state block
   - Fix state variables to reasonable values
   - Check degrees of freedom == 0
   - Initialize the state block
   - Solve and check termination condition
   - Verify key property values against expected ranges
   - Use `@pytest.mark.component` marker
3. Optionally: test with a simple unit model (Heater or Flash)

**Output**: Test file alongside the property package

### Stage 6: Validate and Report

**Actions**:
1. Run the generated test
2. Check for common issues:
   - Import errors
   - Degrees of freedom != 0
   - Solver convergence failures
   - Unit consistency errors
3. If issues found, diagnose and fix iteratively
4. Run IDAES `DiagnosticsToolbox` if solver fails
5. Present final summary to the user

**Output**: Working property package + passing test + summary

---

## Knowledge Source Priority

When the skill needs information (parameter data, API details, patterns):

1. **IDAES Repository** (`codebase` MCP) - Search the indexed codebase for
   existing examples, base class APIs, and available methods
2. **IDAES Documentation** (`grounded-docs` MCP) - Search indexed docs for
   tutorials, how-to guides, and API reference
3. **Web Search** - Only when parameters are missing from sources 1-2.
   Use NIST WebBook, Perry's, etc. for thermodynamic data.

---

## Import Path Reference (Current IDAES v2.11+)

```python
# Core
from idaes.core import (LiquidPhase, VaporPhase, SolidPhase, Component,
                         PhaseType, PhysicalParameterBlock, StateBlockData,
                         StateBlock, declare_process_block_class,
                         MaterialFlowBasis, MaterialBalanceType,
                         EnergyBalanceType)

# Generic Framework
from idaes.models.properties.modular_properties.base.generic_property import (
    GenericParameterBlock)

# State Definitions
from idaes.models.properties.modular_properties.state_definitions import (
    FTPx, FpcTP, FcTP, FPhx, FcPh)

# Equations of State
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.eos.ceos import Cubic, CubicType

# Phase Equilibrium
from idaes.models.properties.modular_properties.phase_equil import (
    SmoothVLE, CubicComplementarityVLE)
from idaes.models.properties.modular_properties.phase_equil.bubble_dew import (
    IdealBubbleDew, LogBubbleDew)
from idaes.models.properties.modular_properties.phase_equil.forms import (
    fugacity, log_fugacity)

# Pure Component Methods
from idaes.models.properties.modular_properties.pure import (
    NIST, RPP4, RPP5, Perrys, ConstantProperties,
    ChapmanEnskogLennardJones, Eucken)

# Transport Properties
from idaes.models.properties.modular_properties.transport_properties import (
    ViscosityWilke, ThermalConductivityWMS, NoMethod)
```

---

## Design Principles

1. **Configuration over code** - Prefer the Generic Framework unless the user
   truly needs custom equations
2. **Units everywhere** - All parameters must have Pyomo units attached
3. **Source everything** - Every parameter value must have an inline comment
   citing its data source
4. **Test immediately** - Generate and run a validation test before declaring
   success
5. **Use current IDAES patterns** - Follow `idaes.models.properties.modular_properties`
   import paths (not the legacy `idaes.generic_models` paths)
6. **Minimal viable package** - Only include properties the user actually needs;
   do not over-specify
