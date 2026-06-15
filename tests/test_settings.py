"""Unit tests for settings.py.

These tests cover environment loading and required-variable validation
without launching a browser.
"""

import logging
from unittest.mock import patch

import pytest

from PNCC_tee_time import settings


def test_get_required_env_returns_value_when_present():
    # Arrange
    with patch("PNCC_tee_time.settings.os.getenv", return_value="member1"):
        # Act
        result = settings.get_required_env("PNCC_USERNAME")

        # Assert
        assert result == "member1", (
            "get_required_env() should return the existing environment value "
            "for PNCC_USERNAME."
        )


def test_get_required_env_raises_when_missing():
    # Arrange
    with patch("PNCC_tee_time.settings.os.getenv", return_value=None):

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match=(
                "Missing environment variable: PNCC_USERNAME\\. "
                "Create/update your \\.env file with required credentials\\."
            ),
        ):
            settings.get_required_env("PNCC_USERNAME")


def test_get_required_env_raises_when_empty_string():
    # Arrange
    with patch("PNCC_tee_time.settings.os.getenv", return_value=""):

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match=(
                "Missing environment variable: PNCC_PASSWORD\\. "
                "Create/update your \\.env file with required credentials\\."
            ),
        ):
            settings.get_required_env("PNCC_PASSWORD")


@patch("PNCC_tee_time.settings.load_dotenv")
@patch("PNCC_tee_time.settings.get_required_env")
def test_get_credentials_loads_dotenv_and_returns_tuple(
    mock_get_required_env, mock_load_dotenv
):
    # Arrange
    mock_get_required_env.side_effect = ["member1", "secret-password"]

    # Act
    result = settings.get_credentials()

    # Assert
    assert result == ("member1", "secret-password"), (
        "get_credentials() should return a tuple of username and password "
        "from the required environment lookups."
    )

    mock_load_dotenv.assert_called_once_with(override=False)
    assert mock_get_required_env.call_args_list == [
        (("PNCC_USERNAME",),),
        (("PNCC_PASSWORD",),),
    ], "get_credentials() should request PNCC_USERNAME before PNCC_PASSWORD."


@patch("PNCC_tee_time.settings.load_dotenv")
@patch("PNCC_tee_time.settings.get_required_env")
def test_get_credentials_propagates_username_lookup_failure(
    mock_get_required_env, mock_load_dotenv
):
    # Arrange
    mock_get_required_env.side_effect = RuntimeError(
        "Missing environment variable: PNCC_USERNAME. "
        "Create/update your .env file with required credentials."
    )

    # Act / Assert
    with pytest.raises(
        RuntimeError,
        match=(
            "Missing environment variable: PNCC_USERNAME\\. "
            "Create/update your \\.env file with required credentials\\."
        ),
    ):
        settings.get_credentials()

    mock_load_dotenv.assert_called_once_with(override=False)
    mock_get_required_env.assert_called_once_with("PNCC_USERNAME")


@patch("PNCC_tee_time.settings.logging.basicConfig")
@patch("PNCC_tee_time.settings.os.getenv")
def test_setup_logging_uses_info_level_when_env_missing(
    mock_getenv, mock_basic_config
):
    # Arrange
    mock_getenv.side_effect = lambda name, default=None: default

    # Act
    settings.setup_logging()

    # Assert
    kwargs = mock_basic_config.call_args.kwargs
    assert kwargs["level"] == settings.logging.INFO
    assert kwargs["force"] is True
    assert len(kwargs["handlers"]) == 1
    assert isinstance(kwargs["handlers"][0].formatter, settings.IndentingFormatter)


@patch("PNCC_tee_time.settings.logging.FileHandler")
@patch("PNCC_tee_time.settings.logging.basicConfig")
@patch("PNCC_tee_time.settings.os.getenv")
def test_setup_logging_adds_file_handler_when_env_set(
    mock_getenv, mock_basic_config, mock_file_handler
):
    # Arrange
    values = {
        "PNCC_LOG_LEVEL": "DEBUG",
        "PNCC_LOG_FILE": "pncc.log",
    }
    mock_getenv.side_effect = lambda name, default=None: values.get(name, default)

    # Act
    settings.setup_logging()

    # Assert
    mock_file_handler.assert_called_once_with("pncc.log")
    assert mock_file_handler.return_value.setFormatter.called
    kwargs = mock_basic_config.call_args.kwargs
    assert kwargs["level"] == settings.logging.DEBUG
    assert len(kwargs["handlers"]) == 2


@patch("PNCC_tee_time.settings.logging.basicConfig")
@patch("PNCC_tee_time.settings.os.getenv")
def test_setup_logging_uses_warning_level_when_configured(
    mock_getenv, mock_basic_config
):
    # Arrange
    values = {
        "PNCC_LOG_LEVEL": "WARNING",
        "PNCC_LOG_FILE": "",
        "PNCC_LOG_DEBUG_MODULES": "",
    }
    mock_getenv.side_effect = lambda name, default=None: values.get(name, default)

    # Act
    settings.setup_logging()

    # Assert
    kwargs = mock_basic_config.call_args.kwargs
    assert kwargs["level"] == settings.logging.WARNING


