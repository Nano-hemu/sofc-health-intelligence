# GitHub release checklist

- [ ] Run `sofc-health all` from a clean environment.
- [ ] Run `ruff check .`, `mypy src`, and `pytest`.
- [ ] Restart and run every notebook in numerical order.
- [ ] Remove notebook execution noise and secrets.
- [ ] Export final figures with units, uncertainty, and readable legends.
- [ ] Populate the model card with out-of-fold results.
- [ ] Verify README commands on Windows Git Bash.
- [ ] Confirm raw/processed data and trained binaries are ignored.
- [ ] Add repository topics: `sofc`, `time-series`, `prognostics`, `eis`, `python`.
- [ ] Create a tagged release only after metrics reproduce from the tag.
