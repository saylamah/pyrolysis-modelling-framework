"""
Pyrolysis Modelling Framework extension — Common validation and uncertainty metrics v1.0

Rules:
- no metric comparison without matching observable/basis/context;
- R2 is not accepted as a sole accuracy metric;
- relative error requires a stable, non-zero reference;
- closure metrics are implementation/ledger integrity unless separately tied
  to experimental measurements;
- no universal scalar model score exists.
"""

from dataclasses import dataclass
from typing import Sequence, Mapping
import math
import numpy as np

@dataclass(frozen=True)
class ComparisonIdentity:
    observable: str
    unit: str
    basis: str
    context: str

    def key(self):
        return (self.observable,self.unit,self.basis,self.context)

def errors(pred: Sequence[float], ref: Sequence[float]):
    p=np.asarray(pred,dtype=float); r=np.asarray(ref,dtype=float)
    if p.shape != r.shape or p.size==0:
        raise ValueError("prediction/reference must have identical non-empty shape")
    if not np.isfinite(p).all() or not np.isfinite(r).all():
        raise ValueError("non-finite values are not allowed")
    e=p-r
    return {
        "bias":float(np.mean(e)),
        "mae":float(np.mean(np.abs(e))),
        "rmse":float(np.sqrt(np.mean(e*e))),
        "max_abs_error":float(np.max(np.abs(e))),
    }

def relative_error_percent(pred: float, ref: float, min_abs_reference: float=1e-12) -> float:
    if abs(ref) <= min_abs_reference:
        raise ValueError("relative error unstable/undefined for near-zero reference")
    return 100.0*(pred-ref)/ref

def nrmse(pred: Sequence[float], ref: Sequence[float], *, normalization: str) -> float:
    p=np.asarray(pred,dtype=float); r=np.asarray(ref,dtype=float)
    rmse=errors(p,r)["rmse"]
    if normalization=="range":
        den=float(np.max(r)-np.min(r))
    elif normalization=="mean_abs":
        den=float(np.mean(np.abs(r)))
    elif normalization=="rms_ref":
        den=float(np.sqrt(np.mean(r*r)))
    else:
        raise ValueError("normalization must be range, mean_abs or rms_ref")
    if den <= 1e-15:
        raise ValueError("normalization scale is zero/unstable")
    return rmse/den

def closure_error(components: Sequence[float], target: float=100.0) -> Mapping[str,float]:
    x=np.asarray(components,dtype=float)
    if not np.isfinite(x).all():
        raise ValueError("non-finite closure component")
    total=float(np.sum(x))
    e=total-target
    return {"total":total,"signed_error":e,"abs_error":abs(e)}

def method_dispersion(values: Sequence[float]) -> Mapping[str,float]:
    x=np.asarray(values,dtype=float)
    if len(x)<2 or not np.isfinite(x).all():
        raise ValueError("at least two finite values required")
    mean=float(np.mean(x)); sd=float(np.std(x,ddof=1))
    return {"mean":mean,"sd":sd,"range":float(np.ptp(x)),
            "cv_percent":100.0*sd/mean if mean != 0 else float("nan")}

def heating_rate_response(T_low: float, T_high: float, beta_low: float, beta_high: float) -> float:
    if beta_low<=0 or beta_high<=0 or beta_low==beta_high:
        raise ValueError("heating rates must be positive and distinct")
    return (T_high-T_low)/math.log(beta_high/beta_low)

def comparable(a: ComparisonIdentity,b: ComparisonIdentity) -> bool:
    return a.key()==b.key()

def require_accuracy_metric(metric_names: Sequence[str]) -> None:
    names={m.lower() for m in metric_names}
    residual={"mae","rmse","bias","max_abs_error","absolute_error","relative_error"}
    if "r2" in names and not (names & residual):
        raise ValueError("R2 alone is insufficient as an accuracy metric")

def universal_model_score(*args,**kwargs):
    raise RuntimeError("PROHIBITED: heterogeneous model evidence may not be collapsed into one universal score.")