@patch("PNCC_tee_time.settings.logging.basicConfig")
@patch("PNCC_tee_time.settings.os.getenv")
def test_setup_logging_defaults_to_info_on_invalid_level(
    mock_getenv, mock_basic_config
):
    # Arrange
    values = {
        "PNCC_LOG_LEVEL": "INVALID",
        "PNCC_LOG_FILE": "",
        "PNCC_LOG_DEBUG_MODULES": "",
    }
    mock_getenv.side_effect = lambda name, default=None: values.get(name, default)

    # Act
    settings.setup_logging()

    # Assert
    kwargs = mock_basic_config.call_args.kwargs
    assert kwargs["level"] == settings.logging.INFO


@patch("PNCC_tee_time.settings.logging.getLogger")
@patch("PNCC_tee_time.settings.logging.basicConfig")
@patch("PNCC_tee_time.settings.os.getenv")
def test_setup_logging_applies_debug_level_to_selected_modules(
    mock_getenv, mock_basic_config, mock_get_logger
):
    # Arrange
    values = {
        "PNCC_LOG_LEVEL": "INFO",
        "PNCC_LOG_FILE": "",
        "PNCC_LOG_DEBUG_MODULES": (
            "PNCC_tee_time.pages, PNCC_tee_time.date_time_utils"
        ),
    }
    mock_getenv.side_effect = lambda name, default=None: values.get(name, default)
    mock_pages_logger = mock_get_logger.return_value

    # Act
    settings.setup_logging()

    # Assert
    mock_basic_config.assert_called_once()
    assert mock_get_logger.call_args_list == [
        (("PNCC_tee_time.pages",),),
        (("PNCC_tee_time.date_time_utils",),),
    ]
    assert mock_pages_logger.setLevel.call_count == 2
    mock_pages_logger.setLevel.assert_called_with(settings.logging.DEBUG)


@patch("PNCC_tee_time.settings.logging.getLogger")
@patch("PNCC_tee_time.settings.logging.basicConfig")
@patch("PNCC_tee_time.settings.os.getenv")
def test_setup_logging_ignores_blank_debug_module_entries(
    mock_getenv, mock_basic_config, mock_get_logger
):
    # Arrange
    values = {
        "PNCC_LOG_DEBUG_MODULES": "PNCC_tee_time.pages, ,   ,PNCC_tee_time.base",
    }
    mock_getenv.side_effect = lambda name, default=None: values.get(name, default)

    # Act
    settings.setup_logging()

    # Assert
    assert mock_get_logger.call_args_list == [
        (("PNCC_tee_time.pages",),),
        (("PNCC_tee_time.base",),),
    ]
    mock_basic_config.assert_called_once()


@patch("PNCC_tee_time.settings.get_required_env")
def test_get_runtime_config_splits_and_trims_preferred_times(mock_get_required_env):
    # Arrange
    mock_get_required_env.return_value = "9:00 AM, 9:10 AM ,10:00 AM"

    # Act
    result = settings.get_runtime_config()

    # Assert
    assert result == ["9:00 AM", "9:10 AM", "10:00 AM"]
    mock_get_required_env.assert_called_once_with("PNCC_PREFERRED_TIMES")


@patch("PNCC_tee_time.settings.get_required_env")
def test_get_runtime_config_filters_empty_entries(mock_get_required_env):
    # Arrange
    mock_get_required_env.return_value = "9:00 AM, , ,10:00 AM, "

    # Act
    result = settings.get_runtime_config()

    # Assert
    assert result == ["9:00 AM", "10:00 AM"]


def test_indenting_formatter_indents_multiline_messages():
    formatter = settings.IndentingFormatter(
        "%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s"
    )
    record = logging.LogRecord(
        name="PNCC_tee_time.pages",
        level=logging.DEBUG,
        pathname=__file__,
        lineno=1,
        msg="first line\nsecond line\nthird line",
        args=(),
        exc_info=None,
    )
    record.funcName = "test_indenting_formatter_indents_multiline_messages"

    formatted = formatter.format(record)

    assert formatted.startswith(
        "2026-"
    )
    assert (
        "[PNCC_tee_time.pages.test_indenting_formatter_indents_multiline_messages]"
        in formatted
    )
    assert "\r\n    first line" in formatted
    assert "\r\n    second line" in formatted
    assert "\r\n    third line" in formatted


def test_indenting_formatter_wraps_long_messages_at_word_breaks():
    formatter = settings.IndentingFormatter(
        "%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s"
    )
    record = logging.LogRecord(
        name="PNCC_tee_time.pages",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=(
            "This log message is intentionally long so that it should wrap at a "
            "word boundary instead of splitting a word in the middle."
        ),
        args=(),
        exc_info=None,
    )
    record.funcName = (
        "test_indenting_formatter_wraps_long_messages_at_word_breaks"
    )

    formatted = formatter.format(record)

    lines = formatted.splitlines()
    assert lines[1] == (
        "    This log message is intentionally long so that it should wrap at a "
        "word boundary"
    )
    assert lines[2] == "    instead of splitting a word in the middle."


@patch("PNCC_tee_time.settings.get_required_env")
def test_get_runtime_config_single_tee_time(mock_get_required_env):
    # Arrange
    mock_get_required_env.return_value = "8:00 AM"

    # Act
    result = settings.get_runtime_config()

    # Assert
    assert result == ["8:00 AM"]


@patch("PNCC_tee_time.settings.get_required_env")
def test_get_runtime_config_many_tee_times(mock_get_required_env):
    # Arrange
    tee_times = ", ".join([f"{hour}:00 AM" for hour in range(8, 17)])
    mock_get_required_env.return_value = tee_times

    # Act
    result = settings.get_runtime_config()

    # Assert
    assert len(result) == 9
    assert result[0] == "8:00 AM"