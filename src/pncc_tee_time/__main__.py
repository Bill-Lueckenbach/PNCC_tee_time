"""Entry point for ``python -m pncc_tee_time``.

Usage::

    # Set credentials via environment variables, then run:
    export PNCC_USERNAME="your_username"
    export PNCC_PASSWORD="your_password"
    export PNCC_TEE_DATE="05/15/2025"   # optional; defaults to today
    export PNCC_NUM_PLAYERS="2"          # optional; defaults to 1
    export PNCC_HEADLESS="true"          # optional; run Chrome headlessly

    python -m pncc_tee_time
"""

import logging
import sys

from pncc_tee_time import config
from pncc_tee_time.tee_time_booker import book_tee_time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> int:
    """Read configuration from the environment and run the booking automation.

    Returns:
        int: Exit code – 0 for success, 1 for failure.
    """
    try:
        username = config.get_username()
        password = config.get_password()
        tee_date = config.get_tee_date()
        num_players = config.get_num_players()
        headless = config.is_headless()
    except EnvironmentError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        print(
            "\nSet the required environment variables before running:\n"
            "  PNCC_USERNAME   – your Porter's Neck CC login username\n"
            "  PNCC_PASSWORD   – your Porter's Neck CC login password\n"
            "  PNCC_TEE_DATE   – desired date in MM/DD/YYYY (default: today)\n"
            "  PNCC_NUM_PLAYERS – number of players 1-4 (default: 1)\n"
            "  PNCC_HEADLESS   – '1' or 'true' for headless Chrome (default: visible)",
            file=sys.stderr,
        )
        return 1

    print(
        f"\n=== PNCC Tee Time Booking ===\n"
        f"  Date       : {tee_date}\n"
        f"  Players    : {num_players}\n"
        f"  Headless   : {headless}\n"
    )

    try:
        confirmation = book_tee_time(
            username=username,
            password=password,
            tee_date=tee_date,
            num_players=num_players,
            headless=headless,
        )
        print(f"\n✅  SUCCESS – {confirmation}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"\n❌  BOOKING FAILED – {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
