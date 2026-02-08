# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IDAES PSE (Institute for the Design of Advanced Energy Systems - Process Systems Engineering) is a Pyomo-based Python framework for modeling, simulating, and optimizing chemical/energy process systems. It provides base classes for unit models, property packages, and control volumes that build on Pyomo's algebraic modeling language.

## Common Commands

### Installation (development)
```bash
pip install -r requirements-dev.txt   # installs in editable mode with all extras
```

### Running Tests
```bash
# All tests (excludes integration and performance by default)
pytest --pyargs idaes

# Single test file
pytest idaes/core/base/tests/test_unit_model.py

# Single test method
pytest idaes/core/base/tests/test_unit_model.py::TestClassName::test_method_name

# By marker
pytest --pyargs idaes -m unit          # fast tests, no solver needed, <2s each
pytest --pyargs idaes -m component     # may require a solver
pytest --pyargs idaes -m integration   # long-running tests

# With coverage
pytest -c pytest-dev.ini --pyargs idaes
```

### Code Formatting & Linting
```bash
black .                                              # format (line length 88)
pylint --rcfile=./.pylint/pylintrc --disable=R idaes # lint
```

### Building Documentation
```bash
cd docs && python build.py --timeout 600
```

## Test Markers

Every test **must** have exactly one of these markers: `@pytest.mark.unit`, `@pytest.mark.component`, `@pytest.mark.integration`, or `@pytest.mark.performance`. Tests will fail without one.

Platform-specific markers: `@pytest.mark.linux`, `@pytest.mark.win32`, `@pytest.mark.darwin`, and negated forms like `@pytest.mark.nowin32`.

Performance tests are opt-in only via `--performance` flag.

## Project Structure

```
idaes-pse/
├── idaes/                              # Main package
│   ├── core/                           # Framework core
│   │   ├── base/                       # Base classes (unit_model, property_base, control_volume0d/1d, costing_base, etc.)
│   │   ├── initialization/             # Initialization framework (InitializerBase, BlockTriangularization)
│   │   ├── scaling/                    # Scaling/normalization (CustomScalerBase, autoscaling)
│   │   ├── solvers/                    # Solver integration (get_solver, homotopy, PETSc)
│   │   ├── plugins/                    # Pyomo transformation plugins
│   │   └── util/                       # Utilities (model_diagnostics, model_statistics, tables, exceptions)
│   ├── models/                         # Standard unit models
│   │   ├── unit_models/                # Feed, heater, flash, mixer, separator, HX, CSTR, PFR, pipe, etc.
│   │   ├── properties/                 # Standard property packages (IAPWS95, Modular, etc.)
│   │   ├── costing/                    # Costing models
│   │   └── control/                    # Process control models
│   ├── generic_models/                 # Template-based/generic models
│   │   ├── unit_models/                # Generic unit models (columns, distillation)
│   │   ├── properties/                 # Generic property framework
│   │   │   ├── core/                   # Modular property package framework
│   │   │   ├── cubic_eos/              # Cubic equation of state
│   │   │   ├── activity_coeff_models/  # Activity coefficient models
│   │   │   └── helmholtz/              # Helmholtz equation of state
│   │   └── costing/                    # Generic costing
│   ├── models_extra/                   # Extended/specialized models
│   │   ├── carbon_capture/             # Carbon capture processes
│   │   ├── power_generation/           # Power generation units
│   │   ├── gas_solid_contactors/       # Gas-solid contact models
│   │   └── temperature_swing_adsorption/ # TSA models
│   ├── commands/                       # CLI commands (idaes get-extensions, env-info, config)
│   ├── surrogate/                      # Surrogate/ML modeling (ALAMO, PySMO, Keras/OMLT)
│   ├── apps/                           # Applications (grid integration)
│   ├── dmf/                            # Data management framework
│   └── tests/                          # Top-level tests (imports, config, headers)
├── docs/                               # Sphinx documentation (RST)
├── scripts/                            # Utility scripts
├── .pylint/                            # Pylint config and custom plugins
├── .github/workflows/                  # CI (core.yml, integration.yml)
├── pyproject.toml                      # Build config, dependencies, entry points
├── pytest.ini                          # Pytest config
├── pytest-dev.ini                      # Pytest config with coverage
├── requirements-dev.txt                # Dev dependencies
└── .pre-commit-config.yaml             # Pre-commit hooks (Black)
```

## Architecture

### Core Class Hierarchy
All models inherit from Pyomo `Block` via IDAES base classes:

- **`ProcessBlockData`** - root base for all IDAES models
  - **`UnitModelBlockData`** (`idaes/core/base/unit_model.py`) - base for unit operations (heaters, reactors, separators, etc.)
  - **`PhysicalParameterBlock`** / **`StateBlock`** (`idaes/core/base/property_base.py`) - thermodynamic property packages
  - **`ReactionParameterBlock`** / **`ReactionBlock`** (`idaes/core/base/reaction_base.py`) - reaction kinetics
  - **`ControlVolumeBlockData`** (`idaes/core/base/control_volume_base.py`) - material/energy/momentum balances
    - **`ControlVolume0DBlockData`** - lumped (well-mixed) control volumes
    - **`ControlVolume1DBlockData`** - distributed (spatial) control volumes

### Key Subsystems

- **`idaes/core/`** - Framework core: base classes, initialization, scaling, solvers, diagnostics
- **`idaes/models/`** - Standard unit models (feed, heater, flash, mixer, separator, heat exchangers, CSTR, PFR, pressure changer, pipe, etc.)
- **`idaes/generic_models/`** - Template-based/generic models and property packages (cubic EOS, activity coefficients, Helmholtz)
- **`idaes/models_extra/`** - Extended models (carbon capture, power generation, gas-solid contactors, TSA)
- **`idaes/core/util/model_diagnostics.py`** - Diagnostic tools for debugging models (largest file in the codebase)
- **`idaes/core/initialization/`** - Hierarchical initialization framework (`InitializerBase`, `BlockTriangularizationInitializer`)
- **`idaes/core/scaling/`** - Model scaling/normalization (`CustomScalerBase`, autoscaling)

### How Unit Models Work
1. Decorated with `@declare_process_block_class("Name")`
2. Inherit from `UnitModelBlockData`
3. Configured via Pyomo `ConfigBlock` (property_package, reaction_package, dynamic, etc.)
4. `build()` creates ports, state blocks, control volumes, variables, and constraints
5. Optionally implement custom `Initializer` and `Scaler` classes

### Property Package System
Property packages are decoupled from unit models. A unit model's `CONFIG.property_package` accepts any `PhysicalParameterBlock` that provides the required properties. The generic property framework (`idaes/generic_models/properties/core/`) allows building property packages from configuration dictionaries.

## File Conventions

- All `.py` files must have the IDAES copyright header (enforced by `idaes/tests/test_headers.py`)
- Python 3.10+ (3.9 support was dropped)
- Black formatting with 88-char line length
- Pylint config at `.pylint/pylintrc` (ignores test files, custom transform plugin at `.pylint/idaes_transform.py`)
