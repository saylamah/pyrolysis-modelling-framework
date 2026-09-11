"""
Pyrolysis Modelling Framework extension — S4 — Parent model-selection and applicability router v1.0

The router selects:
1) the minimum sufficient CORE chemistry/yield fidelity (L1-L7), and
2) optional particle (L8) and reactor/process (L9) overlays.

It never treats L8/L9 as replacements for chemistry.
It never returns a universal "best model".
"""

from dataclasses import dataclass, asdict
from typing import FrozenSet, Iterable, Tuple, Dict, Any

CORE_TARGET_LEVEL = {
    "source_bounded_yield": 1,
    "bulk_TG_DTG": 2,
    "E_alpha": 3,
    "lumped_stages_products": 4,
    "structure_mineral_char": 5,
    "selected_molecular_species": 6,
    "detailed_reaction_network": 7,
}

@dataclass(frozen=True)
class StudyRequest:
    targets: FrozenSet[str]
    heating_rates_available: int = 0
    source_domain_match: bool = True
    mixed_feed: bool = False
    interaction_attribution: bool = False
    particle_internal_gradients: bool = False
    reactor_process_outputs: bool = False
    finite_particle_in_reactor: bool = False
    detailed_mechanism_available: bool = False
    structural_feedstock_data_available: bool = False
    validation_data_available: bool = True
    pressure_dependent_question: bool = False

def select_framework(req: StudyRequest) -> Dict[str, Any]:
    unknown = set(req.targets) - set(CORE_TARGET_LEVEL)
    if unknown:
        raise ValueError(f"Unknown target(s): {sorted(unknown)}")
    if not req.targets:
        raise ValueError("At least one scientific/engineering target is required.")

    base = max(CORE_TARGET_LEVEL[t] for t in req.targets)
    reasons = [f"Core L{base} is the minimum level resolving target set {sorted(req.targets)}."]
    holds = []
    blocks = []
    prerequisites = []

    if base >= 3 and "E_alpha" in req.targets and req.heating_rates_available < 3:
        holds.append("E_alpha target requires at least three compatible heating rates.")
    if base >= 5 and not req.structural_feedstock_data_available:
        holds.append("L5 structural/mineral/char model requires source-consistent structural/composition data.")
    if base >= 7 and not req.detailed_mechanism_available:
        holds.append("L7 detailed chemistry requires a rights-cleared, source-defined detailed mechanism.")
    if not req.validation_data_available:
        blocks.append("Predictive validation claims are blocked; execution may be exploratory/diagnostic only.")
    if not req.source_domain_match:
        blocks.append("Source-domain mismatch: transfer/extrapolation status must be explicit.")

    if req.mixed_feed and req.interaction_attribution:
        prerequisites.append("Measured same-protocol component baselines plus explicit contact-topology/regime passport.")
        blocks.append("Causal synergy/mechanism attribution is blocked until null-model and topology requirements are satisfied.")

    if req.pressure_dependent_question:
        holds.append("Pressure-dependent modelling is not currently qualified; dedicated evidence is required before use.")

    particle = bool(req.particle_internal_gradients or req.finite_particle_in_reactor)
    reactor = bool(req.reactor_process_outputs)

    if particle:
        reasons.append("Add L8 particle overlay because internal gradients/finite-particle transport are decision variables.")
        prerequisites.append("Particle geometry + thermal/transport properties + boundary-condition identity.")
    if reactor:
        reasons.append("Add L9 reactor/process overlay because hydrodynamics/residence/energy/process outputs are decision variables.")
        prerequisites.append("Reactor geometry/model + flow/residence/mixing + process boundary.")
    if req.finite_particle_in_reactor and not reactor:
        blocks.append("finite_particle_in_reactor=True without reactor_process_outputs; L8 can be studied, but L9 is not automatically selected.")

    return {
        "core_level": base,
        "particle_overlay_L8": particle,
        "reactor_overlay_L9": reactor,
        "selection_reasons": tuple(reasons),
        "prerequisites": tuple(dict.fromkeys(prerequisites)),
        "holds": tuple(dict.fromkeys(holds)),
        "blocked_claims": tuple(dict.fromkeys(blocks)),
        "status": "HOLD" if holds else ("BOUNDED" if blocks else "ELIGIBLE"),
    }

def escalate(current_core_level: int, missing_information: str) -> int:
    mapping = {
        "conversion_heating_rate_dependence": 3,
        "distinct_stages_or_lumped_products": 4,
        "structure_mineral_char_effects": 5,
        "selected_molecular_species": 6,
        "detailed_reaction_network": 7,
    }
    if current_core_level not in range(1,8):
        raise ValueError("current_core_level must be 1..7")
    if missing_information not in mapping:
        raise ValueError("unknown escalation reason")
    target = mapping[missing_information]
    return max(current_core_level, target)

def should_stop_escalation(current_core_level: int,
                           requested_information_resolved: bool,
                           validation_sufficient_for_decision: bool,
                           higher_fidelity_has_unique_information_gain: bool) -> bool:
    if current_core_level not in range(1,8):
        raise ValueError("current_core_level must be 1..7")
    return (requested_information_resolved
            and validation_sufficient_for_decision
            and not higher_fidelity_has_unique_information_gain)

def universal_best_model(*args, **kwargs):
    raise RuntimeError("PROHIBITED: Pyrolysis Modelling Framework extension — selects the minimum sufficient model for a defined question; no universal best model exists.")
