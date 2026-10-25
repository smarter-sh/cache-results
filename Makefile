PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: init test coverage lint clean

# create the virtual environment, install the package with its test tools, and the git hooks.
init:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[test,redis]" pre-commit
	$(BIN)/pre-commit install

# set CACHE_RESULTS_TEST_REDIS_URL, e.g. to redis://localhost:6379/15, to test against Redis.
test:
	$(BIN)/python -m pytest

coverage:
	$(BIN)/coverage run -m pytest
	$(BIN)/coverage report
	$(BIN)/coverage xml

lint:
	$(BIN)/pre-commit run --all-files

clean:
	rm -rf build dist .pytest_cache .coverage coverage.xml htmlcov
	find . -name __pycache__ -type d -prune -not -path "./$(VENV)/*" -exec rm -rf {} +
