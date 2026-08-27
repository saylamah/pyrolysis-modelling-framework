# Pyrolysis Modelling Framework v0.1.0

First public technical-preview release of the Pyrolysis Modelling Framework.

## Included

- Evidence-aware StudyCase / feedstock / regime workflow
- Deterministic model eligibility and Evidence Passport v2
- Qualified `SFOR_RWTH` executable branch for extracted cellulose, hemicellulose and lignin
- Inert-atmosphere linear-ramp and isothermal execution
- Mass and element ledger handling
- Deterministic JSON-schema / preflight validation
- User-facing evidence, uncertainty, warning and rights/provenance reporting
- Four qualified reproducible example cases
- MIT License for the original framework code

## Verification

Release-gate CI passed on:

- Ubuntu / Python 3.10
- Ubuntu / Python 3.13
- Windows / Python 3.13

The four qualified example outputs remain identical to the frozen controlled baseline.

## Evidence boundary

`SFOR_RWTH` remains **calibrated / source-domain**. Software reproducibility, clean installation and CI success do not constitute independent experimental validation.

This release does not claim validated executable support for detailed product chemistry, CRECK, CPD/CPDSpatial, polymers, manure/dung, CO2/oxidative/autothermal pyrolysis, co-pyrolysis interaction chemistry, pressure-dependent kinetics or a universal biomass kinetic model.

## Source attribution

The executable SFOR branch is based on:

Pielsticker, S.; Gövert, B.; Umeki, K.; Kneer, R. (2021). *Flash Pyrolysis Kinetics of Extracted Lignocellulosic Biomass Components*. Frontiers in Energy Research, 9:737011. DOI: `10.3389/fenrg.2021.737011`.

Supplementary dataset DOI: `10.18154/RWTH-2021-05544`.

Raw source data are not redistributed in this repository.