"""Security and token generation utilities for ballots and sessions."""

import secrets


def generate_ballot_token(length: int = 16) -> str:
    """Generate a secure, URL-safe random token for ballot access."""
    return secrets.token_urlsafe(length)


def generate_3digit_code() -> str:
    """Generate a random 3-digit blind code for sensory samples (100-999)."""
    return f"{secrets.randbelow(900) + 100}"
