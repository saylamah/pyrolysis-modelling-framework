# Qualified Examples

The example suite is deliberately small. Its purpose is to demonstrate the qualified executable branch, not to create a broad benchmark catalogue.

| Example | Component | Program | Source parameter branch |
|---|---|---|---|
| `cellulose_tga` | cellulose | 303–1173 K, 5 K/min | TGA |
| `hemicellulose_tga` | hemicellulose | 303–1173 K, 5 K/min | TGA |
| `lignin_tga` | lignin | 303–1173 K, 5 K/min | TGA |
| `cellulose_fbr_isothermal` | cellulose | 823 K, 1 s | high-FBR |

Run all examples:

```bash
pyrolysis-examples examples/suite_manifest.json --reruns 2
```

Each example must pass preflight, reproduce the frozen selected model and evidence status, and reproduce deterministic result hashes.

The SFOR evidence status remains `calibrated`.
