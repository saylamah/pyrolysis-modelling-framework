# Qualified Examples

The example suite is deliberately small. Its purpose is to verify the qualified public execution branch and its evidence controls.

| Example | Component | Thermal programme | Parameter branch | Evidence |
|---|---|---|---|---|
| `cellulose_tga` | cellulose | 303–1173 K, 5 K/min | TGA | calibrated/source-domain |
| `hemicellulose_tga` | hemicellulose | 303–1173 K, 5 K/min | TGA | calibrated/source-domain |
| `lignin_tga` | lignin | 303–1173 K, 5 K/min | TGA | calibrated/source-domain |
| `cellulose_fbr_isothermal` | cellulose | 823 K, 1 s | high-FBR | calibrated/source-parameter demonstration |

Run all examples:

```bash
pyrolysis-examples examples/suite_manifest.json --reruns 2
```

The verifier checks that every case:

- passes preflight;
- selects `SFOR_RWTH`;
- preserves the frozen evidence status;
- reproduces the frozen scientific outputs and integrity hashes;
- closes the mass ledger;
- gives identical result bytes on repeated execution.

The verifier now uses temporary output paths, so routine verification does not leave generated result JSON files in the repository.

## Interpretation

The three TGA examples exercise source-calibrated component parameter sets.

The isothermal cellulose case exercises the high-FBR source parameter branch. It is a deterministic software/scientific demonstration, not an independent reproduction of the experimental FTIR detector trace.

No example should be interpreted as a universal biomass prediction.
