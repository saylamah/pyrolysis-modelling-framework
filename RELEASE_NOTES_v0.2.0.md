# Pyrolysis Modelling Framework v0.2.0

## Release type

Bounded scientific/software capability extension of the v0.1.1 public baseline.

Version v0.2.0 preserves the qualified `SFOR_RWTH` execution branch and adds rights-safe multi-feedstock analysis, validation and decision-support utilities developed in the associated pyrolysis modelling study.

## Added

- bounded empirical biomass product-yield interpolation and holdout case;
- local manure gas-phase-N interpolation and leave-one-interior-point-out assessment;
- source-bounded HDPE peak-response relation;
- measured-component biomass–PP additive-char null baseline;
- KAS, FWO, Friedman and Starink isoconversional analysis plus source-specific DAEM utilities;
- validation metrics and compatible-observable comparison harness;
- sewage-sludge model-identification/reference diagnostics;
- food-waste cross-study kinetic and reactor-reference diagnostics;
- L1–L9 minimum-sufficient model-selection guards;
- chemistry-fidelity eligibility guards;
- evidence-constrained Pareto and robustness utilities;
- model, evidence/validation and manuscript-to-code catalogues;
- compact validation examples and machine-readable model-access registry;
- release-integrity guard for v0.2.0 metadata/evidence boundaries.

## Evidence discipline

The release explicitly keeps predictive validation, source reproduction, same-study holdout, independent transfer, measured-component baselines/null tests and diagnostics separate. Negative and partial results are retained.

Representative retained evidence includes:

- biomass-yield holdout RMSE 2.488 percentage points;
- manure-N interpolation RMSE 7.000 percentage points;
- biomass–PP additive-null RMSE 1.845 percentage points;
- HDPE no-refit peak-temperature RMSE 15.74 K;
- food-waste reactor deviations approximately −7.4% H₂, −6.8% bio-oil and +33% biochar.

The high-temperature char O/C assessment remains an **independent cross-study trend comparison**, not a same-feedstock transfer claim. LDPE use of the common-PE formulation is classified as **independent cross-grade transfer**.

## Backward compatibility

The v0.1.1 qualified SFOR branch is not refitted or redefined by this release. Existing baseline scientific claims remain bounded to their previous evidence.

## Not redistributed

Third-party CRECK/Ranzi, Bio-CPD/CPD, Cellulose V23, detailed gas-phase and detailed polymer mechanism files are not redistributed merely because they are discussed or referenced.

## Not claimed

This release does not define a universal best pyrolysis model, universal kinetic parameter, universal synergy coefficient, universal optimum or validated pressure-dependent model. Passing tests does not constitute experimental validation.

## Archival

The version-specific Zenodo DOI for v0.2.0 is reserved as `10.5281/zenodo.22707516` in the existing software concept/version chain. The DOI is not registered/live until the v0.2.0 Zenodo record is published. On or after 2026-10-01, the exact tagged release artifact will be archived in that reserved new-version draft only after the final release gate passes. The concept DOI remains `10.5281/zenodo.22129133`.
