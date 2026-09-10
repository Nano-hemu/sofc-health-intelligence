# Notebook sequence

Run notebooks in order after `sofc-health all`:

| Notebook | Engineering decision |
|---|---|
| 01 | Is the normalized dataset structurally trustworthy? |
| 02 | Which signal changes are physically credible, and does EIS pass validity gates? |
| 03 | Which SOH definition is defensible and how sensitive is EOL? |
| 04 | Which causal features are available, stable, and non-redundant? |
| 05 | Do temporal models beat persistence across horizons? |
| 06 | Do multimodal ML features generalize to unseen cells? |
| 07 | Are RUL labels observed or censored, and are intervals calibrated? |
| 08 | Which conclusions survive ablation and domain-shift checks? |

Each notebook contains a short mathematical explanation and an interview reasoning checkpoint. Core
logic belongs in `src/`; notebooks orchestrate experiments and communicate evidence.
