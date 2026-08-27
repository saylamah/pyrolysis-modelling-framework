# Pyrolysis Modelling Framework

**Release candidate:** `0.1.0rc2`  
**Planned first public release:** `v0.1.0`  
**Status:** technical preview / qualified baseline — **not yet authorized for public tagging**

The Pyrolysis Modelling Framework is an engineering-oriented Python framework for controlled pyrolysis modelling. Its purpose is not to provide one universal kinetic model. It separates feedstock description, operating regime, model eligibility, numerical execution, balances, evidence status, uncertainty and applicability so that a result is difficult to over-interpret.

## Current executable scope

This release candidate contains one qualified executable kinetic branch:

- `SFOR_RWTH` for extracted cellulose, hemicellulose and lignin;
- inert atmosphere;
- linear-ramp and isothermal execution;
- total volatile release / remaining solid;
- mass and element ledgers;
- deterministic preflight validation;
- Evidence Passport and user-facing evidence/uncertainty reporting.

The SFOR branch is **calibrated/source-domain**. Reproducible software execution is not independent experimental validation.

## Not claimed in v0.1.0

This release does not provide validated executable support for detailed product chemistry, CRECK, CPD/CPDSpatial, polymers, manure/dung, CO2/oxidative/autothermal pyrolysis, co-pyrolysis interaction chemistry, pressure-dependent kinetics, or a universal biomass kinetic model.

## Quick start

Create an environment with Python 3.10 or newer and install the package:

```bash
python -m pip install .
```

Validate a case without running kinetics:

```bash
pyrolysis-validate examples/cellulose_tga_run.json
```

Run a qualified example:

```bash
pyrolysis-run examples/cellulose_tga_run.json
```

Render an existing result:

```bash
pyrolysis-report examples/cellulose_tga_result.json --format markdown
```

Verify the compact example suite:

```bash
pyrolysis-examples examples/suite_manifest.json --reruns 2
```

## Result discipline

A complete result carries an Evidence Passport with:

- selected model;
- scientific evidence status and evidence ceiling;
- domain/applicability status;
- uncertainty modes;
- warnings and blocked claims;
- rights/provenance boundary;
- deterministic integrity hashes.

`PASS_WITH_WARNINGS` is a usability/report status. It does **not** mean experimentally validated prediction.

## Qualified examples

The repository includes four deterministic examples:

1. cellulose TGA, 5 K/min;
2. hemicellulose TGA, 5 K/min;
3. lignin TGA, 5 K/min;
4. cellulose high-temperature isothermal SFOR demonstration.

The isothermal example exercises the source parameter branch; it is not presented as independent FBR detector-trace validation.

## Source kinetic model

The current executable SFOR branch is based on:

Stefan Pielsticker, Benjamin Gövert, Kentaro Umeki, and Reinhold Kneer (2021), *Flash Pyrolysis Kinetics of Extracted Lignocellulosic Biomass Components*, **Frontiers in Energy Research**, 9:737011. DOI: `10.3389/fenrg.2021.737011`.

Supplementary dataset: DOI `10.18154/RWTH-2021-05544`.

Raw source data are **not redistributed** in this repository. See `THIRD_PARTY_NOTICES.md`.

## Documentation

- `docs/EVIDENCE_AND_LIMITATIONS.md`
- `docs/INSTALLATION.md`
- `docs/EXAMPLES.md`
- `THIRD_PARTY_NOTICES.md`
- `CITATION.cff`

## Release-candidate licence status

The original framework code is licensed under the MIT License. See `LICENSE`.

## Compatibility status

Direct clean-environment execution has been verified on Linux / Python 3.13.5. The repository includes a CI workflow for the release gate on:

- Ubuntu / Python 3.10;
- Ubuntu / Python 3.13;
- Windows / Python 3.13.

The first public tag remains blocked until that endpoint matrix passes.

## Development direction

Later model adapters may be added only when their evidence, rights, executable integration and validation justify release. Higher fidelity is not a release objective by itself.


## License

Original Pyrolysis Modelling Framework code is released under the MIT License. See `LICENSE`. Third-party/source attribution remains governed by `THIRD_PARTY_NOTICES.md`.
