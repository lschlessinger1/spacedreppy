import datetime

import pytest

from spacedreppy.schedulers.leitner import (
    DEFAULT_INTERVALS,
    LeitnerScheduler,
    leitner,
)
from spacedreppy.schedulers.spaced_repetition_scheduler import SpacedRepetitionScheduler


@pytest.fixture
def scheduler() -> LeitnerScheduler:
    return LeitnerScheduler()


def test_leitner_return_type():
    result = leitner(correct=True, current_box=0, num_boxes=5)
    assert isinstance(result, int)


@pytest.mark.parametrize(
    "current_box, expected_box",
    [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
    ],
)
def test_leitner_correct_promotes(current_box: int, expected_box: int) -> None:
    assert leitner(correct=True, current_box=current_box, num_boxes=5) == expected_box


def test_leitner_correct_at_max_box_stays():
    assert leitner(correct=True, current_box=4, num_boxes=5) == 4


@pytest.mark.parametrize("current_box", [0, 1, 2, 3, 4])
def test_leitner_incorrect_demotes_to_zero(current_box: int) -> None:
    assert leitner(correct=False, current_box=current_box, num_boxes=5) == 0


def test_leitner_invalid_num_boxes_zero():
    with pytest.raises(ValueError, match="num_boxes must be positive"):
        leitner(correct=True, current_box=0, num_boxes=0)


def test_leitner_invalid_num_boxes_negative():
    with pytest.raises(ValueError, match="num_boxes must be positive"):
        leitner(correct=True, current_box=0, num_boxes=-1)


def test_leitner_invalid_current_box_negative():
    with pytest.raises(ValueError, match="current_box must be in"):
        leitner(correct=True, current_box=-1, num_boxes=5)


def test_leitner_invalid_current_box_too_large():
    with pytest.raises(ValueError, match="current_box must be in"):
        leitner(correct=True, current_box=5, num_boxes=5)


def test_leitner_single_box():
    assert leitner(correct=True, current_box=0, num_boxes=1) == 0
    assert leitner(correct=False, current_box=0, num_boxes=1) == 0


# --- LeitnerScheduler tests ---


def test_scheduler_is_spaced_repetition_scheduler(scheduler: LeitnerScheduler) -> None:
    assert isinstance(scheduler, SpacedRepetitionScheduler)


def test_scheduler_initialization_defaults(scheduler: LeitnerScheduler) -> None:
    assert scheduler.current_box == 0
    assert scheduler.interval == 0
    assert scheduler.intervals == DEFAULT_INTERVALS
    assert scheduler.num_boxes == 5
    assert scheduler.due_timestamp is None


def test_scheduler_custom_intervals():
    s = LeitnerScheduler(intervals=[2, 5, 10])
    assert s.intervals == [2, 5, 10]
    assert s.num_boxes == 3


def test_scheduler_empty_intervals_raises():
    with pytest.raises(ValueError, match="intervals must not be empty"):
        LeitnerScheduler(intervals=[])


def test_scheduler_non_positive_intervals_raises():
    with pytest.raises(ValueError, match="all intervals must be positive"):
        LeitnerScheduler(intervals=[1, 0, 3])


def test_scheduler_invalid_current_box_raises():
    with pytest.raises(ValueError, match="current_box must be in"):
        LeitnerScheduler(current_box=5)


def test_scheduler_invalid_current_box_negative_raises():
    with pytest.raises(ValueError, match="current_box must be in"):
        LeitnerScheduler(current_box=-1)


@pytest.mark.parametrize("invalid_result", [-1, 2, 5, 999])
def test_scheduler_invalid_result_raises(scheduler: LeitnerScheduler, invalid_result: int) -> None:
    attempted_at = datetime.datetime.now(datetime.UTC)
    with pytest.raises(ValueError, match="result must be"):
        scheduler.compute_next_due_interval(attempted_at=attempted_at, result=invalid_result)


