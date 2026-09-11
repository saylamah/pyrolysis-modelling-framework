"""
Pyrolysis Modelling Framework extension — P2-FW1 — Food-waste source/reference adapter v1.0

No universal food-waste kinetic model is defined.

The module implements only source-published, source-bounded Yasir et al. (2025)
reaction-order and frequency-factor correlations plus source-traceable diagnostics.
Activation-energy execution from raw multi-rate data must reuse Pyrolysis Modelling Framework extension — P1-B.
"""

import math
from typing import Mapping, Sequence
import numpy as np

R_J_MOL_K = 8.31446261815324

def yasir_stage_order(alpha: float) -> float:
    if not (0.0 <= alpha <= 0.90):
        raise ValueError("Source staged-order mapping is bounded to 0 <= alpha <= 0.90.")
    if alpha < 0.35:
        return 11.0
    if alpha < 0.70:
        return 9.6
    if alpha < 0.80:
        return 9.4
    return 11.2

def yasir_n_of_alpha(alpha: float) -> float:
    if not (0.0 <= alpha <= 0.90):
        raise ValueError("Source correlation outside qualified conversion domain.")
    return 14.57*alpha**2 - 15.27*alpha + 13.28

def yasir_A_of_alpha(alpha: float) -> float:
    if not (0.0 <= alpha <= 0.90):
        raise ValueError("Source correlation outside qualified conversion domain.")
    return 1.0e20*alpha**2 - 1.0e20*alpha + 3.0e19

def yasir_n_of_temperature_C(T_C: float) -> float:
    if not (25.0 <= T_C <= 900.0):
        raise ValueError("Outside source TGA temperature envelope.")
    return 5.38e-5*T_C**2 - 4.03e-2*T_C + 16.94

def yasir_A_of_temperature_C(T_C: float) -> float:
    if not (25.0 <= T_C <= 900.0):
        raise ValueError("Outside source TGA temperature envelope.")
    return 4.0e14*T_C**2 - 3.0e17*T_C + 6.0e19

def arrhenius_k(A: float, E_kJ_mol: float, T_K: float) -> float:
    if A <= 0 or E_kJ_mol <= 0 or T_K <= 0:
        raise ValueError("A, E and T must be positive.")
    return A*math.exp(-(E_kJ_mol*1000.0)/(R_J_MOL_K*T_K))

def source_rate(C_vol_kmol_m3: float, A: float, E_kJ_mol: float, T_K: float, n: float) -> float:
    if C_vol_kmol_m3 < 0 or n <= 0:
        raise ValueError("C_vol must be non-negative and n positive.")
    return arrhenius_k(A,E_kJ_mol,T_K)*(C_vol_kmol_m3**n)

def method_dispersion(E_values_kJ_mol: Sequence[float]) -> Mapping[str,float]:
    x=np.asarray(E_values_kJ_mol,dtype=float)
    if len(x)<2 or np.any(x<=0):
        raise ValueError("At least two positive activation energies are required.")
    mean=float(np.mean(x))
    sd=float(np.std(x,ddof=1))
    return {
        "mean_kJ_mol":mean,
        "sd_kJ_mol":sd,
        "range_kJ_mol":float(np.ptp(x)),
        "cv_percent":100.0*sd/mean,
    }

def validation_error_class(relative_error_percent: float) -> str:
    a=abs(relative_error_percent)
    if a <= 10:
        return "within_10_percent"
    if a <= 25:
        return "10_to_25_percent"
    return "greater_than_25_percent"

def universal_food_waste_kinetics(*args,**kwargs):
    raise RuntimeError(
        "PROHIBITED: FW1 preserves feedstock/source-specific staged kinetics; "
        "no universal food-waste kinetic triplet is defined."
    )
