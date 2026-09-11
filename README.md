# Pyrolysis Modelling Framework

**Prepared software version:** `v0.2.0`  
**Release state in this source tree:** release-ready / version DOI assigned only after archival  
**Previous published version:** `v0.1.1` — DOI `10.5281/zenodo.22143183`  
**Concept DOI:** `10.5281/zenodo.22129133`

The Pyrolysis Modelling Framework is an evidence-aware engineering framework for controlled pyrolysis modelling. Its governing rule is:

> use the smallest model that can answer the scientific or engineering question, and do not claim more than the evidence supports.

Version `v0.2.0` preserves the qualified `SFOR_RWTH` baseline from `v0.1.1` and adds rights-safe empirical, kinetic-analysis, diagnostic, model-selection and evidence-constrained optimization utilities developed in the associated multi-feedstock study. It does **not** turn all represented feedstocks or model families into universally validated predictive models.

## Scientific architecture

The invariant workflow remains:

`StudyCase → Feedstock Passport → Regime Passport → Model Eligibility → Model Adapter → Canonical Products → Mass/Element/Energy Ledgers → Evidence Passport → Validation/Uncertainty → optional Optimization`

The main principles are:

1. **Basis integrity.** Dry, dry-ash-free and as-received composition data are not silently mixed.
2. **Regime integrity.** Heating rate, atmosphere, residence time and other regime variables remain explicit.
3. **Minimum-sufficient fidelity.** Higher complexity requires a named information gain.
4. **No invented product split.** Unresolved quantities remain unresolved.
5. **Evidence ceilings.** Predictive claims are blocked when they exceed the evidence status of the selected branch.
6. **Rights/provenance visibility.** External mechanisms and datasets are cited without assuming redistribution rights.

## Qualified executable baseline carried forward

The original qualified adapter remains `SFOR_RWTH` for extracted cellulose, hemicellulose and lignin under inert conditions, with linear-ramp and isothermal temperature programmes, total volatile release / remaining solid, conservation accounting and deterministic preflight checks. Its scientific evidence remains **calibrated / source-domain**. Reproducible execution and passing tests are not independent experimental validation.

## New rights-safe v0.2.0 extensions

The `dp06_pyrolysis.extensions` package adds:

- bounded biomass product-yield interpolation with a same-study 600 °C holdout;
- local manure gas-phase-N interpolation with leave-one-interior-point-out assessment;
- a source-bounded HDPE heating-rate / DTG-peak relation;
- a measured-component biomass–PP additive-char null baseline;
- KAS, FWO, Friedman and Starink isoconversional tools plus source-specific DAEM utilities, kept methodologically distinct;
- validation metrics and a comparison harness that prevent incompatible observables from being collapsed into one score;
- sewage-sludge and food-waste source/reference diagnostics;
- minimum-sufficient model-selection guards across L1–L9;
- chemistry-fidelity eligibility guards;
- evidence-constrained Pareto and robustness utilities for optimization within qualified domains.

These additions have different evidence roles. Some are predictive comparisons, some are bounded interpolation, some are measured-component baselines, and some are diagnostic or decision-support utilities. See [`docs/VALIDATION_CATALOG.md`](docs/VALIDATION_CATALOG.md).

## Quick start

Python 3.10 or newer is required.

```bash
python -m pip install .
```

Existing qualified CLI workflow:

```bash
pyrolysis-validate examples/cellulose_tga_run.json
pyrolysis-run examples/cellulose_tga_run.json
pyrolysis-examples examples/suite_manifest.json --reruns 2
```

Example use of a v0.2.0 extension:

```python
from dp06_pyrolysis.extensions.empirical import emp_bio1_outer_anchor_holdout_600
print(emp_bio1_outer_anchor_holdout_600())
```

See [`docs/QUICKSTART_EXTENSIONS.md`](docs/QUICKSTART_EXTENSIONS.md) and [`docs/READER_ACCESS.md`](docs/READER_ACCESS.md).

## Representative evidence boundaries

- Biomass product-yield holdout: MAE 2.178 percentage points; RMSE 2.488 percentage points. This is bounded same-study interpolation, not cross-feedstock validation.
- Manure gas-phase-N interpolation: MAE 6.722 percentage points; RMSE 7.000 percentage points; non-monotonic source behaviour is retained.
- Biomass–PP additive-char null: RMSE 1.845 percentage points; causal synergy is not established.
- HDPE common-PE no-refit comparison: peak-temperature RMSE 15.74 K; systematic timing mismatch is retained rather than hidden by refitting.
- Sewage-sludge Coats–Redfern example: R² 0.984 versus 0.982 for the next candidate; fit coefficient alone does not identify a unique mechanism.
- Food-waste reactor example: deviations are output-specific (approximately −7.4% H₂, −6.8% bio-oil, +33% biochar).

Negative, partial and HOLD results are preserved because they define applicability limits.

## Reader access

- [`docs/MODEL_CATALOG.md`](docs/MODEL_CATALOG.md) — scientific role, source and executable/access status;
- [`docs/VALIDATION_CATALOG.md`](docs/VALIDATION_CATALOG.md) — predictive validation, source reproduction, baseline/null and diagnostic evidence records;
- [`docs/MANUSCRIPT_CODE_CROSSWALK.md`](docs/MANUSCRIPT_CODE_CROSSWALK.md) — manuscript terminology mapped to code and examples;
- [`data/model_access_registry.json`](data/model_access_registry.json) — machine-readable model/tool access registry;
- [`docs/EVIDENCE_AND_LIMITATIONS.md`](docs/EVIDENCE_AND_LIMITATIONS.md) — framework-wide evidence vocabulary and claim boundaries;
- [`docs/SCIENTIFIC_BASIS.md`](docs/SCIENTIFIC_BASIS.md) — core equations and physical accounting logic.

## Rights and redistribution boundary

Original framework code is released under the MIT License. Source-derived parameters and compact rights-safe values are used only where justified. Third-party CRECK/Ranzi, Bio-CPD/CPD, detailed polymer mechanisms and other external mechanisms are **not** redistributed unless their exact executable source and redistribution terms are explicitly qualified. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Not claimed

Version `v0.2.0` does not claim:

- one universally validated pyrolysis model across all feedstocks;
- universal kinetic parameters for biomass, polymers, manure, sewage sludge or food waste;
- validated detailed product chemistry merely because a mechanism is referenced;
- predictive pressure-dependent kinetics;
- universal co-pyrolysis synergy coefficients;
- that software tests constitute experimental validation;
- that diagnostic/reference utilities are predictive reactor models.

## Citation

Use the version-specific Zenodo DOI once `v0.2.0` has been archived. Until that DOI exists, the concept DOI `10.5281/zenodo.22129133` identifies the evolving software record. Source models and datasets used by a specific calculation should also be cited.

## License

Original framework code is released under the MIT License. Third-party source material remains subject to its own rights and citation conditions.
