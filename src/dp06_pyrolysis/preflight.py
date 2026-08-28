from __future__ import annotations
from dataclasses import dataclass, asdict
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib, json

from jsonschema import Draft202012Validator

from .io import load_case_json
from .integrity import IntegrityError
from .evidence_passport_v2 import ResultRequest, build_evidence_passport
from .adapters import adapter_for, AdapterNotImplementedError
from .profiles import load_model_profiles

PHASE_ORDER = {
    "config_schema":1,
    "file_resolution":2,
    "case_schema":3,
    "case_semantics":4,
    "selector":5,
    "model_contract":6,
    "adapter_contract":7,
}

@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    phase: str
    code: str
    path: str
    message: str

@dataclass(frozen=True)
class PreflightReport:
    status: str
    config_path: str
    selected_model: Optional[str]
    issue_count: int
    issues: List[Dict[str,Any]]
    report_sha256: str

class PreflightValidationError(ValueError):
    def __init__(self, report: PreflightReport):
        self.report=report
        super().__init__(render_preflight_text(report))

def _schema(name: str) -> Dict[str,Any]:
    p=files("dp06_pyrolysis.schemas").joinpath(name)
    return json.loads(p.read_text(encoding="utf-8"))

def _json_path(parts) -> str:
    if not parts:
        return "$"
    s="$"
    for x in parts:
        if isinstance(x,int):
            s += f"[{x}]"
        else:
            s += f".{x}"
    return s

def _add_schema_issues(issues, validator, raw, phase, code):
    errs=sorted(validator.iter_errors(raw),key=lambda e:(list(e.absolute_path),e.message))
    for e in errs:
        issues.append(ValidationIssue(
            "error",phase,code,_json_path(e.absolute_path),e.message
        ))

def _resolve(base: Path, value: str) -> Path:
    p=Path(value)
    return p if p.is_absolute() else (base/p).resolve()

def _atmosphere_label(case) -> str:
    cls=case.regime.atmosphere_class.value
    if cls=="inert": return "inert"
    if cls=="co2_containing": return "co2"
    if cls in {"oxidative","autothermal_candidate"}: return "oxidative"
    return cls

def _adapter_contract_issues(selected: str, cfg: Dict[str,Any], case) -> List[ValidationIssue]:
    out=[]
    ai=cfg.get("adapter_inputs",{})
    if selected=="SFOR_RWTH":
        component=ai.get("component")
        if component is None:
            out.append(ValidationIssue(
                "error","adapter_contract","ADAPTER_INPUT_MISSING",
                "$.adapter_inputs.component",
                "SFOR_RWTH requires adapter_inputs.component."
            ))
        elif str(component).lower() not in {"cellulose","hemicellulose","lignin"}:
            out.append(ValidationIssue(
                "error","adapter_contract","ADAPTER_INPUT_INVALID",
                "$.adapter_inputs.component",
                "SFOR_RWTH component must be cellulose, hemicellulose, or lignin."
            ))

        regime=str(ai.get("regime","tga"))
        if regime not in {"tga","fbr_low","fbr_high","fbr_full","fbr_peak"}:
            out.append(ValidationIssue(
                "error","adapter_contract","ADAPTER_INPUT_INVALID",
                "$.adapter_inputs.regime",
                f"Unsupported SFOR_RWTH regime '{regime}'."
            ))

        if case.feedstock.family.value!="lignocellulosic_biomass":
            out.append(ValidationIssue(
                "error","adapter_contract","ADAPTER_DOMAIN_ERROR",
                "$.case.feedstock.family",
                "SFOR_RWTH executable adapter requires lignocellulosic_biomass."
            ))
        if case.regime.atmosphere_class.value!="inert":
            out.append(ValidationIssue(
                "error","adapter_contract","ADAPTER_DOMAIN_ERROR",
                "$.case.regime.atmosphere.class",
                "SFOR_RWTH executable adapter requires inert atmosphere."
            ))
        if case.regime.thermal_program.type not in {"linear_ramp","isothermal"}:
            out.append(ValidationIssue(
                "error","adapter_contract","ADAPTER_DOMAIN_ERROR",
                "$.case.regime.thermal_program.type",
                "SFOR_RWTH executable adapter supports linear_ramp or isothermal only."
            ))

        dT=ai.get("dT_K",0.05)
        if not isinstance(dT,(int,float)) or dT<=0:
            out.append(ValidationIssue(
                "error","adapter_contract","ADAPTER_INPUT_INVALID",
                "$.adapter_inputs.dT_K",
                "dT_K must be a positive number."
            ))
    return out

