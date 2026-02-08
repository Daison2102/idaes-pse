# Requirements Schema

Normalize input to this schema.

```yaml
package_name: string
components:
  - name: string
    elemental_composition: {element: count}
phases:
  - name: string   # e.g., Liq, Vap, Sol
    phase_type: string  # LiquidPhase, VaporPhase, SolidPhase
state_definition: FTPx|FpcTP|FcTP|FPhx|FcPh
required_properties:
  profile: minimum|comprehensive
  include:
    - property_name
  exclude:
    - property_name
equilibrium:
  required: true|false
  phase_pairs:
    - [Vap, Liq]
  form_by_component:  # optional overrides
    component_name: fugacity|log_fugacity
eos:
  by_phase:
    Liq: Ideal|PR|SRK
    Vap: Ideal|PR|SRK
transport:
  include: true|false
  requested:
    - visc_d_phase
    - therm_cond_phase
notes: string
```

## Follow-up Questions
Ask only for missing high-impact fields:
1. Which state definition should be used?
2. Use `minimum` or `comprehensive` required-properties profile?
3. Is phase equilibrium required? If yes, which phase pairs?
4. Which EOS should be used per phase?

## Validation
Reject or request clarification when:
1. phase pair references undefined phases
2. EOS requested is incompatible with phase type
3. requested property has no supported method and no fallback is provided
