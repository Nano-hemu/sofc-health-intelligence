# Path from laboratory cells to field-installed SOFC/SOEC systems

The current open dataset is laboratory redox-cycling data. A credible field extension needs a
different observation model and validation boundary.

## Minimum field telemetry

- timestamp, accumulated operating hours, starts/stops, load set point, stack voltage/current;
- cell-voltage distribution, inlet/outlet temperatures and pressures;
- fuel/air flow, utilization, steam-to-carbon ratio or electrolysis steam conversion;
- alarms, purge events, maintenance, calibration, replacement, and shutdown causes;
- periodic EIS or diagnostic polarization data when available.

## Additional engineering problems

Irregular sampling, sensor drift, missing-not-at-random data, maintenance interventions, operating
regime changes, seasonal demand, unit-to-unit configuration differences, and partial failure labels
must be modeled. Calendar-time splits and site holdouts replace laboratory assessment-only splits.

## Transfer strategy

1. Keep laboratory-derived features as priors or candidate representations.
2. Recalibrate targets against field KPIs and verified maintenance/failure events.
3. Compare no-transfer, frozen-feature, fine-tuned, and hierarchical models.
4. Quantify covariate and concept shift before reporting field RUL.
5. Use abstention or wide uncertainty when telemetry falls outside training support.

This extension would convert the portfolio from a strong experimental prognostics project into a
deployment study; it cannot be claimed without suitable real-system data.
