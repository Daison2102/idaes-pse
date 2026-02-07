# Select Approach: Generic vs Class-Based

Default: use Generic unless a strong reason exists for Class-Based.

## Step-by-step checklist

1. Check if modular methods cover required properties.
- If yes, Generic remains viable.
- If no, move toward Class-Based.

2. Check if state definition is standard.
- If FTPx, FpcTP, or another built-in is acceptable, Generic remains viable.
- If a custom state is required, Class-Based is required.

3. Check EOS and equilibrium formulations.
- If EOS and phase equilibrium are supported in modular properties, Generic remains viable.
- If not supported, Class-Based is required.

4. Check for custom constraints.
- If you need custom property equations or constraints, Class-Based is required.

5. Check initialization and scaling needs.
- If default initialization works, Generic is fine.
- If custom initialization logic is essential, Class-Based may be required.

## Decision Rule

- If any Class-Based condition is true, select Class-Based.
- Otherwise, proceed with Generic.

Next step:
- Generic path: `workflow/20_generic_build.md`
- Class-based path: `workflow/30_class_build.md`
