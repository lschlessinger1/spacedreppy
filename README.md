
# SpacedRepPy

<div style="text-align: center">

[![Build status](https://github.com/lschlessinger1/spacedreppy/workflows/build/badge.svg?branch=main&event=push)](https://github.com/lschlessinger1/spacedreppy/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/spacedreppy.svg)](https://pypi.org/project/spacedreppy/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/lschlessinger1/spacedreppy/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/lschlessinger1/spacedreppy/blob/main/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/lschlessinger1/spacedreppy/releases)
[![License](https://img.shields.io/github/license/lschlessinger1/spacedreppy)](https://github.com/lschlessinger1/spacedreppy/blob/main/LICENSE)
![Coverage Report](assets/images/coverage.svg)

A spaced repetition Python library.

</div>

## Installation

Use [uv](https://docs.astral.sh/uv/) or [pip](https://pip.pypa.io/en/stable/) to install `spacedreppy`.

```bash
uv add spacedreppy
# or
pip install spacedreppy
```

## Usage

```python
from datetime import datetime
from spacedreppy.schedulers.sm2 import SM2Scheduler

# returns next due timestamp and next interval.
scheduler = SM2Scheduler()
due_timestamp, interval = scheduler.compute_next_due_interval(
    attempted_at=datetime.utcnow(), result=3
)
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
