"""Extended unit tests for settings.py.

Tests for setup_logging() and get_runtime_config().
"""

import logging
from unittest.mock import patch

import pytest

from PNCC_tee_time import settings


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------


class TestSetupLogging:
    """Tests for setup_logging()."""

    @patch.dict("os.environ", {}, clear=True)
    def test_setup_logging_uses_default_info_level(self):
        """Should use INFO level when PNCC_LOG_LEVEL not set."""
        # Arrange
        # Clear root logger handlers to start fresh
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Act
        settings.setup_logging()

        # Assert
        assert root_logger.level == logging.INFO or root_logger.level == logging.NOTSET

    @patch.dict("os.environ", {"PNCC_LOG_LEVEL": "DEBUG"})
    def test_setup_logging_uses_custom_log_level(self):
        """Should use PNCC_LOG_LEVEL environment variable."""
        # Arrange
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Act
        settings.setup_logging()

        # Assert
        assert root_logger.level == logging.DEBUG

    @patch.dict("os.environ", {"PNCC_LOG_LEVEL": "WARNING"})
    def test_setup_logging_handles_different_log_levels(self):
        """Should handle various log level names."""
        # Arrange
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Act
        settings.setup_logging()

        # Assert
        assert root_logger.level == logging.WARNING

    @patch.dict("os.environ", {"PNCC_LOG_LEVEL": "INVALID"})
    def test_setup_logging_defaults_to_info_on_invalid_level(self):
        """Should default to INFO if PNCC_LOG_LEVEL is invalid."""
        # Arrange
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Act
        settings.setup_logging()

        # Assert
        assert root_logger.level == logging.INFO or root_logger.level == logging.NOTSET

    @patch.dict("os.environ", {}, clear=True)
    def test_setup_logging_adds_stream_handler(self):
        """Should add at least one StreamHandler."""
        # Arrange
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Act
        settings.setup_logging()

        # Assert
        stream_handlers = [h for h in root_logger.handlers
                          if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) >= 1

    @patch("builtins.open", create=True)
    @patch.dict("os.environ", {"PNCC_LOG_FILE": "/tmp/test.log"})
    def test_setup_logging_adds_file_handler_when_specified(self, mock_open):
        """Should add FileHandler when PNCC_LOG_FILE is set."""
        # Arrange
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        mock_open.return_value.__enter__ = lambda s: s
        mock_open.return_value.__exit__ = lambda s, *args: None

        # Act
        settings.setup_logging()

        # Assert
        file_handlers = [h for h in root_logger.handlers
                        if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) >= 1

    @patch.dict("os.environ", {"PNCC_LOG_DEBUG_MODULES": "PNCC_tee_time.pages"})
    def test_setup_logging_sets_debug_level_for_specific_modules(self):
        """Should set DEBUG level for modules specified in PNCC_LOG_DEBUG_MODULES."""
        # Arrange
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Act
        settings.setup_logging()

        # Assert
        pages_logger = logging.getLogger("PNCC_tee_time.pages")
        assert pages_logger.level == logging.DEBUG

    @patch.dict("os.environ", {
        "PNCC_LOG_DEBUG_MODULES": "PNCC_tee_time.pages, PNCC_tee_time.base"
    })
    def test_setup_logging_handles_multiple_debug_modules(self):
        """Should handle comma-separated module list."""
        # Arrange
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Act
        settings.setup_logging()

        # Assert
        pages_logger = logging.getLogger("PNCC_tee_time.pages")
        base_logger = logging.getLogger("PNCC_tee_time.base")
        assert pages_logger.level == logging.DEBUG
        assert base_logger.level == logging.DEBUG


# ---------------------------------------------------------------------------
# get_runtime_config
# ---------------------------------------------------------------------------


class TestGetRuntimeConfig:
    """Tests for get_runtime_config()."""

    @patch("PNCC_tee_time.settings.get_required_env")
    def test_get_runtime_config_returns_list_of_tee_times(self, mock_get_required_env):
        """Should return a list of preferred tee time strings."""
        # Arrange
        mock_get_required_env.return_value = "8:00 AM, 8:10 AM, 8:20 AM"

        # Act
        result = settings.get_runtime_config()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 3

    @patch("PNCC_tee_time.settings.get_required_env")
    def test_get_runtime_config_trims_whitespace(self, mock_get_required_env):
        """Should trim whitespace around each tee time."""
        # Arrange
        mock_get_required_env.return_value = "  8:00 AM  ,  8:10 AM  ,  8:20 AM  "

        # Act
        result = settings.get_runtime_config()

        # Assert
        assert result == ["8:00 AM", "8:10 AM", "8:20 AM"]

    @patch("PNCC_tee_time.settings.get_required_env")
    def test_get_runtime_config_skips_empty_entries(self, mock_get_required_env):
        """Should skip empty entries from split."""
        # Arrange
        mock_get_required_env.return_value = "8:00 AM,,8:10 AM"

        # Act
        result = settings.get_runtime_config()

        # Assert
        assert result == ["8:00 AM", "8:10 AM"]

    @patch("PNCC_tee_time.settings.get_required_env")
    def test_get_runtime_config_single_tee_time(self, mock_get_required_env):
        """Should handle single tee time."""
        # Arrange
        mock_get_required_env.return_value = "8:00 AM"

        # Act
        result = settings.get_runtime_config()

        # Assert
        assert result == ["8:00 AM"]

    @patch("PNCC_tee_time.settings.get_required_env")
    def test_get_runtime_config_many_tee_times(self, mock_get_required_env):
        """Should handle many tee times."""
        # Arrange
        tee_times = ", ".join([f"{h}:00 AM" for h in range(8, 17)])
        mock_get_required_env.return_value = tee_times

        # Act
        result = settings.get_runtime_config()

        # Assert
        assert len(result) == 9  # 8 AM to 4 PM
        assert result[0] == "8:00 AM"

    @patch("PNCC_tee_time.settings.get_required_env")
    def test_get_runtime_config_raises_when_env_var_missing(self, mock_get_required_env):
        """Should raise when PNCC_PREFERRED_TIMES is not set."""
        # Arrange
        mock_get_required_env.side_effect = RuntimeError(
            "Missing environment variable: PNCC_PREFERRED_TIMES. "
            "Create/update your .env file with required credentials."
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="PNCC_PREFERRED_TIMES"):
            settings.get_runtime_config()

    @patch("PNCC_tee_time.settings.get_required_env")
    def test_get_runtime_config_calls_get_required_env(self, mock_get_required_env):
        """Should call get_required_env to fetch environment variable."""
        # Arrange
        mock_get_required_env.return_value = "8:00 AM"

        # Act
        settings.get_runtime_config()

        # Assert
        mock_get_required_env.assert_called_once_with("PNCC_PREFERRED_TIMES")
