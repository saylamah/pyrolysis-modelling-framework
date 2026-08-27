from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from .core import StudyCase, ModelManifest, EvidencePassport
from .types import EvidenceStatus
from .integrity import validate_study_case
from .products import ProductState
from .balances import MassLedger, ElementLedger
from .kinetics import ArrheniusReaction, first_order_isothermal_conversion, first_order_linear_ramp

@dataclass(frozen=True)
class MinimalModelResult:
    case_id: str
    model_manifest: ModelManifest
    conversion: float
    product_state: ProductState
    mass_ledger: MassLedger
    element_ledger: ElementLedger
    energy_ledger: Dict[str, Any]
    evidence_passport: EvidencePassport
    warnings: tuple

def _dry_ash_fraction(case: StudyCase) -> float:
    prox = case.feedstock.proximate_analysis
    if prox.basis.value != "dry":
        raise ValueError("minimal baseline currently requires dry-basis proximate analysis")
    return prox.values.get("ash", 0.0)

def _feed_element_inputs(case: StudyCase, dry_mass_kg: float):
    ult = case.feedstock.ultimate_analysis
    if ult is None:
        return {}
    # G2 baseline uses the declared ultimate-analysis basis without inventing cross-basis chemistry.
    if ult.basis.value == "dry_ash_free":
        organic_mass = dry_mass_kg * (1.0 - _dry_ash_fraction(case))
        return {el: frac * organic_mass for el, frac in ult.values.items()}
    if ult.basis.value == "dry":
        return {el: frac * dry_mass_kg for el, frac in ult.values.items()}
    raise ValueError("as-received ultimate analysis not supported by minimal dry-feed baseline")

class FirstOrderScreeningModel:
    def __init__(self, reaction: ArrheniusReaction):
        self.reaction = reaction
        self.manifest = ModelManifest(
            model_id="FIRST_ORDER_SCREENING_L1",
            model_name="First-order Arrhenius screening model",
            version="0.1",
            fidelity_level="L1",
            feedstock_families=[
                "lignocellulosic_biomass","agricultural_residue","cattle_manure","camel_dung"
            ],
            supported_atmospheres=["inert"],
            required_input_blocks=["proximate_analysis"],
            supported_outputs=["conversion"],
            licence_class="internal",
            redistribution_allowed=True,
            known_limitations=[
                "No product-phase prediction",
                "No mineral catalysis",
                "No secondary vapor chemistry",
                "No oxidative/steam chemistry",
                "Not a universal pyrolysis model"
            ],
        )

    def run(self, case: StudyCase, dry_feed_mass_kg: float = 1.0, dt_s: float = 0.01) -> MinimalModelResult:
        validate_study_case(case)
        if dry_feed_mass_kg <= 0:
            raise ValueError("dry_feed_mass_kg must be > 0")
        tp = case.regime.thermal_program
        if case.regime.atmosphere_class.value != "inert":
            raise ValueError("FirstOrderScreeningModel supports inert atmosphere only")

        if tp.type == "isothermal":
            if tp.T_K is None or tp.hold_time_s is None:
                raise ValueError("isothermal run requires T_K and hold_time_s")
            alpha = first_order_isothermal_conversion(self.reaction, tp.T_K, tp.hold_time_s)
        elif tp.type == "linear_ramp":
            hist = first_order_linear_ramp(
                self.reaction, tp.T_initial_K, tp.T_final_K, tp.heating_rate_K_per_s, dt_s
            )
            alpha = hist[-1][2]
        else:
            raise ValueError("minimal first-order model supports isothermal or linear_ramp only")

        ash = _dry_ash_fraction(case)
        if ash < 0 or ash > 1:
            raise ValueError("ash fraction outside [0,1]")
        organic = dry_feed_mass_kg * (1.0 - ash)
        ash_mass = dry_feed_mass_kg * ash
        unconverted = organic * (1.0 - alpha)
        converted_unresolved = organic * alpha

        products = ProductState(
            inorganic_residue_kg=ash_mass,
            unresolved_solid_kg=unconverted,
            unresolved_total_kg=converted_unresolved,
        )
        mass = MassLedger.from_product_state(dry_feed_mass_kg, products)

        e_inputs = _feed_element_inputs(case, dry_feed_mass_kg)
        # No phase speciation at L1: all tracked elemental mass remains accounted but unresolved.
        elements = ElementLedger.from_totals(e_inputs, dict(e_inputs))

        evidence = EvidencePassport(
            evidence_status=EvidenceStatus.SCREENING,
            case_domain_status="synthetic_or_unvalidated_baseline",
            claim_boundary=(
                "G2 screening implementation only. Conversion follows supplied Arrhenius parameters; "
                "no feedstock-general predictive validation or product-yield claim."
            ),
            rights_status="clear",
            warnings=["Minimal G2 model; not experimentally validated in this package."],
        )

        return MinimalModelResult(
            case_id=case.case_id,
            model_manifest=self.manifest,
            conversion=alpha,
            product_state=products,
            mass_ledger=mass,
            element_ledger=elements,
            energy_ledger={"status":"not_available"},
            evidence_passport=evidence,
            warnings=("No product-phase resolution; converted organic mass stored as unresolved.",),
        )
