import datetime

import pytest

from spacedreppy.schedulers.sm2 import SM2Scheduler, sm2


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
def test_SM2_update_params_twice(qualities, expected_repetitions, expected_interval):
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
def test_SM2_update_thrice(qualities, expected_repetitions, expected_interval):
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
    attempted_at = datetime.datetime.utcnow()
    due_timestamp, interval = scheduler.compute_next_due_interval(
        attempted_at=attempted_at, result=quality
    )
    assert isinstance(due_timestamp, datetime.datetime)
    assert isinstance(interval, datetime.timedelta)
    assert due_timestamp == scheduler.due_timestamp
    assert interval == scheduler.interval
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
    due_timestamp_1, interval_1 = scheduler.compute_next_due_interval(
        attempted_at=attempted_at_1, result=qualities[0]
    )
    due_timestamp_2, interval_2 = scheduler.compute_next_due_interval(
        attempted_at=attempted_at_2, result=qualities[1]
    )
    assert isinstance(due_timestamp_2, datetime.datetime)
    assert isinstance(interval_2, datetime.timedelta)
    assert due_timestamp_2 == scheduler.due_timestamp
    assert interval_2 == scheduler.interval
    assert interval_2 == datetime.timedelta(days=expected_interval)
    assert scheduler.repetitions == expected_repetitions
    assert scheduler.due_timestamp == due_timestamp_1 + datetime.timedelta(days=expected_interval)
