# Class-Based Workflow

Use this path when modular libraries cannot represent required behavior.

## Required Classes
Create three classes:
1. `PhysicalParameterBlock` data class
2. `StateBlock` methods class
3. `StateBlockData` class

## Parameter Block
In `build()`:
1. call `super().build()`
2. set `self._state_block_class`
3. define phase and component objects
4. define global parameters

In `define_metadata()`:
1. declare supported properties (`add_properties`)
2. declare base units (`add_default_units`)

## StateBlock Methods Class
Implement:
1. `initialize(...)`
2. `release_state(...)`

Optional:
1. `fix_initialization_states(...)`
2. custom state initialization helpers

## StateBlockData
In `build()`:
1. call `super().build()`
2. create state variables
3. add closure/normalization constraints
4. add on-demand property builders

Implement required interface methods:
1. `get_material_flow_basis`
2. `get_material_flow_terms`
3. `get_material_density_terms`
4. `get_enthalpy_flow_terms`
5. `get_energy_density_terms`
6. `default_material_balance_type`
7. `default_energy_balance_type`
8. `define_state_vars`

Recommended methods:
1. `define_display_vars`
2. `define_port_members`
3. `model_check`

## Optional Additions
1. phase equilibrium constraints
2. bubble/dew calculations
3. `CustomScalerBase` subclass for scaling

## Templates
Start from:
1. `templates/class_based/parameter_block_template.py`
2. `templates/class_based/state_block_methods_template.py`
3. `templates/class_based/state_block_data_template.py`
