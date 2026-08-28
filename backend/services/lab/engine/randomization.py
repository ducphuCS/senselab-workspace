"""Serving order randomization (Decision D5)."""

import random
from typing import Sequence, TypeVar

T = TypeVar("T")


def randomize_serving_order(items: Sequence[T]) -> list[T]:
    """Randomize the presentation order of samples for a panelist."""
    shuffled = list(items)
    random.shuffle(shuffled)
    return shuffled
