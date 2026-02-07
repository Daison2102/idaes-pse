#################################################################################
# Custom class-based IDAES property package
#
# System: methanol + water + ammonia
# State variables: FTPx (flow_mol, temperature, pressure, mole_frac_comp)
# Assumptions: ideal vapor + ideal liquid, Raoult-law VLE
#
# Placeholder data are physically sensible and source-tagged in comments below.
#################################################################################

from pyomo.environ import (
    Constraint,
    Expression,
    NonNegativeReals,
    Param,
    Reals,
    Set,
    Var,
    units as pyunits,
    value,
)

from idaes.core import (
    Component,
    EnergyBalanceType,
    LiquidPhase,
    MaterialBalanceType,
    MaterialFlowBasis,
    PhysicalParameterBlock,
    StateBlock,
    StateBlockData,
    VaporPhase,
    declare_process_block_class,
)
from idaes.core.util.initialization import fix_state_vars, revert_state_vars
import idaes.logger as idaeslog

__author__ = "Codex (GPT-5)"

_log = idaeslog.getLogger(__name__)


@declare_process_block_class("MWAIdealParameterBlock")
class MWAIdealParameterData(PhysicalParameterBlock):
    """
    Class-based property package for methanol/water/ammonia with ideal VLE.
    """

    def build(self):
        super().build()

        self._state_block_class = MWAIdealStateBlock

        # Phases
        self.Liq = LiquidPhase()
        self.Vap = VaporPhase()

        # Components
        self.methanol = Component()
        self.water = Component()
        self.ammonia = Component()

        # Phase equilibrium indexing required by IDAES Flash control volume
        self.phase_equilibrium_idx = Set(initialize=[1, 2, 3])
        self.phase_equilibrium_list = {
            1: ["methanol", ("Vap", "Liq")],
            2: ["water", ("Vap", "Liq")],
            3: ["ammonia", ("Vap", "Liq")],
        }

        # Reference state
        self.pressure_ref = Param(
            mutable=True,
            initialize=101325.0,
            units=pyunits.Pa,
            doc="Reference pressure",
        )
        self.temperature_ref = Param(
            mutable=True,
            initialize=298.15,
            units=pyunits.K,
            doc="Reference temperature",
        )

        # Molecular weight [kg/mol]
        # Source: NIST WebBook (species pages)
        self.mw_comp = Param(
            self.component_list,
            initialize={
                "methanol": 32.0419e-3,
                "water": 18.0153e-3,
                "ammonia": 17.0305e-3,
            },
            mutable=True,
            units=pyunits.kg / pyunits.mol,
            doc="Molecular weight",
        )

        # Critical constants (for completeness in parameterization)
        # Source: NIST WebBook phase-change data
        self.temperature_critical = Param(
            self.component_list,
            initialize={
                "methanol": 513.0,
                "water": 647.0,
                "ammonia": 405.4,
            },
            mutable=True,
            units=pyunits.K,
            doc="Critical temperature",
        )
        self.pressure_critical = Param(
            self.component_list,
            initialize={
                "methanol": 81.0e5,
                "water": 220.64e5,
                "ammonia": 113.0e5,
            },
            mutable=True,
            units=pyunits.Pa,
            doc="Critical pressure",
        )

        # Pure liquid molar density [mol/m^3] placeholders for ideal-liquid mixture density
        # Sources:
        # - water: IDAES examples (55,388 mol/m^3)
        # - methanol/ammonia: EngineeringToolbox density-based conversions near ambient
        self.dens_mol_liq_comp = Param(
            self.component_list,
            initialize={
                "methanol": 24540.0,
                "water": 55388.0,
                "ammonia": 36259.0,
            },
            mutable=True,
            units=pyunits.mol / pyunits.m**3,
            doc="Pure liquid molar density placeholder",
        )

        # Antoine coefficients for log10(P_bar) = A - B / (T + C), T in K
        # Sources: NIST WebBook phase-change pages
        self.antoine_A = Param(
            self.component_list,
            initialize={
                "methanol": 5.20409,  # 288.1-356.8 K
                "water": 4.6543,  # 255.9-373 K
                "ammonia": 4.86886,  # 239.6-371.5 K
            },
            mutable=True,
            doc="Antoine A coefficient",
        )
        self.antoine_B = Param(
            self.component_list,
            initialize={
                "methanol": 1581.341,
                "water": 1435.264,
                "ammonia": 1113.928,
            },
            mutable=True,
            units=pyunits.K,
            doc="Antoine B coefficient",
        )
        self.antoine_C = Param(
            self.component_list,
            initialize={
                "methanol": -33.50,
                "water": -64.848,
                "ammonia": -10.409,
            },
            mutable=True,
            units=pyunits.K,
            doc="Antoine C coefficient",
        )

        # Ideal-gas cp polynomial coefficients:
        # Cp = A + B*T + C*T^2 + D*T^3 [J/mol/K]
        # Sources:
        # - water/ammonia: IDAES methane_combustion_ideal values (Reid/Perry based)
        # - methanol: placeholder fit around NIST Cp trend
        self.cp_mol_vap_A = Param(
            self.component_list,
            initialize={"methanol": 20.0, "water": 32.24, "ammonia": 27.31},
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K,
        )
        self.cp_mol_vap_B = Param(
            self.component_list,
            initialize={
                "methanol": 8.0e-2,
                "water": 1.924e-3,
                "ammonia": 2.383e-2,
            },
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K**2,
        )
        self.cp_mol_vap_C = Param(
            self.component_list,
            initialize={
                "methanol": 1.0e-5,
                "water": 1.055e-5,
                "ammonia": 1.707e-5,
            },
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K**3,
        )
        self.cp_mol_vap_D = Param(
            self.component_list,
            initialize={
                "methanol": -1.5e-8,
                "water": -3.596e-9,
                "ammonia": -1.185e-8,
            },
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K**4,
        )

        # Liquid cp polynomial coefficients:
        # Cp = A + B*T + C*T^2 + D*T^3 + E*T^4 [J/mol/K]
        # Source anchors:
        # - methanol: EngineeringToolbox ~81.2 J/mol/K near 298 K
        # - water: NIST condensed-phase Cp around 298 K (~75.3 J/mol/K)
        # - ammonia: EngineeringToolbox ~80.8 J/mol/K near ambient
        self.cp_mol_liq_A = Param(
            self.component_list,
            initialize={"methanol": 81.2, "water": 75.3, "ammonia": 80.8},
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K,
        )
        self.cp_mol_liq_B = Param(
            self.component_list,
            initialize={"methanol": 0.0, "water": 0.0, "ammonia": 0.0},
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K**2,
        )
        self.cp_mol_liq_C = Param(
            self.component_list,
            initialize={"methanol": 0.0, "water": 0.0, "ammonia": 0.0},
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K**3,
        )
        self.cp_mol_liq_D = Param(
            self.component_list,
            initialize={"methanol": 0.0, "water": 0.0, "ammonia": 0.0},
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K**4,
        )
        self.cp_mol_liq_E = Param(
            self.component_list,
            initialize={"methanol": 0.0, "water": 0.0, "ammonia": 0.0},
            mutable=True,
            units=pyunits.J / pyunits.mol / pyunits.K**5,
        )

        # Standard formation enthalpy references [J/mol]
        # Sources:
        # - methanol/water: NIST (gas/liquid)
        # - ammonia vapor: NIST
        # - ammonia liquid: placeholder from vapor minus latent heat scale
        self.enth_mol_form_vap_comp_ref = Param(
            self.component_list,
            initialize={
                "methanol": -205.0e3,
                "water": -241.826e3,
                "ammonia": -45.90e3,
            },
            mutable=True,
            units=pyunits.J / pyunits.mol,
        )
        self.enth_mol_form_liq_comp_ref = Param(
            self.component_list,
            initialize={
                "methanol": -239.0e3,
                "water": -285.83e3,
                "ammonia": -69.2e3,
            },
            mutable=True,
            units=pyunits.J / pyunits.mol,
        )

        # Default variable scaling
        self.set_default_scaling("flow_mol", 1e-2)
        self.set_default_scaling("temperature", 1e-2)
        self.set_default_scaling("pressure", 1e-5)
        self.set_default_scaling("mole_frac_comp", 10)
        self.set_default_scaling("flow_mol_phase", 1e-2)
        self.set_default_scaling("mole_frac_phase_comp", 10)
        self.set_default_scaling("pressure_sat_comp", 1e-5)

    @classmethod
    def define_metadata(cls, obj):
        obj.add_properties(
            {
                "flow_mol": {"method": None, "units": "mol/s"},
                "mole_frac_comp": {"method": None, "units": "dimensionless"},
                "temperature": {"method": None, "units": "K"},
                "pressure": {"method": None, "units": "Pa"},
                "flow_mol_phase": {"method": None, "units": "mol/s"},
                "mole_frac_phase_comp": {"method": None, "units": "dimensionless"},
                "pressure_sat_comp": {"method": None, "units": "Pa"},
                "dens_mol_phase": {"method": None, "units": "mol/m^3"},
                "enth_mol_phase_comp": {"method": None, "units": "J/mol"},
                "enth_mol_phase": {"method": None, "units": "J/mol"},
            }
        )
        obj.add_default_units(
            {
                "time": pyunits.s,
                "length": pyunits.m,
                "mass": pyunits.kg,
                "amount": pyunits.mol,
                "temperature": pyunits.K,
            }
        )


