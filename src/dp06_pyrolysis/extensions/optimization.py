"""
Pyrolysis Modelling Framework extension — v77 — Evidence-constrained process optimization utilities.

This is a framework utility, NOT a universal pyrolysis optimizer.

It only:
- checks candidate-domain / evidence / closure constraints,
- constructs non-dominated Pareto sets for explicit objectives,
- evaluates robustness of feasibility under supplied scenarios.

It does NOT:
- create missing model outputs,
- extrapolate silently,
- assign a universal scalar score,
- select one "best" operating point without an explicit decision rule.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple
import numpy as np

@dataclass(frozen=True)
class OptimizationDomain:
    bounds: Mapping[str, Tuple[float,float]]
    pressure_enabled: bool = False

@dataclass(frozen=True)
class EvidenceEligibility:
    model_eligible: bool
    predictive_validation_adequate: bool
    uncertainty_available: bool
    exploratory_only: bool = False

def inside_domain(point: Mapping[str,float], domain: OptimizationDomain) -> bool:
    for k,v in point.items():
        if k == "P" and not domain.pressure_enabled:
            raise ValueError("Pressure optimization is outside the currently validated public domain.")
        if k not in domain.bounds:
            raise ValueError(f"Variable {k} is not declared in optimization domain.")
        lo,hi=domain.bounds[k]
        if lo>hi:
            raise ValueError(f"Invalid bounds for {k}.")
        if not (lo <= float(v) <= hi):
            return False
    return True

def optimization_status(point: Mapping[str,float],
                        domain: OptimizationDomain,
                        evidence: EvidenceEligibility,
                        closure_ok: bool,
                        engineering_constraints_ok: bool) -> str:
    if not evidence.model_eligible:
        return "BLOCKED_MODEL_INELIGIBLE"
    if not inside_domain(point,domain):
        return "BLOCKED_OUTSIDE_DOMAIN"
    if not closure_ok:
        return "BLOCKED_CLOSURE"
    if not engineering_constraints_ok:
        return "BLOCKED_ENGINEERING_CONSTRAINT"
    if not evidence.predictive_validation_adequate:
        return "EXPLORATORY_ONLY" if evidence.exploratory_only else "BLOCKED_VALIDATION"
    if not evidence.uncertainty_available:
        return "BOUNDED_NO_QUANTIFIED_UNCERTAINTY"
    return "ELIGIBLE_FOR_DECISION_OPTIMIZATION"

def pareto_front(values: Sequence[Sequence[float]],
                 directions: Sequence[str]) -> List[int]:
    a=np.asarray(values,dtype=float)
    if a.ndim != 2 or a.shape[0]==0:
        raise ValueError("values must be a non-empty 2D array")
    if len(directions)!=a.shape[1]:
        raise ValueError("directions length must equal number of objectives")
    sign=[]
    for d in directions:
        if d=="max": sign.append(1.0)
        elif d=="min": sign.append(-1.0)
        else: raise ValueError("direction must be 'max' or 'min'")
    z=a*np.asarray(sign)
    keep=[]
    for i in range(len(z)):
        dominated=False
        for j in range(len(z)):
            if i==j: continue
            if np.all(z[j] >= z[i]) and np.any(z[j] > z[i]):
                dominated=True
                break
        if not dominated:
            keep.append(i)
    return keep

def robust_feasibility(scenario_feasible: Sequence[bool],
                       required_fraction: float=1.0) -> Mapping[str,float|bool]:
    x=np.asarray(scenario_feasible,dtype=bool)
    if x.size==0:
        raise ValueError("at least one uncertainty scenario is required")
    if not (0 < required_fraction <= 1):
        raise ValueError("required_fraction must lie in (0,1]")
    frac=float(np.mean(x))
    return {
        "feasible_fraction":frac,
        "robustly_feasible":bool(frac >= required_fraction)
    }

def universal_optimum(*args,**kwargs):
    raise RuntimeError(
        "PROHIBITED: Pyrolysis Modelling Framework extension — does not define a universal optimum. "
        "Optima are feedstock/regime/model/objective/constraint specific."
    )
