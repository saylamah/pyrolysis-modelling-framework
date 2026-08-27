from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math

R = 8.31446261815324

@dataclass(frozen=True)
class LogisticYieldParameters:
    C1: float
    C2: float
    C3_per_K: float
    C4_K: float
    C5: float

@dataclass(frozen=True)
class ArrheniusParameters:
    A_per_s: float
    E_J_per_mol: float

@dataclass(frozen=True)
class TwoStepParameters:
    primary: ArrheniusParameters
    secondary: ArrheniusParameters
    A_phi: float
    E_phi_J_per_mol: float
    phi_LT: float
    phi_HT: float

FINAL_YIELD_PARAMS: Dict[str, LogisticYieldParameters] = {
    "cellulose": LogisticYieldParameters(0.932, 3.105, 1.946, 534.5, 79.77),
    "hemicellulose": LogisticYieldParameters(0.784, 2.625, 1.072, 477.8, 90.44),
    "lignin_full": LogisticYieldParameters(0.698, 3.214, 0.882, 535.5, 67.63),
    "lignin_peak": LogisticYieldParameters(0.662, 1.950, 0.198, 755.2, 40.57),
}

SFOR_PARAMS: Dict[str, ArrheniusParameters] = {
    "cellulose_tga": ArrheniusParameters(1.09e19, 245e3),
    "cellulose_fbr_high": ArrheniusParameters(6.66e7, 124e3),
    "hemicellulose_tga": ArrheniusParameters(7.17e5, 80e3),
    "hemicellulose_fbr_low": ArrheniusParameters(2.54e5, 77e3),
    "hemicellulose_fbr_high": ArrheniusParameters(3.37e2, 37e3),
    "lignin_tga": ArrheniusParameters(1.65, 39e3),
    "lignin_fbr_full": ArrheniusParameters(4.93e3, 78e3),
    "lignin_fbr_peak": ArrheniusParameters(1.16e3, 57e3),
}

TWO_STEP_PARAMS: Dict[str, TwoStepParameters] = {
    "cellulose": TwoStepParameters(
        primary=ArrheniusParameters(2.19e7, 112e3),
        secondary=ArrheniusParameters(6.24e5, 108e3),
        A_phi=1.90e6, E_phi_J_per_mol=104.3e3, phi_LT=0.53, phi_HT=0.00,
    ),
    "lignin": TwoStepParameters(
        primary=ArrheniusParameters(1.72e2, 41.2e3),
        secondary=ArrheniusParameters(2.17e-1, 23.4e3),
        A_phi=6.47e1, E_phi_J_per_mol=27.02e3, phi_LT=1.00, phi_HT=0.47,
    ),
}

HEMICELLULOSE_TWO_STEP_LOW = TwoStepParameters(
    primary=ArrheniusParameters(1.70e5, 70.3e3),
    secondary=ArrheniusParameters(4.26e4, 77.5e3),
    A_phi=1.22e2, E_phi_J_per_mol=31.31e3, phi_LT=0.71, phi_HT=0.00,
)
HEMICELLULOSE_TWO_STEP_HIGH = TwoStepParameters(
    primary=ArrheniusParameters(6.30e1, 22.6e3),
    secondary=ArrheniusParameters(7.45e-1, 9.58e3),
    A_phi=1.22e2, E_phi_J_per_mol=31.31e3, phi_LT=0.71, phi_HT=0.00,
)

def arrhenius_rate(T_K: float, p: ArrheniusParameters) -> float:
    if T_K <= 0:
        raise ValueError("T_K must be > 0")
    return p.A_per_s * math.exp(-p.E_J_per_mol/(R*T_K))

def final_volatile_yield(T_K: float, component: str, lignin_mode: str = "full") -> float:
    if T_K <= 0:
        raise ValueError("T_K must be > 0")
    key = component
    if component == "lignin":
        key = "lignin_peak" if lignin_mode == "peak" else "lignin_full"
    p = FINAL_YIELD_PARAMS[key]
    return p.C1/(1.0 + p.C2*math.exp(-p.C3_per_K*(T_K-p.C4_K)/p.C5))

def sfor_parameter_key(component: str, regime: str) -> str:
    if component == "cellulose":
        if regime not in {"tga","fbr_high"}:
            raise ValueError("cellulose regime must be 'tga' or 'fbr_high'")
        return f"cellulose_{regime}"
    if component == "hemicellulose":
        if regime not in {"tga","fbr_low","fbr_high"}:
            raise ValueError("hemicellulose regime must be tga/fbr_low/fbr_high")
        return f"hemicellulose_{regime}"
    if component == "lignin":
        if regime == "tga":
            return "lignin_tga"
        if regime == "fbr_full":
            return "lignin_fbr_full"
        if regime == "fbr_peak":
            return "lignin_fbr_peak"
        raise ValueError("lignin regime must be tga/fbr_full/fbr_peak")
    raise ValueError("unsupported component")

