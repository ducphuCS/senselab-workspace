"""Blind code generation for sensory samples (Decision D5)."""

import random


def generate_unique_3digit_codes(count: int, existing: set[str] | None = None) -> list[str]:
    """Generate a list of unique 3-digit blind codes (100-999)."""
    used = set(existing or ())
    codes: list[str] = []
    pool = [f"{n:03d}" for n in range(100, 1000) if f"{n:03d}" not in used]
    random.shuffle(pool)

    if count > len(pool):
        raise ValueError("Requested more unique 3-digit codes than available in pool.")

    return pool[:count]
