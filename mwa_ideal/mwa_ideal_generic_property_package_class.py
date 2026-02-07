# pylint: disable=all

from pyomo.environ import Var, units as pyunits

from idaes.core import Component, LiquidPhase, PhaseType, VaporPhase, declare_process_block_class
from idaes.models.properties.modular_properties.base.generic_property import GenericParameterData
from idaes.models.properties.modular_properties.eos.ideal import Ideal
from idaes.models.properties.modular_properties.phase_equil import SmoothVLE
from idaes.models.properties.modular_properties.phase_equil.bubble_dew import IdealBubbleDew
from idaes.models.properties.modular_properties.phase_equil.forms import fugacity
from idaes.models.properties.modular_properties.pure import Constant, NIST
from idaes.models.properties.modular_properties.state_definitions import FTPx


BASE_UNITS = {
    "time": pyunits.s,
    "length": pyunits.m,
    "mass": pyunits.kg,
    "amount": pyunits.mol,
    "temperature": pyunits.K,
}


@declare_process_block_class("MWAClassGenericParameterBlock")
class MWAClassGenericParameterData(GenericParameterData):
    def configure(self):
        # GenericParameterData requires components/phases config mappings.
        # Using class hooks here keeps selection logic in configure(self).
        self.config.components = {
            "Methanol": {
                "type": Component,
                "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
                "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
                "cp_mol_ig_comp": Constant.cp_mol_ig_comp,
                "enth_mol_ig_comp": Constant.enth_mol_ig_comp,
                "entr_mol_ig_comp": Constant.entr_mol_ig_comp,
                "cp_mol_liq_comp": Constant.cp_mol_liq_comp,
                "enth_mol_liq_comp": Constant.enth_mol_liq_comp,
                "entr_mol_liq_comp": Constant.entr_mol_liq_comp,
                "dens_mol_liq_comp": Constant.dens_mol_liq_comp,
                "pressure_sat_comp": NIST,
                "parameter_data": {
                    "mw": (0.0320419, pyunits.kg / pyunits.mol),
                    "pressure_crit": (80.9e5, pyunits.Pa),
                    "temperature_crit": (512.6, pyunits.K),
                    "omega": 0.556,
                    "cp_mol_ig_comp_coeff": (44.0, pyunits.J / pyunits.mol / pyunits.K),
                    "cp_mol_liq_comp_coeff": (81.0, pyunits.J / pyunits.mol / pyunits.K),
                    "dens_mol_liq_comp_coeff": (24700.0, pyunits.mol / pyunits.m**3),
                    "pressure_sat_comp_coeff": {"A": 5.15853, "B": 1569.613, "C": -34.846},
                    "enth_mol_form_liq_comp_ref": (-238.4e3, pyunits.J / pyunits.mol),
                    "entr_mol_form_liq_comp_ref": (127.19, pyunits.J / pyunits.mol / pyunits.K),
                    "enth_mol_form_ig_comp_ref": (-201.0e3, pyunits.J / pyunits.mol),
                    "entr_mol_form_ig_comp_ref": (239.81, pyunits.J / pyunits.mol / pyunits.K),
                },
            },
            "Water": {
                "type": Component,
                "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
                "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
                "cp_mol_ig_comp": Constant.cp_mol_ig_comp,
                "enth_mol_ig_comp": Constant.enth_mol_ig_comp,
                "entr_mol_ig_comp": Constant.entr_mol_ig_comp,
                "cp_mol_liq_comp": Constant.cp_mol_liq_comp,
                "enth_mol_liq_comp": Constant.enth_mol_liq_comp,
                "entr_mol_liq_comp": Constant.entr_mol_liq_comp,
                "dens_mol_liq_comp": Constant.dens_mol_liq_comp,
                "pressure_sat_comp": NIST,
                "parameter_data": {
                    "mw": (0.01801528, pyunits.kg / pyunits.mol),
                    "pressure_crit": (221.2e5, pyunits.Pa),
                    "temperature_crit": (647.3, pyunits.K),
                    "omega": 0.344,
                    "cp_mol_ig_comp_coeff": (33.6, pyunits.J / pyunits.mol / pyunits.K),
                    "cp_mol_liq_comp_coeff": (75.3, pyunits.J / pyunits.mol / pyunits.K),
                    "dens_mol_liq_comp_coeff": (55300.0, pyunits.mol / pyunits.m**3),
                    "pressure_sat_comp_coeff": {"A": 5.40221, "B": 1838.675, "C": -31.737},
                    "enth_mol_form_liq_comp_ref": (-285.83e3, pyunits.J / pyunits.mol),
                    "entr_mol_form_liq_comp_ref": (69.95, pyunits.J / pyunits.mol / pyunits.K),
                    "enth_mol_form_ig_comp_ref": (-241.826e3, pyunits.J / pyunits.mol),
                    "entr_mol_form_ig_comp_ref": (188.84, pyunits.J / pyunits.mol / pyunits.K),
                },
            },
            "Ammonia": {
                "type": Component,
                "valid_phase_types": [PhaseType.vaporPhase, PhaseType.liquidPhase],
                "phase_equilibrium_form": {("Vap", "Liq"): fugacity},
                "cp_mol_ig_comp": Constant.cp_mol_ig_comp,
                "enth_mol_ig_comp": Constant.enth_mol_ig_comp,
                "entr_mol_ig_comp": Constant.entr_mol_ig_comp,
                "cp_mol_liq_comp": Constant.cp_mol_liq_comp,
                "enth_mol_liq_comp": Constant.enth_mol_liq_comp,
                "entr_mol_liq_comp": Constant.entr_mol_liq_comp,
                "dens_mol_liq_comp": Constant.dens_mol_liq_comp,
                "pressure_sat_comp": NIST,
                "parameter_data": {
                    "mw": (0.0170305, pyunits.kg / pyunits.mol),
                    "pressure_crit": (113.0e5, pyunits.Pa),
                    "temperature_crit": (405.4, pyunits.K),
                    "omega": 0.256,
                    "cp_mol_ig_comp_coeff": (37.0, pyunits.J / pyunits.mol / pyunits.K),
                    "cp_mol_liq_comp_coeff": (80.8, pyunits.J / pyunits.mol / pyunits.K),
                    "dens_mol_liq_comp_coeff": (40000.0, pyunits.mol / pyunits.m**3),
                    "pressure_sat_comp_coeff": {"A": 4.8572, "B": 1113.928, "C": -10.409},
                    "enth_mol_form_liq_comp_ref": (-80.3e3, pyunits.J / pyunits.mol),
                    "entr_mol_form_liq_comp_ref": (111.3, pyunits.J / pyunits.mol / pyunits.K),
                    "enth_mol_form_ig_comp_ref": (-46.11e3, pyunits.J / pyunits.mol),
                    "entr_mol_form_ig_comp_ref": (192.8, pyunits.J / pyunits.mol / pyunits.K),
                },
            },
        }
        self.config.phases = {
            "Vap": {"type": VaporPhase, "equation_of_state": Ideal},
            "Liq": {"type": LiquidPhase, "equation_of_state": Ideal},
        }
        self.config.state_definition = FTPx
        self.config.state_bounds = {
            "flow_mol": (1e-8, 100.0, 1e6, pyunits.mol / pyunits.s),
            "temperature": (220.0, 330.0, 700.0, pyunits.K),
            "pressure": (1e4, 101325.0, 5e7, pyunits.Pa),
        }
        self.config.pressure_ref = (101325.0, pyunits.Pa)
        self.config.temperature_ref = (298.15, pyunits.K)
        self.config.base_units = BASE_UNITS
        self.config.phases_in_equilibrium = [("Vap", "Liq")]
        self.config.phase_equilibrium_state = {("Vap", "Liq"): SmoothVLE}
        self.config.bubble_dew_method = IdealBubbleDew
        self.config.include_enthalpy_of_formation = True

        # In this IDAES build, base units metadata is initialized before configure()
        # is called, so set them here explicitly as well for class-definition usage.
        self.get_metadata().add_default_units(BASE_UNITS)

    def parameters(self):
        # Example explicit class-defined parameters (as in docs pattern).
        self.phase_split_seed = Var(
            initialize=0.5,
            bounds=(1e-6, 1 - 1e-6),
            units=pyunits.dimensionless,
            doc="User-defined initialization seed",
        )
        self.component_bias = Var(
            self.component_list,
            initialize=1.0,
            units=pyunits.dimensionless,
            doc="User-defined component tuning factors",
        )
