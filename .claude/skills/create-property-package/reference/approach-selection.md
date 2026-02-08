# Approach Selection: Generic vs Class-Based

## Decision Matrix

| Criterion | Generic Framework | Class-Based |
|-----------|:-----------------:|:-----------:|
| Standard EOS (Ideal, PR, SRK) | YES | possible |
| Custom/novel EOS equations | no | YES |
| Standard property methods (NIST, RPP, Perrys) | YES | possible |
| Custom correlations or proprietary equations | no | YES |
| Standard VLE with fugacity-based equilibrium | YES | possible |
| Non-standard equilibrium formulations | no | YES |
| Standard state definitions (FTPx, FpcTP, etc.) | YES | possible |
| Custom state variable formulations | no | YES |
| Electrolyte systems (e-NRTL) | YES | possible |
| Transport properties (viscosity, conductivity) | YES | possible |
| Rapid prototyping / minimum code | YES | no |
| Maximum control over every equation | no | YES |
| Needs runtime configurability (select components/phases dynamically) | YES | possible |

## Recommendation Rules

1. **Default to Generic Framework** unless the user explicitly needs custom
   equations or non-standard formulations

2. **Use Class-Based** when:
   - The user has custom thermodynamic correlations not available in IDAES
   - Non-standard equations of state are required
   - The user wants direct control over every variable, constraint, and
     initialization step
   - The system involves unusual phase behavior not covered by SmoothVLE
     or CubicComplementarityVLE

3. **Use Generic Framework** when:
   - Standard EOS and property methods cover the user's needs
   - The user wants minimal boilerplate code
   - The system is a standard VLE mixture
   - The user wants to leverage IDAES's built-in scaling and initialization

## What to Tell the User

When recommending an approach, explain:
- **Why** this approach fits their requirements
- **What trade-offs** exist (Generic = less code, less control; Class-Based =
  more code, full control)
- That the Generic approach is the officially recommended path for most
  standard systems
