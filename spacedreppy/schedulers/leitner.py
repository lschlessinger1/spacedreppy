"""Leitner system spaced repetition scheduler."""

from datetime import datetime, timedelta

from spacedreppy.schedulers.spaced_repetition_scheduler import SpacedRepetitionScheduler

# Leitner system constants
MIN_RESULT = 0
MAX_RESULT = 1
CORRECT_RESULT = 1
DEFAULT_INTERVALS: list[int] = [1, 3, 7, 14, 30]


def leitner(correct: bool, current_box: int, num_boxes: int) -> int:
    """Leitner system box promotion/demotion.

    Args:
        correct: Whether the answer was correct.
        current_box: The current box index (0-based).
        num_boxes: The total number of boxes.

    Returns:
        The new box index.

    Raises:
        ValueError: If num_boxes is not positive or current_box is out of range.
    """
    if num_boxes <= 0:
        raise ValueError(f"num_boxes must be positive, got {num_boxes}")
    if not 0 <= current_box < num_boxes:
        raise ValueError(f"current_box must be in [0, {num_boxes}), got {current_box}")

    if not correct:
        return 0

    return min(current_box + 1, num_boxes - 1)


class LeitnerScheduler(SpacedRepetitionScheduler):
    """Spaced repetition scheduler using the Leitner system.

    Args:
        intervals: Review intervals (in days) for each box. Defaults to [1, 3, 7, 14, 30].
        current_box: The current box index (0-based). Defaults to 0.
        interval: The current interval in days. Defaults to 0.
    """

    def __init__(
        self,
        intervals: list[int] | None = None,
        current_box: int = 0,
        interval: int = 0,
    ) -> None:
        super().__init__(interval=interval)
        self.intervals = intervals if intervals is not None else list(DEFAULT_INTERVALS)

        if not self.intervals:
            raise ValueError("intervals must not be empty")
        if any(i <= 0 for i in self.intervals):
            raise ValueError("all intervals must be positive")

        self.num_boxes = len(self.intervals)

        if not 0 <= current_box < self.num_boxes:
            raise ValueError(f"current_box must be in [0, {self.num_boxes}), got {current_box}")
        self.current_box = current_box

    def _update_params(self, result: int) -> None:
        """Update box and interval based on the result.

        Args:
            result: 1 for correct, 0 for incorrect.
        """
        if result not in (MIN_RESULT, MAX_RESULT):
            raise ValueError(f"result must be {MIN_RESULT} or {MAX_RESULT}, got {result}")
        correct = result == CORRECT_RESULT
        self.current_box = leitner(correct, self.current_box, self.num_boxes)
        self.interval = self.intervals[self.current_box]

    def _compute_next_due_interval(
        self, attempted_at: datetime, result: int
    ) -> tuple[datetime, timedelta]:
        """Calculate the next due timestamp and interval.

        Args:
            attempted_at: The timestamp of the attempt.
            result: 1 for correct, 0 for incorrect.

        Returns:
            A tuple of the next due timestamp and the interval timedelta.
        """
        self._update_params(result)
        new_timedelta_interval = timedelta(days=self.interval)
        prev_start_timestamp = self.due_timestamp if self.due_timestamp else attempted_at
        due_timestamp = prev_start_timestamp + new_timedelta_interval
        return due_timestamp, new_timedelta_interval
