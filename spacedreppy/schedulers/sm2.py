from datetime import datetime, timedelta

from spacedreppy.schedulers.spaced_repetition_scheduler import SpacedRepetitionScheduler


def sm2(quality: int, interval: int, repetitions: int, easiness: float) -> tuple[int, int, float]:
    """SuperMemo-2 Algorithm (SM-2).

    :param quality: a performance measure ranging 0 (complete blackout) to 5 (perfect response)
    :param interval: the number of consecutive correct answers (quality >= 3)
    :param repetitions: inter-repetition interval after the n-th repetition (in days)
    :param easiness: easiness factor reflecting the easiness of memorizing and retaining a given item in memory
    :return: the new interval, repetition number, and easiness
    Algorithm SM-2, (C) Copyright SuperMemo World, 1991.

    https://www.supermemo.com
    https://www.supermemo.eu
    """
    if quality < 3:  # Incorrect response.
        interval = 1
        repetitions = 0
    else:  # Correct response.
        # Set interval.
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * easiness)

        repetitions += 1

    # Set easiness.
    easiness += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    if easiness < 1.3:
        easiness = 1.3

    return interval, repetitions, easiness


class SM2Scheduler(SpacedRepetitionScheduler):
    def __init__(self, easiness: float = 2.5, interval: int = 0, repetitions: int = 0):
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
