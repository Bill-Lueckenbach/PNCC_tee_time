"""Application settings and environment loading helpers.

This module centralises configuration concerns that are independent of the
browser automation layers. It is responsible for loading values from the
environment and validating that required settings are present.
"""

import logging
import os
import textwrap

from dotenv import load_dotenv


class IndentingFormatter(logging.Formatter):
    """Formatter that indents continuation lines in multiline log records."""

    _message_width = 80

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        message_lines = message.splitlines() or [""]
        wrapped_lines: list[str] = []
        for message_line in message_lines:
            wrapped_lines.extend(
                textwrap.wrap(
                    message_line,
                    width=self._message_width,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                or [""]
            )

        header_record = logging.makeLogRecord(record.__dict__.copy())
        header_record.msg = ""
        header_record.args = ()
        header_record.exc_info = None
        header = super().format(header_record).rstrip()

        indented_message = "\r\n    ".join(wrapped_lines)
        return f"{header}\r\n    {indented_message}"


class ModuleDebugOnlyFilter(logging.Filter):
    """Allow only DEBUG records from selected logger names/prefixes."""

    def __init__(self, module_names: list[str]):
        super().__init__()
        self._module_names = module_names

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno != logging.DEBUG:
            return False

        for module_name in self._module_names:
            if record.name == module_name or record.name.startswith(f"{module_name}."):
                return True
        return False


def setup_logging() -> None:
    """Configure application-wide logging once at process startup.

    Environment variables:
        PNCC_LOG_LEVEL: Logging level name (default: INFO).
        PNCC_LOG_FILE: Optional path to a log file.
        PNCC_LOG_DEBUG_MODULES: Optional comma-separated logger names to force
            to DEBUG level (e.g. "PNCC_tee_time.pages,PNCC_tee_time.base").
    """
    # Load .env before reading logging-related environment variables so
    # DEBUG/handler configuration can be driven from local project settings.
    # Use override=True to avoid stale terminal-session PNCC_LOG_* values.
    load_dotenv(override=True)

    level_name = os.getenv("PNCC_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    if not isinstance(level, int):
        level = logging.INFO

    module_list_raw = os.getenv("PNCC_LOG_DEBUG_MODULES", "")
    debug_modules = [
        module_name.strip()
        for module_name in module_list_raw.split(",")
        if module_name.strip()
    ]

    stream_handler = logging.StreamHandler()
    # Keep terminal output at INFO+ so module-level DEBUG diagnostics can be
    # routed to file without flooding the console.
    stream_handler.setLevel(logging.INFO)

    handlers: list[logging.Handler] = [stream_handler]
    log_file = os.getenv("PNCC_LOG_FILE", "").strip()
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        if debug_modules:
            file_handler.addFilter(ModuleDebugOnlyFilter(debug_modules))
        handlers.append(file_handler)

    formatter = IndentingFormatter(
        "%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s"
    )
    for handler in handlers:
        handler.setFormatter(formatter)

    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,
    )

    # Allow selective deep diagnostics while keeping the global log level
    # higher (for example, global INFO with only pages.py at DEBUG).
    for module_name in debug_modules:
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
    load_dotenv(override=False)
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