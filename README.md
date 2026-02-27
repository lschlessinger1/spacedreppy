
# SpacedRepPy

[![Build status](https://github.com/lschlessinger1/spacedreppy/workflows/build/badge.svg?branch=main&event=push)](https://github.com/lschlessinger1/spacedreppy/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/spacedreppy.svg)](https://pypi.org/project/spacedreppy/)
[![License](https://img.shields.io/github/license/lschlessinger1/spacedreppy)](https://github.com/lschlessinger1/spacedreppy/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/lschlessinger1/spacedreppy/blob/main/.pre-commit-config.yaml)
![Coverage Report](assets/images/coverage.svg)

A spaced repetition Python library.

## Installation

Use [uv](https://docs.astral.sh/uv/) or [pip](https://pip.pypa.io/en/stable/) to install `spacedreppy`.

```bash
uv add spacedreppy
# or
pip install spacedreppy
```

## Usage

```python
from datetime import datetime, timezone
from spacedreppy import SM2Scheduler

scheduler = SM2Scheduler()

# Each call returns the next due timestamp and interval.
due_timestamp, interval = scheduler.compute_next_due_interval(
    attempted_at=datetime.now(timezone.utc), result=4
)
```

The `result` parameter is a quality score from the SM-2 algorithm:

| Score | Meaning |
|-------|---------|
| 0 | Complete blackout — no recall at all |
| 1 | Incorrect response, but the correct answer seemed easy to recall once seen |
| 2 | Incorrect response, but the correct answer was remembered upon seeing it |
| 3 | Correct response with serious difficulty |
| 4 | Correct response after some hesitation |
| 5 | Perfect response with no hesitation |

Scores of 3 or higher count as correct and advance the repetition schedule. Scores below 3 reset the interval.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [just](https://github.com/casey/just) as a command runner.

```bash
# Install dependencies
just install

# Run tests
just test

# Run formatters
just codestyle

# Run all linting (tests + style + mypy + safety)
just lint
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
