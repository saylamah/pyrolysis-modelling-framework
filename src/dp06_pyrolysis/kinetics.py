from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence
import math

R_J_PER_MOL_K = 8.31446261815324

@dataclass(frozen=True)
class ArrheniusReaction:
    A_per_s: float
    E_J_per_mol: float
    weight: float = 1.0

    def __post_init__(self):
        if self.A_per_s < 0:
            raise ValueError("A_per_s must be >= 0")
        if self.E_J_per_mol < 0:
            raise ValueError("E_J_per_mol must be >= 0")
        if self.weight < 0:
            raise ValueError("weight must be >= 0")

    def k(self, T_K: float) -> float:
        if T_K <= 0:
            raise ValueError("temperature must be > 0 K")
        return self.A_per_s * math.exp(-self.E_J_per_mol / (R_J_PER_MOL_K * T_K))

def first_order_isothermal_conversion(reaction: ArrheniusReaction, T_K: float, t_s: float) -> float:
    if t_s < 0:
        raise ValueError("t_s must be >= 0")
    k = reaction.k(T_K)
    return 1.0 - math.exp(-k * t_s)

def _rk4_step(alpha: float, T: float, dt: float, beta: float, rxn: ArrheniusReaction) -> float:
    # dα/dt = k(T)*(1-α); dT/dt = beta
    def f(a, temp):
        return rxn.k(temp) * (1.0 - a)
    k1 = f(alpha, T)
    k2 = f(alpha + 0.5*dt*k1, T + 0.5*dt*beta)
    k3 = f(alpha + 0.5*dt*k2, T + 0.5*dt*beta)
    k4 = f(alpha + dt*k3, T + dt*beta)
    anew = alpha + dt*(k1 + 2*k2 + 2*k3 + k4)/6.0
    return min(1.0, max(0.0, anew))

def first_order_linear_ramp(
    reaction: ArrheniusReaction,
    T_initial_K: float,
    T_final_K: float,
    heating_rate_K_per_s: float,
    dt_s: float = 0.01,
):
    if T_initial_K <= 0 or T_final_K <= T_initial_K:
        raise ValueError("require 0 < T_initial_K < T_final_K")
    if heating_rate_K_per_s <= 0:
        raise ValueError("heating_rate_K_per_s must be > 0")
    if dt_s <= 0:
        raise ValueError("dt_s must be > 0")

    total_t = (T_final_K - T_initial_K) / heating_rate_K_per_s
    n = max(1, math.ceil(total_t / dt_s))
    dt = total_t / n
    alpha = 0.0
    T = T_initial_K
    history = [(0.0, T, alpha)]
    t = 0.0
    for _ in range(n):
        alpha = _rk4_step(alpha, T, dt, heating_rate_K_per_s, reaction)
        t += dt
        T = T_initial_K + heating_rate_K_per_s * t
        history.append((t, T, alpha))
    return history

def independent_parallel_conversion(
    reactions: Sequence[ArrheniusReaction],
    T_initial_K: float,
    T_final_K: float,
    heating_rate_K_per_s: float,
    dt_s: float = 0.01,
):
    if not reactions:
        raise ValueError("at least one reaction is required")
    wsum = sum(r.weight for r in reactions)
    if wsum <= 0:
        raise ValueError("sum of reaction weights must be > 0")

    normalized = [ArrheniusReaction(r.A_per_s, r.E_J_per_mol, r.weight/wsum) for r in reactions]
    histories = [
        first_order_linear_ramp(r, T_initial_K, T_final_K, heating_rate_K_per_s, dt_s)
        for r in normalized
    ]
    times = [row[0] for row in histories[0]]
    temps = [row[1] for row in histories[0]]
    combined = []
    for j in range(len(times)):
        a = sum(r.weight * histories[i][j][2] for i, r in enumerate(normalized))
        combined.append((times[j], temps[j], a))
    return combined