class _MWAIdealStateBlock(StateBlock):
    """
    Methods on indexed state block.
    """

    def fix_initialization_states(self):
        fix_state_vars(self)

    def initialize(
        blk,
        state_args=None,
        state_vars_fixed=False,
        hold_state=False,
        outlvl=idaeslog.NOTSET,
        solver=None,
        optarg=None,
    ):
        init_log = idaeslog.getInitLogger(blk.name, outlvl, tag="properties")

        if not state_vars_fixed:
            flags = fix_state_vars(blk, state_args)
        else:
            flags = None

        for b in blk.values():
            for p in b.params.phase_list:
                if not b.flow_mol_phase[p].fixed:
                    b.flow_mol_phase[p].set_value(0.5 * value(b.flow_mol))
                for j in b.params.component_list:
                    if not b.mole_frac_phase_comp[p, j].fixed:
                        b.mole_frac_phase_comp[p, j].set_value(
                            max(1e-8, value(b.mole_frac_comp[j]))
                        )

        if hold_state:
            init_log.info("Initialization complete (state held).")
            return flags

        if flags is not None:
            blk.release_state(flags)
        init_log.info("Initialization complete.")
        return None

    def release_state(blk, flags, outlvl=idaeslog.NOTSET):
        if flags is None:
            return
        revert_state_vars(blk, flags)
        init_log = idaeslog.getInitLogger(blk.name, outlvl, tag="properties")
        init_log.info("State Released.")


