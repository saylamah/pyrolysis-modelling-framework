"""Pyrolysis Modelling Framework extension — empirical reference layer — v0.2.0 rights-safe reconstruction.

Reconstructed from the frozen v63 gate and parent matrix without changing
scientific values. These are SOURCE-BOUNDED interpolation/null references.
No extrapolation and no cross-feedstock transfer are authorized.
"""
from __future__ import annotations
import math
from typing import Mapping
import numpy as np

BIO_T_C=np.array([500.0,600.0,800.0])
BIO_GAS=np.array([7.3,22.9,63.9])
BIO_OIL=np.array([75.4,62.1,27.2])
BIO_CHAR=np.array([17.3,15.0,8.9])

MAN_T_C=np.array([400.,450.,500.,550.,600.,700.,800.])
MAN_GAS_N_PCT=np.array([15.0,15.0,23.3333333333333,16.6666666666667,30.0,38.3333333333333,35.0])

EMP_MIX1_FROZEN_METRICS={"mae_pp":1.411,"rmse_pp":1.845,"bias_pp":-1.186,"max_abs_pp":3.583}

def _bounded_interp(x: float, xp: np.ndarray, fp: np.ndarray) -> float:
    if not (float(xp.min()) <= x <= float(xp.max())):
        raise ValueError("Extrapolation is prohibited for this source-bounded reference.")
    return float(np.interp(float(x),xp,fp))

def emp_bio1(T_C: float) -> Mapping[str,float]:
    """Pinewood sawdust, external steam S/B=4, CSBR; 500–800 °C only."""
    gas=_bounded_interp(T_C,BIO_T_C,BIO_GAS)
    oil=_bounded_interp(T_C,BIO_T_C,BIO_OIL)
    char=100.0-gas-oil
    return {"gas_wt_pct":gas,"biooil_wt_pct":oil,"char_wt_pct":char}

def emp_bio1_outer_anchor_holdout_600() -> Mapping[str,float]:
    """Frozen 600 °C same-study holdout using only 500 and 800 °C anchors."""
    gas=float(np.interp(600.0,[500.,800.],[7.3,63.9]))
    oil=float(np.interp(600.0,[500.,800.],[75.4,27.2]))
    char=100.0-gas-oil
    ref=np.array([22.9,62.1,15.0]); pred=np.array([gas,oil,char]); e=pred-ref
    return {"gas_wt_pct":gas,"biooil_wt_pct":oil,"char_wt_pct":char,
            "mae_pp":float(np.mean(np.abs(e))),"rmse_pp":float(np.sqrt(np.mean(e*e)))}

def emp_man1(T_C: float) -> Mapping[str,float]:
    """Chicken-manure gas-phase elemental-N ledger; 400–800 °C source domain."""
    gas=_bounded_interp(T_C,MAN_T_C,MAN_GAS_N_PCT)
    return {"gas_phase_N_pct_initial_N":gas,"non_gas_N_pct_initial_N":100.0-gas}

def emp_man1_leave_one_interior_out() -> Mapping[str,float]:
    errs=[]
    for i in range(1,len(MAN_T_C)-1):
        pred=float(np.interp(MAN_T_C[i],[MAN_T_C[i-1],MAN_T_C[i+1]],[MAN_GAS_N_PCT[i-1],MAN_GAS_N_PCT[i+1]]))
        errs.append(pred-MAN_GAS_N_PCT[i])
    e=np.asarray(errs,dtype=float)
    return {"mae_pp":float(np.mean(np.abs(e))),"rmse_pp":float(np.sqrt(np.mean(e*e))),"max_abs_pp":float(np.max(np.abs(e)))}

def emp_pl1(beta_C_min: float) -> float:
    """HDPE DTG-peak response; source-bounded to 2.5–10 °C min^-1."""
    beta=float(beta_C_min)
    if not (2.5 <= beta <= 10.0):
        raise ValueError("EMP-PL1 is bounded to 2.5–10 °C min^-1.")
    beta_ref=1.0  # K min^-1; makes the logarithm dimensionless
    b=(471.0-440.0)/(math.log(10.0/beta_ref)-math.log(2.5/beta_ref))
    a=440.0-b*math.log(2.5/beta_ref)
    return a+b*math.log(beta/beta_ref)

def emp_mix1_char_null(biomass_fraction: float, char_biomass: float, char_pp: float) -> float:
    """Measured-component additive char null; no interaction coefficient."""
    w=float(biomass_fraction)
    if not (0.0 <= w <= 1.0):
        raise ValueError("biomass_fraction must lie in [0,1].")
    return w*float(char_biomass)+(1.0-w)*float(char_pp)
