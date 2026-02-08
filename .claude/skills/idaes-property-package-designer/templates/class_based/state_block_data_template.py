"""Template: class-based StateBlockData implementation."""

from pyomo.environ import Var, Constraint, NonNegativeReals, units as pyunits
from idaes.core import (
    declare_process_block_class,
    StateBlockData,
    MaterialFlowBasis,
    MaterialBalanceType,
    EnergyBalanceType,
)

# from .state_block_methods_template import _TemplateStateBlock


@declare_process_block_class("TemplateStateBlock", block_class=None)
class TemplateStateBlockData(StateBlockData):
    """Replace block_class=None with your methods class and complete methods."""

    def build(self):
        super().build()

        self.flow_mol = Var(
            initialize=1.0,
            domain=NonNegativeReals,
            units=pyunits.mol / pyunits.s,
        )
        self.temperature = Var(initialize=298.15, units=pyunits.K)
        self.pressure = Var(initialize=101325.0, units=pyunits.Pa)

        self.mole_frac_comp = Var(
            self.params.component_list,
            initialize=1.0 / max(1, len(self.params.component_list)),
        )

        self.sum_mole_frac = Constraint(
            expr=sum(self.mole_frac_comp[j] for j in self.params.component_list) == 1.0
        )

    def _enth_mol(self):
        # Replace with model-specific enthalpy expression/constraints.
        self.enth_mol = Var(initialize=0.0, units=pyunits.J / pyunits.mol)

    def get_material_flow_basis(self):
        return MaterialFlowBasis.molar

    def get_material_flow_terms(self, p, j):
        return self.flow_mol * self.mole_frac_comp[j]

    def get_material_density_terms(self, p, j):
        raise NotImplementedError("Implement material density terms for your package.")

    def get_enthalpy_flow_terms(self, p):
        return self.flow_mol * self.enth_mol

    def get_energy_density_terms(self, p):
        raise NotImplementedError("Implement energy density terms for your package.")

    def default_material_balance_type(self):
        return MaterialBalanceType.componentPhase

    def default_energy_balance_type(self):
        return EnergyBalanceType.enthalpyTotal

    def define_state_vars(self):
        return {
            "flow_mol": self.flow_mol,
            "mole_frac_comp": self.mole_frac_comp,
            "temperature": self.temperature,
            "pressure": self.pressure,
        }
