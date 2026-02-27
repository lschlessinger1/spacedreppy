from datetime import datetime, timedelta

from spacedreppy.schedulers.spaced_repetition_scheduler import SpacedRepetitionScheduler

# SM-2 algorithm constants
MIN_QUALITY = 0
MAX_QUALITY = 5
CORRECT_QUALITY_THRESHOLD = 3
INITIAL_INTERVAL = 1
SECOND_INTERVAL = 6
MIN_EASINESS = 1.3
EASINESS_OFFSET = 0.1
EASINESS_LINEAR_COEFF = 0.08
EASINESS_QUADRATIC_COEFF = 0.02


def sm2(quality: int, interval: int, repetitions: int, easiness: float) -> tuple[int, int, float]:
    """SuperMemo-2 Algorithm (SM-2).

    Args:
        quality: A performance measure ranging 0 (complete blackout) to 5 (perfect response).
        interval: Inter-repetition interval after the n-th repetition (in days).
        repetitions: The number of consecutive correct answers (quality >= 3).
        easiness: Easiness factor reflecting the easiness of memorizing
            and retaining a given item in memory.

    Returns:
        The new interval, repetition number, and easiness.

    Raises:
        ValueError: If quality is not in [0, 5], or interval, repetitions,
            or easiness are negative.

    Algorithm SM-2, (C) Copyright SuperMemo World, 1991.

    https://www.supermemo.com
    https://www.supermemo.eu
    """
    if not MIN_QUALITY <= quality <= MAX_QUALITY:
        raise ValueError(f"quality must be between {MIN_QUALITY} and {MAX_QUALITY}, got {quality}")
    if interval < 0:
        raise ValueError(f"interval must be non-negative, got {interval}")
    if repetitions < 0:
        raise ValueError(f"repetitions must be non-negative, got {repetitions}")
    if easiness < 0:
        raise ValueError(f"easiness must be non-negative, got {easiness}")

    if quality < CORRECT_QUALITY_THRESHOLD:  # Incorrect response.
        interval = INITIAL_INTERVAL
        repetitions = 0
    else:  # Correct response.
        # Set interval.
        if repetitions == 0:
            interval = INITIAL_INTERVAL
        elif repetitions == 1:
            interval = SECOND_INTERVAL
        else:
            interval = round(interval * easiness)

        repetitions += 1

    # Set easiness.
    easiness += EASINESS_OFFSET - (MAX_QUALITY - quality) * (
        EASINESS_LINEAR_COEFF + (MAX_QUALITY - quality) * EASINESS_QUADRATIC_COEFF
    )
    if easiness < MIN_EASINESS:
        easiness = MIN_EASINESS

    return interval, repetitions, easiness


class SM2Scheduler(SpacedRepetitionScheduler):
    def __init__(self, easiness: float = 2.5, interval: int = 0, repetitions: int = 0) -> None:
        super().__init__(interval=interval)
        self.easiness = easiness
        self.repetitions = repetitions

    def _update_params(self, quality: int) -> None:
        interval, repetitions, easiness = sm2(
            quality, self.interval, self.repetitions, self.easiness
        )

        self.interval = interval
        self.repetitions = repetitions
        self.easiness = easiness

    def _compute_next_due_interval(
        self, attempted_at: datetime, result: int
    ) -> tuple[datetime, timedelta]:
        self._update_params(quality=result)
        new_timedelta_interval = timedelta(days=self.interval)
        prev_start_timestamp = self.due_timestamp if self.due_timestamp else attempted_at
        due_timestamp = prev_start_timestamp + new_timedelta_interval
        return due_timestamp, new_timedelta_interval
