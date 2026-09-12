# Windows Git Bash setup

## Environment

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[analysis,ml,dev]"
```

If `py -3.12` is unavailable, install Python 3.12 and select “Add Python to PATH.” Do not use the
older NASA project's environment; isolation makes dependency failures reproducible.

## Build and inspect

```bash
sofc-health all
ruff check .
mypy src
pytest
jupyter lab
```

Run notebooks 01 through 09 in order. Stop when a validation contract fails; downstream plots are
not evidence if upstream data or split assumptions are invalid.

## GitHub

```bash
git init -b main
git add .
git status
git commit -m "Build SOFC health intelligence pipeline"
git remote add origin https://github.com/YOUR_USERNAME/sofc-health-intelligence.git
git push -u origin main
```

If the remote already exists, inspect it with `git remote -v` instead of adding a second origin.
Never force-push or upload the raw archive.
