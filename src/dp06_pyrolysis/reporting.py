from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import hashlib, json

def _humanize(value: Any) -> str:
    if value is None:
        return "not available"
    return str(value).replace("_"," ").strip()

def _upper_human(value: Any) -> str:
    return _humanize(value).upper()

def _fmt_number(x: Any) -> str:
    if x is None:
        return "not available"
    if isinstance(x,bool):
        return str(x)
    if isinstance(x,(int,float)):
        if abs(float(x)) != 0 and (abs(float(x)) < 1e-5 or abs(float(x)) >= 1e5):
            return f"{float(x):.6e}"
        return f"{float(x):.9g}"
    return str(x)

def _output_unit(name: str) -> str:
    if name.endswith("_fraction"):
        return "fraction"
    if name.endswith("_kg"):
        return "kg"
    if name.endswith("_K"):
        return "K"
    if name.endswith("_Pa"):
        return "Pa"
    if name.endswith("_s"):
        return "s"
    return ""

def _dedup(seq: List[str]) -> List[str]:
    out=[]
    seen=set()
    for x in seq:
        x=str(x).strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out

def build_user_report(result: Dict[str,Any]) -> Dict[str,Any]:
    ep=result["evidence_passport"]
    app=ep["applicability"]
    evidence=ep["evidence"]
    uncertainty=ep["uncertainty"]

    model_warnings=_dedup(list(result.get("model_warnings",[])))
    applicability_warnings=_dedup(list(app.get("warnings",[])))
    blockers=_dedup(list(app.get("blocked_claims",[])))
    limitations=_dedup(list(result.get("model_manifest",{}).get("known_limitations",[])))

    claim_eligible=bool(app.get("claim_eligible",False))
    warning_count=len(model_warnings)+len(applicability_warnings)+len(limitations)
    if not claim_eligible or blockers:
        overall="BLOCKED"
    elif warning_count:
        overall="PASS_WITH_WARNINGS"
    else:
        overall="PASS"

    outputs=[
        {"name":k,"value":v,"unit":_output_unit(k)}
        for k,v in sorted(result.get("outputs",{}).items())
    ]

    mass=result.get("mass_ledger",{})
    mass_residual=mass.get("closure_residual")
    mass_status="not_available"
    if isinstance(mass_residual,(int,float)):
        mass_status="PASS" if abs(float(mass_residual)) <= 1e-9 else "CHECK"

    report={
        "schema":"PyrolysisFramework_UserFacingReport_v1",
        "overall_status":overall,
        "case_id":result.get("case_id"),
        "selected_model":result.get("selected_model"),
        "model_name":result.get("model_manifest",{}).get("model_name"),
        "model_fidelity":result.get("model_manifest",{}).get("fidelity_level"),
        "evidence":{
            "result_status":evidence.get("result_status"),
            "model_evidence_ceiling":evidence.get("model_evidence_ceiling"),
            "domain_status":evidence.get("domain_status"),
            "validation_strength":evidence.get("validation_strength"),
            "claim_eligible":claim_eligible,
            "claim_boundary":ep.get("claim_boundary"),
        },
        "uncertainty":{
            "overall_mode":uncertainty.get("overall_mode"),
            "components":[
                {
                    "class":x.get("uncertainty_class"),
                    "mode":x.get("quantification_mode"),
                    "guard":x.get("guard"),
                }
                for x in uncertainty.get("components",[])
            ],
            "quantitative_refs":list(uncertainty.get("quantitative_refs",[])),
        },
        "outputs":outputs,
        "balances":{
            "mass":{
                "status":mass_status,
                "input_mass_kg":mass.get("input_mass_kg"),
                "output_mass_kg":mass.get("output_mass_kg"),
                "closure_residual":mass_residual,
            },
            "energy_status":result.get("energy_ledger",{}).get("status","not_available"),
        },
        "warnings":{
            "applicability":applicability_warnings,
            "model":model_warnings,
            "known_limitations":limitations,
        },
        "blocked_claims":blockers,
        "rights_provenance":ep.get("rights_provenance",{}),
        "source_provenance":list(ep.get("source_provenance",[])),
        "assumptions":list(ep.get("assumptions",[])),
        "integrity":{
            "preflight_sha256":result.get("preflight",{}).get("report_sha256"),
            "evidence_passport_sha256":ep.get("passport_sha256"),
            "run_sha256":result.get("run_sha256"),
        },
    }
    canonical=json.dumps(report,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    report["user_report_sha256"]=hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return report

def render_user_report_text(report: Dict[str,Any]) -> str:
    e=report["evidence"]
    u=report["uncertainty"]
    b=report["balances"]
    rights=report["rights_provenance"]
    lines=[
        f"PYROLYSIS MODELLING FRAMEWORK RESULT — {_upper_human(report['overall_status'])}",
        f"Case: {report['case_id']}",
        f"Model: {report['selected_model']} — {report.get('model_name') or 'name unavailable'}",
        f"Fidelity: {report.get('model_fidelity') or 'not available'}",
        "",
        "EVIDENCE & APPLICABILITY",
        f"  Evidence status: {_upper_human(e.get('result_status'))}",
        f"  Evidence ceiling: {_upper_human(e.get('model_evidence_ceiling'))}",
        f"  Domain status: {_upper_human(e.get('domain_status'))}",
        f"  Claim eligible: {'YES' if e.get('claim_eligible') else 'NO'}",
        f"  Validation strength: {e.get('validation_strength') or 'not available'}",
        f"  Claim boundary: {e.get('claim_boundary') or 'not available'}",
        "",
        "UNCERTAINTY",
        f"  Overall mode: {_upper_human(u.get('overall_mode'))}",
    ]
    for x in u["components"]:
        lines.append(
            f"  - {_humanize(x['class'])}: {_humanize(x['mode'])}"
            + (f" — {x['guard']}" if x.get("guard") else "")
        )
    if not u["components"]:
        lines.append("  - No uncertainty components recorded.")

    lines += ["", "OUTPUTS"]
    for x in report["outputs"]:
        unit=f" {x['unit']}" if x.get("unit") else ""
        lines.append(f"  - {_humanize(x['name'])}: {_fmt_number(x['value'])}{unit}")
    if not report["outputs"]:
        lines.append("  - No numerical outputs recorded.")

    lines += [
        "",
        "BALANCES",
        f"  Mass closure: {b['mass']['status']}",
        f"  Mass residual: {_fmt_number(b['mass']['closure_residual'])} kg",
        f"  Energy status: {_upper_human(b.get('energy_status'))}",
        "",
        "WARNINGS & LIMITATIONS",
    ]
    any_warn=False
    for label,key in [
        ("Applicability","applicability"),
        ("Model","model"),
        ("Known limitation","known_limitations"),
    ]:
        for x in report["warnings"][key]:
            any_warn=True
            lines.append(f"  - [{label}] {x}")
    if not any_warn:
        lines.append("  - None.")

    lines += ["", "BLOCKED CLAIMS"]
    if report["blocked_claims"]:
        lines.extend(f"  - {x}" for x in report["blocked_claims"])
    else:
        lines.append("  - None for this declared request.")

    lines += [
        "",
        "RIGHTS / PROVENANCE",
        f"  Status: {rights.get('status','not available')}",
        f"  Boundary: {rights.get('boundary','not available')}",
        "",
        "INTEGRITY",
        f"  Preflight SHA256: {report['integrity'].get('preflight_sha256') or '-'}",
        f"  Evidence Passport SHA256: {report['integrity'].get('evidence_passport_sha256') or '-'}",
        f"  Run SHA256: {report['integrity'].get('run_sha256') or '-'}",
        f"  User report SHA256: {report.get('user_report_sha256','-')}",
    ]
    return "\n".join(lines)

def render_user_report_markdown(report: Dict[str,Any]) -> str:
    e=report["evidence"]
    u=report["uncertainty"]
    b=report["balances"]
    rights=report["rights_provenance"]
    out=[
        f"# Pyrolysis Modelling Framework Result — {_upper_human(report['overall_status'])}",
        "",
        f"**Case:** `{report['case_id']}`  ",
        f"**Model:** `{report['selected_model']}` — {report.get('model_name') or 'name unavailable'}  ",
        f"**Fidelity:** `{report.get('model_fidelity') or 'not available'}`",
        "",
        "## Evidence & applicability",
        "",
        f"- **Evidence status:** `{e.get('result_status')}`",
        f"- **Evidence ceiling:** `{e.get('model_evidence_ceiling')}`",
        f"- **Domain status:** `{e.get('domain_status')}`",
        f"- **Claim eligible:** `{'yes' if e.get('claim_eligible') else 'no'}`",
        f"- **Validation strength:** {e.get('validation_strength') or 'not available'}",
        f"- **Claim boundary:** `{e.get('claim_boundary') or 'not available'}`",
        "",
        "## Uncertainty",
        "",
        f"**Overall mode:** `{u.get('overall_mode')}`",
        "",
    ]
    for x in u["components"]:
        out.append(
            f"- **{_humanize(x['class'])}:** `{x['mode']}`"
            + (f" — {x['guard']}" if x.get("guard") else "")
        )
    if not u["components"]:
        out.append("- No uncertainty components recorded.")

    out += ["", "## Outputs", "", "| Quantity | Value | Unit |", "|---|---:|---|"]
    for x in report["outputs"]:
        out.append(f"| {_humanize(x['name'])} | {_fmt_number(x['value'])} | {x.get('unit') or ''} |")
    if not report["outputs"]:
        out.append("| — | — | — |")

    out += [
        "",
        "## Balances",
        "",
        f"- **Mass closure:** `{b['mass']['status']}`",
        f"- **Mass residual:** `{_fmt_number(b['mass']['closure_residual'])} kg`",
        f"- **Energy status:** `{b.get('energy_status')}`",
        "",
        "## Warnings & limitations",
        "",
    ]
    any_warn=False
    for label,key in [
        ("Applicability","applicability"),
        ("Model","model"),
        ("Known limitation","known_limitations"),
    ]:
        for x in report["warnings"][key]:
            any_warn=True
            out.append(f"- **{label}:** {x}")
    if not any_warn:
        out.append("- None.")

    out += ["", "## Blocked claims", ""]
    if report["blocked_claims"]:
        out.extend(f"- {x}" for x in report["blocked_claims"])
    else:
        out.append("- None for this declared request.")

    out += [
        "",
        "## Rights / provenance",
        "",
        f"- **Status:** {rights.get('status','not available')}",
        f"- **Boundary:** {rights.get('boundary','not available')}",
        "",
        "## Integrity",
        "",
        f"- Preflight SHA-256: `{report['integrity'].get('preflight_sha256') or '-'}`",
        f"- Evidence Passport SHA-256: `{report['integrity'].get('evidence_passport_sha256') or '-'}`",
        f"- Run SHA-256: `{report['integrity'].get('run_sha256') or '-'}`",
        f"- User report SHA-256: `{report.get('user_report_sha256','-')}`",
        "",
        "> This report describes evidence, applicability, uncertainty, and execution integrity. "
        "It does not upgrade the underlying scientific evidence status."
    ]
    return "\n".join(out)

def build_blocked_request_report(preflight: Dict[str,Any]) -> Dict[str,Any]:
    issues=list(preflight.get("issues",[]))
    report={
        "schema":"PyrolysisFramework_BlockedRequest_v1",
        "overall_status":"BLOCKED",
        "selected_model":preflight.get("selected_model"),
        "numerical_execution_performed":False,
        "issue_count":preflight.get("issue_count",len(issues)),
        "issues":issues,
        "preflight_sha256":preflight.get("report_sha256"),
    }
    canonical=json.dumps(report,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    report["user_report_sha256"]=hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return report

def render_blocked_request_text(report: Dict[str,Any]) -> str:
    lines=[
        "PYROLYSIS MODELLING FRAMEWORK REQUEST — BLOCKED BEFORE NUMERICAL EXECUTION",
        f"Selected model: {report.get('selected_model') or '-'}",
        f"Issues: {report.get('issue_count',0)}",
        "Numerical execution performed: NO",
        "",
        "REASONS",
    ]
    for i,x in enumerate(report.get("issues",[]),1):
        lines.append(
            f"  {i:02d}. [{x.get('code','ISSUE')}] {x.get('message','')}"
            f" ({x.get('path','$')})"
        )
    if not report.get("issues"):
        lines.append("  - No detailed issue was supplied.")
    lines += [
        "",
        f"Preflight SHA256: {report.get('preflight_sha256') or '-'}",
        f"User report SHA256: {report.get('user_report_sha256') or '-'}",
    ]
    return "\n".join(lines)

def load_result(path: str | Path) -> Dict[str,Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
