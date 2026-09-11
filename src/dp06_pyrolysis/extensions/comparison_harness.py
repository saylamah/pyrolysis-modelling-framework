"""
Pyrolysis Modelling Framework extension — — Unified frozen-adapter comparison harness v1.0

Only metrics with identical declared observable, unit, basis and comparison context are numerically grouped. Missing or incommensurate outputs remain explicitly unavailable. No universal scalar model score is generated.
"""

from dataclasses import dataclass, asdict
from typing import Iterable, Mapping, Optional
import math, json
from collections import defaultdict

@dataclass(frozen=True)
class MetricRecord:
    branch_id: str
    feedstock_family: str
    model_family: str
    fidelity: str
    evidence_status: str
    record_role: str
    metric_id: str
    value: float
    unit: str
    basis: str
    observable: str
    comparison_context: str
    source_id: str
    model_id: str = ""
    reference_value: Optional[float] = None
    blocked_outputs: str = ""
    notes: str = ""

    def comparison_key(self):
        return (self.metric_id, self.unit, self.basis, self.observable, self.comparison_context)

def validate_record(r: MetricRecord) -> None:
    required = {"branch_id":r.branch_id,"feedstock_family":r.feedstock_family,"model_family":r.model_family,"fidelity":r.fidelity,
                "evidence_status":r.evidence_status,"record_role":r.record_role,"metric_id":r.metric_id,"unit":r.unit,"basis":r.basis,
                "observable":r.observable,"comparison_context":r.comparison_context,"source_id":r.source_id}
    missing=[k for k,v in required.items() if not str(v).strip()]
    if missing: raise ValueError(f"Missing required fields: {missing}")
    if not math.isfinite(float(r.value)): raise ValueError("metric value must be finite")
    if r.reference_value is not None and not math.isfinite(float(r.reference_value)):
        raise ValueError("reference value must be finite when supplied")

def validate_registry(records: Iterable[MetricRecord]) -> list[MetricRecord]:
    recs=list(records)
    if not recs: raise ValueError("registry must not be empty")
    seen=set()
    for r in recs:
        validate_record(r)
        identity=(r.branch_id,r.model_id,r.metric_id,r.comparison_context,r.source_id,r.value,r.reference_value)
        if identity in seen: raise ValueError(f"exact duplicate metric record: {identity}")
        seen.add(identity)
    return recs

def comparable_groups(records: Iterable[MetricRecord], min_size: int = 2):
    groups=defaultdict(list)
    for r in validate_registry(records): groups[r.comparison_key()].append(r)
    return {k:v for k,v in groups.items() if len(v)>=min_size}

def paired_reference_errors(records: Iterable[MetricRecord]):
    out=[]
    for r in validate_registry(records):
        if r.reference_value is None: continue
        err=float(r.value)-float(r.reference_value)
        out.append({"branch_id":r.branch_id,"model_id":r.model_id,"metric_id":r.metric_id,"comparison_context":r.comparison_context,
                    "prediction":float(r.value),"reference":float(r.reference_value),"error":err,"abs_error":abs(err),"unit":r.unit,
                    "evidence_status":r.evidence_status,"source_id":r.source_id})
    return out

def coverage_matrix(records: Iterable[MetricRecord]):
    recs=validate_registry(records); feedstocks=sorted({r.feedstock_family for r in recs}); families=sorted({r.model_family for r in recs})
    matrix={f:{m:0 for m in families} for f in feedstocks}
    for r in recs: matrix[r.feedstock_family][r.model_family]+=1
    return feedstocks,families,matrix

def evidence_output_map(records: Iterable[MetricRecord]):
    out=defaultdict(set)
    for r in validate_registry(records): out[(r.branch_id,r.evidence_status)].add(r.observable)
    return {k:tuple(sorted(v)) for k,v in out.items()}

def ingest_public_sfor_result(result: Mapping, *, branch_id: str, feedstock_family: str, evidence_status: str, source_id: str, comparison_context: str):
    outputs=result.get("outputs",result)
    mapping={"total_volatile_yield_fraction":("fraction_dry_feed","dry_feed","total_volatile_yield"),
             "remaining_solid_fraction":("fraction_dry_feed","dry_feed","remaining_solid")}
    recs=[]
    for key,(unit,basis,observable) in mapping.items():
        if key in outputs:
            recs.append(MetricRecord(branch_id=branch_id,feedstock_family=feedstock_family,model_family="global_kinetics",fidelity="L1",
                evidence_status=evidence_status,record_role="frozen_model_result",metric_id=key,value=float(outputs[key]),unit=unit,basis=basis,
                observable=observable,comparison_context=comparison_context,source_id=source_id,model_id="SFOR_RWTH",
                blocked_outputs="phase-resolved gas/condensable split; detailed products",
                notes="Imported without changing the frozen SFOR equations or parameters."))
    return recs

def export_jsonl(records: Iterable[MetricRecord], path: str):
    with open(path,"w",encoding="utf-8") as f:
        for r in validate_registry(records): f.write(json.dumps(asdict(r),sort_keys=True)+"\n")
