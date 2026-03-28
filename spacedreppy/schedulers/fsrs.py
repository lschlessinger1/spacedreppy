"""FSRS-6 (Free Spaced Repetition Scheduler) implementation.

Implements the FSRS-6 algorithm which models memory with two state variables —
Stability (S) and Difficulty (D) — using a power-law forgetting curve with
21 trainable parameters.

Reference: https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta

from spacedreppy.schedulers.spaced_repetition_scheduler import SpacedRepetitionScheduler

# Rating constants
AGAIN = 1
HARD = 2
GOOD = 3
EASY = 4
MIN_RATING = AGAIN
MAX_RATING = EASY

# Algorithm constants
NUM_WEIGHTS = 21
MIN_DIFFICULTY = 1.0
MAX_DIFFICULTY = 10.0
MIN_STABILITY = 0.1

# Default FSRS-6 parameters (21 weights)
DEFAULT_WEIGHTS: tuple[float, ...] = (
    0.212,
    1.2931,
    2.3065,
    8.2956,
    6.4133,
    0.8334,
    3.0194,
    0.001,
    1.8722,
    0.1666,
    0.796,
    1.4835,
    0.0614,
    0.2629,
    1.6483,
    0.6014,
    1.8729,
    0.5425,
    0.0912,
    0.0658,
    0.1542,
)

DEFAULT_REQUEST_RETENTION = 0.9
DEFAULT_MAXIMUM_INTERVAL = 36500


def _constrain_difficulty(d: float) -> float:
    return min(max(d, MIN_DIFFICULTY), MAX_DIFFICULTY)


def _initial_stability(rating: int, w: tuple[float, ...]) -> float:
    """S0(G) = max(w[G-1], 0.1)."""
    return max(w[rating - 1], MIN_STABILITY)


def _initial_difficulty(rating: int, w: tuple[float, ...]) -> float:
    """D0(G) = w[4] - exp(w[5] * (G - 1)) + 1, constrained to [1, 10]."""
    return _constrain_difficulty(w[4] - math.exp(w[5] * (rating - 1)) + 1)


def _forgetting_curve(elapsed_days: float, stability: float, decay: float, factor: float) -> float:
    """R(t, S) = (1 + factor * t / S) ^ decay."""
    return float((1 + factor * elapsed_days / stability) ** decay)


def _linear_damping(delta_d: float, old_d: float) -> float:
    return delta_d * (MAX_DIFFICULTY - old_d) / 9


def _mean_reversion(init: float, current: float, w7: float) -> float:
    return w7 * init + (1 - w7) * current


def _next_difficulty(d: float, rating: int, w: tuple[float, ...]) -> float:
    """Compute new difficulty after review with linear damping and mean reversion."""
    delta_d = -w[6] * (rating - 3)
    next_d = d + _linear_damping(delta_d, d)
    # Mean reversion towards D0(4) (Easy) in FSRS-5+
    d0_easy = _initial_difficulty(EASY, w)
    return _constrain_difficulty(_mean_reversion(d0_easy, next_d, w[7]))


def _next_recall_stability(
    d: float, s: float, r: float, rating: int, w: tuple[float, ...]
) -> float:
    """S'r — new stability after successful recall (Hard, Good, or Easy)."""
    hard_penalty = w[15] if rating == HARD else 1.0
    easy_bonus = w[16] if rating == EASY else 1.0
    return float(
        s
        * (
            1
            + math.exp(w[8])
            * (11 - d)
            * s ** (-w[9])
            * (math.exp((1 - r) * w[10]) - 1)
            * hard_penalty
            * easy_bonus
        )
    )


def _next_forget_stability(d: float, s: float, r: float, w: tuple[float, ...]) -> float:
    """S'f — new stability after forgetting (Again), capped at s_min."""
    s_min = s / math.exp(w[17] * w[18])
    return float(
        min(
            w[11] * d ** (-w[12]) * ((s + 1) ** w[13] - 1) * math.exp((1 - r) * w[14]),
            s_min,
        )
    )


def _next_short_term_stability(s: float, rating: int, w: tuple[float, ...]) -> float:
    """S'(S, G) for same-day reviews.

    S' = S * e^(w17 * (G - 3 + w18)) * S^(-w19),
    with SInc >= 1 when G >= 3.
    """
    s_inc = math.exp(w[17] * (rating - 3 + w[18])) * s ** (-w[19])
    if rating >= GOOD:
        s_inc = max(s_inc, 1.0)
    return float(s * s_inc)


def _next_interval(
    stability: float,
    request_retention: float,
    maximum_interval: int,
    decay: float,
    factor: float,
) -> int:
    """I(r, S) = S / factor * (r^(1/decay) - 1), clamped to [1, maximum_interval]."""
    ivl = stability / factor * (request_retention ** (1 / decay) - 1)
    return int(min(max(round(ivl), 1), maximum_interval))


