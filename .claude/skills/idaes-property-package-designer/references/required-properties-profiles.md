# Required Properties Profiles

Resolve required properties from one of these canonical profiles.

## Minimum Profile (default)
Use for fast and robust package creation.

1. `temperature`
2. `pressure`
3. one flow representation: `flow_mol` or `flow_mol_comp` or `flow_mol_phase_comp`
4. one composition representation: `mole_frac_comp` or `mole_frac_phase_comp`
5. `phase_frac` (multiphase only)
6. `enth_mol` or `enth_mol_phase`
7. `dens_mol` or `dens_mol_phase`
8. `mw`
9. `cp_mol` or `cp_mol_phase`
10. `pressure_sat_comp` (if VLE/bubble/dew required)
11. `fug_phase_comp` (if fugacity-based equilibrium form is required)

## Comprehensive Profile
Use for broad thermodynamic and transport coverage.

1. `flow_mol`
2. `flow_mol_comp`
3. `flow_mol_phase`
4. `flow_mol_phase_comp`
5. `mole_frac_comp`
6. `mole_frac_phase_comp`
7. `phase_frac`
8. `mass_frac_phase_comp`
9. `mw`
10. `dens_mol`
11. `dens_mol_phase`
12. `dens_mass`
13. `dens_mass_phase`
14. `enth_mol`
15. `enth_mol_phase`
16. `enth_mol_phase_comp`
17. `entr_mol`
18. `entr_mol_phase`
19. `gibbs_mol`
20. `cp_mol`
21. `cp_mol_phase`
22. `cv_mol_phase`
23. `compress_fact_phase`
24. `fug_phase_comp`
25. `pressure_sat_comp`
26. `temperature_bubble`
27. `temperature_dew`
28. `pressure_bubble`
29. `pressure_dew`
30. `visc_d_phase`
31. `therm_cond_phase`
32. `diffus_phase_comp`
33. `prandtl_phase`

## Resolution Rules
1. Start from selected profile.
2. Add user `include` properties.
3. Remove user `exclude` properties.
4. Remove unsupported properties and mark as `not_supported`.
5. Mark unresolved data dependencies as `placeholder`.

## Output
Emit property status map:

```yaml
resolved_properties:
  property_name:
    status: supported|placeholder|not_supported
    reason: string
```
