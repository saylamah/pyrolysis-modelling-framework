# Installation and Command-Line Use

## Requirements

- Python `>=3.10`
- runtime dependency: `jsonschema>=4.18`

Install from the repository:

```bash
python -m pip install .
```

## Commands

Validate a run configuration without executing kinetics:

```bash
pyrolysis-validate <run-config.json>
```

Run a qualified configuration:

```bash
pyrolysis-run <run-config.json>
```

Render a result:

```bash
pyrolysis-report <result.json>
```

Verify the complete qualified example suite:

```bash
pyrolysis-examples examples/suite_manifest.json --reruns 2
```

The example-suite verifier uses temporary result files and should not modify the source tree.

## Portability status

The `v0.1.0` release gate was verified on:

- Ubuntu / Python 3.10;
- Ubuntu / Python 3.13;
- Windows / Python 3.13.

macOS and fully offline dependency bundling were not first-release requirements.

## Recommended workflow

1. start from one of the qualified example cases;
2. change only documented inputs;
3. run `pyrolysis-validate`;
4. inspect any warnings or blockers;
5. run the case only after preflight passes;
6. read the Evidence Passport before interpreting the numerical result.

A successful command does not by itself establish experimental validation.
