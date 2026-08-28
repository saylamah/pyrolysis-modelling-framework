# Reproducibility and Release Integrity

## 1. What reproducibility means here

Reproducibility is separated into three layers:

1. **software integrity** — code executes deterministically and obeys its contracts;
2. **numerical integrity** — numerical methods reproduce analytical/high-accuracy references and converge as expected;
3. **scientific evidence** — model results remain within the evidence status and domain supported by source/validation evidence.

Passing layers 1 and 2 does not establish layer 3.

## 2. Public verification layers

The public tests cover:

- JSON/schema and semantic preflight;
- composition-basis and atmosphere closure guards;
- evidence-ceiling blocking;
- explicit failure for unintegrated model adapters;
- deterministic qualified examples;
- mass and element closure;
- unresolved-product preservation;
- analytical first-order identities;
- high-accuracy reference comparison for linear-ramp integration;
- numerical convergence;
- stable SFOR integration checks;
- evidence-profile guards.

The qualified example suite is deliberately small. It tests the public baseline; it is not a broad validation database.

## 3. Cross-platform CI

The release-gate workflow runs on:

- Ubuntu / Python 3.10;
- Ubuntu / Python 3.13;
- Windows / Python 3.13.

A release candidate is not considered technically ready until the complete matrix passes.

## 4. Deterministic example execution

`pyrolysis-examples` reruns each qualified case and compares the result bytes and frozen scientific hashes.

From the quality-hardening branch onward, suite verification uses temporary output paths. Running the verification suite therefore does not leave generated `*_result.json` files in the source tree.

This protects release-archive integrity.

## 5. Release archive rule

A source archive for a formal release must be built from the exact Git tag for that release.

The release archive must not contain:

- `.pytest_cache`;
- `__pycache__`;
- local build directories;
- audit workspaces;
- generated example results unless they are intentionally part of the tagged release;
- stale checksum manifests.

If a checksum manifest is supplied, it must be generated **after** final archive assembly and must reference only files actually included in that release artifact.

## 6. Rights and source data

Third-party raw source data are not redistributed merely because they were used during validation or comparison.

The repository carries source citations and rights boundaries in `THIRD_PARTY_NOTICES.md` and model-passport metadata.

## 7. Scientific reproducibility boundary

The current public SFOR adapter is calibrated/source-domain.

A user who reruns the examples should obtain the same software outputs, but this does not constitute independent experimental validation of the model outside the source/calibration domain.