def _canonical_report(status, config_path, selected_model, issues):
    ordered=sorted(
        issues,
        key=lambda x:(PHASE_ORDER.get(x.phase,99),x.path,x.code,x.message)
    )
    hash_payload={
        "status":status,
        "selected_model":selected_model,
        "issue_count":len(ordered),
        "issues":[asdict(x) for x in ordered],
    }
    raw=json.dumps(hash_payload,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return PreflightReport(
        status=status,
        config_path=str(config_path),
        selected_model=selected_model,
        issue_count=len(ordered),
        issues=hash_payload["issues"],
        report_sha256=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    )

def preflight_config(config_path: str | Path) -> PreflightReport:
    config_path=Path(config_path).resolve()
    issues=[]
    selected=None

    try:
        cfg=json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        issues.append(ValidationIssue(
            "error","config_schema","CONFIG_JSON_ERROR","$",
            f"Cannot parse configuration JSON: {type(e).__name__}: {e}"
        ))
        return _canonical_report("FAIL",config_path,selected,issues)

    _add_schema_issues(
        issues,Draft202012Validator(_schema("run_config.schema.json")),
        cfg,"config_schema","CONFIG_SCHEMA_ERROR"
    )
    if issues:
        return _canonical_report("FAIL",config_path,selected,issues)

    base=config_path.parent
    case_path=_resolve(base,cfg["case_file"])
    profiles_path=_resolve(base,cfg["profiles_file"])

    for label,p,pathstr in [
        ("case_file",case_path,"$.case_file"),
        ("profiles_file",profiles_path,"$.profiles_file")
    ]:
        if not p.is_file():
            issues.append(ValidationIssue(
                "error","file_resolution","FILE_NOT_FOUND",pathstr,
                f"{label} does not resolve to an existing file: {p}"
            ))
    if issues:
        return _canonical_report("FAIL",config_path,selected,issues)

    try:
        case_raw=json.loads(case_path.read_text(encoding="utf-8"))
    except Exception as e:
        issues.append(ValidationIssue(
            "error","case_schema","CASE_JSON_ERROR","$.case_file",
            f"Cannot parse StudyCase JSON: {type(e).__name__}: {e}"
        ))
        return _canonical_report("FAIL",config_path,selected,issues)

    _add_schema_issues(
        issues,Draft202012Validator(_schema("study_case.schema.json")),
        case_raw,"case_schema","CASE_SCHEMA_ERROR"
    )
    if issues:
        return _canonical_report("FAIL",config_path,selected,issues)

    try:
        case=load_case_json(case_path)
    except (IntegrityError,ValueError,KeyError,TypeError) as e:
        issues.append(ValidationIssue(
            "error","case_semantics","CASE_SEMANTIC_ERROR","$.case_file",str(e)
        ))
        return _canonical_report("FAIL",config_path,selected,issues)

    try:
        profiles=load_model_profiles(profiles_path)
    except Exception as e:
        issues.append(ValidationIssue(
            "error","file_resolution","PROFILES_JSON_ERROR","$.profiles_file",
            f"Cannot parse profiles JSON: {type(e).__name__}: {e}"
        ))
        return _canonical_report("FAIL",config_path,selected,issues)

    rq=cfg["request"]
    req=ResultRequest(
        case_id=case.case_id,
        feedstock_family=case.feedstock.family.value,
        output=str(rq["output"]),
        atmosphere=_atmosphere_label(case),
        heating_rate_class=str(rq.get("heating_rate_class","unspecified")),
        moisture_nonzero=bool(rq.get("moisture_nonzero",False)),
        polymer_type=rq.get("polymer_type"),
        evidence_requirement=str(rq["evidence_requirement"]),
        particle_scale_required=bool(rq.get("particle_scale_required",False)),
        hdpe_ldpe_differentiation_required=bool(rq.get("hdpe_ldpe_differentiation_required",False)),
        energy_claim=bool(rq.get("energy_claim",False)),
        autothermal_claim=bool(rq.get("autothermal_claim",False)),
        interaction_claim=bool(rq.get("interaction_claim",False)),
    )
    passport=build_evidence_passport(
        req,profiles,
        assumptions=list(cfg.get("assumptions",[])),
        numerical_controls=list(cfg.get("numerical_controls",[])),
        source_provenance=list(cfg.get("source_provenance",[])),
    )

    selected=passport["selection"]["primary_model"]
    if not passport["applicability"]["claim_eligible"]:
        blockers=passport["applicability"]["blocked_claims"] or ["claim_not_eligible"]
        for b in blockers:
            issues.append(ValidationIssue(
                "error","selector","SELECTOR_BLOCKED","$.request",str(b)
            ))
        return _canonical_report("FAIL",config_path,selected,issues)

    if selected is None:
        issues.append(ValidationIssue(
            "error","selector","NO_PRIMARY_MODEL","$.request",
            "evidence-aware selector returned no primary model."
        ))
        return _canonical_report("FAIL",config_path,selected,issues)

    fixed=case.model_request.requested_model_id
    if fixed is not None and fixed!=selected:
        issues.append(ValidationIssue(
            "error","model_contract","MODEL_CONFLICT",
            "$.case.model_request.requested_model_id",
            f"StudyCase requested_model_id={fixed} conflicts with evidence-aware selector={selected}."
        ))

    if rq["output"] not in case.outputs_requested:
        issues.append(ValidationIssue(
            "error","model_contract","OUTPUT_NOT_DECLARED_IN_CASE",
            "$.request.output",
            f"Requested output '{rq['output']}' is not listed in StudyCase.outputs_requested."
        ))

    try:
        adapter_for(selected)
    except AdapterNotImplementedError as e:
        issues.append(ValidationIssue(
            "error","adapter_contract","ADAPTER_NOT_INTEGRATED","$.request",str(e)
        ))

    issues.extend(_adapter_contract_issues(selected,cfg,case))

    return _canonical_report("PASS" if not issues else "FAIL",config_path,selected,issues)

def render_preflight_text(report: PreflightReport) -> str:
    lines=[
        f"Pyrolysis Modelling Framework preflight: {report.status}",
        f"Config: {report.config_path}",
        f"Selected model: {report.selected_model or '-'}",
        f"Issues: {report.issue_count}",
        f"Report SHA256: {report.report_sha256}",
    ]
    for i,x in enumerate(report.issues,1):
        lines.append(
            f"{i:02d}. [{x['severity'].upper()}] {x['code']} "
            f"({x['phase']}, {x['path']}): {x['message']}"
        )
    return "\n".join(lines)

def write_preflight_report(report: PreflightReport, path: str | Path):
    Path(path).write_text(
        json.dumps(asdict(report),indent=2,sort_keys=True),
        encoding="utf-8"
    )
