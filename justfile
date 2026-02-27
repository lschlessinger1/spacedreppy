# Use Git Bash on Windows, default shell on Unix
# Git Bash shares Windows PATH, unlike WSL
set windows-shell := ["C:\\Program Files\\Git\\bin\\bash.exe", "-cu"]

# Show available recipes
default:
    @just --list

# Install dependencies and set up the project
install:
    uv sync
    -uv run mypy --install-types --non-interactive ./

# Install pre-commit hooks
pre-commit-install:
    uv run pre-commit install

# Run formatters
codestyle:
    uv run isort --settings-path pyproject.toml ./
    uv run black --config pyproject.toml ./
    uv run darglint --verbosity 2 spacedreppy tests

# Alias for codestyle
formatting: codestyle

# Run tests with coverage
test:
    uv run pytest -c pyproject.toml tests/ --cov-report=html --cov=spacedreppy
    uv run coverage-badge -o assets/images/coverage.svg -f

# Check code style without modifying
check-codestyle:
    uv run isort --diff --check-only --settings-path pyproject.toml ./
    uv run black --diff --check --config pyproject.toml ./

# Run mypy type checker
mypy:
    uv run mypy --config-file pyproject.toml ./

# Run safety and security checks
check-safety:
    uv run bandit -ll --recursive spacedreppy tests

# Run all linting: tests, codestyle, mypy, safety
lint: test check-codestyle mypy check-safety
