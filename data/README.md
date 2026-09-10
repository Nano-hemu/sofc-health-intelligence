# Data directory

| Directory | Contents | Git policy |
|---|---|---|
| `raw/` | Verified source ZIP and extracted MATLAB tables | ignored |
| `interim/` | Temporary transformations | ignored |
| `processed/` | Canonical Parquet, feature, target, manifest, and audit tables | ignored |

Rebuild everything with `sofc-health all`. Do not rename or manually edit source files. The raw
archive is governed by CC BY-NC 4.0; see `DATA_LICENSE.md` in the repository root.