@pytest.mark.parametrize(
    "result, expected_box, expected_interval_days",
    [
        (1, 1, 3),
        (0, 0, 1),
    ],
)
def test_scheduler_compute_next_due_interval_once(
    scheduler: LeitnerScheduler,
    result: int,
    expected_box: int,
    expected_interval_days: int,
) -> None:
    attempted_at = datetime.datetime.now(datetime.UTC)
    due_timestamp, interval_td = scheduler.compute_next_due_interval(
        attempted_at=attempted_at, result=result
    )
    assert isinstance(due_timestamp, datetime.datetime)
    assert isinstance(interval_td, datetime.timedelta)
    assert due_timestamp == scheduler.due_timestamp
    assert interval_td == scheduler.interval_td
    assert interval_td == datetime.timedelta(days=expected_interval_days)
    assert scheduler.current_box == expected_box
    assert scheduler.due_timestamp == attempted_at + datetime.timedelta(days=expected_interval_days)


@pytest.mark.parametrize(
    "results, expected_box, expected_interval_days",
    [
        ((1, 1), 2, 7),
        ((1, 0), 0, 1),
        ((0, 1), 1, 3),
        ((0, 0), 0, 1),
    ],
)
def test_scheduler_compute_next_due_interval_twice(
    scheduler: LeitnerScheduler,
    results: tuple[int, int],
    expected_box: int,
    expected_interval_days: int,
) -> None:
    attempted_at_1 = datetime.datetime(year=2021, month=10, day=13)
    attempted_at_2 = datetime.datetime(year=2021, month=10, day=15)
    due_timestamp_1, _ = scheduler.compute_next_due_interval(
        attempted_at=attempted_at_1, result=results[0]
    )
    due_timestamp_2, interval_td_2 = scheduler.compute_next_due_interval(
        attempted_at=attempted_at_2, result=results[1]
    )
    assert isinstance(due_timestamp_2, datetime.datetime)
    assert isinstance(interval_td_2, datetime.timedelta)
    assert interval_td_2 == datetime.timedelta(days=expected_interval_days)
    assert scheduler.current_box == expected_box
    assert scheduler.due_timestamp == due_timestamp_1 + datetime.timedelta(
        days=expected_interval_days
    )


@pytest.mark.parametrize(
    "results, expected_box, expected_interval_days",
    [
        ((1, 1, 1), 3, 14),
        ((1, 1, 0), 0, 1),
        ((1, 0, 1), 1, 3),
        ((0, 0, 0), 0, 1),
        ((1, 1, 1, 1), 4, 30),
        ((1, 1, 1, 1, 1), 4, 30),  # stays at max box
        ((1, 1, 1, 1, 0), 0, 1),  # demoted from max box
    ],
)
def test_scheduler_compute_next_due_interval_multiple(
    scheduler: LeitnerScheduler,
    results: tuple[int, ...],
    expected_box: int,
    expected_interval_days: int,
) -> None:
    attempted_at = datetime.datetime(year=2021, month=10, day=1)
    for result in results:
        scheduler.compute_next_due_interval(attempted_at=attempted_at, result=result)
    assert scheduler.current_box == expected_box
    assert scheduler.interval == expected_interval_days


def test_scheduler_custom_intervals_review():
    s = LeitnerScheduler(intervals=[2, 5, 10])
    attempted_at = datetime.datetime(year=2021, month=10, day=1)

    s.compute_next_due_interval(attempted_at=attempted_at, result=1)
    assert s.current_box == 1
    assert s.interval == 5

    s.compute_next_due_interval(attempted_at=attempted_at, result=1)
    assert s.current_box == 2
    assert s.interval == 10

    s.compute_next_due_interval(attempted_at=attempted_at, result=1)
    assert s.current_box == 2  # stays at max
    assert s.interval == 10

    s.compute_next_due_interval(attempted_at=attempted_at, result=0)
    assert s.current_box == 0
    assert s.interval == 2
