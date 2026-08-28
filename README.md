# Pyrolysis Modelling Framework

**Published version:** `v0.1.0`  
**Status:** technical preview / qualified baseline  
**Version DOI:** `10.5281/zenodo.22129134`  
**Concept DOI:** `10.5281/zenodo.22129133`

The Pyrolysis Modelling Framework is an evidence-aware engineering framework for controlled pyrolysis modelling. It is designed around a simple rule:

> use the smallest model that can answer the engineering question, and do not claim more than the evidence supports.

The framework separates the physical case, model choice, numerical execution, balances, evidence status, uncertainty and applicability. This makes model limitations visible instead of hiding them inside a single prediction.

## What is qualified now

The public workflow currently has one qualified executable model adapter:

- `SFOR_RWTH`;
- extracted cellulose, hemicellulose and lignin;
- inert atmosphere;
- linear-ramp and isothermal temperature programmes;
- total volatile release and remaining solid;
- mass and element ledgers;
- deterministic preflight checks;
- Evidence Passport v2 and user-facing warnings.

The `SFOR_RWTH` branch is **calibrated / source-domain**. Reproducible execution, numerical checks and CI success do **not** constitute independent experimental validation.

Other model families are retained as bounded eligibility/evidence metadata. They are not silently substituted for an unavailable executable model.

## Scientific architecture

The invariant workflow is:

`StudyCase → Feedstock Passport → Regime Passport → Model Eligibility → Model Adapter → Canonical Products → Mass/Element/Energy Ledgers → Evidence Passport → Validation/Uncertainty → optional Optimization`

The main design principles are:

1. **Basis integrity.** Dry, dry-ash-free and as-received composition data are not silently mixed.
2. **Regime integrity.** Heating rate, atmosphere, residence time and other regime variables remain explicit.
3. **Minimum-sufficient fidelity.** Higher model complexity requires a named information gain.
4. **No invented product split.** Unresolved volatile mass stays unresolved when the model cannot separate gas, tar/oil and water.
5. **Evidence ceilings.** A requested claim is blocked when it exceeds the evidence level of the selected branch.
6. **Rights/provenance visibility.** External mechanisms or datasets are referenced without assuming redistribution rights.

See [`docs/SCIENTIFIC_BASIS.md`](docs/SCIENTIFIC_BASIS.md) for the equations and physical accounting logic.

## Quick start

Python 3.10 or newer is required.

```bash
python -m pip install .
```

Validate a case before numerical execution:

```bash
pyrolysis-validate examples/cellulose_tga_run.json
```

Run a qualified case:

```bash
pyrolysis-run examples/cellulose_tga_run.json
```

Render a result:

```bash
pyrolysis-report examples/cellulose_tga_result.json --format markdown
```

Verify all four qualified examples without leaving generated result files in the repository:

```bash
pyrolysis-examples examples/suite_manifest.json --reruns 2
```

## Evidence and model status

The framework distinguishes:

`validated · independently_reproduced · calibrated · screening · diagnostic · extrapolative · exploratory`

These labels describe scientific evidence, not software quality.

The current public model metadata include higher-fidelity and future branches because model eligibility is part of the framework. Their evidence status and executable status are stored separately. In `v0.1.0`, `SFOR_RWTH` is the only model adapter exposed through the qualified execution workflow.

Generic Arrhenius and first-order utilities are also present as software/architecture utilities. They are **not** feedstock-general validated pyrolysis models and must not be interpreted as additional qualified model adapters.

## Qualified examples

| Example | Component | Thermal programme | Purpose |
|---|---|---|---|
| `cellulose_tga` | cellulose | 303–1173 K, 5 K/min | calibrated TGA branch |
| `hemicellulose_tga` | hemicellulose | 303–1173 K, 5 K/min | calibrated TGA branch |
| `lignin_tga` | lignin | 303–1173 K, 5 K/min | calibrated TGA branch |
| `cellulose_fbr_isothermal` | cellulose | 823 K, 1 s | source-parameter isothermal demonstration |

The isothermal example exercises the high-FBR source parameter branch. It is not presented as independent detector-trace validation.

## Source kinetic model

The qualified SFOR adapter is based on:

Stefan Pielsticker, Benjamin Gövert, Kentaro Umeki, and Reinhold Kneer (2021), *Flash Pyrolysis Kinetics of Extracted Lignocellulosic Biomass Components*, **Frontiers in Energy Research**, 9:737011. DOI: `10.3389/fenrg.2021.737011`.

Supplementary dataset: DOI `10.18154/RWTH-2021-05544`.

Raw source data are not redistributed in this repository. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Documentation

For fast access:

- [`docs/SCIENTIFIC_BASIS.md`](docs/SCIENTIFIC_BASIS.md) — equations, balances and physical interpretation;
- [`docs/EVIDENCE_AND_LIMITATIONS.md`](docs/EVIDENCE_AND_LIMITATIONS.md) — model/evidence matrix, claim boundaries and HOLD branches;
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) — numerical checks, CI and release-integrity rules;
- [`docs/INSTALLATION.md`](docs/INSTALLATION.md) — installation and command-line use;
- [`docs/EXAMPLES.md`](docs/EXAMPLES.md) — qualified example cases.

## Not claimed

This release does not provide validated executable support for:

- detailed product chemistry;
- CRECK execution or redistribution;
- CPD/CPDSpatial execution;
- polymers;
- manure or dung prediction;
- reactive CO2, steam, oxidative or autothermal pyrolysis;
- co-pyrolysis interaction chemistry;
- pressure-dependent kinetics;
- a universal biomass kinetic model.

## Citation

For the exact published `v0.1.0` software release:

`10.5281/zenodo.22129134`

For the evolving software record across versions:

`10.5281/zenodo.22129133`

If the framework is used in scientific work, cite the software release and the source kinetic model.

## License

Original framework code is released under the MIT License. Third-party source material remains subject to its own rights and citation conditions.

## Development rule

Later model adapters are added only when their scientific value, data, validation, executable integration and rights justify release. Higher fidelity is not an objective by itself.
