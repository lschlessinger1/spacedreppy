import datetime

import pytest

from spacedreppy.schedulers.fsrs import (
    AGAIN,
    DEFAULT_MAXIMUM_INTERVAL,
    DEFAULT_REQUEST_RETENTION,
    DEFAULT_WEIGHTS,
    EASY,
    GOOD,
    HARD,
    FSRSScheduler,
    fsrs,
)
from spacedreppy.schedulers.spaced_repetition_scheduler import SpacedRepetitionScheduler


@pytest.fixture
def scheduler() -> FSRSScheduler:
    return FSRSScheduler()


def test_fsrs_return_types():
    stability, difficulty, interval = fsrs(rating=GOOD, stability=0, difficulty=0, elapsed_days=0)
    assert isinstance(stability, float)
    assert isinstance(difficulty, float)
    assert isinstance(interval, int)


@pytest.mark.parametrize(
    "rating, expected_stability, expected_difficulty, expected_interval",
    [
        (AGAIN, 0.212, 6.4133, 1),
        (HARD, 1.2931, 5.112170705601055, 1),
        (GOOD, 2.3065, 2.118103970459015, 2),
        (EASY, 8.2956, 1.0, 8),
    ],
)
def test_fsrs_new_card(
    rating: int,
    expected_stability: float,
    expected_difficulty: float,
    expected_interval: int,
) -> None:
    stability, difficulty, interval = fsrs(rating=rating, stability=0, difficulty=0, elapsed_days=0)
    assert stability == pytest.approx(expected_stability)
    assert difficulty == pytest.approx(expected_difficulty)
    assert interval == expected_interval


@pytest.mark.parametrize(
    "rating, elapsed_days, expected_stability, expected_difficulty, expected_interval",
    [
        # New Good -> 2d Good
        (GOOD, 2, 10.964332335820703, 2.1169858664885557, 11),
        # New Good -> 2d Again (forget path)
        (AGAIN, 2, 0.6075801062519337, 7.40027437198288, 1),
    ],
)
def test_fsrs_review_after_new_good(
    rating: int,
    elapsed_days: int,
    expected_stability: float,
    expected_difficulty: float,
    expected_interval: int,
) -> None:
    # First: new card with Good
    s0 = 2.3065
    d0 = 2.118103970459015
    stability, difficulty, interval = fsrs(
        rating=rating, stability=s0, difficulty=d0, elapsed_days=elapsed_days
    )
    assert stability == pytest.approx(expected_stability)
    assert difficulty == pytest.approx(expected_difficulty)
    assert interval == expected_interval


def test_fsrs_review_after_new_easy_hard():
    # New Easy -> 8d Hard
    s0, d0 = 8.2956, 1.0
    stability, difficulty, interval = fsrs(rating=HARD, stability=s0, difficulty=d0, elapsed_days=8)
    assert stability == pytest.approx(26.704183359371367)
    assert difficulty == pytest.approx(4.016380600000001)
    assert interval == 27


def test_fsrs_same_day_review():
    # New Again -> same-day Good
    s0, d0 = 0.212, 6.4133
    stability, difficulty, interval = fsrs(rating=GOOD, stability=s0, difficulty=d0, elapsed_days=0)
    assert stability == pytest.approx(0.24668918777567272)
    assert difficulty == pytest.approx(6.4078867)
    assert interval == 1


@pytest.mark.parametrize(
    "rating, expected_stability",
    [
        (AGAIN, 0.08335671711031603),
        (HARD, 0.14339874769184835),
        (GOOD, 0.24668918777567272),
        (EASY, 0.42437996387663374),
    ],
)
def test_fsrs_same_day_all_ratings(rating: int, expected_stability: float) -> None:
    s0, d0 = 0.212, 6.4133
    stability, _difficulty, _interval = fsrs(
        rating=rating, stability=s0, difficulty=d0, elapsed_days=0
    )
    assert stability == pytest.approx(expected_stability)


