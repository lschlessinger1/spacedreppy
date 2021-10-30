# SpacedRepPy
A spaced repetition Python library.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `spacedreppy`.

```bash
pip install spacedreppy
```

## Usage

```python
from datetime import datetime
from spacedreppy.schedulers.sm2 import SM2Scheduler

# returns next due timestamp and next interval.
scheduler = SM2Scheduler()
due_timestamp, interval = scheduler.compute_next_due_interval(attempted_at=datetime.utcnow(), result=3)
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
