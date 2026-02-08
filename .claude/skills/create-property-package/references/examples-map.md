# Examples Map

Use this map to quickly find canonical patterns in the repository.

## Official Generic Framework Examples

1. `idaes/models/properties/modular_properties/examples/BT_ideal.py`
2. `idaes/models/properties/modular_properties/examples/BT_PR.py`
3. `idaes/models/properties/modular_properties/examples/HC_PR.py`
4. `idaes/models/properties/modular_properties/examples/CO2_H2O_Ideal_VLE.py`

Associated tests:
1. `idaes/models/properties/modular_properties/examples/tests/test_BTIdeal.py`
2. `idaes/models/properties/modular_properties/examples/tests/test_BT_PR.py`
3. `idaes/models/properties/modular_properties/examples/tests/test_HC_PR.py`
4. `idaes/models/properties/modular_properties/examples/tests/test_CO2_H2O_Ideal_VLE.py`

## Official Class-Based Example Patterns

1. `idaes/models/properties/examples/saponification_thermo.py`
2. `idaes/models/properties/examples/tests/test_saponification_thermo.py`

These files provide patterns for:
1. Parameter block structure.
2. StateBlock methods (`initialize`/`release_state`).
3. Contract methods and metadata definitions.
4. Scaler integration.

## Optional Local Legacy References (non-canonical)

When available in workspace, these can be used only for structural inspiration:
1. `custom_example_pro_pack/WE_ideal_FTPx_class.py`
2. `custom_example_pro_pack/WE_ideal_FTPx.py`
3. `custom_example_pro_pack/WE_ideal_FpcTP.py`
4. `custom_example_pro_pack/methanol_ceos.py`

Guidance:
1. Do not treat legacy local files as authority for current APIs.
2. Use them to infer useful skill capabilities and template ergonomics.
3. For generic style, prioritize the newer methanol-style dictionary assembly patterns when present.
