# Data card

## Dataset identity

**Name:** Tubular SOFC under Redox Cycling Degradation
**Creator:** Zeynab Salehi, University of Alberta
**DOI:** <https://doi.org/10.7939/82178>
**Licence:** CC BY-NC 4.0

## Intended use

This project uses the data for non-commercial research and portfolio demonstration in:

- SOFC degradation characterization
- state-of-health definition and sensitivity analysis
- time-series forecasting and remaining-useful-life estimation
- EIS/DRT feature extraction
- generalization studies across cells and redox regimes

It is not intended to support safety-critical control, warranty decisions, or commercial
deployment without independent validation.

## Experimental structure

Eight tubular SOFCs were evaluated from beginning of life to end of life. Each assessment includes
an IV curve and an EIS spectrum. Transient dynamic measurements occur between successive
assessments. Cells `N1`–`N6` use regular redox cycling; `R1` and `R2` use randomized redox cycling.

## Raw signals

| Signal | Canonical variables | Physical role |
|---|---|---|
| EIS | frequency, real/imaginary impedance, amplitude, bias, time | Separates ohmic and polarization processes |
| IV | voltage, current density, time | Measures electrochemical performance over load |
| Transient | voltage, current density, time | Captures within-cycle dynamics and stress response |

## Known data-quality conditions

- Source files are MATLAB table objects rather than plain numeric matrices.
- Column labels occur in two naming styles.
- The N5 transient directory is misspelled `Transinet_dynamics` in the source archive.
- N5 `IV13.mat` and `IV22.mat` have non-standard table schemas and require deterministic repair.
- Transient durations vary materially across cells.
- Local experiment time often resets at the next assessment and must not be treated as global time.
- Randomized-redox trajectories may be non-monotonic, so monotonic SOH assumptions require testing.

## Leakage risks

Rows within one curve are strongly dependent. Randomly splitting raw rows would place near-duplicate
experimental states in both training and test data. Evaluation must hold out complete cells and
preserve assessment order.

## Provenance controls

The downloader verifies the immutable archive against the SHA-256 recorded in
`src/sofc_health/config.py`. The raw and derived datasets are excluded from Git.
