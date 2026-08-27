from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Protocol
import math

from .core import StudyCase, ModelManifest
from .integrity import validate_study_case
from .products import ProductState
from .balances import MassLedger, ElementLedger
from .models.rwth2021 import (
    sfor_linear_ramp, sfor_isothermal_release, final_volatile_yield,
    arrhenius_rate, SFOR_PARAMS, sfor_parameter_key
)

class AdapterDomainError(ValueError):
    pass

class AdapterNotImplementedError(NotImplementedError):
    pass

@dataclass(frozen=True)
class AdapterResult:
    case_id: str
    model_manifest: ModelManifest
    outputs: Dict[str, float]
    product_state: ProductState
    mass_ledger: MassLedger
    element_ledger: ElementLedger
    energy_ledger: Dict[str, Any]
    warnings: tuple[str, ...]

class ModelAdapter(Protocol):
    model_id: str
    def run(self, case: StudyCase, adapter_inputs: Dict[str, Any], dry_feed_mass_kg: float=1.0) -> AdapterResult:
        ...

def _element_inputs(case: StudyCase, dry_feed_mass_kg: float):
    ult = case.feedstock.ultimate_analysis
    if ult is None:
        return {}
    if ult.basis.value == "dry":
        return {k: float(v)*dry_feed_mass_kg for k,v in ult.values.items()}
    if ult.basis.value == "dry_ash_free":
        ash = float(case.feedstock.proximate_analysis.values.get("ash",0.0))
        organic = dry_feed_mass_kg*(1.0-ash)
        return {k: float(v)*organic for k,v in ult.values.items()}
    return {}


def stable_sfor_linear_ramp(
    T_initial_K: float,
    T_final_K: float,
    beta_K_per_s: float,
    component: str,
    regime: str = "tga",
    dT_K: float = 0.05,
    lignin_mode: str = "full",
):
    """
    Numerically stable integration of the same source SFOR ODE:
        dy/dt = k(T) * (y_inf(T) - y)

    A midpoint exponential update is used over each temperature interval.
    It changes no source equation or coefficient and remains bounded for the
    stiff high-temperature tail where the inherited explicit RK4 can become unstable.
    """
    if not (0 < T_initial_K < T_final_K):
        raise ValueError("require 0 < T_initial_K < T_final_K")
    if beta_K_per_s <= 0 or dT_K <= 0:
        raise ValueError("beta_K_per_s and dT_K must be > 0")

    p = SFOR_PARAMS[sfor_parameter_key(component, regime)]
    T = float(T_initial_K)
    y = 0.0
    hist=[(0.0,T,y)]
    t=0.0
    while T < T_final_K - 1e-14:
        step=min(float(dT_K), T_final_K-T)
        Tmid=T+0.5*step
        dt=step/beta_K_per_s
        kval=arrhenius_rate(Tmid,p)
        yinf=final_volatile_yield(Tmid,component,lignin_mode)
        y=yinf+(y-yinf)*math.exp(-kval*dt)
        t += dt
        T += step
        hist.append((t,T,y))
    return hist

