# Planned repository — completion map

This file is the repository contract. A checked item means the implementation file exists; it does
not mean final scientific claims have been approved.

## Repository and reproducibility

- [x] `README.md`, `LICENSE`, `DATA_LICENSE.md`, `CITATION.cff`
- [x] `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `environment.yml`
- [x] `Makefile`, `Dockerfile`, `.dockerignore`, `.pre-commit-config.yaml`
- [x] `.github/workflows/ci.yml`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`

## Data and configuration

- [x] `configs/base.yaml`
- [x] `configs/experiments/{baselines,ml,deep}.yaml`
- [x] `data/{raw,interim,processed}/` and `data/README.md`
- [x] Acquisition, safe extraction, MATLAB parsing, canonicalization, preparation, and audit modules

## Scientific code

- [x] EIS, IV, and transient feature extractors plus multimodal feature builder
- [x] Optional Lin-KK validity, declared equivalent-circuit, and DRT analysis interfaces
- [x] SOH candidates, geometric composite, threshold RUL, and censoring
- [x] Complete-cell and rolling-origin split utilities
- [x] Regression and interval metrics
- [x] Persistence, drift, damped trend, ETS, ARIMA, tabular ML, optional GRU
- [x] Split-conformal intervals, backtesting, modality ablations, and result persistence
- [x] Shared plotting API and reproducible scripts

## Guided notebooks

- [x] `01_data_audit.ipynb`
- [x] `02_physics_aware_eda.ipynb`
- [x] `03_soh_target_design.ipynb`
- [x] `04_feature_engineering.ipynb`
- [x] `05_statistical_baselines.ipynb`
- [x] `06_multimodal_ml.ipynb`
- [x] `07_rul_and_uncertainty.ipynb`
- [x] `08_eis_health_coupling.ipynb`
- [x] `09_ablation_and_portfolio_story.ipynb`
- [x] `notebooks/README.md` execution order and decision map

## Documentation and quality

- [x] Data card, architecture, mathematics, modeling strategy, experiment protocol
- [x] Model-card template, interview guide, GitHub release checklist, field-data extension plan
- [x] Unit tests for ingestion safety, schema repair, features, targets, splits, metrics, models

## Scientific execution status

The nine-notebook workflow has been executed and reviewed. Final model selection is horizon
specific, cross-regime transfer is rejected, exact 80% SOH RUL remains unidentifiable because all
cells are right-censored, and the verified portfolio claims are recorded in Notebook 09. These
results describe an offline laboratory study, not a field-validated deployment model.
