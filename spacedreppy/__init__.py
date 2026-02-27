"""SpacedRepPy — A spaced repetition Python library."""

from importlib.metadata import version

from spacedreppy.schedulers.sm2 import SM2Scheduler
from spacedreppy.schedulers.spaced_repetition_scheduler import SpacedRepetitionScheduler

__version__ = version("spacedreppy")
__all__ = ["SM2Scheduler", "SpacedRepetitionScheduler", "__version__"]
