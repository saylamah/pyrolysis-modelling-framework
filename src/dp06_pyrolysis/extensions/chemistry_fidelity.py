"""
Pyrolysis Modelling Framework extension — chemistry-fidelity eligibility helper.

It distinguishes:
- L5 structural/semi-mechanistic,
- L6 semi-detailed chemistry,
- L7 detailed chemistry.

It does not create mechanisms.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class ChemistryEvidence:
    structural_data: bool=False
    semi_detailed_mechanism: bool=False
    detailed_mechanism: bool=False
    provenance_rights_clear: bool=False
    molecular_validation_data: bool=False
    feedstock_mapping_defined: bool=False
    numerical_integrity_verified: bool=False
    no_refit_transfer_evidence: bool=False

def chemistry_level_for_question(question: str, ev: ChemistryEvidence) -> dict:
    if question=="structure_mineral_char":
        if not ev.structural_data:
            return {"level":"HOLD","reason":"L5 requires structural/mineral/feedstock data."}
        return {"level":"L5","reason":"Structural/semi-mechanistic information is sufficient."}

    if question=="selected_species_or_families":
        if not (ev.semi_detailed_mechanism and ev.provenance_rights_clear and ev.feedstock_mapping_defined):
            return {"level":"HOLD","reason":"L6 requires source-locked semi-detailed chemistry and feedstock mapping."}
        status="PREDICTIVE_BOUNDED" if ev.molecular_validation_data else "EXPLORATORY_SOURCE_BOUNDED"
        return {"level":"L6","reason":status}

    if question=="detailed_reaction_network":
        req=(ev.detailed_mechanism and ev.provenance_rights_clear and ev.feedstock_mapping_defined
             and ev.numerical_integrity_verified)
        if not req:
            return {"level":"HOLD","reason":"L7 prerequisites are incomplete."}
        if not ev.molecular_validation_data:
            return {"level":"L7","reason":"IMPLEMENTATION/MECHANISTIC EXPLORATION ONLY; predictive molecular validation absent."}
        transfer="WITH_TRANSFER_EVIDENCE" if ev.no_refit_transfer_evidence else "SOURCE_DOMAIN_ONLY"
        return {"level":"L7","reason":f"PREDICTIVE_BOUNDED_{transfer}"}

    raise ValueError("unknown chemistry question")

def detailed_chemistry_stop(lower_level_resolves_question: bool,
                            detailed_outputs_validated: bool,
                            unique_information_gain: bool) -> bool:
    return bool(lower_level_resolves_question and
                (not unique_information_gain or not detailed_outputs_validated))

def universal_detailed_mechanism(*args,**kwargs):
    raise RuntimeError("PROHIBITED: no universal detailed pyrolysis mechanism is defined across Pyrolysis Modelling Framework extension feedstocks.")
