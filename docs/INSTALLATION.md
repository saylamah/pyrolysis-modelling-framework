# Installation

## Supported metadata

Python: `>=3.10`  
Runtime dependency: `jsonschema>=4.18`

Install from the repository:

```bash
python -m pip install .
```

Or install the release-candidate wheel from `dist/`:

```bash
python -m pip install dist/pyrolysis_modelling_framework-0.1.0rc2-py3-none-any.whl
```

## Commands

```bash
pyrolysis-validate <run-config.json>
pyrolysis-run <run-config.json>
pyrolysis-report <result.json>
pyrolysis-examples <suite-manifest.json>
```

## Portability status

Direct clean-environment execution has been verified on Linux with Python 3.13.5.

The release gate still requires the included CI matrix to pass on Ubuntu/Python 3.10, Ubuntu/Python 3.13 and Windows/Python 3.13 before `v0.1.0` may be tagged.

macOS and fully offline dependency bundling are not first-release requirements.
