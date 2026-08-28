from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json


def _minimal_public_profile(model_id: str, control: Dict[str, Any]) -> Dict[str, Any]:
    basis = control["basis"]
    return {
        "model_id": model_id,
        "canonical_evidence_status": control["claim_status"],
        "validation_strength": basis,
        "feedstock_domain": "see controlled DP-06 branch evidence and selector constraints",
        "regime_domain": "see controlled DP-06 branch evidence and selector constraints",
        "output_domain": "eligibility/claim-control metadata only in this public release",
        "required_inputs": "branch-specific inputs; executable integration not public in this release",
        "recommended_role": "eligibility/evidence reference only; not a public executable adapter",
        "rights_provenance": {
            "status": "metadata_only",
            "boundary": "This registry entry authorizes no model redistribution or executable claim."
        },
        "uncertainty_components": [
            {
                "uncertainty_class": "model_form",
                "quantification_mode": "categorical_only",
                "evidence_basis": basis,
                "guard": "no probabilistic or predictive uncertainty implied"
            }
        ],
        "quantitative_uncertainty_refs": [],
        "public_executable": bool(control["public_executable"]),
        "public_evidence_basis": basis,
    }


def load_model_profiles(path: str | Path) -> Dict[str, Any]:
    """Load detailed profiles and apply the bundled public claim registry.

    `model_passport_profiles.json` carries detailed metadata for model branches
    that are distributed with the package. `public_evidence_registry.json`
    separately controls outward claim status and public executable status.

    Registry-only branches are represented by conservative metadata-only
    profiles. This lets the selector explain why a branch is relevant without
    implying that its model code, source data or full validation package is
    distributed here.
    """
    p = Path(path)
    profiles = json.loads(p.read_text(encoding="utf-8"))
    registry_path = p.parent / "public_evidence_registry.json"
    if not registry_path.is_file():
        return profiles

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for model_id, control in registry.get("models", {}).items():
        profile = profiles.get(model_id)
        if profile is None:
            profiles[model_id] = _minimal_public_profile(model_id, control)
            continue
        profile["canonical_evidence_status"] = control["claim_status"]
        profile["public_executable"] = bool(control["public_executable"])
        profile["public_evidence_basis"] = control["basis"]
    return profiles