@declare_process_block_class("MWAIdealStateBlock", block_class=_MWAIdealStateBlock)
class MWAIdealStateBlockData(StateBlockData):
    """
    State block data for methanol/water/ammonia ideal package.
    """

    def build(self):
        super().build()

        self.flow_mol = Var(
            initialize=1.0,
            domain=NonNegativeReals,
            units=pyunits.mol / pyunits.s,
            doc="Total molar flow rate",
        )
        self.temperature = Var(
            initialize=298.15,
            domain=Reals,
            bounds=(288.0, 357.0),
            units=pyunits.K,
            doc="State temperature",
        )
        self.pressure = Var(
            initialize=101325.0,
            domain=Reals,
            bounds=(5e4, 2e6),
            units=pyunits.Pa,
            doc="State pressure",
        )
        self.mole_frac_comp = Var(
            self.params.component_list,
            initialize=1.0 / len(self.params.component_list),
            domain=NonNegativeReals,
            bounds=(1e-12, 1.0),
            units=pyunits.dimensionless,
            doc="Overall mole fraction",
        )

        self.flow_mol_phase = Var(
            self.params.phase_list,
            initialize=0.5,
            domain=NonNegativeReals,
            units=pyunits.mol / pyunits.s,
            doc="Phase molar flow",
        )
        self.mole_frac_phase_comp = Var(
            self.params.phase_list,
            self.params.component_list,
            initialize=1.0 / len(self.params.component_list),
            domain=NonNegativeReals,
            bounds=(1e-12, 1.0),
            units=pyunits.dimensionless,
            doc="Phase mole fraction",
        )

        @self.Expression(
            self.params.component_list,
            doc="Pure component saturation pressure from Antoine [Pa]",
        )
        def pressure_sat_comp(b, j):
            return (
                1e5 * pyunits.Pa
                * 10
                ** (
                    b.params.antoine_A[j]
                    - b.params.antoine_B[j] / (b.temperature + b.params.antoine_C[j])
                )
            )

        if self.config.defined_state is False:
            self.eq_mole_frac_comp = Constraint(
                expr=sum(self.mole_frac_comp[j] for j in self.params.component_list)
                == 1.0
            )

        self.eq_total_flow = Constraint(
            expr=self.flow_mol_phase["Liq"] + self.flow_mol_phase["Vap"] == self.flow_mol
        )

        self.eq_sum_mol_frac = Constraint(
            expr=sum(
                self.mole_frac_phase_comp["Liq", j] for j in self.params.component_list
            )
            - sum(
                self.mole_frac_phase_comp["Vap", j] for j in self.params.component_list
            )
            == 0.0
        )

        @self.Constraint(self.params.component_list)
        def eq_component_split(b, j):
            return b.flow_mol * b.mole_frac_comp[j] == sum(
                b.flow_mol_phase[p] * b.mole_frac_phase_comp[p, j]
                for p in b.params.phase_list
            )

        if self.config.has_phase_equilibrium:

            @self.Constraint(self.params.component_list)
            def eq_phase_equilibrium(b, j):
                return (
                    b.mole_frac_phase_comp["Vap", j] * b.pressure
                    == b.mole_frac_phase_comp["Liq", j] * b.pressure_sat_comp[j]
                )

        @self.Expression(
            self.params.phase_list,
            self.params.component_list,
            doc="Component molar enthalpy in each phase",
        )
        def enth_mol_phase_comp(b, p, j):
            t = b.temperature
            tr = b.params.temperature_ref
            if p == "Vap":
                return b.params.enth_mol_form_vap_comp_ref[j] + (
                    b.params.cp_mol_vap_A[j] * (t - tr)
                    + b.params.cp_mol_vap_B[j] * (t**2 - tr**2) / 2.0
                    + b.params.cp_mol_vap_C[j] * (t**3 - tr**3) / 3.0
                    + b.params.cp_mol_vap_D[j] * (t**4 - tr**4) / 4.0
                )
            return b.params.enth_mol_form_liq_comp_ref[j] + (
                b.params.cp_mol_liq_A[j] * (t - tr)
                + b.params.cp_mol_liq_B[j] * (t**2 - tr**2) / 2.0
                + b.params.cp_mol_liq_C[j] * (t**3 - tr**3) / 3.0
                + b.params.cp_mol_liq_D[j] * (t**4 - tr**4) / 4.0
                + b.params.cp_mol_liq_E[j] * (t**5 - tr**5) / 5.0
            )

        @self.Expression(self.params.phase_list, doc="Phase molar enthalpy")
        def enth_mol_phase(b, p):
            return sum(
                b.mole_frac_phase_comp[p, j] * b.enth_mol_phase_comp[p, j]
                for j in b.params.component_list
            )

        @self.Expression(self.params.phase_list, doc="Phase molar density")
        def dens_mol_phase(b, p):
            if p == "Vap":
                return b.pressure / (8.314462618 * b.temperature)
            return sum(
                b.mole_frac_phase_comp["Liq", j] * b.params.dens_mol_liq_comp[j]
                for j in b.params.component_list
            )

    def get_material_flow_terms(b, p, j):
        return b.flow_mol_phase[p] * b.mole_frac_phase_comp[p, j]

    def get_enthalpy_flow_terms(b, p):
        return b.flow_mol_phase[p] * b.enth_mol_phase[p]

    def get_material_density_terms(b, p, j):
        return b.dens_mol_phase[p] * b.mole_frac_phase_comp[p, j]

    def get_energy_density_terms(b, p):
        return b.dens_mol_phase[p] * b.enth_mol_phase[p]

    def default_material_balance_type(self):
        return MaterialBalanceType.componentPhase

    def default_energy_balance_type(self):
        return EnergyBalanceType.enthalpyTotal

    def get_material_flow_basis(b):
        return MaterialFlowBasis.molar

    def define_state_vars(b):
        return {
            "flow_mol": b.flow_mol,
            "mole_frac_comp": b.mole_frac_comp,
            "temperature": b.temperature,
            "pressure": b.pressure,
        }

    def define_display_vars(b):
        return {
            "Molar Flowrate": b.flow_mol,
            "Mole Fraction": b.mole_frac_comp,
            "Temperature": b.temperature,
            "Pressure": b.pressure,
        }

    def model_check(blk):
        if value(blk.temperature) < blk.temperature.lb:
            _log.error("%s temperature below lower bound.", blk.name)
        if value(blk.temperature) > blk.temperature.ub:
            _log.error("%s temperature above upper bound.", blk.name)
        if value(blk.pressure) < blk.pressure.lb:
            _log.error("%s pressure below lower bound.", blk.name)
        if value(blk.pressure) > blk.pressure.ub:
            _log.error("%s pressure above upper bound.", blk.name)
