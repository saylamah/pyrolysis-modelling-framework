# Evidence, Applicability and Limitations

## Evidence vocabulary

The framework keeps the following scientific evidence statuses distinct:

`validated` · `independently_reproduced` · `calibrated` · `screening` · `diagnostic` · `extrapolative` · `exploratory`

Software tests establish implementation and numerical integrity. They do not convert a calibrated model into an experimentally validated model.

## Current executable branch

`SFOR_RWTH` is currently exposed as a **calibrated/source-domain** branch for extracted lignocellulosic components under inert conditions.

It is useful for controlled total volatile-release / remaining-solid calculations in its declared source regime.

It does not provide:

- detailed gas, tar or oil composition;
- reactive CO2, steam or oxidative chemistry;
- mineral-aware chemistry;
- particle-scale spatial transport;
- universal biomass transfer;
- validated pressure dependence.

## Product resolution

The executable SFOR model does not resolve volatile matter into gas and condensable product families. Volatile product mass therefore remains explicitly unresolved rather than being assigned to invented oil/tar/gas fractions.

## Uncertainty

Uncertainty classes remain separate. Model-form spread, parameter uncertainty, numerical error, measurement uncertainty and extrapolation/domain uncertainty are not collapsed into one unsupported confidence interval.

## Model selection

The selector follows a minimum-sufficient-fidelity rule. A more detailed model is not selected merely because it is more complex.

If a selected scientific branch is not integrated into the public executable package, preflight fails explicitly rather than substituting another model.

## Release boundary

Only the SFOR branch is executable in the first public release candidate. Other model families appearing in eligibility metadata are retained as bounded framework knowledge, not advertised as executable release capabilities.
