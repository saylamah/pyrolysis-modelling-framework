from __future__ import annotations
from dataclasses import dataclass
from typing import List
from .core import StudyCase, ModelManifest
from .types import EligibilityStatus

@dataclass(frozen=True)
class EligibilityDecision:
    status: EligibilityStatus
    reasons: List[str]

def check_eligibility(case: StudyCase, manifest: ModelManifest) -> EligibilityDecision:
    reasons = []
    if case.feedstock.family.value not in manifest.feedstock_families:
        return EligibilityDecision(EligibilityStatus.INELIGIBLE_DOMAIN, ["feedstock family unsupported"])

    if case.regime.atmosphere_class.value not in manifest.supported_atmospheres:
        return EligibilityDecision(EligibilityStatus.INELIGIBLE_DOMAIN, ["atmosphere unsupported"])

    for block in manifest.required_input_blocks:
        if getattr(case.feedstock, block, None) is None:
            reasons.append(f"missing required input block: {block}")
    if reasons:
        return EligibilityDecision(EligibilityStatus.INELIGIBLE_MISSING_INPUTS, reasons)

    unsupported = [o for o in case.outputs_requested if o not in manifest.supported_outputs]
    if unsupported:
        return EligibilityDecision(
            EligibilityStatus.INELIGIBLE_OUTPUT,
            [f"unsupported requested output(s): {', '.join(unsupported)}"]
        )

    if manifest.redistribution_allowed is None and "external" in manifest.licence_class:
        return EligibilityDecision(
            EligibilityStatus.ELIGIBLE_WITH_WARNING,
            ["external asset reuse/redistribution terms are not fully resolved"]
        )

    return EligibilityDecision(EligibilityStatus.ELIGIBLE, [])
