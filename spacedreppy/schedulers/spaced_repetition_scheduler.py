from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional


class SpacedRepetitionScheduler(ABC):
    def __init__(self, interval: int) -> None:
        self.interval = interval
        self.interval_td: Optional[timedelta] = None
        self.due_timestamp: Optional[datetime] = None

    def compute_next_due_interval(
        self, attempted_at: datetime, result: int
    ) -> tuple[datetime, timedelta]:
        """Calculate the next due timestamp and interval."""
        self.due_timestamp, self.interval_td = self._compute_next_due_interval(attempted_at, result)
        return self.due_timestamp, self.interval_td

    @abstractmethod
    def _compute_next_due_interval(
        self, attempted_at: datetime, result: int
    ) -> tuple[datetime, timedelta]:
        """Calculate the next due timestamp and interval."""
