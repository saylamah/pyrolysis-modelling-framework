"""
Pyrolysis Modelling Framework extension — — Common DAEM / isoconversional comparison instrument v0.1

Purpose
-------
Reusable, source-bounded comparison functions for non-isothermal TGA kinetics.
This module deliberately separates:
1) source-parameterized DAEM distribution descriptors, and
2) model-free / multi-heating-rate isoconversional activation-energy estimates.

Evidence boundary
-----------------
Numerical agreement with source tables or synthetic identities verifies
implementation integrity. It does not constitute new experimental validation.

No model fitting is performed automatically.
No universal activation energy is inferred across feedstocks.
"""

from dataclasses import dataclass
from typing import Iterable, Sequence, Mapping, Optional
import math
import numpy as np

R_J_MOL_K = 8.31446261815324

@dataclass(frozen=True)
class RegressionResult:
    slope: float
    intercept: float
    r2: float
    n: int

@dataclass(frozen=True)
class IsoResult:
    method: str
    alpha: Optional[float]
    E_kJ_mol: float
    regression: RegressionResult
    notes: str = ""

@dataclass(frozen=True)
class DAEMComponent:
    weight: float
    log10_k0_s: float
    E_kJ_mol: float
    sigma_kJ_mol: float

@dataclass(frozen=True)
class TGRun:
    beta_K_min: float
    temperature_K: np.ndarray
    mass: np.ndarray
    m0: float
    mf: float
    source_id: str = ""

    def conversion(self) -> np.ndarray:
        denom = self.m0 - self.mf
        if denom <= 0:
            raise ValueError("m0 must exceed mf for the chosen source-defined conversion basis.")
        return (self.m0 - np.asarray(self.mass, dtype=float)) / denom

def linear_regression(x: Sequence[float], y: Sequence[float]) -> RegressionResult:
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y) or len(x) < 3:
        raise ValueError("x and y must be 1-D arrays of equal length with at least 3 points.")
    A = np.column_stack([x, np.ones_like(x)])
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    yhat = slope * x + intercept
    ss_res = float(np.sum((y - yhat)**2)); ss_tot = float(np.sum((y - np.mean(y))**2))
    r2 = 1.0 if ss_tot == 0.0 and ss_res == 0.0 else 1.0 - ss_res / ss_tot
    return RegressionResult(float(slope), float(intercept), float(r2), int(len(x)))

def _check_beta_T(beta_K_min: Sequence[float], T_K: Sequence[float]):
    beta = np.asarray(beta_K_min, dtype=float); T = np.asarray(T_K, dtype=float)
    if len(beta) < 3: raise ValueError("At least three heating rates are required.")
    if len(beta) != len(T): raise ValueError("beta and T must have equal length.")
    if np.any(beta <= 0) or np.any(T <= 0): raise ValueError("beta and T must be positive.")
    return beta, T

def kas(beta_K_min: Sequence[float], T_alpha_K: Sequence[float], alpha=None) -> IsoResult:
    beta, T = _check_beta_T(beta_K_min, T_alpha_K)
    reg = linear_regression(1.0/T, np.log(beta/(T*T)))
    return IsoResult("KAS", alpha, -reg.slope * R_J_MOL_K / 1000.0, reg, "ln(beta/T^2) vs 1/T")

def daem_integral_source2021(beta_K_min: Sequence[float], T_alpha_K: Sequence[float], alpha=None) -> IsoResult:
    beta, T = _check_beta_T(beta_K_min, T_alpha_K)
    reg = linear_regression(1.0/T, np.log(beta/(T*T)))
    return IsoResult("DAEM-integral-source2021", alpha, -reg.slope * R_J_MOL_K / 1000.0, reg,
                     "Source-specific multi-rate DAEM linear form; same E slope as KAS.")

def fwo(beta_K_min: Sequence[float], T_alpha_K: Sequence[float], alpha=None) -> IsoResult:
    beta, T = _check_beta_T(beta_K_min, T_alpha_K)
    reg = linear_regression(1.0/T, np.log(beta))
    return IsoResult("FWO", alpha, -reg.slope * R_J_MOL_K / (1.052 * 1000.0), reg, "ln(beta) vs 1/T; source coefficient 1.052")

