# Transport Properties

## Step-by-step checklist

1. Identify transport properties required by unit models.
- Viscosity
- Thermal conductivity
- Diffusivity (if required)

2. Select models per phase.
- Vapor: Wilke mixing or Chapman-Enskog.
- Liquid: model if required, otherwise `NoMethod`.

3. Configure mixing rules and options.
- Add callbacks if required.

4. Provide component parameters.
- Add Lennard-Jones or other method parameters.
- Record sources and units.

5. Validate units and ranges.
- Confirm parameter units and temperature ranges.

## Codebase pointers

- `idaes/models/properties/modular_properties/transport_properties/`

Guidance:

- If no transport data is required, set phase transport methods to `NoMethod`.
- For vapor, Wilke mixing is common.
- Always confirm unit consistency and valid temperature ranges.
