from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from .products import ProductState

@dataclass(frozen=True)
class MassLedger:
    input_mass_kg: float
    output_mass_kg: float
    closure_residual: float

    @classmethod
    def from_product_state(cls, input_mass_kg: float, products: ProductState):
        if input_mass_kg <= 0:
            raise ValueError("input_mass_kg must be > 0")
        products.validate_nonnegative()
        out = products.accounted_total_kg()
        residual = (input_mass_kg - out) / input_mass_kg
        return cls(input_mass_kg, out, residual)

@dataclass(frozen=True)
class ElementBalance:
    input_kg: float
    output_kg: float
    closure_residual: float

@dataclass(frozen=True)
class ElementLedger:
    elements: Dict[str, ElementBalance]

    @classmethod
    def from_totals(cls, inputs_kg: Dict[str, float], outputs_kg: Dict[str, float]):
        data = {}
        for element, inp in inputs_kg.items():
            if inp < 0:
                raise ValueError(f"{element}: negative element input")
            out = outputs_kg.get(element, 0.0)
            if out < 0:
                raise ValueError(f"{element}: negative element output")
            residual = 0.0 if inp == 0 and out == 0 else ((inp - out) / inp if inp != 0 else float("inf"))
            data[element] = ElementBalance(inp, out, residual)
        extra = set(outputs_kg) - set(inputs_kg)
        if extra:
            raise ValueError(f"outputs contain elements absent from inputs: {sorted(extra)}")
        return cls(data)

    def max_abs_residual(self) -> float:
        vals = [abs(v.closure_residual) for v in self.elements.values() if v.closure_residual != float("inf")]
        return max(vals) if vals else 0.0
