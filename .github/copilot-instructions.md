# Copilot Instructions for SpacedRepPy

## Project Overview

SpacedRepPy is a spaced repetition Python library implementing the SM-2 algorithm. It provides a scheduler abstraction (`SpacedRepetitionScheduler`) with a concrete SM-2 implementation (`SM2Scheduler`).

## Tech Stack

- **Language**: Python 3.11+
- **Build system**: Hatchling
- **Package/dependency manager**: [uv](https://docs.astral.sh/uv/)
- **Task runner**: [just](https://github.com/casey/just) (see `justfile`)
- **Linter/formatter**: [Ruff](https://docs.astral.sh/ruff/)
- **Type checker**: [mypy](https://mypy-lang.org/) (strict mode)
- **Testing**: pytest with pytest-cov
- **Security**: bandit
- **Pre-commit**: pre-commit hooks configured in `.pre-commit-config.yaml`

## Code Style & Conventions

- Follow [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) (enforced by Ruff's `D` rules).
- Use modern Python type syntax: `X | None` instead of `Optional[X]`, `list[T]` instead of `List[T]`, etc.
- Target Ruff's `py311` compatibility.
- Line length limit: 100 characters.
- All public functions and methods must have docstrings; tests are exempt.

## Architecture

- `spacedreppy/schedulers/spaced_repetition_scheduler.py` — Abstract base class defining the scheduler interface.
- `spacedreppy/schedulers/sm2.py` — SM-2 algorithm implementation and `SM2Scheduler` class.
- `tests/test_sm2.py` — Test suite using pytest with parametrized tests.

## Development Workflow

```bash
just install        # Install dependencies
just test           # Run tests with coverage
just codestyle      # Run formatters (ruff format + ruff check --fix)
just mypy           # Run mypy type checker
just lint           # Run all checks (tests + style + mypy + safety)
```

## Key Practices

- All code must pass mypy in strict mode (see `[tool.mypy]` in `pyproject.toml`).
- All code must pass ruff linting and formatting checks.
- Tests use `pytest.mark.parametrize` extensively — follow this pattern for new tests.
- Keep the SM-2 algorithm pure function (`sm2()`) separate from the scheduler class.
