# Extension Quick Start — v0.2.0

These modules are the rights-safe v0.2.0 extension layer for the public `pyrolysis-modelling-framework` repository.

After integration into the repository package:

```python
from dp06_pyrolysis.extensions import empirical
print(empirical.emp_bio1_outer_anchor_holdout_600())
```

For multi-rate kinetics:

```python
from dp06_pyrolysis.extensions.daem_isoconversional import kas
r = kas([5,10,20], [600,620,640], alpha=0.5)
print(r.E_kJ_mol)
```

Read `docs/MODEL_CATALOG.md` before selecting a model and `docs/VALIDATION_CATALOG.md` before transferring it to a new feedstock or regime.
