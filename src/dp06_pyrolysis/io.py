from __future__ import annotations
import json
from pathlib import Path
from .core import (
    CompositionBlock, FeedstockPassport, ThermalProgram, RegimePassport,
    ModelRequest, StudyCase
)
from .types import Basis, QualityStatus, FeedstockFamily, AtmosphereClass, EvidenceIntent
from .integrity import validate_study_case

def _comp(data):
    if data is None:
        return None
    return CompositionBlock(
        basis=Basis(data["basis"]),
        quality_status=QualityStatus(data["quality_status"]),
        values=dict(data["values"]),
        complete_balance=bool(data["complete_balance"]),
        source_ref=data.get("source_ref"),
        method=data.get("method"),
        oxygen_method=data.get("oxygen_method"),
    )

def load_case_json(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    f = data["feedstock"]
    feedstock = FeedstockPassport(
        feedstock_id=f["feedstock_id"],
        family=FeedstockFamily(f["family"]),
        name=f["name"],
        source_type=f["source_type"],
        provenance_id=f["provenance_id"],
        proximate_analysis=_comp(f["proximate_analysis"]),
        ultimate_analysis=_comp(f.get("ultimate_analysis")),
        biochemical_composition=_comp(f.get("biochemical_composition")),
        polymer_composition=_comp(f.get("polymer_composition")),
        mineral_composition=_comp(f.get("mineral_composition")),
        physical_properties=dict(f.get("physical_properties", {})),
    )
    r = data["regime"]
    tp = r["thermal_program"]
    regime = RegimePassport(
        thermal_program=ThermalProgram(
            type=tp["type"],
            T_initial_K=tp.get("T_initial_K"),
            T_final_K=tp.get("T_final_K"),
            heating_rate_K_per_s=tp.get("heating_rate_K_per_s"),
            T_K=tp.get("T_K"),
            hold_time_s=tp.get("hold_time_s"),
            profile=tp.get("profile"),
        ),
        pressure_Pa=r["pressure_Pa"],
        atmosphere_class=AtmosphereClass(r["atmosphere"]["class"]),
        atmosphere_mole_fractions=dict(r["atmosphere"]["mole_fractions"]),
        vapor_residence_time_s=r.get("vapor_residence_time_s"),
        solid_residence_time_s=r.get("solid_residence_time_s"),
        equivalence_ratio=r.get("equivalence_ratio"),
    )
    mr = data["model_request"]
    case = StudyCase(
        case_id=data["case_metadata"]["case_id"],
        purpose=data["case_metadata"]["purpose"],
        evidence_intent=EvidenceIntent(data["case_metadata"]["evidence_intent"]),
        feedstock=feedstock,
        regime=regime,
        model_request=ModelRequest(
            requested_fidelity=mr["requested_fidelity"],
            selection_mode=mr["selection_mode"],
            requested_model_id=mr.get("requested_model_id"),
        ),
        outputs_requested=list(data["outputs_requested"]),
        validation_context=dict(data.get("validation_context", {})),
        optimization_request=data.get("optimization_request"),
    )
    validate_study_case(case)
    return case

def dump_case_json(case: StudyCase, path):
    from dataclasses import asdict
    def convert(obj):
        if hasattr(obj, "value"):
            return obj.value
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj
    raw = convert(asdict(case))
    data = {
        "case_metadata": {
            "case_id": raw["case_id"],
            "purpose": raw["purpose"],
            "evidence_intent": raw["evidence_intent"],
        },
        "feedstock": raw["feedstock"],
        "regime": {
            "thermal_program": raw["regime"]["thermal_program"],
            "pressure_Pa": raw["regime"]["pressure_Pa"],
            "atmosphere": {
                "class": raw["regime"]["atmosphere_class"],
                "mole_fractions": raw["regime"]["atmosphere_mole_fractions"],
            },
            "vapor_residence_time_s": raw["regime"]["vapor_residence_time_s"],
            "solid_residence_time_s": raw["regime"]["solid_residence_time_s"],
            "equivalence_ratio": raw["regime"]["equivalence_ratio"],
        },
        "model_request": raw["model_request"],
        "outputs_requested": raw["outputs_requested"],
        "validation_context": raw["validation_context"],
        "optimization_request": raw["optimization_request"],
    }
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
