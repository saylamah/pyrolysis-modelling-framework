"""
Pyrolysis Modelling Framework extension — — Sewage-sludge source/reference adapter v1.0

This module does NOT implement a universal sewage-sludge kinetic solver.

It provides:
- source-locked feedstock/regime/passport integrity checks;
- product-yield closure;
- Coats-Redfern candidate ranking/ambiguity diagnostics;
- relative feedstock-state change diagnostics;
- evidence-routing logic that prevents single-rate fits from being upgraded
  into validated or transferable mechanisms.

Raw multi-rate isoconversional execution should reuse the already-qualified
Pyrolysis Modelling Framework extension — instrument when source rows become byte-local.
"""

from dataclasses import dataclass
from typing import Iterable, Sequence, Mapping
import math
import numpy as np

@dataclass(frozen=True)
class CoatsRedfernCandidate:
    model: str
    E_kJ_mol: float
    A_min_inv: float
    r2: float

@dataclass(frozen=True)
class ProductYieldPoint:
    char_wt_pct: float
    oil_wt_pct: float
    gas_wt_pct: float

def product_mass_closure(point: ProductYieldPoint) -> Mapping[str, float]:
    vals = np.array([point.char_wt_pct, point.oil_wt_pct, point.gas_wt_pct], dtype=float)
    if np.any(vals < 0):
        raise ValueError("Product yields must be non-negative.")
    total = float(vals.sum())
    return {
        "total_wt_pct": total,
        "closure_error_percentage_points": total - 100.0,
        "abs_closure_error_percentage_points": abs(total - 100.0),
    }

def rank_coats_redfern(candidates: Iterable[CoatsRedfernCandidate]):
    c = list(candidates)
    if len(c) < 2:
        raise ValueError("At least two candidate models are required for ambiguity assessment.")
    for x in c:
        if not (0.0 <= x.r2 <= 1.0):
            raise ValueError("R2 must lie in [0,1].")
        if x.E_kJ_mol <= 0 or x.A_min_inv <= 0:
            raise ValueError("Kinetic parameters must be positive.")
    return sorted(c, key=lambda x: x.r2, reverse=True)

def top_model_r2_gap(candidates: Iterable[CoatsRedfernCandidate]) -> Mapping[str, float | str]:
    ranked = rank_coats_redfern(candidates)
    return {
        "best_model": ranked[0].model,
        "best_r2": ranked[0].r2,
        "second_model": ranked[1].model,
        "second_r2": ranked[1].r2,
        "delta_r2": ranked[0].r2 - ranked[1].r2,
    }

def mechanism_identifiability_from_r2(candidates: Iterable[CoatsRedfernCandidate],
                                      close_gap_threshold: float = 0.01) -> str:
    gap = top_model_r2_gap(candidates)["delta_r2"]
    if gap < close_gap_threshold:
        return "UNDERDETERMINED_BY_R2"
    return "R2_SEPARATION_PRESENT_BUT_MECHANISM_NOT_VALIDATED"

def relative_change_percent(initial: float, final: float) -> float:
    if initial == 0:
        raise ValueError("Relative change undefined for zero initial value.")
    return 100.0 * (final - initial) / initial

def reported_category_closure(values: Sequence[float], *,
                              mutually_exclusive_basis_confirmed: bool = False):
    if not mutually_exclusive_basis_confirmed:
        raise ValueError(
            "Closure not authorized: source categories have not been established "
            "as mutually exclusive on one common mass basis."
        )
    vals = np.asarray(values, dtype=float)
    return float(vals.sum())

def kinetic_evidence_route(evidence_type: str) -> Mapping[str, str]:
    routes = {
        "single_dataset_coats_redfern": {
            "evidence_class":"diagnostic/source-fit",
            "allowed":"source-specific candidate ranking and diagnostic reconstruction",
            "blocked":"mechanism validation; universal sewage-sludge activation energy; transfer without validation",
        },
        "multi_rate_isoconversional": {
            "evidence_class":"source-specific conversion-dependent kinetic evidence",
            "allowed":"preserve E(alpha), method identity, heating-rate domain and feedstock state",
            "blocked":"scalarization without scientific reason; universal transfer",
        },
        "multi_stage_masterplot": {
            "evidence_class":"source-specific multistep kinetic reconstruction",
            "allowed":"retain stage structure and source-selected model forms",
            "blocked":"automatic transfer to another sludge state/feedstock",
        },
    }
    if evidence_type not in routes:
        raise ValueError("Unknown evidence type.")
    return routes[evidence_type]

def universal_sludge_activation_energy(*args, **kwargs):
    raise RuntimeError(
        "PROHIBITED: does not define a universal sewage-sludge activation energy."
    )