def test_fsrs_three_step_sequence():
    # New Good -> 2d Good -> 11d Easy
    s, d, _ = fsrs(rating=GOOD, stability=0, difficulty=0, elapsed_days=0)
    s, d, _ = fsrs(rating=GOOD, stability=s, difficulty=d, elapsed_days=2)
    s, d, ivl = fsrs(rating=EASY, stability=s, difficulty=d, elapsed_days=11)
    assert s == pytest.approx(77.06450547606927)
    assert d == pytest.approx(1.0)
    assert ivl == 77


def test_fsrs_difficulty_clamped_at_max():
    # Repeated Again ratings should push difficulty towards max but never exceed 10
    s, d, _ = fsrs(rating=AGAIN, stability=0, difficulty=0, elapsed_days=0)
    for _ in range(20):
        s, d, _ = fsrs(rating=AGAIN, stability=s, difficulty=d, elapsed_days=0)
    assert d <= 10.0
    assert d >= 1.0


def test_fsrs_difficulty_clamped_at_min():
    # Repeated Easy ratings should push difficulty towards min but never below 1
    s, d, _ = fsrs(rating=EASY, stability=0, difficulty=0, elapsed_days=0)
    assert d == 1.0
    for _ in range(20):
        s, d, _ = fsrs(rating=EASY, stability=s, difficulty=d, elapsed_days=0)
    assert d >= 1.0


def test_fsrs_interval_clamped_to_maximum():
    _stability, _, interval = fsrs(
        rating=GOOD, stability=0, difficulty=0, elapsed_days=0, maximum_interval=1
    )
    assert interval == 1


def test_fsrs_interval_at_least_one():
    _stability, _, interval = fsrs(rating=AGAIN, stability=0, difficulty=0, elapsed_days=0)
    assert interval >= 1


@pytest.mark.parametrize(
    "rating, stability, difficulty, elapsed_days",
    [
        (0, 0, 0, 0),  # rating too low
        (5, 0, 0, 0),  # rating too high
        (GOOD, -1, 0, 0),  # negative stability
        (GOOD, 0, 0, -1),  # negative elapsed_days
    ],
)
def test_fsrs_invalid_inputs(
    rating: int, stability: float, difficulty: float, elapsed_days: float
) -> None:
    with pytest.raises(ValueError):
        fsrs(
            rating=rating,
            stability=stability,
            difficulty=difficulty,
            elapsed_days=elapsed_days,
        )


def test_fsrs_invalid_weights_length():
    with pytest.raises(ValueError, match="weights must have 21 elements"):
        fsrs(rating=GOOD, stability=0, difficulty=0, elapsed_days=0, weights=(1.0, 2.0))


def test_fsrs_invalid_request_retention():
    with pytest.raises(ValueError, match="request_retention"):
        fsrs(rating=GOOD, stability=0, difficulty=0, elapsed_days=0, request_retention=0.0)
    with pytest.raises(ValueError, match="request_retention"):
        fsrs(rating=GOOD, stability=0, difficulty=0, elapsed_days=0, request_retention=1.0)


def test_fsrs_invalid_maximum_interval():
    with pytest.raises(ValueError, match="maximum_interval"):
        fsrs(rating=GOOD, stability=0, difficulty=0, elapsed_days=0, maximum_interval=0)


# --- FSRSScheduler tests ---


def test_scheduler_is_spaced_repetition_scheduler(scheduler: FSRSScheduler) -> None:
    assert isinstance(scheduler, SpacedRepetitionScheduler)


def test_scheduler_initialization_defaults(scheduler: FSRSScheduler) -> None:
    assert scheduler.stability == 0.0
    assert scheduler.difficulty == 0.0
    assert scheduler.interval == 0
    assert scheduler.weights == DEFAULT_WEIGHTS
    assert scheduler.request_retention == DEFAULT_REQUEST_RETENTION
    assert scheduler.maximum_interval == DEFAULT_MAXIMUM_INTERVAL
    assert scheduler.due_timestamp is None
    assert scheduler.last_review_at is None


def test_scheduler_custom_weights():
    custom_w = tuple(float(i) for i in range(21))
    s = FSRSScheduler(weights=custom_w)
    assert s.weights == custom_w


