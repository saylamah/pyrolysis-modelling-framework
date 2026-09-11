# Evidence and Validation Catalogue — v0.2.0

This catalogue records predictive validation, source reproduction, measured-component baselines/null tests and diagnostic assessments. These are not treated as equivalent evidence types. Software tests establish implementation integrity; they are not experimental validation.

| object_id | feedstock_or_case | validation_topology | observable | primary_metric | result | secondary_result | evidence_interpretation | citations |
|---|---|---|---|---|---|---|---|---|
| EMP-BIO1 | Biomass product yields | same-study holdout | gas/oil/char at 600 C | MAE | 2.178 pp | RMSE 2.488 pp | bounded interpolation supported | [61] |
| EMP-MAN1 | Manure gas-phase N | leave-one-interior-point-out | gas-phase N fraction | MAE | 6.722 pp | RMSE 7.000 pp; max 10 pp | bounded interpolation with non-monotonicity limitation | [62] |
| EMP-MIX1 | Biomass+PP char null | same-study/null diagnostic | final char | RMSE | 1.845 pp | bias -1.186 pp; max 3.583 pp | additive null supported; causal synergy not established | [63] |
| SFOR_RWTH | Extracted biomass components | implementation/source-domain | conversion/TGA | deterministic rerun | 0 numerical difference | external model comparison separate | software integrity only | [59,60] |
| CRECK-v2502 | Rice straw | independent/no-refit transfer | peak timing | categorical | quantitative mismatch | useful causal diagnostic | Preserved negative transfer; no refit | [1,4,10] |
| Bio-CPD/CRECK/SFOR | Extracted biomass components | independent cross-model literature comparison | TGA, volatile yield, FBR release, tar | comparative | CRECK best TGA/final volatile; Bio-CPD best FBR release | all overpredict tar | Model-dependent strengths; ash/bed effects suspected | [4] |
| CHAR-O-RET | Beech high-T char | independent cross-study trend comparison | normalized O/C | RMSE | 0.079 | absolute isolated branch 5.9-7.2x whole-char O/C | normalized trend supported; absolute prediction not validated | [66] |
| BIO-PF1 | Biomass particle | source-model reproduction | retained-char yield | MAE | 0.0485 pp | RMSE 0.0601 pp; case errors -0.0804 to +0.0867 pp | source-domain reproduction supported; independent raw validation limited | [8,9] |
| MAN-HF1 | Camel manure | source raw-data reproduction | DTG main peak temperature | MAE | ~0.033 K | RMSE ~0.048 K | local peak reproduced; full curve not yet validated | [13] |
| PE-10R | HDPE | independent same-feedstock no-refit | DTG peak temperatures | MAE | 15.3 K | RMSE 15.741 K; log-rate response ratio ~76.1% | Useful trend, systematic timing mismatch preserved | [18,19] |
| PE-TRANSFER | LDPE | independent cross-grade transfer | TG curves | mean RMSE | ~12.39 pp | peak at 20 K min^-1 495.0 vs 491.85 C | peak timing supported; full TG agreement partial | [16] |
| PP-12R | PP | independent same-feedstock transfer | DTG peak at 2.5 K min^-1 | residual | ~ -2.9 K | 427.1 predicted vs ~430 C | bounded timing agreement | [16] |
| PS-6R | PS | independent same-feedstock transfer | DTG peak | residual | ~ -4 to -5 K | 434.58 predicted vs 438.95-439.91 C | bounded timing agreement | [16] |
| PET-18-22 | PET | independent same-feedstock no-refit | DTG peak | RMSE | 8.10 K | retained char 14.78 wt% vs 8.9-10.5 wt% | Timing bounded; residue bias retained | [17] |
| PVC-MII candidate | PVC | source-equation consistency diagnostic | Cl removal endpoint | residual | -34.405 pp | 65.285% predicted vs 99.69% source | Plain cumulative candidate REJECTED | [64] |
| PVC-MII Eq7-like | PVC | source-equation consistency diagnostic | Cl removal endpoint | residual | -0.062 pp | 99.628% predicted vs 99.69% source | Endpoint consistent; full dynamic implementation not yet validated | [64] |
| SLUDGE-REF | Sewage sludge | source/reference diagnostic | 500 C product closure | closure error | 0 pp | 58.7/22.4/18.9 = 100% | Ledger consistency, not model validation | [24] |
| SLUDGE-CR | Sewage sludge | model-identification diagnostic | Coats-Redfern R2 gap | Delta R2 | 0.002 | .984 vs .982 | Mechanism underdetermined by R2 | [24] |
| FOOD-ISO | Food waste | cross-study kinetic comparison | mean activation energy | difference | 44.965 kJ mol^-1 | ~25.84% of Vikraman mean | Feedstock/study dependence exceeds method dispersion | [29,30] |
| FOOD-CFD | Food waste | cross-reactor/study comparison | H2 / bio-oil / biochar | relative errors | -7.4% / -6.8% / +33% | CO deviation not reduced to one scalar | Output-specific PARTIAL validation | [30] |
