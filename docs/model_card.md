# Model card — template

## Intended use

Forecast assessment-level SOFC performance under the source laboratory redox protocols and study
which diagnostic modalities contribute transferable degradation information.

## Out-of-scope use

- Field-hour RUL or warranty decisions
- Safety-critical control
- Direct transfer to different stack designs, fuels, temperatures, or duty cycles
- Commercial use of the CC BY-NC source data

## Training and evaluation data

Complete after running the final experiment. Include dataset DOI/checksum, cells, assessment ranges,
missing modalities, regime labels, and every exclusion.

## Targets and features

Complete with the chosen SOH definition, threshold sensitivity, causal lag set, and modality list.

## Validation and results

Report outer leave-one-cell-out metrics by cell and horizon. Include persistence improvement,
worst-cell error, randomized-regime error, and 90% interval coverage/width.

## Limitations and risks

The dataset contains only eight laboratory cells. Assessment index is not operating time. The
composite SOH is a modeling construct, not a certified health standard. Equivalent-circuit
parameters can be non-identifiable. Domain shift is expected for field installations.

## Ethical and reproducibility notes

Keep raw data under its original CC BY-NC terms. Publish code under MIT, record random seeds,
environment versions, predictions, and failed experiments.
