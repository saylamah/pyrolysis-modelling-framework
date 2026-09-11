# Manuscript–Code Crosswalk

The manuscript model names map to the following code and example locations.

| Model/tool | Scientific role | Release status | Code path | Example/validation path | Primary source | DOI |
|---|---|---|---|---|---|---|
| SFOR_RWTH | Global biomass-component conversion | Published v0.1.1 | src/dp06_pyrolysis/models/rwth2021.py | examples/cellulose_tga_run.json | Pielsticker et al. 2021 | 10.3389/fenrg.2021.737011 |
| Biomass yield interpolation | Empirical product yield | Included in v0.2.0 | src/dp06_pyrolysis/extensions/empirical.py | examples/validation/empirical_biomass_holdout.json | Fernandez et al. 2022 | 10.1016/j.energy.2021.122053 |
| Manure N interpolation | Empirical elemental fate | Included in v0.2.0 | src/dp06_pyrolysis/extensions/empirical.py | examples/validation/manure_N_leave_one_out.json | Baniasadi 2016 | 10.6092/unibo/amsdottorato/7493 |
| HDPE peak response | Empirical kinetic response | Included in v0.2.0 | src/dp06_pyrolysis/extensions/empirical.py | examples/validation/hdpe_peak_response.json | Rambhia et al. 2025 | 10.1016/j.nxener.2025.100354 |
| Biomass–PP additive char null | Empirical null model | Included in v0.2.0 | src/dp06_pyrolysis/extensions/empirical.py | examples/validation/biomass_pp_char_null.json | Wang et al. 2022 | 10.3389/fevo.2022.964936 |
| KAS/FWO/Friedman/Starink + DAEM | Multi-rate kinetic analysis (distinct isoconversional and DAEM methods) | Included in v0.2.0 | src/dp06_pyrolysis/extensions/daem_isoconversional.py | examples/validation/isoconversional_demo.json | Miura & Maki; ICTAC; source studies | 10.1021/ef970212q |
| Validation metrics | Model-vs-data comparison | Included in v0.2.0 | src/dp06_pyrolysis/extensions/validation_metrics.py | docs/VALIDATION_CATALOG.md | This work | |
| Comparison harness | Comparable-metric grouping | Included in v0.2.0 | src/dp06_pyrolysis/extensions/comparison_harness.py | docs/VALIDATION_CATALOG.md | This work | |
| Sewage-sludge reference diagnostics | Kinetic/reference adapter | Included in v0.2.0 | src/dp06_pyrolysis/extensions/sewage_sludge_reference.py | examples/validation/sewage_sludge_reference.json | Ghodke et al. 2021 | 10.1016/j.jenvman.2021.113450 |
| Food-waste reference diagnostics | Kinetic/reactor reference adapter | Included in v0.2.0 | src/dp06_pyrolysis/extensions/food_waste_reference.py | examples/validation/food_waste_reference.json | Vikraman; Yasir 2025 | |
| Minimum-sufficient model selection | Model applicability decision support | Included in v0.2.0 | src/dp06_pyrolysis/extensions/model_selection.py | docs/MODEL_CATALOG.md | This work | |
| Evidence-constrained optimization | Pareto / robustness utilities | Included in v0.2.0 | src/dp06_pyrolysis/extensions/optimization.py | docs/MODEL_CATALOG.md | This work | |
| Chemistry-fidelity eligibility | Detailed-chemistry applicability guard | Included in v0.2.0 | src/dp06_pyrolysis/extensions/chemistry_fidelity.py | docs/MODEL_CATALOG.md | This work | |
