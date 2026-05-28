"""Application settings and environment loading helpers.

This module centralises configuration concerns that are independent of the
browser automation layers. It is responsible for loading values from the
environment and validating that required settings are present.
"""

import logging
import os

from dotenv import load_dotenv


def setup_logging() -> None:
    """Configure application-wide logging once at process startup.

    Environment variables:
        PNCC_LOG_LEVEL: Logging level name (default: INFO).
        PNCC_LOG_FILE: Optional path to a log file.
        PNCC_LOG_DEBUG_MODULES: Optional comma-separated logger names to force
            to DEBUG level (e.g. "PNCC_tee_time.pages,PNCC_tee_time.base").
    """
    level_name = os.getenv("PNCC_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    if not isinstance(level, int):
        level = logging.INFO

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    log_file = os.getenv("PNCC_LOG_FILE", "").strip()
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=handlers,
        force=True,
    )

    # Allow selective deep diagnostics while keeping the global log level
    # higher (for example, global INFO with only pages.py at DEBUG).
    module_list_raw = os.getenv("PNCC_LOG_DEBUG_MODULES", "")
    for module_name in module_list_raw.split(","):
        module_name = module_name.strip()
        if module_name:
            logging.getLogger(module_name).setLevel(logging.DEBUG)


def get_required_env(name: str) -> str:
    """Return the value of a required environment variable.

    Reads the named variable from the current process environment using
    os.getenv(). If the variable is missing or empty a RuntimeError is raised
    immediately with a human-readable message pointing to the .env file,
    rather than allowing the program to continue with a None/empty value and
    fail later with a confusing error (e.g. an authentication failure on the
    PNCC website).

    Args:
        name: The environment variable name to look up (e.g. "PNCC_USERNAME").

    Returns:
        The non-empty string value of the environment variable.

    Raises:
        RuntimeError: If the variable is not set or is an empty string.
    """
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(
        f"Missing environment variable: {name}. "
        "Create/update your .env file with required credentials."
    )


def get_credentials() -> tuple[str, str]:
    """Load credentials from the .env file and return them as a tuple.

    Calls load_dotenv() to read key=value pairs from the .env file at the
    project root into the current process environment. Variables that are
    already set in the environment (e.g. in CI/CD) are not overwritten, so
    this function works in both local and automated environments.

    After loading, it retrieves PNCC_USERNAME and PNCC_PASSWORD via
    get_required_env(), which raises a RuntimeError if either is missing.

    Returns:
        A (username, password) tuple of strings ready to pass to
        pages.login().

    Raises:
        RuntimeError: If PNCC_USERNAME or PNCC_PASSWORD is not set.
    """
    load_dotenv()
    username = get_required_env("PNCC_USERNAME")
    password = get_required_env("PNCC_PASSWORD")
    return username, password


def get_runtime_config() -> list[str]:
    """Return preferred tee times from env vars.

    Reads:
        PNCC_PREFERRED_TIMES -- comma-separated preferred tee times.
    """
    preferred_raw = get_required_env("PNCC_PREFERRED_TIMES")

    # Step 1: Split the raw CSV-style string into individual tee_time values.
    raw_tee_times = preferred_raw.split(",")

    # Step 2: Trim whitespace around each tee_time value.
    trimmed_tee_times: list[str] = []
    for raw_tee_time in raw_tee_times:
        trimmed_tee_time = raw_tee_time.strip()
        trimmed_tee_times.append(trimmed_tee_time)

    # Step 3: Drop empty entries and keep only valid tee_time strings.
    preferred_tee_times: list[str] = []
    for trimmed_tee_time in trimmed_tee_times:
        if trimmed_tee_time:
            preferred_tee_times.append(trimmed_tee_time)

    return preferred_tee_times