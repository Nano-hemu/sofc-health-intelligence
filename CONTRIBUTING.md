# Contributing

1. Create a Python 3.12 environment and install `.[analysis,ml,dev]`.
2. Create a feature branch; do not commit raw data, generated Parquet files, or model binaries.
3. Add tests for every schema, feature, target, or split-rule change.
4. Run `ruff check .`, `mypy src`, and `pytest` before opening a pull request.
5. Explain the electrochemical assumption and leakage risk of analytical changes.
6. Update the data/model card when inputs, targets, exclusions, or intended use change.

Bug reports should include the command, operating system, Python version, traceback, and whether the
source archive checksum passed. Never attach licensed raw data to a public issue.
