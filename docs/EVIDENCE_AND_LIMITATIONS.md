# Evidence, Applicability and Limitations

## 1. Evidence vocabulary

The framework keeps the following scientific evidence classes distinct:

| Status | Meaning in this framework |
|---|---|
| `validated` | validated against evidence appropriate to the stated claim and domain |
| `independently_reproduced` | independently implemented/reproduced quantitative relation or result, within its stated scope |
| `calibrated` | model parameters or formulation calibrated in the source domain |
| `screening` | useful for bounded screening, not a validated predictive claim |
| `diagnostic` | supports comparison, interpretation or decision logic but not direct predictive use |
| `extrapolative` | used outside the evidence-qualified domain |
| `exploratory` | hypothesis/development branch without sufficient qualification for stronger claims |

Software tests establish implementation and numerical integrity. They do not convert one evidence class into another.

## 2. Public execution versus evidence metadata

`SFOR_RWTH` is the only model adapter currently exposed through the qualified public execution workflow.

Two machine-readable layers are deliberately separated. `data/model_passport_profiles.json` contains detailed metadata for model branches distributed with the package. `data/public_evidence_registry.json` controls outward evidence status and public executable status for all branches recognized by the selector. Registry-only branches are represented conservatively as eligibility/evidence metadata; their presence does not imply that model code, source data or a full validation package is distributed.

This separation prevents a source-comparison or development result from silently becoming a stronger public claim.

## 3. Model/evidence matrix

| Branch | Public executable | Current public evidence status | Current role / boundary |
|---|---:|---|---|
| `SFOR_RWTH` | yes | `calibrated` | source-domain total volatile release / remaining solid |
| `CRECK_BIOMASS` | no | `diagnostic` | higher-fidelity chemistry/product reference from B2 source-output comparison; DP-06 execution not independently reproduced |
| `CPD_FAMILY` | no | `diagnostic` | high-heating-rate release-dynamics reference from B2 source-output comparison |
| `CPDSPATIAL` | no | `exploratory` | particle/spatial branch on HOLD pending direct DP-06 reproduction |
| `AEP_ISOCONVERSIONAL` | no | `diagnostic` | heterogeneous-feed kinetic characterization; table-level/source-locked reproduction, raw-TGA reprocessing deferred |
| `PS_7_6`, `PE_GLOBAL`, `PP_GLOBAL` | no | `screening` | polymer mass-loss screening within source-compatible domains |
| `PET_GLOBAL_OR_SEMIDETAILED`, `PVC_SEMIDETAILED` | no | `screening` | guarded specialist branches; thermochemistry/product limitations remain |
| `MOISTURE_EQ7` | no | `independently_reproduced` | analytical heat-demand relation only; not a product-yield model |
| `CO2_STAGE_BRANCH` | no | `diagnostic` | stage-dependent atmosphere rule; not an independently reproduced predictive CO2 model |
| `AUTOTHERMAL_LEDGER` | no | `screening` | system energy-closure logic; no universal autothermal equivalence ratio |
| `COPYROLYSIS_LINEAR_NULL` | no | `diagnostic` | mandatory null model before any synergy claim |

The authoritative machine-readable outward claim controls are in `data/public_evidence_registry.json`.

## 4. Qualified SFOR boundary

`SFOR_RWTH` supports extracted cellulose, hemicellulose and lignin under inert conditions, using the source parameter branches implemented in the package.

It supports:

- linear-ramp or isothermal execution;
- total volatile yield;
- remaining solid;
- mass and element accounting;
- deterministic preflight and evidence reporting.

It does not provide:

- detailed gas, tar or oil composition;
- reactive CO2, steam or oxidative chemistry;
- mineral-aware chemistry;
- particle-scale spatial transport;
- universal biomass transfer;
- validated pressure dependence.

## 5. Product-resolution boundary

The executable SFOR model does not resolve volatile matter into gas and condensable families. Converted volatile mass therefore remains explicitly unresolved.

No oil/tar/gas split is inferred from total volatile yield.

## 6. Uncertainty

The framework keeps uncertainty classes separate:

- input;
- parameter;
- model form;
- numerical;
- measurement;
- extrapolation/domain.

Unavailable uncertainty is reported as unavailable, not as zero.

Cross-model spread can be useful as a **model-form diagnostic**, but it is not treated as a probability distribution unless a probabilistic basis exists.

## 7. Complexity/value rule

A higher-fidelity branch is justified only when it adds a named, evidence-backed information gain relevant to the engineering decision.

Use:

- **ESCALATE** when the current model cannot answer the required question or the higher-fidelity branch provides a material evidence-backed gain;
- **STOP** when the smaller model is already sufficient;
- **HOLD** when validation, data or rights are not ready;
- **BLOCK** when no available branch can support the requested claim.

Unknown information gain does not justify added complexity.

## 8. Current HOLD branches

The following remain explicitly open but not release-qualified:

- direct CPDSpatial reproduction;
- finite-particle transport branch;
- quantitative K/Ca mineral branch;
- raw-TGA reprocessing for camel-dung AEP;
- co-pyrolysis interaction chemistry beyond the linear null;
- PET/PVC validated energy optimization;
- higher-fidelity HDPE/LDPE differentiation;
- pressure-dependent baseline kinetics.

A HOLD is not a rejection of future value.

## 9. Generic software utilities

The package contains generic Arrhenius and first-order screening utilities used during architecture and numerical verification.

They are software components, not additional qualified feedstock-specific pyrolysis models. Where they generate a result, their evidence remains `screening`.

## 10. Claim rule

A public claim must remain narrower than:

1. the selected model's evidence status;
2. its feedstock domain;
3. its regime/atmosphere domain;
4. its output resolution;
5. its validation source;
6. its rights/provenance boundary.

If any required condition is not met, the framework should warn, HOLD or block rather than silently extrapolate.
