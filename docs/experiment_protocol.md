# Experiment protocol

## Before fitting

- Freeze the target definition, split rules, horizons, metrics, and random seed in YAML.
- Record package versions and dataset checksum.
- Confirm that the feature table key `(cell_id, assessment_index)` is unique.
- Inspect missingness by modality and decide whether absence is informative.

## During fitting

- Use only causal lag features.
- Fit transformations inside each training fold.
- Tune against inner folds; never view outer-cell metrics to select hyperparameters.
- Save one prediction row per cell, origin, target assessment, and horizon.
- Compare against persistence before discussing R².

## After fitting

- Report MAE, RMSE, signed bias, R², and MASE.
- Bootstrap by cell, not by raw row, when estimating confidence intervals.
- Plot residuals against horizon, cell, regime, and predicted health.
- Check conformal interval coverage and width.
- Run every predefined ablation, including removal of repaired source files.
- Document negative results in the model card.

## Claim language

Allowed: “forecasted normalized performance over future degradation assessments in a laboratory
redox protocol.”

Not allowed without additional data: “predicted field life in hours,” “production-ready digital
twin,” or “validated on installed systems.”
