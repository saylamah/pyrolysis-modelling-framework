from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any
import hashlib, json

from .io import load_case_json
from .adapters import adapter_for
from .evidence_passport_v2 import ResultRequest, build_evidence_passport
from .preflight import preflight_config, PreflightValidationError

def _load_profiles(path: str | Path) -> Dict[str,Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _atmosphere_label(case) -> str:
    cls=case.regime.atmosphere_class.value
    if cls=="inert":
        return "inert"
    if cls=="co2_containing":
        return "co2"
    if cls in {"oxidative","autothermal_candidate"}:
        return "oxidative"
    return cls

def _enum_convert(x):
    if hasattr(x,"value"):
        return x.value
    if isinstance(x,dict):
        return {k:_enum_convert(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):
        return [_enum_convert(v) for v in x]
    return x

def _canonical_hash(payload: Dict[str,Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def run_unified_config(config_path: str | Path, output_override: str | Path | None = None) -> str:
    config_path=Path(config_path)
    preflight=preflight_config(config_path)
    if preflight.status != "PASS":
        raise PreflightValidationError(preflight)
    cfg=json.loads(config_path.read_text(encoding="utf-8"))

    def resolve(p):
        q=Path(p)
        return q if q.is_absolute() else (config_path.parent/q).resolve()

    case=load_case_json(resolve(cfg["case_file"]))
    profiles=_load_profiles(resolve(cfg["profiles_file"]))

    request_cfg=cfg["request"]
    output=str(request_cfg.get("output") or case.outputs_requested[0])

    req=ResultRequest(
        case_id=case.case_id,
        feedstock_family=case.feedstock.family.value,
        output=output,
        atmosphere=_atmosphere_label(case),
        heating_rate_class=str(request_cfg.get("heating_rate_class","unspecified")),
        moisture_nonzero=bool(request_cfg.get("moisture_nonzero",False)),
        polymer_type=request_cfg.get("polymer_type"),
        evidence_requirement=str(request_cfg.get("evidence_requirement","screening")),
        particle_scale_required=bool(request_cfg.get("particle_scale_required",False)),
        hdpe_ldpe_differentiation_required=bool(request_cfg.get("hdpe_ldpe_differentiation_required",False)),
        energy_claim=bool(request_cfg.get("energy_claim",False)),
        autothermal_claim=bool(request_cfg.get("autothermal_claim",False)),
        interaction_claim=bool(request_cfg.get("interaction_claim",False)),
    )

    passport=build_evidence_passport(
        req,profiles,
        assumptions=list(cfg.get("assumptions",[])),
        numerical_controls=list(cfg.get("numerical_controls",[])),
        source_provenance=list(cfg.get("source_provenance",[])),
    )

    if not passport["applicability"]["claim_eligible"]:
        raise ValueError(
            "evidence/applicability gate blocked this run: "
            + "; ".join(passport["applicability"]["blocked_claims"])
        )

    selected=passport["selection"]["primary_model"]
    if selected is None:
        raise ValueError("selector returned no primary model")

    fixed=case.model_request.requested_model_id
    if fixed is not None and fixed != selected:
        raise ValueError(
            f"StudyCase requested_model_id={fixed} conflicts with evidence-aware selector={selected}; "
            "no silent override permitted"
        )

    adapter=adapter_for(selected)
    adapter_result=adapter.run(
        case,
        adapter_inputs=dict(cfg.get("adapter_inputs",{})),
        dry_feed_mass_kg=float(cfg.get("dry_feed_mass_kg",1.0)),
    )

    result={
        "schema":"PyrolysisFramework_RunResult_v1",
        "preflight":{
            "status":preflight.status,
            "selected_model":preflight.selected_model,
            "report_sha256":preflight.report_sha256,
        },
        "case_id":case.case_id,
        "selected_model":selected,
        "model_manifest":_enum_convert(asdict(adapter_result.model_manifest)),
        "outputs":adapter_result.outputs,
        "product_state":_enum_convert(asdict(adapter_result.product_state)),
        "mass_ledger":_enum_convert(asdict(adapter_result.mass_ledger)),
        "element_ledger":_enum_convert(asdict(adapter_result.element_ledger)),
        "energy_ledger":adapter_result.energy_ledger,
        "model_warnings":list(adapter_result.warnings),
        "evidence_passport":passport,
    }
    result["run_sha256"]=_canonical_hash(result)

    out = Path(output_override).resolve() if output_override is not None else resolve(cfg["output_file"])
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
    return str(out)
