# SOFC Health Intelligence

Physics-informed, multimodal prognostics for solid oxide fuel cells under redox degradation.

This repository turns raw longitudinal SOFC degradation experiments into an interview-defensible forecasting
system. It combines transient current response, polarization curves, and electrochemical
impedance spectroscopy (EIS) while enforcing leakage-safe validation across cells.

> **Repository status:** all planned data, feature, target, validation, modeling, uncertainty,
> ablation, documentation, and guided-notebook layers are implemented. Final performance claims
> remain intentionally blank until the complete nested-validation experiment is run and reviewed.

## Why this project is different

- Eight independently tested SOFCs, including regular and randomized redox regimes
- Two time axes: time inside an experiment and degradation assessment number
- Multimodal signals rather than a single pre-cleaned health column
- Complete-cell holdouts instead of random row splitting
- Physics-based features, statistical baselines, uncertainty, and model ablations
- Reproducible command-line pipeline, automated tests, CI, data card, and model documentation

## Dataset

The project uses **Tubular SOFC under Redox Cycling Degradation**, published by the University
of Alberta Education & Research Archive.

- DOI: <https://doi.org/10.7939/82178>
- Cells: `N1`–`N6` (regular redox) and `R1`–`R2` (randomized redox)
- Measurements: repeated EIS, IV curves, and intervening transient dynamics
- Licence: CC BY-NC 4.0

The data are not committed to this repository. The downloader retrieves the archive from the
institutional record and verifies SHA-256 before extraction. See [DATA_LICENSE.md](DATA_LICENSE.md).

## Quick start

Python 3.12 is recommended. On Windows Git Bash:

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[analysis,ml,dev]"
sofc-health all
jupyter lab notebooks/01_data_audit.ipynb
```

On Linux or macOS, activate with `source .venv/bin/activate`.

Run the stages separately when debugging:

```bash
sofc-health download
sofc-health prepare
sofc-health audit
```

The pipeline produces:

```text
data/processed/
├── eis.parquet
├── iv.parquet
├── transient.parquet
├── manifest.json
├── audit_report.json
├── features.parquet
└── modeling_table.parquet
```

## Data model

The experiment is hierarchical:

```text
cell_id → assessment_index → sample_index
```

`sample_index` and `elapsed_s` describe observations inside one experiment. They do not form a
single global clock across all redox assessments. A future forecasting table will therefore use
assessment index as the slow degradation axis and summarize the within-assessment dynamics using
physically meaningful features.

## Validation contract

The following rules are fixed before model development:

1. Never randomly split raw rows.
2. Hold out complete cells for final evaluation.
3. Preserve temporal order during inner validation.
4. Fit preprocessing using training folds only.
5. Compare every model against persistence, drift, and statistical baselines.
6. Report performance by cell and forecast horizon, not only one pooled metric.
7. Evaluate uncertainty coverage and interval width for RUL decisions.

## Roadmap

- [x] Dataset due diligence and raw-file audit
- [x] Reproducible downloader and checksum verification
- [x] Robust MATLAB-table loader and schema repair
- [x] Canonical Parquet tables, manifest, audit, tests, and CI
- [x] Physics-aware exploratory analysis workflow
- [x] SOH target sensitivity and censored RUL construction
- [x] Circuit-agnostic EIS, IV, and transient feature pipeline
- [x] Persistence, drift, exponential-smoothing, and ARIMA baselines
- [x] Leakage-safe tabular ML and optional GRU interface
- [x] Conformal uncertainty, domain-shift tests, and modality ablations
- [x] Model-card template, experiment protocol, and resume-claim guardrails
- [ ] Run and review the final nested experiments; populate verified metrics

## Repository map

```text
configs/                Versioned analytical assumptions
data/                   Ignored raw and generated data directories
docs/                   Data card, mathematics, and interview preparation
notebooks/              Guided analysis and communication
reports/                Ignored generated metrics, predictions, and figures
models/                 Ignored trained artifacts
scripts/                Reproducible pipeline and experiment entry points
src/sofc_health/        Reusable production code
tests/                  Offline unit tests
.github/workflows/      Continuous integration
```

## Reproducibility

```bash
ruff check .
pytest
```

## Publish to GitHub

After the quality commands pass, create an empty GitHub repository and run from Git Bash:

```bash
git init -b main
git add .
git commit -m "Build SOFC health intelligence pipeline"
git remote add origin https://github.com/YOUR_USERNAME/sofc-health-intelligence.git
git push -u origin main
```

Use `git status` before committing. The source ZIP, extracted MATLAB files, Parquet tables, model
binaries, and generated experiment outputs must remain ignored.

Generated metrics will not be placed in the README until they can be reproduced from a tagged
commit. This repository is research software, not certified SOFC control or safety software.

## Licences

The code is MIT licensed. The source data remain under CC BY-NC 4.0 and are subject to the data
creator's attribution and non-commercial conditions.
