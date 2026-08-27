from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import hashlib, json

EVIDENCE_ORDER = {
    "exploratory":1,
    "extrapolative":2,
    "diagnostic":3,
    "screening":4,
    "calibrated":5,
    "independently_reproduced":6,
    "validated":7,
}

MODEL_PROFILES: Dict[str, Dict[str, Any]] = {}

@dataclass(frozen=True)
class ResultRequest:
    case_id: str
    feedstock_family: str
    output: str
    atmosphere: str = "inert"
    heating_rate_class: str = "unspecified"
    moisture_nonzero: bool = False
    polymer_type: Optional[str] = None
    evidence_requirement: str = "screening"
    particle_scale_required: bool = False
    hdpe_ldpe_differentiation_required: bool = False
    energy_claim: bool = False
    autothermal_claim: bool = False
    interaction_claim: bool = False

@dataclass(frozen=True)
class Selection:
    status: str
    primary_model: Optional[str]
    supporting_models: List[str]
    warnings: List[str]
    blockers: List[str]
    rationale: List[str]

def register_profiles(profiles: Dict[str, Dict[str, Any]]):
    global MODEL_PROFILES
    MODEL_PROFILES = profiles

def _sel(status, primary, support=None, warnings=None, blockers=None, rationale=None):
    return Selection(
        status=status,
        primary_model=primary,
        supporting_models=support or [],
        warnings=warnings or [],
        blockers=blockers or [],
        rationale=rationale or [],
    )

