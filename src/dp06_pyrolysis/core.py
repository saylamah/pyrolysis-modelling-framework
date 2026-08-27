from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from .types import (
    Basis, QualityStatus, FeedstockFamily, AtmosphereClass,
    EvidenceIntent, EvidenceStatus
)

@dataclass(frozen=True)
class CompositionBlock:
    basis: Basis
    quality_status: QualityStatus
    values: Dict[str, float]
    complete_balance: bool
    source_ref: Optional[str] = None
    method: Optional[str] = None
    oxygen_method: Optional[str] = None

@dataclass(frozen=True)
class FeedstockPassport:
    feedstock_id: str
    family: FeedstockFamily
    name: str
    source_type: str
    provenance_id: str
    proximate_analysis: CompositionBlock
    ultimate_analysis: Optional[CompositionBlock] = None
    biochemical_composition: Optional[CompositionBlock] = None
    polymer_composition: Optional[CompositionBlock] = None
    mineral_composition: Optional[CompositionBlock] = None
    physical_properties: Dict[str, float] = field(default_factory=dict)

@dataclass(frozen=True)
class ThermalProgram:
    type: str
    T_initial_K: Optional[float] = None
    T_final_K: Optional[float] = None
    heating_rate_K_per_s: Optional[float] = None
    T_K: Optional[float] = None
    hold_time_s: Optional[float] = None
    profile: Optional[List[List[float]]] = None

@dataclass(frozen=True)
class RegimePassport:
    thermal_program: ThermalProgram
    pressure_Pa: float
    atmosphere_class: AtmosphereClass
    atmosphere_mole_fractions: Dict[str, float]
    vapor_residence_time_s: Optional[float] = None
    solid_residence_time_s: Optional[float] = None
    equivalence_ratio: Optional[float] = None

@dataclass(frozen=True)
class ModelRequest:
    requested_fidelity: str
    selection_mode: str
    requested_model_id: Optional[str] = None

@dataclass(frozen=True)
class StudyCase:
    case_id: str
    purpose: str
    evidence_intent: EvidenceIntent
    feedstock: FeedstockPassport
    regime: RegimePassport
    model_request: ModelRequest
    outputs_requested: List[str]
    validation_context: Dict[str, Any] = field(default_factory=dict)
    optimization_request: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class ModelManifest:
    model_id: str
    model_name: str
    version: str
    fidelity_level: str
    feedstock_families: List[str]
    supported_atmospheres: List[str]
    required_input_blocks: List[str]
    supported_outputs: List[str]
    licence_class: str
    redistribution_allowed: Optional[bool]
    known_limitations: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class EvidencePassport:
    evidence_status: EvidenceStatus
    case_domain_status: str
    claim_boundary: str
    rights_status: str
    calibration_sources: List[str] = field(default_factory=list)
    independent_validation_sources: List[str] = field(default_factory=list)
    benchmark_ids: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

def to_dict(obj):
    return asdict(obj)
