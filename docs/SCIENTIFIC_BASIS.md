# Scientific Basis

## 1. Purpose

This document explains the physical and mathematical basis of the currently qualified public workflow. It is deliberately narrower than the long-term DP-06 programme.

The qualified numerical branch is `SFOR_RWTH` for extracted cellulose, hemicellulose and lignin under inert conditions. Other model families remain eligibility/evidence references until their own executable and validation gates are satisfied.

## 2. Case description before kinetics

A numerical result is not defined only by a kinetic parameter set. The framework first fixes:

- feedstock identity and provenance;
- composition basis;
- thermal programme;
- pressure;
- atmosphere;
- requested output;
- requested evidence level;
- model-selection constraints.

The main composition bases are:

- `as_received`;
- `dry`;
- `dry_ash_free`.

Complete composition blocks must close to one within tolerance. A complete dry proximate analysis contains volatile matter, fixed carbon and ash; non-zero moisture is not permitted in a dry-basis block. A complete as-received proximate analysis must state moisture explicitly.

This prevents silent rebasing.

## 3. Qualified SFOR equation

For a source component, the qualified adapter follows the source single-first-order-reaction form

\[
\frac{dy}{dt}=k(T)\,[y_\infty(T)-y]
\]

where:

- \(y\) is cumulative volatile yield;
- \(y_\infty(T)\) is the temperature-dependent final volatile yield;
- \(k(T)\) is the Arrhenius rate coefficient.

The Arrhenius coefficient is

\[
k(T)=A\exp\left(-\frac{E}{RT}\right)
\]

with the source-specific pre-exponential factor \(A\) and activation energy \(E\).

The source final-yield function is represented in the code as

\[
y_\infty(T)=\frac{C_1}{1+C_2\exp[-C_3(T-C_4)/C_5]}.
\]

The published parameter sets are stored in `src/dp06_pyrolysis/models/rwth2021.py`. They are used without refitting in the qualified examples.

## 4. Thermal programmes

### Isothermal

At constant temperature, the source SFOR equation has the direct form

\[
y(t)=y_\infty(T)\,[1-\exp(-k(T)t)].
\]

The isothermal example uses this source relation and the corresponding high-FBR parameter branch.

### Linear temperature ramp

For a ramp

\[
\frac{dT}{dt}=\beta,
\]

the framework integrates the same SFOR equation along the prescribed temperature history.

The public adapter uses a **piecewise midpoint-frozen coefficient exponential update** over each temperature interval: within one numerical step, \(k\) and \(y_\infty\) are evaluated at the interval midpoint and the resulting scalar first-order equation is advanced analytically over that step. This is a numerical integration scheme for the unchanged source ODE; it is not an exact closed-form solution for continuously varying \(k(T)\) and \(y_\infty(T)\).

The scheme was introduced to avoid instability in the stiff high-temperature tail of the inherited explicit RK4 implementation. It changes no source kinetic coefficient and no final-yield coefficient.

Numerical verification checks that the stable integration agrees with the inherited formulation where the latter is stable and converges as the temperature step is refined.

## 5. Product accounting

The SFOR model resolves total volatile release, not detailed molecular products.

Therefore the framework does **not** infer an oil/tar/gas split.

For a dry feed mass \(m_0\), the reported product state keeps:

- remaining solid;
- inorganic residue where present;
- converted but unresolved volatile mass.

Mass closure is evaluated as

\[
\varepsilon_m=\frac{m_\mathrm{in}-m_\mathrm{out}}{m_\mathrm{in}}.
\]

A zero closure residual means the bookkeeping closes. It does not mean the product chemistry is experimentally validated.

## 6. Element accounting

When an ultimate analysis is supplied, element masses are calculated on the declared composition basis.

The current SFOR branch does not predict the partition of C, H, O, N, S or Cl among solid, condensable and gaseous products. The present element ledger therefore keeps each tracked input element in an **unresolved conserved inventory**. Its zero residual is an accounting identity/check, not a prediction or validation of elemental fate.

No phase-resolved elemental distribution should be inferred from this ledger. Future product-resolving adapters must supply their own explicit elemental-output mapping before elemental fate can become a predictive result.

## 7. Energy accounting

The qualified SFOR execution does not provide a closed energy balance. Its energy-ledger status is therefore `not_available`.

This is intentional. Autothermal or heat-duty claims require an explicit energy layer with, at minimum, the relevant heat sources, heat losses, oxidation contribution and operating basis.

## 8. Model eligibility

Model choice depends on the engineering question.

Examples:

- total conversion or total volatile yield in the calibrated component/source domain → SFOR can be sufficient;
- detailed product/species distribution → a higher-fidelity chemistry model is required, but no such public adapter is yet qualified;
- high-heating-rate release timing → CPD-family evidence is relevant, but direct DP-06 execution remains unqualified;
- particle-scale prediction → CPDSpatial remains on HOLD pending direct reproduction;
- heat-demand-only moisture screening → the separately qualified analytical moisture relation can be sufficient without escalating to detailed chemistry.

The framework therefore separates **model value** from **model complexity**.

## 9. Evidence ceiling

Every run carries an Evidence Passport. If the requested evidence level is higher than the selected model can support, preflight blocks numerical execution.

For the current qualified SFOR branch, the evidence ceiling is `calibrated`.

Software tests, deterministic reruns and cross-platform CI establish implementation integrity. They do not raise this evidence ceiling.

## 10. Current scientific boundary

The public release is a controlled engineering framework with one calibrated/source-domain executable adapter. It is not a universal pyrolysis simulator.

The long-term architecture can accommodate additional feedstocks, atmospheres, transport models, product chemistry and energy layers, but each addition requires its own evidence, data, rights and complexity-value gate.