def friedman(beta_K_min: Sequence[float], T_alpha_K: Sequence[float], dalpha_dT_at_alpha: Sequence[float], alpha=None) -> IsoResult:
    beta, T = _check_beta_T(beta_K_min, T_alpha_K)
    dadt = np.asarray(dalpha_dT_at_alpha, dtype=float)
    if len(dadt) != len(beta) or np.any(dadt <= 0):
        raise ValueError("dalpha_dT_at_alpha must be positive and match beta length.")
    reg = linear_regression(1.0/T, np.log(beta * dadt))
    return IsoResult("Friedman", alpha, -reg.slope * R_J_MOL_K / 1000.0, reg, "ln(beta*dalpha/dT) vs 1/T")

def starink_source2021(beta_K_min: Sequence[float], T_alpha_K: Sequence[float], alpha=None) -> IsoResult:
    beta, T = _check_beta_T(beta_K_min, T_alpha_K)
    reg = linear_regression(1.0/T, np.log(beta/(T**1.8)))
    q = -reg.slope * R_J_MOL_K / 1000.0
    a = 1.2e-5; b = -1.0070; c = q
    disc = b*b - 4*a*c
    if disc < 0: raise ValueError("Source-specific Starink inversion has no real solution.")
    E1 = (-b - math.sqrt(disc))/(2*a); E2 = (-b + math.sqrt(disc))/(2*a)
    candidates = [e for e in (E1, E2) if e > 0]
    if not candidates: raise ValueError("No positive Starink activation-energy root.")
    return IsoResult("Starink-source2021", alpha, min(candidates), reg,
                     "Source-specific exponent 1.8 and A(E) correction; not silently replaced by another Starink variant.")

def temperature_at_conversion(run: TGRun, alpha_target: float) -> float:
    if not (0.0 < alpha_target < 1.0): raise ValueError("alpha_target must lie strictly between 0 and 1.")
    T = np.asarray(run.temperature_K, dtype=float); a = run.conversion(); order = np.argsort(T); T, a = T[order], a[order]
    if np.any(np.diff(a) < -1e-4): raise ValueError("Conversion is materially non-monotone; source preprocessing must be explicit.")
    a_mon = np.maximum.accumulate(a)
    if alpha_target < a_mon[0] or alpha_target > a_mon[-1]: raise ValueError("Requested conversion lies outside this source-defined run.")
    return float(np.interp(alpha_target, a_mon, T))

def source_daem_mixture_moments(components: Iterable[DAEMComponent]) -> Mapping[str, float]:
    comps = list(components)
    if not comps: raise ValueError("At least one DAEM component is required.")
    w = np.array([c.weight for c in comps], dtype=float)
    if np.any(w < 0): raise ValueError("Weights must be non-negative.")
    sw = float(w.sum())
    if not math.isclose(sw, 1.0, rel_tol=0, abs_tol=2e-3): raise ValueError(f"DAEM component weights must close to 1; got {sw}.")
    w = w/sw; E = np.array([c.E_kJ_mol for c in comps], dtype=float); s = np.array([c.sigma_kJ_mol for c in comps], dtype=float)
    mean = float(np.sum(w*E)); variance = float(np.sum(w*(s*s + (E-mean)**2)))
    return {"E_weighted_mean_kJ_mol": mean, "E_weighted_sd_kJ_mol": math.sqrt(max(variance, 0.0)), "weight_sum": float(sw), "n_components": len(comps)}

def method_ensemble_summary(values_by_method: Mapping[str, float]) -> Mapping[str, float]:
    vals = np.array(list(values_by_method.values()), dtype=float)
    mean = float(np.mean(vals)); sd = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
    return {"mean_kJ_mol": mean, "range_kJ_mol": float(np.ptp(vals)), "sd_kJ_mol": sd,
            "cv_percent": float(100.0*sd/mean) if mean != 0 else float("nan"), "n_methods": int(len(vals))}
