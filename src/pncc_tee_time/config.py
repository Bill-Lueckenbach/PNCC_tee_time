"""Configuration for PNCC Tee Time Booking.

Credentials and booking options are read from environment variables so that
secrets are never hard-coded.

Environment variables
---------------------
PNCC_USERNAME
    Your Porter's Neck Country Club login username / email.
PNCC_PASSWORD
    Your Porter's Neck Country Club login password.
PNCC_TEE_DATE
    The date you want a tee time for, formatted as MM/DD/YYYY.
    Defaults to today's date when not set.
PNCC_HEADLESS
    Set to "1" or "true" to run Chrome in headless mode.
    Defaults to visible (non-headless) so you can watch the automation.
PNCC_NUM_PLAYERS
    Number of players (1-4).  Defaults to "1".
"""

import os
from datetime import date


def get_username() -> str:
    """Return the PNCC login username from the environment.

    Returns:
        str: The value of the PNCC_USERNAME environment variable.

    Raises:
        EnvironmentError: If PNCC_USERNAME is not set.
    """
    username = os.environ.get("PNCC_USERNAME", "")
    if not username:
        raise EnvironmentError(
            "PNCC_USERNAME environment variable is not set. "
            "Set it to your Porter's Neck Country Club login username."
        )
    return username


def get_password() -> str:
    """Return the PNCC login password from the environment.

    Returns:
        str: The value of the PNCC_PASSWORD environment variable.

    Raises:
        EnvironmentError: If PNCC_PASSWORD is not set.
    """
    password = os.environ.get("PNCC_PASSWORD", "")
    if not password:
        raise EnvironmentError(
            "PNCC_PASSWORD environment variable is not set. "
            "Set it to your Porter's Neck Country Club login password."
        )
    return password


def get_tee_date() -> str:
    """Return the desired tee time date in MM/DD/YYYY format.

    Reads PNCC_TEE_DATE from the environment; falls back to today.

    Returns:
        str: Date string in MM/DD/YYYY format.
    """
    tee_date = os.environ.get("PNCC_TEE_DATE", "")
    if not tee_date:
        tee_date = date.today().strftime("%m/%d/%Y")
    return tee_date


def is_headless() -> bool:
    """Return True when Chrome should run in headless mode.

    Returns:
        bool: True if PNCC_HEADLESS is "1" or "true" (case-insensitive).
    """
    value = os.environ.get("PNCC_HEADLESS", "").strip().lower()
    return value in ("1", "true", "yes")


def get_num_players() -> str:
    """Return the number of players as a string.

    Returns:
        str: Number of players (1-4), defaulting to "1".
    """
    return os.environ.get("PNCC_NUM_PLAYERS", "1")
