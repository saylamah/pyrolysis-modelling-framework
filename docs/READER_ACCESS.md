# Reader access to models and validation cases

This document is the fastest route from the manuscript to reusable software.

## Current published baseline

Repository: https://github.com/saylamah/pyrolysis-modelling-framework  
Published release: v0.1.1  
Zenodo DOI: 10.5281/zenodo.22143183

The published baseline contains the qualified `SFOR_RWTH` adapter and the original evidence/reproducibility infrastructure.

## v0.2.0

Version 0.2.0 adds rights-safe models and analysis tools developed with the manuscript:

- bounded empirical product-yield, nitrogen-fate, HDPE peak-response and mixed-feed null models;
- KAS, FWO, Friedman, Starink and DAEM analysis utilities;
- validation metrics and comparison semantics;
- sewage-sludge and food-waste reference diagnostics;
- model-selection, optimization and chemistry-fidelity helpers.

Use:

- `MODEL_CATALOG.md` to identify what a model resolves and its scientific limits;
- `VALIDATION_CATALOG.md` to inspect the experimental/literature evidence;
- `MANUSCRIPT_CODE_CROSSWALK.md` to move from manuscript model names to code paths;
- `examples/validation/` to reproduce compact validation cases;
- `data/model_access_registry.json` for machine-readable discovery.

Third-party detailed mechanisms are linked to their primary sources when redistribution rights or exact executable provenance do not justify bundling them in this repository.
