from __future__ import annotations
from typing import List
from .core import CompositionBlock, FeedstockPassport, RegimePassport, StudyCase
from .types import Basis

DEFAULT_TOL = 1e-8

class IntegrityError(ValueError):
    pass

def _check_fraction_dict(values, label: str):
    if not values:
        raise IntegrityError(f"{label}: values cannot be empty")
    for k, v in values.items():
        if not isinstance(v, (int, float)):
            raise IntegrityError(f"{label}: {k} is not numeric")
        if v < 0 or v > 1:
            raise IntegrityError(f"{label}: {k}={v} outside [0,1]")

def validate_composition_block(block: CompositionBlock, label: str, tol: float = DEFAULT_TOL):
    _check_fraction_dict(block.values, label)
    s = sum(block.values.values())
    if block.complete_balance and abs(s - 1.0) > tol:
        raise IntegrityError(f"{label}: complete balance sums to {s:.12g}, not 1")
    if block.basis == Basis.DRY and "moisture" in block.values and abs(block.values["moisture"]) > tol:
        raise IntegrityError(f"{label}: dry-basis block cannot contain nonzero moisture")
    if label == "proximate_analysis":
        required_any = {"volatile_matter", "fixed_carbon", "ash"}
        if block.complete_balance and not required_any.issubset(block.values):
            raise IntegrityError("proximate_analysis: complete balance requires volatile_matter, fixed_carbon, ash")
        if block.basis == Basis.AS_RECEIVED and block.complete_balance and "moisture" not in block.values:
            raise IntegrityError("proximate_analysis: complete as-received balance requires moisture")
    return True

def validate_feedstock_passport(feedstock: FeedstockPassport):
    if not feedstock.feedstock_id:
        raise IntegrityError("feedstock_id is required")
    if not feedstock.provenance_id:
        raise IntegrityError("provenance_id is required")
    validate_composition_block(feedstock.proximate_analysis, "proximate_analysis")
    if feedstock.ultimate_analysis:
        validate_composition_block(feedstock.ultimate_analysis, "ultimate_analysis")
    if feedstock.biochemical_composition:
        validate_composition_block(feedstock.biochemical_composition, "biochemical_composition")
    if feedstock.polymer_composition:
        validate_composition_block(feedstock.polymer_composition, "polymer_composition")
    if feedstock.mineral_composition:
        validate_composition_block(feedstock.mineral_composition, "mineral_composition")
    return True

def validate_regime_passport(regime: RegimePassport, tol: float = DEFAULT_TOL):
    if regime.pressure_Pa <= 0:
        raise IntegrityError("pressure_Pa must be > 0")
    _check_fraction_dict(regime.atmosphere_mole_fractions, "atmosphere")
    s = sum(regime.atmosphere_mole_fractions.values())
    if abs(s - 1.0) > tol:
        raise IntegrityError(f"atmosphere mole fractions sum to {s:.12g}, not 1")
    tp = regime.thermal_program
    if tp.type == "linear_ramp":
        if tp.T_initial_K is None or tp.T_final_K is None or tp.heating_rate_K_per_s is None:
            raise IntegrityError("linear_ramp requires T_initial_K, T_final_K, heating_rate_K_per_s")
        if tp.heating_rate_K_per_s <= 0:
            raise IntegrityError("heating_rate_K_per_s must be > 0")
        if tp.T_final_K <= tp.T_initial_K:
            raise IntegrityError("T_final_K must exceed T_initial_K for linear_ramp")
    elif tp.type == "isothermal":
        if tp.T_K is None:
            raise IntegrityError("isothermal requires T_K")
        if tp.T_K <= 0:
            raise IntegrityError("T_K must be > 0")
    elif tp.type == "time_temperature_profile":
        if not tp.profile or len(tp.profile) < 2:
            raise IntegrityError("time_temperature_profile requires at least two [time_s, T_K] points")
    else:
        raise IntegrityError(f"unsupported thermal program type: {tp.type}")
    return True

def validate_study_case(case: StudyCase):
    if not case.case_id:
        raise IntegrityError("case_id is required")
    if not case.outputs_requested:
        raise IntegrityError("at least one requested output is required")
    validate_feedstock_passport(case.feedstock)
    validate_regime_passport(case.regime)
    return True
