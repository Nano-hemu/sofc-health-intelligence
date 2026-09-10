.PHONY: install data audit baselines test lint typecheck

install:
	python -m pip install -e ".[analysis,ml,dev]"

data:
	sofc-health all

audit:
	sofc-health audit

baselines:
	python scripts/run_baselines.py

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy src
