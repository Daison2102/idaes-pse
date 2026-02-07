# Select Approach: Generic vs Generic-with-Classes vs Class-Based

Default: use Generic dict/factory style unless a stronger reason exists.

## Step-by-step checklist

1. Check if modular methods cover required properties.
- If yes, Generic remains viable (either dict/factory or class-definition flavor).
- If no, move toward Class-Based.

2. Check if state definition is standard.
- If FTPx, FpcTP, or another built-in is acceptable, Generic remains viable.
- If a custom state is required, Class-Based is required.

3. Check EOS and equilibrium formulations.
- If EOS and phase equilibrium are supported in modular properties, Generic remains viable.
- If not supported, Class-Based is required.

4. Check for custom constraints.
- If you need custom property equations or constraints in state/property expressions,
  Class-Based is required.

5. Check initialization and scaling needs.
- If default initialization works, Generic is fine.
- If custom initialization logic is essential, Class-Based may be required.

6. Check explicit user preference for Generic classes.
- If user explicitly asks for "generic with class definitions", choose Generic-with-Classes.
- If user does not ask explicitly, keep default Generic dict/factory pattern.

## Decision Rule

- If any custom-class condition is true, select Class-Based.
- Else if user explicitly requests generic class definitions, select Generic-with-Classes.
- Else select Generic dict/factory.

Next step:
- Generic dict/factory path: `workflow/20_generic_build.md` (default structure)
- Generic-with-Classes path: `workflow/20_generic_build.md` (alternate structure)
- Class-based path: `workflow/30_class_build.md`
