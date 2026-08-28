# Pyrolysis Modelling Framework v0.1.1

## Release type

Quality-hardening patch release.

This release strengthens scientific documentation, evidence controls, numerical verification, package portability and release integrity. It does **not** expand the qualified scientific domain of `v0.1.0`.

## Qualified executable scope

The qualified public adapter remains `SFOR_RWTH` for extracted cellulose, hemicellulose and lignin under inert conditions, using linear-ramp or isothermal thermal programmes and reporting total volatile release / remaining solid with mass and unresolved element accounting.

Scientific evidence remains **calibrated / source-domain**. Software reproducibility, deterministic reruns and CI success do not constitute independent experimental validation.

## Main improvements

- strengthened scientific-basis and evidence/limitations documentation;
- clearer separation of executable status from scientific evidence status;
- public evidence registry packaged with the installed distribution;
- evidence labels for non-executed reference branches narrowed to what DP-06 actually reproduced;
- expanded numerical, basis-integrity, evidence-control and release-integrity tests;
- qualified-suite verification moved to temporary outputs so tests do not contaminate the source tree;
- built-wheel inspection added;
- clean-wheel installation and execution verified;
- exact-tag release-archive and checksum rules documented;
- release/citation/version metadata reconciled;
- elemental ledger wording clarified as unresolved conservation accounting, not predicted elemental partitioning;
- midpoint-exponential ramp integration documented as a numerical approximation with convergence verification.

## Frozen scientific baseline

The four qualified example numerical outputs remain frozen from `v0.1.0`. The patch therefore improves the public scientific/software quality layer without silently changing the accepted baseline results.

## Explicit non-capabilities

`v0.1.1` does not claim validated executable support for detailed product chemistry, CRECK, CPD/CPDSpatial, polymers, manure/dung, reactive CO2/steam, oxidative/autothermal pyrolysis, co-pyrolysis interaction chemistry, pressure-dependent kinetics, or a universal biomass kinetic model.

## Source model and provenance

The executable SFOR branch is based on Pielsticker et al. (2021), *Flash Pyrolysis Kinetics of Extracted Lignocellulosic Biomass Components*, DOI `10.3389/fenrg.2021.737011`, with associated RWTH supplementary dataset DOI `10.18154/RWTH-2021-05544`.

Raw source data are not redistributed. See `THIRD_PARTY_NOTICES.md`.

## Verification

Release-gate CI is required on:

- Ubuntu / Python 3.10;
- Ubuntu / Python 3.13;
- Windows / Python 3.13.

On Ubuntu / Python 3.13, the release gate also builds and inspects the wheel and verifies execution from a clean wheel installation.
