# Legacy Example Summary (Structural Only)

These are structural references only and are not canonical. Use them for layout and style patterns when building new packages.

## Step-by-step checklist for extracting structure

1. Identify the package type.
- Generic configuration dict vs class-based definitions.

2. Note the organization of phases and components.
- Component entries and parameter data layout.
- Phase definitions and EOS selection.

3. Capture equilibrium setup.
- Phase pairs and fugacity forms.

4. Note transport and method wiring.
- Transport methods and options.

5. Copy style conventions.
- Dictionary layout, naming style, and imports.

## methanol_ceos.py (highest priority)

- Uses `idaes.models.properties.modular_properties` imports and structure.
- Configuration dict splits components and phases with EOS per phase.
- Uses enums to select EOS variants (PR vs Ideal).
- Uses transport models with phase-specific options.
- Organizes parameter_data with clear units and sources.
- Favors explicit dictionaries and clear naming.

## WE_ideal_FTPx.py / WE_ideal_FpcTP.py

- Generic framework configuration dictionary layout.
- Ideal EOS for both phases and fugacity-based VLE.
- Uses Perry, NIST, and RPP methods for pure properties.

## WE_ideal_FTPx_class.py

- Illustrates class-based approach layout.
- Demonstrates custom state block and methods.

Use methanol_ceos style for generic framework structure and naming when possible.
