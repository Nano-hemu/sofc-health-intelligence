# Notebook sequence

Run notebooks in order after `sofc-health all`:

| Notebook | Engineering decision |
|---|---|
| 01 | Is the normalized dataset structurally trustworthy and suitable for assessment-level analysis? |
| 02 | Which signal changes are physically credible, and how do trajectories differ across cells and redox regimes? |
| 03 | Which SOH definition is defensible, and how sensitive are health and EOL conclusions to that definition? |
| 04 | Which inference-time features are physically interpretable, stable, non-redundant, and free from target leakage? |
| 05 | Do temporal models beat persistence across horizons? |
| 06 | Do multimodal ML features generalize to unseen cells? |
| 07 | Are RUL labels observed or censored, and are intervals calibrated? |
| 08 | Which EIS spectra pass Lin-KK screening, what degradation information do they contain, and does EIS add value beyond SOH history? |
| 09 | Which conclusions survive modality ablation, repaired-data exclusion, worst-cell review, and cross-regime domain-shift testing? |

Each notebook contains a short mathematical explanation and an interview reasoning checkpoint. Core
logic belongs in `src/`; notebooks orchestrate experiments and communicate evidence.
