# Modeling strategy and decision gates

## Problem definition

This dataset supports laboratory redox-degradation modeling, not a claim of field RUL in hours.
The primary forecast is future normalized performance by **assessment interval**. Threshold-based
RUL is secondary and explicitly right-censored when a cell never crosses the chosen SOH limit.

## Target ladder

1. Current SOH from steady current density at approximately 0.70 V.
2. Power SOH from the maximum IV power density.
3. IV-current SOH from interpolated current density at 0.70 V.
4. Composite SOH from the geometric mean of available normalized proxies.

No target is forced to be monotonic during construction. End of life requires three consecutive
below-threshold assessments by default, so one noisy dip does not create a false event. A monotonic
smoother may be evaluated as a sensitivity analysis, because irreversible degradation is plausible
but short-term recovery, instrument noise, and operating-condition changes can produce local
increases.

## Model ladder

| Gate | Models | Question |
|---|---|---|
| 0 | Persistence, drift | Is there forecastable information beyond the latest value? |
| 1 | Damped trend, ETS, ARIMA | Does temporal structure improve over simple baselines? |
| 2 | Ridge, Extra Trees, histogram gradient boosting | Do multimodal physics features transfer across cells? |
| 3 | XGBoost/LightGBM | Does tuned boosting add stable value? |
| 4 | GRU | Is sequence complexity justified by cross-cell evidence? |

Complexity advances only when improvement appears across held-out cells and horizons—not from one
pooled score.

## Advanced EIS gate

Circuit-agnostic descriptors are the default. Lin-KK diagnostics screen linearity/causality
consistency; candidate equivalent circuits are compared using residual structure and parameter
stability; DRT is used as a regularized timescale representation. None of these automatically maps
an arc to a mechanism. Results enter forecasting only after convergence, identifiability, and
leave-one-cell-out stability checks.

## Validation

The outer loop holds out an entire cell. The inner loop is expanding-window validation on the
remaining cells. Imputation, scaling, feature selection, and hyperparameter tuning are fit only on
inner-training observations. Final claims aggregate untouched outer-fold predictions.

## Failure analysis

Every experiment must examine:

- regular (`N*`) versus randomized (`R*`) redox regimes;
- early-life versus late-life error;
- cell-level bias and worst-cell performance;
- forecast-horizon degradation;
- repaired-file inclusion/exclusion;
- single-modality and leave-one-modality-out ablations;
- interval coverage and width, not only point error.