@pytest.mark.parametrize(
    "rating, expected_stability, expected_difficulty, expected_interval",
    [
        (AGAIN, 0.212, 6.4133, 1),
        (HARD, 1.2931, 5.112170705601055, 1),
        (GOOD, 2.3065, 2.118103970459015, 2),
        (EASY, 8.2956, 1.0, 8),
    ],
)
def test_scheduler_compute_next_due_interval_once(
    scheduler: FSRSScheduler,
    rating: int,
    expected_stability: float,
    expected_difficulty: float,
    expected_interval: int,
) -> None:
    attempted_at = datetime.datetime.now(datetime.UTC)
    due_timestamp, interval_td = scheduler.compute_next_due_interval(
        attempted_at=attempted_at, result=rating
    )
    assert isinstance(due_timestamp, datetime.datetime)
    assert isinstance(interval_td, datetime.timedelta)
    assert due_timestamp == scheduler.due_timestamp
    assert interval_td == scheduler.interval_td
    assert interval_td == datetime.timedelta(days=expected_interval)
    assert scheduler.stability == pytest.approx(expected_stability)
    assert scheduler.difficulty == pytest.approx(expected_difficulty)
    assert scheduler.due_timestamp == attempted_at + datetime.timedelta(days=expected_interval)
    assert scheduler.last_review_at == attempted_at


def test_scheduler_compute_next_due_interval_twice(scheduler: FSRSScheduler) -> None:
    attempted_at_1 = datetime.datetime(year=2025, month=1, day=1, tzinfo=datetime.UTC)
    attempted_at_2 = datetime.datetime(year=2025, month=1, day=3, tzinfo=datetime.UTC)

    due_1, _ = scheduler.compute_next_due_interval(attempted_at=attempted_at_1, result=GOOD)
    due_2, interval_2 = scheduler.compute_next_due_interval(
        attempted_at=attempted_at_2, result=GOOD
    )

    assert isinstance(due_2, datetime.datetime)
    assert isinstance(interval_2, datetime.timedelta)
    assert scheduler.stability == pytest.approx(10.964332335820703)
    assert scheduler.difficulty == pytest.approx(2.1169858664885557)
    assert interval_2 == datetime.timedelta(days=11)
    assert scheduler.due_timestamp == due_1 + datetime.timedelta(days=11)


def test_scheduler_compute_next_due_interval_thrice(scheduler: FSRSScheduler) -> None:
    at1 = datetime.datetime(year=2025, month=1, day=1, tzinfo=datetime.UTC)
    at2 = datetime.datetime(year=2025, month=1, day=3, tzinfo=datetime.UTC)
    at3 = datetime.datetime(year=2025, month=1, day=14, tzinfo=datetime.UTC)

    scheduler.compute_next_due_interval(attempted_at=at1, result=GOOD)
    scheduler.compute_next_due_interval(attempted_at=at2, result=GOOD)
    due_3, interval_3 = scheduler.compute_next_due_interval(attempted_at=at3, result=EASY)

    assert isinstance(due_3, datetime.datetime)
    assert isinstance(interval_3, datetime.timedelta)
    assert scheduler.stability == pytest.approx(77.06450547606927)
    assert scheduler.difficulty == pytest.approx(1.0)
    assert interval_3 == datetime.timedelta(days=77)
    assert isinstance(scheduler.interval, int)


def test_scheduler_forget_path(scheduler: FSRSScheduler) -> None:
    at1 = datetime.datetime(year=2025, month=1, day=1, tzinfo=datetime.UTC)
    at2 = datetime.datetime(year=2025, month=1, day=3, tzinfo=datetime.UTC)

    scheduler.compute_next_due_interval(attempted_at=at1, result=GOOD)
    scheduler.compute_next_due_interval(attempted_at=at2, result=AGAIN)

    assert scheduler.stability == pytest.approx(0.6075801062519337)
    assert scheduler.difficulty == pytest.approx(7.40027437198288)
    assert scheduler.interval == 1
