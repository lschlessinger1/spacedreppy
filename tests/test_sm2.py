import datetime

import pytest

from spacedreppy.schedulers.sm2 import SM2Scheduler, sm2
from spacedreppy.schedulers.spaced_repetition_scheduler import SpacedRepetitionScheduler


@pytest.fixture
def scheduler():
    return SM2Scheduler()


def test_sm2_return_types():
    interval, repetitions, easiness = sm2(quality=3, interval=2, repetitions=2, easiness=2)
    assert isinstance(interval, int)
    assert isinstance(repetitions, int)
    assert isinstance(easiness, float)


@pytest.mark.parametrize(
    "quality, expected_repetitions",
    [
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 1),
        (4, 1),
        (5, 1),
    ],
)
def test_sm2_update_once(quality, expected_repetitions):
    interval, repetitions, easiness = sm2(quality, interval=0, repetitions=0, easiness=2.5)
    assert interval == 1
    assert easiness == 2.5 + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    assert repetitions == expected_repetitions


@pytest.mark.parametrize(
    "qualities, expected_repetitions, expected_interval",
    [
        ((1, 2), 0, 1),
        ((2, 5), 1, 1),
        ((3, 2), 0, 1),
        ((4, 2), 0, 1),
        ((5, 3), 2, 6),
    ],
)
def test_sm2_update_params_twice(qualities, expected_repetitions, expected_interval):
    interval, repetitions, easiness = sm2(qualities[0], interval=0, repetitions=0, easiness=2.5)
    interval, repetitions, easiness = sm2(
        qualities[1], interval=interval, repetitions=repetitions, easiness=easiness
    )

    assert repetitions == expected_repetitions
    assert interval == expected_interval


@pytest.mark.parametrize(
    "qualities, expected_repetitions, expected_interval",
    [
        ((1, 2, 3), 1, 1),
        ((2, 5, 3), 2, 6),
        ((3, 2, 5), 1, 1),
        ((4, 3, 1), 0, 1),
        ((5, 3, 5), 3, 15),
    ],
)
def test_sm2_update_thrice(qualities, expected_repetitions, expected_interval):
    interval, repetitions, easiness = sm2(qualities[0], interval=0, repetitions=0, easiness=2.5)
    interval, repetitions, easiness = sm2(
        qualities[1], interval=interval, repetitions=repetitions, easiness=easiness
    )
    interval, repetitions, easiness = sm2(
        qualities[2], interval=interval, repetitions=repetitions, easiness=easiness
    )

    assert repetitions == expected_repetitions
    assert interval == expected_interval


def test_sm2_scheduler_initialization(scheduler):
    assert scheduler.interval == 0
    assert scheduler.repetitions == 0
    assert scheduler.easiness == 2.5
    assert scheduler.due_timestamp is None


@pytest.mark.parametrize(
    "quality, expected_repetitions",
    [
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 1),
        (4, 1),
        (5, 1),
    ],
)
def test_sm2_scheduler_compute_next_due_interval_once(scheduler, quality, expected_repetitions):
    attempted_at = datetime.datetime.now(datetime.timezone.utc)
    due_timestamp, interval = scheduler.compute_next_due_interval(
        attempted_at=attempted_at, result=quality
    )
    assert isinstance(due_timestamp, datetime.datetime)
    assert isinstance(interval, datetime.timedelta)
    assert due_timestamp == scheduler.due_timestamp
    assert interval == scheduler.interval_td
    assert interval == datetime.timedelta(days=1)
    assert scheduler.repetitions == expected_repetitions
    assert scheduler.easiness == 2.5 + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    assert scheduler.due_timestamp == attempted_at + datetime.timedelta(days=1)


@pytest.mark.parametrize(
    "qualities, expected_repetitions, expected_interval",
    [
        ((1, 2), 0, 1),
        ((2, 5), 1, 1),
        ((3, 2), 0, 1),
        ((4, 2), 0, 1),
        ((5, 3), 2, 6),
    ],
)
def test_sm2_scheduler_compute_next_due_interval_twice(
    scheduler, qualities, expected_repetitions, expected_interval
):
    attempted_at_1 = datetime.datetime(year=2021, month=10, day=13)
    attempted_at_2 = datetime.datetime(year=2021, month=10, day=15)
    due_timestamp_1, _interval_1 = scheduler.compute_next_due_interval(
        attempted_at=attempted_at_1, result=qualities[0]
    )
    due_timestamp_2, interval_2 = scheduler.compute_next_due_interval(
        attempted_at=attempted_at_2, result=qualities[1]
    )
    assert isinstance(due_timestamp_2, datetime.datetime)
    assert isinstance(interval_2, datetime.timedelta)
    assert due_timestamp_2 == scheduler.due_timestamp
    assert interval_2 == scheduler.interval_td
    assert interval_2 == datetime.timedelta(days=expected_interval)
    assert scheduler.repetitions == expected_repetitions
    assert scheduler.due_timestamp == due_timestamp_1 + datetime.timedelta(days=expected_interval)


@pytest.mark.parametrize(
    "qualities, expected_repetitions, expected_interval",
    [
        ((5, 3, 5), 3, 15),
        ((4, 4, 4), 3, 15),
        ((5, 5, 5), 3, 16),
        ((3, 3, 3), 3, 13),
        ((5, 5, 1), 0, 1),
    ],
)
def test_sm2_scheduler_compute_next_due_interval_thrice(
    scheduler, qualities, expected_repetitions, expected_interval
):
    """Regression test: ensures self.interval stays int across 3+ calls.

    Before the fix, self.interval was overwritten with a timedelta on
    the first call, causing a TypeError on the 3rd call when
    repetitions >= 2 and quality >= 3 (round(timedelta * float)).
    """
    attempted_at_1 = datetime.datetime(year=2021, month=10, day=13)
    attempted_at_2 = datetime.datetime(year=2021, month=10, day=14)
    attempted_at_3 = datetime.datetime(year=2021, month=10, day=15)
    scheduler.compute_next_due_interval(attempted_at=attempted_at_1, result=qualities[0])
    scheduler.compute_next_due_interval(attempted_at=attempted_at_2, result=qualities[1])
    due_timestamp_3, interval_3 = scheduler.compute_next_due_interval(
        attempted_at=attempted_at_3, result=qualities[2]
    )
    assert isinstance(due_timestamp_3, datetime.datetime)
    assert isinstance(interval_3, datetime.timedelta)
    assert interval_3 == datetime.timedelta(days=expected_interval)
    assert scheduler.repetitions == expected_repetitions
    assert isinstance(scheduler.interval, int)
    assert scheduler.interval == expected_interval


@pytest.mark.parametrize(
    "quality, interval, repetitions, easiness",
    [
        (-1, 0, 0, 2.5),
        (6, 0, 0, 2.5),
        (3, -1, 0, 2.5),
        (3, 0, -1, 2.5),
        (3, 0, 0, -0.1),
    ],
)
def test_sm2_invalid_inputs(quality, interval, repetitions, easiness):
    with pytest.raises(ValueError):
        sm2(quality=quality, interval=interval, repetitions=repetitions, easiness=easiness)


def test_spaced_repetition_scheduler_is_abstract():
    with pytest.raises(TypeError):
        SpacedRepetitionScheduler(interval=0)


def test_sm2_easiness_floor():
    """Easiness should never drop below 1.3, even with the worst quality."""
    _, _, easiness = sm2(quality=0, interval=0, repetitions=0, easiness=1.3)
    assert easiness == 1.3

    _, _, easiness = sm2(quality=0, interval=1, repetitions=1, easiness=1.4)
    assert easiness >= 1.3
