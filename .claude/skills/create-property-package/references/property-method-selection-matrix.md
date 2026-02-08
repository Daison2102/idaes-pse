# Property Method Selection Matrix

Use this matrix to map user requirements to IDAES method choices.

## EOS Selection

| Requirement | Recommended EOS | Notes |
|---|---|---|
| Low-complexity, idealized vapor/liquid behavior | `Ideal` | Fast and simpler parameter requirements |
| Non-ideal hydrocarbon and gas processing | `Cubic` + `CubicType.PR` | Requires critical properties, acentric factors, interaction params |
| SRK preference | `Cubic` + `CubicType.SRK` | Similar requirements to PR |

## Equilibrium Form Selection

| EOS context | Equilibrium form | Equilibrium state method | Bubble/dew method |
|---|---|---|---|
| Ideal-style VLE | `fugacity` | `SmoothVLE` | `IdealBubbleDew` |
| Cubic EOS VLE | `log_fugacity` (common) | `CubicComplementarityVLE` or compatible smooth/cubic method | `LogBubbleDew` |

Always confirm exact compatibility from current IDAES docs and examples.

## Pure Property Methods (common)

| Property group | Typical methods |
|---|---|
| Ideal-gas Cp/H/S | `NIST`, `RPP4`, `RPP5` |
| Liquid density/enthalpy/entropy | `Perrys` |
| Constant-property fallback | `ConstantProperties` |
| Saturation pressure | `NIST`, `RPP4`, `RPP5` (method-dependent) |

## Transport Methods (optional)

| Transport property | Typical phase method | Typical component method support |
|---|---|---|
| Dynamic viscosity | `ViscosityWilke` | `ChapmanEnskogLennardJones` (+ callback where required) |
| Thermal conductivity | `ThermalConductivityWMS` | `Eucken` or method-specific coefficients |
| Not modeled | `NoMethod` | Use when transport is intentionally excluded |

## Method Selection Rules

1. Start from required-properties coverage mode.
2. Prefer methods already proven in official IDAES examples with similar system profile.
3. Reject method combinations with unresolved minimum-required parameters.
4. If method set cannot satisfy requirements in Generic framework, switch to class-based.
