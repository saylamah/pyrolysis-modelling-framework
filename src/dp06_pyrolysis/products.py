from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class ProductState:
    organic_char_kg: float = 0.0
    inorganic_residue_kg: float = 0.0
    unresolved_solid_kg: float = 0.0

    organic_condensables_kg: float = 0.0
    water_kg: float = 0.0
    heavy_tar_kg: float = 0.0
    unresolved_condensables_kg: float = 0.0

    gas_species_kg: Dict[str, float] = field(default_factory=dict)
    unresolved_gas_kg: float = 0.0
    unresolved_total_kg: float = 0.0

    def solid_total_kg(self) -> float:
        return self.organic_char_kg + self.inorganic_residue_kg + self.unresolved_solid_kg

    def condensables_total_kg(self) -> float:
        return (
            self.organic_condensables_kg + self.water_kg + self.heavy_tar_kg
            + self.unresolved_condensables_kg
        )

    def gas_total_kg(self) -> float:
        return sum(self.gas_species_kg.values()) + self.unresolved_gas_kg

    def accounted_total_kg(self) -> float:
        return (
            self.solid_total_kg() + self.condensables_total_kg()
            + self.gas_total_kg() + self.unresolved_total_kg
        )

    def validate_nonnegative(self):
        vals = [
            self.organic_char_kg, self.inorganic_residue_kg, self.unresolved_solid_kg,
            self.organic_condensables_kg, self.water_kg, self.heavy_tar_kg,
            self.unresolved_condensables_kg, self.unresolved_gas_kg, self.unresolved_total_kg
        ] + list(self.gas_species_kg.values())
        if any(v < 0 for v in vals):
            raise ValueError("product masses must be nonnegative")
        return True