def select(req: ResultRequest) -> Selection:
    # Mixtures first.
    if req.feedstock_family in {"biomass_plastic_mixture","plastic_mixture"}:
        blockers=[]
        if req.interaction_claim:
            blockers.append("synergy_claim_requires_reproducible_residual_uncertainty_and_mechanism")
        return _sel(
            "ineligible" if blockers else "eligible_with_warning",
            "COPYROLYSIS_LINEAR_NULL",
            warnings=["linear_null_required_before_interaction_model"],
            blockers=blockers,
            rationale=["same_protocol_linear_component_baseline_first"]
        )

    if req.particle_scale_required:
        return _sel(
            "hold","CPDSPATIAL",
            warnings=["direct_CPDSpatial_reproduction_B3_pending"],
            blockers=["validated_particle_scale_claim_blocked"],
            rationale=["finite_particle_claim_requires_spatial_model_and_B3"]
        )

    if req.autothermal_claim or req.output in {"autothermal_feasibility","energy_closure"}:
        support=[]
        if req.feedstock_family in {"lignocellulosic_biomass","agricultural_residue"}:
            support=["CRECK_BIOMASS"] if req.output=="energy_closure" else ["SFOR_RWTH"]
        return _sel(
            "eligible_with_warning","AUTOTHERMAL_LEDGER",support=support,
            warnings=[
                "ER_or_O2_balance_required",
                "parasitic_heat_loss_required",
                "oxidation_source_partition_required",
                "product_selective_oxidation_must_be_resolved_or_bounded",
                "no_universal_autothermal_ER",
            ],
            rationale=["autothermal_claim_is_system_energy_closure"]
        )

    if req.output in {"heat_demand","moisture_heat_demand"}:
        return _sel(
            "eligible","MOISTURE_EQ7",
            warnings=[] if req.moisture_nonzero else ["moisture_relation_trivial_at_zero_moisture"],
            rationale=["minimum_sufficient_energy_relation"]
        )

    if req.output=="atmosphere_effect" and req.atmosphere=="co2":
        warn=[]
        if req.feedstock_family!="cattle_manure":
            warn.append("CO2_stage_rule_transfer_is_extrapolative_outside_B7_cattle_manure")
        return _sel(
            "eligible_with_warning" if warn else "eligible",
            "CO2_STAGE_BRANCH",warnings=warn,
            rationale=["stage_dependent_CO2_logic_required"]
        )

    if req.feedstock_family in {"cattle_manure","camel_dung"}:
        if req.output in {"kinetic_characterization","activation_energy_profile","conversion_kinetics"}:
            return _sel(
                "eligible","AEP_ISOCONVERSIONAL",
                rationale=["heterogeneous_feed_requires_conversion_dependent_kinetic_characterization"]
            )
        if req.output in {"detailed_products","product_distribution"}:
            return _sel(
                "ineligible",None,
                blockers=["no_G4_qualified_detailed_product_model_for_manure_or_dung"],
                rationale=["baseline_evidence_is_kinetic_characterization_only"]
            )

    if req.feedstock_family=="plastic_single":
        p=(req.polymer_type or "").upper()
        if req.output in {"mass_loss","degradation_timing","conversion"}:
            if p in {"PS","POLYSTYRENE"}:
                model="PS_7_6"
            elif p in {"HDPE","LDPE","PE"}:
                model="PE_GLOBAL"
            elif p in {"PP","POLYPROPYLENE"}:
                model="PP_GLOBAL"
            elif p=="PET":
                model="PET_GLOBAL_OR_SEMIDETAILED"
            elif p=="PVC":
                model="PVC_SEMIDETAILED"
            else:
                return _sel("ineligible",None,blockers=["unsupported_polymer_type"])

            warnings=[]
            blockers=[]
            if model=="PE_GLOBAL" and req.hdpe_ldpe_differentiation_required:
                blockers.append("source_global_PE_kinetics_cannot_validate_HDPE_vs_LDPE_differentiation")
            if model=="PET_GLOBAL_OR_SEMIDETAILED":
                warnings.append("amorphous_PET_source_domain")
            if model=="PVC_SEMIDETAILED":
                warnings.append("chlorine_HCl_ledger_required")
            if req.energy_claim and model in {"PET_GLOBAL_OR_SEMIDETAILED","PVC_SEMIDETAILED"}:
                blockers.append("validated_energy_claim_blocked_by_thermochemistry_limit")
            return _sel(
                "ineligible" if blockers else ("eligible_with_warning" if warnings else "eligible"),
                model,warnings=warnings,blockers=blockers,
                rationale=["single_polymer_global_or_guarded_branch"]
            )

        if req.output in {"detailed_products","product_distribution"}:
            if p=="PET":
                return _sel("eligible_with_warning","PET_GLOBAL_OR_SEMIDETAILED",
                            warnings=["source_guarded_specialist_branch","amorphous_PET_source_domain"])
            if p=="PVC":
                return _sel("eligible_with_warning","PVC_SEMIDETAILED",
                            warnings=["source_guarded_specialist_branch","chlorine_HCl_ledger_required"])
            return _sel(
                "hold",None,
                blockers=["higher_fidelity_polymer_product_model_not_G4_qualified"],
                rationale=["do_not_escalate_without_product_validation"]
            )

    if req.feedstock_family in {"lignocellulosic_biomass","agricultural_residue"}:
        warnings=[]
        if req.moisture_nonzero and req.output in {"total_yield","product_distribution","detailed_products"}:
            warnings += [
                "vapour_residence_or_transport_proxy_required",
                "water_and_organic_condensate_must_be_separated"
            ]
        if req.output in {"volatile_release_timing","volatile_release_rate"}:
            model="CPD_FAMILY" if req.heating_rate_class=="high" else "SFOR_RWTH"
            rationale=[
                "CPD_family_for_high_heating_rate_release_dynamics"
                if model=="CPD_FAMILY" else
                "SFOR_minimum_sufficient_for_calibrated_release_rate"
            ]
        elif req.output in {"detailed_products","product_distribution","species"}:
            model="CRECK_BIOMASS"
            rationale=["detailed_product_resolution_requires_high_fidelity_chemistry"]
        elif req.output in {"total_yield","conversion"}:
            model="SFOR_RWTH"
            rationale=["SFOR_minimum_sufficient_for_total_conversion_or_yield_screening"]
        else:
            return _sel("ineligible",None,blockers=["unsupported_biomass_output"])
        return _sel("eligible_with_warning" if warnings else "eligible",
                    model,warnings=warnings,rationale=rationale)

    return _sel("ineligible",None,blockers=["no_baseline_branch_for_request"])

def _domain_status(req: ResultRequest, sel: Selection) -> str:
    if sel.status=="ineligible":
        return "blocked"
    if sel.status=="hold":
        return "hold"
    if sel.primary_model=="CO2_STAGE_BRANCH" and req.feedstock_family!="cattle_manure":
        return "extrapolative"
    if sel.primary_model=="CPDSPATIAL":
        return "hold"
    return "in_domain_with_declared_limits"

def _canonical_claim_status(sel: Selection, req: ResultRequest, profile: Optional[Dict[str,Any]]) -> str:
    if sel.status=="ineligible":
        return "blocked"
    if sel.status=="hold":
        return "exploratory"
    if _domain_status(req,sel)=="extrapolative":
        return "extrapolative"
    if profile is None:
        return "exploratory"
    return profile["canonical_evidence_status"]

