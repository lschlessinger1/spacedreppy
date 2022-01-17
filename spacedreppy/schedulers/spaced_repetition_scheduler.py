from typing import Optional, Tuple

from datetime import datetime, timedelta


class SpacedRepetitionScheduler:
    def __init__(self, interval):
        self.interval = interval
        self.due_timestamp: Optional[datetime] = None

    def compute_next_due_interval(
        self, attempted_at: datetime, result
    ) -> Tuple[datetime, timedelta]:
        """Calculate the next due timestamp and interval."""
        self.due_timestamp, self.interval = self._compute_next_due_interval(attempted_at, result)
        return self.due_timestamp, self.interval

    def _compute_next_due_interval(
        self, attempted_at: datetime, result
    ) -> Tuple[datetime, timedelta]:
        """Calculate the next due timestamp and interval."""
        raise NotImplementedError
