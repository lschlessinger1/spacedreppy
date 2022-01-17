#* Variables
SHELL := /usr/bin/env bash
PYTHON := python

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) -

#* Installation
.PHONY: install
install:
	poetry lock -n && poetry export --without-hashes > requirements.txt
	poetry install -n

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

#* Linting
.PHONY: test
test:
	poetry run pytest -c pyproject.toml tests/ --cov-report=html --cov=spacedreppy

.PHONY: check-safety
check-safety:
	poetry check
	poetry run safety check --full-report
	poetry run bandit -ll --recursive spacedreppy tests

.PHONY: lint
lint: test check-safety