def _uncertainty_summary(profile: Optional[Dict[str,Any]]) -> Dict[str,Any]:
    if profile is None:
        return {
            "overall_mode":"unavailable",
            "components":[],
            "quantitative_refs":[]
        }
    modes=[x["quantification_mode"] for x in profile["uncertainty_components"]]
    if not modes:
        overall="unavailable"
    elif any(m in {"reported_standard_uncertainty","replicate_statistics"} for m in modes):
        overall="mixed_with_probabilistic_support"
    elif any(m in {"bounded_interval","numerical_refinement_bound","model_ensemble_spread","deterministic_sensitivity"} for m in modes):
        overall="mixed_nonprobabilistic_quantitative"
    else:
        overall="categorical_or_unavailable"
    return {
        "overall_mode":overall,
        "components":profile["uncertainty_components"],
        "quantitative_refs":profile["quantitative_uncertainty_refs"]
    }

def build_evidence_passport(req: ResultRequest,
                            profiles: Dict[str,Dict[str,Any]],
                            assumptions: Optional[List[str]]=None,
                            numerical_controls: Optional[List[str]]=None,
                            source_provenance: Optional[List[str]]=None) -> Dict[str,Any]:
    register_profiles(profiles)
    sel=select(req)
    profile=profiles.get(sel.primary_model) if sel.primary_model else None

    claim_status=_canonical_claim_status(sel,req,profile)
    claim_eligible=sel.status in {"eligible","eligible_with_warning"}

    warnings=list(sel.warnings)
    blockers=list(sel.blockers)

    # Evidence-ceiling guard: no claim may exceed selected model status.
    if profile and req.evidence_requirement in EVIDENCE_ORDER:
        ceiling=profile["canonical_evidence_status"]
        if EVIDENCE_ORDER[ceiling] < EVIDENCE_ORDER[req.evidence_requirement]:
            blockers.append(
                f"requested_evidence_{req.evidence_requirement}_exceeds_model_evidence_{ceiling}"
            )
            claim_eligible=False

    # Rights/provenance must always be visible.
    rights=profile["rights_provenance"] if profile else {
        "status":"unavailable","boundary":"No primary model selected."
    }

    supporting=[]
    for mid in sel.supporting_models:
        p=profiles.get(mid)
        supporting.append({
            "model_id":mid,
            "evidence_status":p["canonical_evidence_status"] if p else "exploratory",
            "recommended_role":p["recommended_role"] if p else "unavailable",
            "rights_provenance":p["rights_provenance"] if p else {"status":"unavailable","boundary":"unavailable"}
        })

    payload={
        "schema":"PyrolysisFramework_EvidencePassport_v2",
        "case_id":req.case_id,
        "request":asdict(req),
        "selection":{
            "status":sel.status,
            "primary_model":sel.primary_model,
            "supporting_models":supporting,
            "rationale":sel.rationale,
        },
        "evidence":{
            "result_status":claim_status,
            "model_evidence_ceiling":profile["canonical_evidence_status"] if profile else None,
            "domain_status":_domain_status(req,sel),
            "validation_strength":profile["validation_strength"] if profile else None,
            "feedstock_domain":profile["feedstock_domain"] if profile else None,
            "regime_domain":profile["regime_domain"] if profile else None,
            "output_domain":profile["output_domain"] if profile else None,
        },
        "uncertainty":_uncertainty_summary(profile),
        "applicability":{
            "required_inputs":profile["required_inputs"] if profile else None,
            "warnings":warnings,
            "blocked_claims":blockers,
            "claim_eligible":claim_eligible and not blockers,
            "recommended_role":profile["recommended_role"] if profile else None,
        },
        "rights_provenance":rights,
        "assumptions":assumptions or [],
        "numerical_controls":numerical_controls or [],
        "source_provenance":source_provenance or [],
    }

    # Claim boundary: compact machine-readable stop statement.
    if payload["applicability"]["claim_eligible"]:
        payload["claim_boundary"]="eligible_only_within_declared_feedstock_regime_output_and_evidence_domain"
    else:
        payload["claim_boundary"]="claim_blocked_or_on_hold_until_listed_blockers_are_resolved"

    canonical=json.dumps(payload,sort_keys=True,separators=(",",":"))
    payload["passport_sha256"]=hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload
