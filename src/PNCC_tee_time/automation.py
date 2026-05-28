
"""
automation.py
----------------
Main entry point and CLI orchestration for PNCC tee time booking automation.

This module provides:
    - Command-line argument parsing and validation
    - Booking request scheduling logic
    - Main booking workflow (login, navigation, booking steps)

Functions/classes:
    MaxPlayersAction: Argparse action that enforces a maximum of four player names.
    argparse_setup(): Configures the command line argument parser for the CLI.
    main(): Orchestrates the booking workflow: parses args, schedules booking, logs in,
            and (future) books tee time.

Imported helpers:
    get_tee_date() and get_request_date() are provided by
    PNCC_tee_time.date_time_utils.

Each function is documented with accepted arguments, return values, 
   and error conditions.
"""

import argparse
import datetime as dt
import logging

import PNCC_tee_time.date_time_utils
from PNCC_tee_time import base, locators, pages, settings

logger = logging.getLogger(__name__)


class MaxPlayersAction(argparse.Action):
    """Argparse action that enforces a maximum of four player names."""

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        if values is None:
            players: list[str] = []
        elif isinstance(values, str):
            players = [values]
        else:
            players = list(values)

        if len(players) > 4:
            parser.error("A maximum of 4 players may be provided.")
        setattr(namespace, self.dest, players)


def argparse_setup() -> argparse.ArgumentParser:
    """Configure the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog = "PNCC_tee_time",
        description="Automate PNCC tee time booking.",
        formatter_class=argparse.RawTextHelpFormatter
        )

    parser.add_argument(
        'tee_date',                      # Argument name for the desired tee date
        help=(
            'Booking date.\n'
            'Accepted formats:\n'
            '  YYYY-MM-DD (e.g. "2024-06-15")\n'
            '  "Today", "Tomorrow", or weekday name (e.g. "Saturday")\n'
        )
    )
    
    parser.add_argument(
        'tee_time',                      # Argument name for the preferred tee time
        type = str.lower,                # Convert input to lowercase for easier parsing
        nargs='?',                       # Make this argument optional to allow default
        default = "8am",                 # Default to 8am if not provided
        help=(
            'Preferred tee time.\n'
            'Accepted formats:\n'
            '  HHam-HHam (e.g. "8am-1pm")\n'
            '  HH:MM-HH:MM (e.g. "08:00-13:00")\n'
            '  HHam (e.g. "8am" is treated as earliest tee_time after 08:00)\n'
            '  HH:MM (e.g. "08:00" is treated as earliest tee_time after 08:00)\n'
        ),
    )


    parser.add_argument(
        'players',                       # Argument name for all players
        nargs='*',                       # Accept zero or more player names
        action=MaxPlayersAction,
        default=["Lueckenbach, Bill"],  # Default to account holder if not provided
        help=(
            'Optional player names as separate arguments.\n'
            'Examples:\n'
            '  PNCC_tee_time Today 8am "Lueckenbach, Bill"\n'
            '  PNCC_tee_time Today 8am "Lueckenbach, Bill" "Doe, Jane"\n'
            'Omit players to book for member only.\n'
        ),
    )

    return parser



    
    
    





def main() -> None:
    """Run the PNCC tee-time booking automation workflow.

    Usage:
        python -m PNCC_tee_time <tee_date> [tee_time] [players...]

    Arguments:
        tee_date:
            Required booking date string.
            Supported forms are defined in PNCC_tee_time.date_time_utils.get_tee_date.
        tee_time:
            Optional preferred tee time string. Defaults to "8am".
        players:
            Optional list of player names (maximum 4). If omitted, defaults to
            the account holder.

    Workflow:
        1. Configure logging and parse command-line arguments.
        2. Parse tee_date and tee_time, then compute request_tee_date.
        3. If request_tee_date is not today, exit after logging 
           (scheduled-run logic is TODO).
        4. Load credentials, open the site, and log in.
        5. Booking-page navigation and slot selection are TODO.
    """
    # Ensure logging is configured regardless of entrypoint (module or script).
    settings.setup_logging()

    # Step 1: Parse command line arguments
    parser = argparse_setup()
    args = parser.parse_args()
    logger.debug(
        "Parsed arguments: tee_date=%s tee_time=%s players=%s",
        args.tee_date,
        args.tee_time,
        args.players,
    )
    
     # Step 2: Determine when to request tee time.

    tee_date = PNCC_tee_time.date_time_utils.get_tee_date(args.tee_date)
    tee_times = PNCC_tee_time.date_time_utils.get_tee_times(args.tee_time)
    request_tee_date = PNCC_tee_time.date_time_utils.get_request_date(tee_date)
    today = dt.date.today()

    
    logger.info("tee_date=%s", tee_date)
    logger.info("request_tee_date=%s", request_tee_date)
    logger.info("tee time: %s", args.tee_time)
    logger.info("Players: %s", args.players)

    #Step 3: Implement schedule  logic
    if request_tee_date != today:
        #[TODO] Implement logic to schedule the booking steps to run 
        # at 6am on the request_tee_date.
        logger.info("Only request-today logic is implemented at this time.")
        exit(0)
    #default to schedule now logic if request_tee_date is today.

    #Step 4: Open driver and log in to the PNCC website.
        # Remainder of the steps require an active WebDriver session.
        # Do remainder of steps inside of Try / Finally loop to ensure
        # the browser is always closed on errors.
    username, password = settings.get_credentials()
    # Set driver to None here so it can be referenced in the finally block for teardown,
    # even if an exception occurs during driver creation.
    driver = None
    try:
        driver = base.create_driver()

        # Navigate to the login page and perform login.  
        # The login function will raise an exception if login fails.
        # If we reach the next line we can assume login succeeded.
        base.open_page(driver, locators.LOGIN_URL)
        pages.login(driver, username, password)
        logger.info("Login succeeded.")

        # Step 5: [TODO] Navigate to the booking page, select the desired date,
        # and attempt to book the preferred time slot with the specified players.
        pages.navigate_and_select_tee_time(driver, tee_date, tee_times, args.players)
        
    finally:
        if driver is not None:
            base.teardown(driver)
 

if __name__ == "__main__":
    main()
