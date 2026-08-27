from enum import Enum

class Basis(str, Enum):
    AS_RECEIVED = "as_received"
    DRY = "dry"
    DRY_ASH_FREE = "dry_ash_free"

class QualityStatus(str, Enum):
    MEASURED_PRIMARY = "measured_primary"
    MEASURED_SECONDARY = "measured_secondary_source"
    DERIVED = "derived"
    ESTIMATED = "estimated"
    ASSUMED = "assumed"
    MISSING = "missing"

class FeedstockFamily(str, Enum):
    LIGNOCELLULOSIC_BIOMASS = "lignocellulosic_biomass"
    AGRICULTURAL_RESIDUE = "agricultural_residue"
    CATTLE_MANURE = "cattle_manure"
    CAMEL_DUNG = "camel_dung"
    PLASTIC_SINGLE = "plastic_single"
    PLASTIC_MIXTURE = "plastic_mixture"
    BIOMASS_PLASTIC_MIXTURE = "biomass_plastic_mixture"

class AtmosphereClass(str, Enum):
    INERT = "inert"
    CO2_CONTAINING = "co2_containing"
    STEAM_CONTAINING = "steam_containing"
    OXIDATIVE = "oxidative"
    AUTOTHERMAL_CANDIDATE = "autothermal_candidate"
    CUSTOM = "custom"

class EvidenceIntent(str, Enum):
    SCREENING = "screening"
    DIAGNOSTIC = "diagnostic"
    REPRODUCTION = "reproduction"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    EXPLORATORY = "exploratory"

class EvidenceStatus(str, Enum):
    VALIDATED = "validated"
    INDEPENDENTLY_REPRODUCED = "independently_reproduced"
    CALIBRATED = "calibrated"
    SCREENING = "screening"
    DIAGNOSTIC = "diagnostic"
    EXTRAPOLATIVE = "extrapolative"
    EXPLORATORY = "exploratory"

class EligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_WITH_WARNING = "eligible_with_warning"
    SCREENING_ONLY = "screening_only"
    EXTRAPOLATIVE = "extrapolative"
    INELIGIBLE_MISSING_INPUTS = "ineligible_missing_inputs"
    INELIGIBLE_DOMAIN = "ineligible_domain"
    INELIGIBLE_RIGHTS = "ineligible_rights"
    INELIGIBLE_OUTPUT = "ineligible_output"
