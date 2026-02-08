# Methanol-Water-Ammonia Class-Based Property Package

This folder contains a custom IDAES class-based property package for a
`methanol + water + ammonia` system with:

- State definition: `FTPx` (`flow_mol`, `temperature`, `pressure`, `mole_frac_comp`)
- Phases: `Liq`, `Vap`
- VLE assumption: ideal vapor + ideal liquid (`y_i P = x_i P_sat,i`)
- Vapor pressure model: Antoine (NIST form, `log10(P_bar) = A - B/(T + C)`)

## Files

- `methanol_water_ammonia_ideal_vle.py`: parameter block and state block classes
- `test_methanol_water_ammonia_ideal_vle.py`: pytest smoke/validation tests
- `flash_example.py`: small runnable `Flash` unit example

## Run Flash Example

```bash
python methanol_water_ammonia_property_package/flash_example.py
```

## Data Sources

Primary (component constants and Antoine coefficients):

- Methanol (NIST):
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Mask=4
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Mask=1
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C67561&Mask=4&Type=ANTOINE&Plot=on
- Water (NIST):
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=4
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=2
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=4&Type=ANTOINE&Plot=on
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=887&Type=JANAFG&Table=on
- Ammonia (NIST):
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Mask=4
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Mask=1
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Mask=4&Type=ANTOINE&Plot=on
  - https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Mask=887&Type=JANAFG&Table=on

Public engineering tables used for placeholder liquid constants where needed:

- Water density table:
  - https://www.engineeringtoolbox.com/water-density-specific-weight-d_595.html
- Water vapor specific heat table:
  - https://www.engineeringtoolbox.com/water-vapor-d_979.html
- Methanol density table:
  - https://www.engineeringtoolbox.com/methanol-density-specific-weight-temperature-pressure-d_2091.html
- Liquid ammonia thermal properties:
  - https://www.engineeringtoolbox.com/ammonia-liquid-thermal-properties-d_1765.html

## Placeholder Notes

- Ammonia liquid reference enthalpy/entropy are physically consistent placeholders
  estimated from NIST gas-phase values and vaporization trends near ambient
  conditions.
- Methanol ideal-gas Cp uses a constant-Cp placeholder anchored to NIST
  `Cp,gas(298.15 K)` since a directly parsed NIST Shomate table was not
  available from the same endpoint in this workflow.
