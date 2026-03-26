# SpacedRepPy

A spaced repetition Python library implementing SM-2 and Leitner scheduling algorithms.

## Project Structure

- `spacedreppy/schedulers/` - Core scheduler implementations (SM-2, Leitner, base class)
- `tests/` - Test files (`test_sm2.py`, `test_leitner.py`)
- `justfile` - Task runner commands
- `pyproject.toml` - Project config, linting, typing, and test settings

## Development

- **Package manager**: uv
- **Task runner**: just
- **Python**: >=3.11

### Common Commands

```bash
just install        # Install dependencies
just test           # Run tests with coverage
just codestyle      # Run ruff format + fix
just check-codestyle # Check style without modifying
just mypy           # Type checking
just check-safety   # Security checks (bandit)
just lint           # All checks: test + style + mypy + safety
```

## Code Style

- Formatter/linter: ruff (line length 100, target py311)
- Docstrings: Google convention (pydocstyle)
- Type checking: mypy (strict mode)
- Pre-commit hooks enabled