class RWTHSFORAdapter:
    model_id = "SFOR_RWTH"

    def __init__(self):
        self.manifest = ModelManifest(
            model_id=self.model_id,
            model_name="RWTH 2021 source-faithful SFOR adapter",
            version="0.1.0rc2",
            fidelity_level="L1",
            feedstock_families=["lignocellulosic_biomass"],
            supported_atmospheres=["inert"],
            required_input_blocks=["proximate_analysis","component_identity","thermal_program"],
            supported_outputs=["total_yield","conversion","remaining_solid_fraction"],
            licence_class="source_equations_parameters_citable",
            redistribution_allowed=True,
            known_limitations=[
                "Calibrated/source-domain model, not universal biomass kinetics.",
                "No detailed product chemistry.",
                "No CO2/steam/oxidative chemistry.",
                "Component-specific source parameters required.",
            ],
        )

    def run(self, case: StudyCase, adapter_inputs: Dict[str, Any], dry_feed_mass_kg: float=1.0) -> AdapterResult:
        validate_study_case(case)
        if dry_feed_mass_kg <= 0:
            raise ValueError("dry_feed_mass_kg must be >0")
        if case.feedstock.family.value != "lignocellulosic_biomass":
            raise AdapterDomainError("SFOR_RWTH public SFOR adapter requires lignocellulosic_biomass")
        if case.regime.atmosphere_class.value != "inert":
            raise AdapterDomainError("SFOR_RWTH public SFOR adapter supports inert atmosphere only")

        component = str(adapter_inputs.get("component","")).lower()
        if component not in {"cellulose","hemicellulose","lignin"}:
            raise AdapterDomainError("adapter_inputs.component must be cellulose/hemicellulose/lignin")

        regime = str(adapter_inputs.get("regime","tga"))
        lignin_mode = str(adapter_inputs.get("lignin_mode","full"))
        dT_K = float(adapter_inputs.get("dT_K",0.05))
        tp = case.regime.thermal_program

        if tp.type == "linear_ramp":
            if tp.T_initial_K is None or tp.T_final_K is None or tp.heating_rate_K_per_s is None:
                raise ValueError("linear_ramp requires T_initial_K, T_final_K and heating_rate_K_per_s")
            hist = stable_sfor_linear_ramp(
                tp.T_initial_K, tp.T_final_K, tp.heating_rate_K_per_s,
                component=component, regime=regime, dT_K=dT_K, lignin_mode=lignin_mode
            )
            yvol = float(hist[-1][2])
            T_final = float(hist[-1][1])
            yinf = float(final_volatile_yield(T_final,component,lignin_mode))
        elif tp.type == "isothermal":
            if tp.T_K is None or tp.hold_time_s is None:
                raise ValueError("isothermal requires T_K and hold_time_s")
            points = sfor_isothermal_release(
                tp.T_K,[tp.hold_time_s],component=component,regime=regime,lignin_mode=lignin_mode
            )
            yvol = float(points[-1][1])
            yinf = float(final_volatile_yield(tp.T_K,component,lignin_mode))
        else:
            raise AdapterDomainError("SFOR_RWTH public SFOR adapter supports linear_ramp/isothermal only")

        yvol = min(max(yvol,0.0),1.0)
        remaining = 1.0-yvol
        volatile_mass = dry_feed_mass_kg*yvol
        solid_mass = dry_feed_mass_kg*remaining

        products = ProductState(
            unresolved_solid_kg=solid_mass,
            unresolved_total_kg=volatile_mass,
        )
        mass = MassLedger.from_product_state(dry_feed_mass_kg,products)

        element_in = _element_inputs(case,dry_feed_mass_kg)
        # No phase-resolved chemistry in SFOR: elements stay accounted but unresolved.
        elements = ElementLedger.from_totals(element_in,dict(element_in))

        warnings = (
            "SFOR volatile yield is unresolved across gas/condensable product phases.",
            "Use only within the declared component/regime/evidence domain.",
        )

        return AdapterResult(
            case_id=case.case_id,
            model_manifest=self.manifest,
            outputs={
                "total_volatile_yield_fraction":yvol,
                "remaining_solid_fraction":remaining,
                "source_final_volatile_yield_limit_fraction":yinf,
            },
            product_state=products,
            mass_ledger=mass,
            element_ledger=elements,
            energy_ledger={"status":"not_available"},
            warnings=warnings,
        )

def adapter_for(model_id: str):
    if model_id == "SFOR_RWTH":
        return RWTHSFORAdapter()
    raise AdapterNotImplementedError(
        f"public SFOR adapter not yet integrated for selected model {model_id}. "
        "This is an explicit usability HOLD, not a fallback to another model."
    )
