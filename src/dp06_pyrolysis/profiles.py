from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json


def load_model_profiles(path: str | Path) -> Dict[str, Any]:
    """Load detailed model profiles and apply the bundled public claim registry.

    The detailed profile file preserves domain, uncertainty and rights metadata.
    The public evidence registry separately controls outward claim status and
    executable-release status. This prevents historical/source-comparison
    metadata from silently becoming a stronger public claim.
    """
    p = Path(path)
    profiles = json.loads(p.read_text(encoding="utf-8"))
    registry_path = p.parent / "public_evidence_registry.json"
    if not registry_path.is_file():
        return profiles

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    models = registry.get("models", {})
    for model_id, control in models.items():
        profile = profiles.get(model_id)
        if profile is None:
            continue
        profile["canonical_evidence_status"] = control["claim_status"]
        profile["public_executable"] = bool(control["public_executable"])
        profile["public_evidence_basis"] = control["basis"]
    return profiles
