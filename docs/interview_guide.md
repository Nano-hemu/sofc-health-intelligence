# Interview guide

## Phase 1: data engineering and experimental reasoning

### Why did you choose this dataset?

It contains eight independent longitudinal SOFC degradation trajectories with repeated EIS,
polarization, and transient measurements. This supports cross-cell validation and lets me connect
time-series behaviour to electrochemical mechanisms rather than modelling a single precomputed
health column.

### Why not describe the data as field data?

The measurements are repeated experimental cell data, not telemetry from a permanently installed
commercial system. I retain that distinction because deployment conditions, balance-of-plant
effects, maintenance actions, and sensor drift would change the data-generating process.

### Why convert MATLAB files to Parquet?

The MATLAB tables are the immutable source format. Parquet gives typed columns, compression, fast
columnar reads, and interoperability with Python analytics. The conversion is reproducible because
the archive checksum, schema repairs, and transformation code are version controlled.

### Why not put the raw dataset in GitHub?

The institutional DOI remains the source of truth, the data carry a separate CC BY-NC licence, and
derived files are reproducible. Keeping data outside Git also prevents repository bloat and avoids
confusing the code licence with the data licence.

### What defects did you identify?

The source contains inconsistent column names, one misspelled directory, two malformed IV schemas,
variable transient lengths, and local clocks that reset. The loader repairs only known structural
issues and records the repaired source files in the manifest and audit report.

### What is the first modelling risk?

Data leakage. Random row splitting would place correlated samples from the same physical curve and
cell in both training and test sets. The final test unit must be a complete unseen cell, with
ordered inner validation for model selection.

## Modeling and mathematical reasoning

### Why define several SOH candidates?

SOH is not directly measured here; it is a construct derived from performance. Current retention,
maximum-power retention, and resistance growth emphasize different failure modes. I compare their
monotonicity, noise, cross-cell consistency, and sensitivity before selecting a primary target.

### Why use a geometric composite?

After within-cell normalization, a geometric mean treats proportional changes consistently and
limits compensation: a severely degraded modality cannot be fully hidden by an unusually high
value in another. I require at least two available modalities and retain the components for audit.

### Why is assessment-based RUL not field RUL?

An assessment index orders experiments but does not state operating hours or duty-cycle severity.
I therefore forecast remaining assessment intervals under the laboratory protocol. Conversion to
field hours would require exposure histories and external validation.

### Why can R² be negative?

R² compares squared model error with a mean predictor. It becomes negative when the forecast is
worse than that reference on a test set. For degradation forecasting I prioritize MAE/RMSE, bias,
MASE versus persistence, horizon curves, and cell-level distributions.

### Why not start with a GRU or Transformer?

There are many raw rows but only eight independent cell trajectories. A high-capacity sequence
model can memorize cell identity. It is justified only after simple temporal and tabular models are
beaten consistently under complete-cell holdout and uncertainty remains calibrated.

### What does conformal prediction add?

It turns calibration residuals into empirical prediction intervals without assuming Gaussian
errors. I still test coverage by horizon and cell because time dependence and domain shift weaken
the exchangeability assumption.

### What ablation would you show an interviewer?

I would compare all modalities, each modality alone, and each leave-one-out combination. I would
also exclude the two repaired N5 IV files. This distinguishes genuine information contribution from
performance driven by one data-cleaning choice.