def fsrs(
    rating: int,
    stability: float,
    difficulty: float,
    elapsed_days: float,
    weights: tuple[float, ...] = DEFAULT_WEIGHTS,
    request_retention: float = DEFAULT_REQUEST_RETENTION,
    maximum_interval: int = DEFAULT_MAXIMUM_INTERVAL,
) -> tuple[float, float, int]:
    """FSRS-6 algorithm.

    Computes new memory states and the next review interval based on the rating.
    Handles three scenarios based on current state:
    - New card (stability == 0): initializes stability and difficulty.
    - Same-day review (elapsed_days == 0, stability > 0): short-term stability update.
    - Regular review (elapsed_days > 0, stability > 0): full stability/difficulty update.

    Args:
        rating: A grade from 1 (Again) to 4 (Easy).
        stability: Current memory stability in days (0 for new cards).
        difficulty: Current difficulty in [1, 10] (0 for new cards).
        elapsed_days: Days since last review (0 for new or same-day reviews).
        weights: Tuple of 21 FSRS-6 model weights.
        request_retention: Target retention probability (0 < r < 1).
        maximum_interval: Maximum allowed interval in days.

    Returns:
        A tuple of (new_stability, new_difficulty, interval_days).

    Raises:
        ValueError: If any input is out of valid range.
    """
    if not MIN_RATING <= rating <= MAX_RATING:
        raise ValueError(f"rating must be between {MIN_RATING} and {MAX_RATING}, got {rating}")
    if stability < 0:
        raise ValueError(f"stability must be non-negative, got {stability}")
    if elapsed_days < 0:
        raise ValueError(f"elapsed_days must be non-negative, got {elapsed_days}")
    if len(weights) != NUM_WEIGHTS:
        raise ValueError(f"weights must have {NUM_WEIGHTS} elements, got {len(weights)}")
    if not 0 < request_retention < 1:
        raise ValueError(
            f"request_retention must be between 0 and 1 exclusive, got {request_retention}"
        )
    if maximum_interval <= 0:
        raise ValueError(f"maximum_interval must be positive, got {maximum_interval}")

    w = weights
    decay = -w[20]
    factor = 0.9 ** (1 / decay) - 1

    if stability == 0:
        # New card
        new_s = _initial_stability(rating, w)
        new_d = _initial_difficulty(rating, w)
    elif elapsed_days == 0:
        # Same-day review
        new_s = _next_short_term_stability(stability, rating, w)
        new_d = _next_difficulty(difficulty, rating, w)
    else:
        # Regular review
        r = _forgetting_curve(elapsed_days, stability, decay, factor)
        new_d = _next_difficulty(difficulty, rating, w)
        if rating == AGAIN:
            new_s = _next_forget_stability(difficulty, stability, r, w)
        else:
            new_s = _next_recall_stability(difficulty, stability, r, rating, w)

    interval = _next_interval(new_s, request_retention, maximum_interval, decay, factor)
    return new_s, new_d, interval


class FSRSScheduler(SpacedRepetitionScheduler):
    """Spaced repetition scheduler using the FSRS-6 algorithm.

    Args:
        stability: Current memory stability in days. Defaults to 0 (new card).
        difficulty: Current difficulty. Defaults to 0 (new card).
        weights: Tuple of 21 FSRS-6 model weights.
        request_retention: Target retention probability. Defaults to 0.9.
        maximum_interval: Maximum allowed interval in days. Defaults to 36500.
        interval: The current interval in days. Defaults to 0.
    """

    def __init__(
        self,
        stability: float = 0.0,
        difficulty: float = 0.0,
        weights: tuple[float, ...] = DEFAULT_WEIGHTS,
        request_retention: float = DEFAULT_REQUEST_RETENTION,
        maximum_interval: int = DEFAULT_MAXIMUM_INTERVAL,
        interval: int = 0,
    ) -> None:
        super().__init__(interval=interval)
        self.stability = stability
        self.difficulty = difficulty
        self.weights = weights
        self.request_retention = request_retention
        self.maximum_interval = maximum_interval
        self.last_review_at: datetime | None = None

    def _compute_next_due_interval(
        self, attempted_at: datetime, result: int
    ) -> tuple[datetime, timedelta]:
        """Calculate the next due timestamp and interval.

        Args:
            attempted_at: The timestamp of the review attempt.
            result: Rating from 1 (Again) to 4 (Easy).

        Returns:
            A tuple of the next due timestamp and the interval timedelta.
        """
        if self.last_review_at is not None:
            elapsed_days = max((attempted_at - self.last_review_at).days, 0)
        else:
            elapsed_days = 0

        new_s, new_d, interval_days = fsrs(
            rating=result,
            stability=self.stability,
            difficulty=self.difficulty,
            elapsed_days=elapsed_days,
            weights=self.weights,
            request_retention=self.request_retention,
            maximum_interval=self.maximum_interval,
        )

        self.stability = new_s
        self.difficulty = new_d
        self.interval = interval_days
        self.last_review_at = attempted_at

        new_timedelta_interval = timedelta(days=self.interval)
        prev_start_timestamp = self.due_timestamp if self.due_timestamp else attempted_at
        due_timestamp = prev_start_timestamp + new_timedelta_interval
        return due_timestamp, new_timedelta_interval