def sfor_isothermal_release(
    T_K: float, times_s: List[float], component: str, regime: str, lignin_mode: str = "full"
) -> List[Tuple[float,float,float]]:
    p = SFOR_PARAMS[sfor_parameter_key(component, regime)]
    rate = arrhenius_rate(T_K, p)
    yinf = final_volatile_yield(T_K, component, lignin_mode)
    out=[]
    for t in times_s:
        if t < 0:
            raise ValueError("times must be >=0")
        y = yinf*(1.0-math.exp(-rate*t))
        dydt = rate*(yinf-y)
        out.append((float(t),y,dydt))
    return out

def _rk4_scalar(y, T, dt, beta, component, regime, lignin_mode):
    def f(yy, TT):
        p=SFOR_PARAMS[sfor_parameter_key(component,regime)]
        return arrhenius_rate(TT,p)*(final_volatile_yield(TT,component,lignin_mode)-yy)
    k1=f(y,T)
    k2=f(y+0.5*dt*k1,T+0.5*dt*beta)
    k3=f(y+0.5*dt*k2,T+0.5*dt*beta)
    k4=f(y+dt*k3,T+dt*beta)
    return y + dt*(k1+2*k2+2*k3+k4)/6.0

def sfor_linear_ramp(
    T_initial_K: float, T_final_K: float, beta_K_per_s: float,
    component: str, regime: str = "tga", dt_s: float = 0.02, lignin_mode: str = "full"
):
    if not (0 < T_initial_K < T_final_K):
        raise ValueError("require 0 < T_initial_K < T_final_K")
    if beta_K_per_s <= 0 or dt_s <= 0:
        raise ValueError("beta and dt must be >0")
    total=(T_final_K-T_initial_K)/beta_K_per_s
    n=max(1,math.ceil(total/dt_s))
    dt=total/n
    t=0.0; T=T_initial_K; y=0.0
    hist=[(t,T,y)]
    for _ in range(n):
        y=_rk4_scalar(y,T,dt,beta_K_per_s,component,regime,lignin_mode)
        t += dt
        T = T_initial_K + beta_K_per_s*t
        hist.append((t,T,y))
    return hist

def phi_intermediate(T_K: float, component: str) -> float:
    if component == "hemicellulose":
        p=HEMICELLULOSE_TWO_STEP_LOW
    else:
        p=TWO_STEP_PARAMS[component]
    z=p.A_phi*math.exp(-p.E_phi_J_per_mol/(R*T_K))
    return p.phi_LT - (p.phi_LT-p.phi_HT)*(1.0-math.exp(-z))

def two_step_parameters(component: str, T_K: float) -> TwoStepParameters:
    if component == "hemicellulose":
        return HEMICELLULOSE_TWO_STEP_LOW if T_K < 723.0 else HEMICELLULOSE_TWO_STEP_HIGH
    return TWO_STEP_PARAMS[component]

def two_step_isothermal(
    T_K: float, t_end_s: float, component: str, dt_s: float = 0.001, lignin_mode: str = "full"
):
    if t_end_s < 0 or dt_s <= 0:
        raise ValueError("invalid time settings")
    p=two_step_parameters(component,T_K)
    rp=arrhenius_rate(T_K,p.primary)
    rs=arrhenius_rate(T_K,p.secondary)
    phi=phi_intermediate(T_K,component)
    yinf=final_volatile_yield(T_K,component,lignin_mode)
    ychar_inf=1.0-yinf

    def deriv(s):
        yc, yi, yvp, yvs=s
        pot=max(0.0,yc-ychar_inf)
        q=rp*pot
        return (-q, phi*q-rs*yi, (1.0-phi)*q, rs*yi)

    n=max(1,math.ceil(t_end_s/dt_s)) if t_end_s>0 else 0
    dt=t_end_s/n if n else 0.0
    s=(1.0,0.0,0.0,0.0)
    hist=[(0.0,*s)]
    t=0.0
    for _ in range(n):
        k1=deriv(s)
        s2=tuple(s[i]+0.5*dt*k1[i] for i in range(4))
        k2=deriv(s2)
        s3=tuple(s[i]+0.5*dt*k2[i] for i in range(4))
        k3=deriv(s3)
        s4=tuple(s[i]+dt*k3[i] for i in range(4))
        k4=deriv(s4)
        s=tuple(s[i]+dt*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6.0 for i in range(4))
        t += dt
        hist.append((t,*s))
    return hist
