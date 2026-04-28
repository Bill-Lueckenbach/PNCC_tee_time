"""Tests for the PNCC Tee Time Booking automation.

These tests exercise the configuration helpers and the step functions
using mocked Selenium objects so that no real browser or network
connection is required.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# config.py tests
# ---------------------------------------------------------------------------


class TestConfig:
    """Unit tests for pncc_tee_time.config helpers."""

    def test_get_username_returns_env_value(self, monkeypatch):
        """get_username() returns the PNCC_USERNAME env var."""
        monkeypatch.setenv("PNCC_USERNAME", "test_user")
        from pncc_tee_time import config

        assert config.get_username() == "test_user"

    def test_get_username_raises_when_not_set(self, monkeypatch):
        """get_username() raises EnvironmentError when PNCC_USERNAME is absent."""
        monkeypatch.delenv("PNCC_USERNAME", raising=False)
        from pncc_tee_time import config

        with pytest.raises(EnvironmentError, match="PNCC_USERNAME"):
            config.get_username()

    def test_get_password_returns_env_value(self, monkeypatch):
        """get_password() returns the PNCC_PASSWORD env var."""
        monkeypatch.setenv("PNCC_PASSWORD", "secret123")
        from pncc_tee_time import config

        assert config.get_password() == "secret123"

    def test_get_password_raises_when_not_set(self, monkeypatch):
        """get_password() raises EnvironmentError when PNCC_PASSWORD is absent."""
        monkeypatch.delenv("PNCC_PASSWORD", raising=False)
        from pncc_tee_time import config

        with pytest.raises(EnvironmentError, match="PNCC_PASSWORD"):
            config.get_password()

    def test_get_tee_date_returns_env_value(self, monkeypatch):
        """get_tee_date() returns the PNCC_TEE_DATE env var when set."""
        monkeypatch.setenv("PNCC_TEE_DATE", "07/04/2025")
        from pncc_tee_time import config

        assert config.get_tee_date() == "07/04/2025"

    def test_get_tee_date_defaults_to_today(self, monkeypatch):
        """get_tee_date() defaults to today's date when PNCC_TEE_DATE is not set."""
        monkeypatch.delenv("PNCC_TEE_DATE", raising=False)
        from pncc_tee_time import config

        result = config.get_tee_date()
        expected = date.today().strftime("%m/%d/%Y")
        assert result == expected

    def test_is_headless_false_by_default(self, monkeypatch):
        """is_headless() returns False when PNCC_HEADLESS is not set."""
        monkeypatch.delenv("PNCC_HEADLESS", raising=False)
        from pncc_tee_time import config

        assert config.is_headless() is False

    @pytest.mark.parametrize("value", ["1", "true", "True", "TRUE", "yes", "YES"])
    def test_is_headless_true_variants(self, monkeypatch, value):
        """is_headless() returns True for recognized truthy PNCC_HEADLESS values."""
        monkeypatch.setenv("PNCC_HEADLESS", value)
        from pncc_tee_time import config

        assert config.is_headless() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", ""])
    def test_is_headless_false_variants(self, monkeypatch, value):
        """is_headless() returns False for falsy PNCC_HEADLESS values."""
        monkeypatch.setenv("PNCC_HEADLESS", value)
        from pncc_tee_time import config

        assert config.is_headless() is False

    def test_get_num_players_default(self, monkeypatch):
        """get_num_players() returns '1' when PNCC_NUM_PLAYERS is not set."""
        monkeypatch.delenv("PNCC_NUM_PLAYERS", raising=False)
        from pncc_tee_time import config

        assert config.get_num_players() == "1"

    def test_get_num_players_returns_env_value(self, monkeypatch):
        """get_num_players() returns the PNCC_NUM_PLAYERS env var."""
        monkeypatch.setenv("PNCC_NUM_PLAYERS", "3")
        from pncc_tee_time import config

        assert config.get_num_players() == "3"


# ---------------------------------------------------------------------------
# tee_time_booker.py – unit tests with mocked driver
# ---------------------------------------------------------------------------


class TestStepFunctions:
    """Unit tests for the individual step functions in tee_time_booker."""

    @pytest.fixture()
    def driver(self):
        """Return a MagicMock that mimics a Selenium WebDriver."""
        mock_driver = MagicMock()
        mock_driver.title = "Porter's Neck Country Club"
        return mock_driver

    # ------------------------------------------------------------------
    # step1_open_website
    # ------------------------------------------------------------------

    def test_step1_opens_site_url(self, driver):
        """step1_open_website calls driver.get() with the correct URL."""
        from pncc_tee_time.tee_time_booker import SITE_URL, step1_open_website

        with patch("pncc_tee_time.tee_time_booker.wait_for", return_value=MagicMock()):
            step1_open_website(driver)

        driver.get.assert_called_once_with(SITE_URL)

    # ------------------------------------------------------------------
    # step3_fill_credentials
    # ------------------------------------------------------------------

    def test_step3_sends_credentials(self, driver):
        """step3_fill_credentials sends username and password to the correct fields."""
        from pncc_tee_time.tee_time_booker import step3_fill_credentials

        mock_username_field = MagicMock()
        mock_password_field = MagicMock()

        call_count = [0]

        def fake_wait_for(drv, by, value, timeout=20):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_username_field
            return mock_password_field

        with patch("pncc_tee_time.tee_time_booker.wait_for", side_effect=fake_wait_for):
            step3_fill_credentials(driver, "user@example.com", "p@ssw0rd")

        mock_username_field.send_keys.assert_called_once_with("user@example.com")
        mock_password_field.send_keys.assert_called_once_with("p@ssw0rd")

    # ------------------------------------------------------------------
    # step7_find_earliest_tee_time
    # ------------------------------------------------------------------

    def test_step7_clicks_first_available_slot(self, driver):
        """step7_find_earliest_tee_time clicks the first available slot element."""
        from pncc_tee_time.tee_time_booker import step7_find_earliest_tee_time

        slot1 = MagicMock()
        slot1.text = "8:00 AM"
        slot2 = MagicMock()
        slot2.text = "8:30 AM"

        driver.find_elements.return_value = [slot1, slot2]

        result = step7_find_earliest_tee_time(driver)

        slot1.click.assert_called_once()
        slot2.click.assert_not_called()
        assert result == "8:00 AM"

    def test_step7_raises_when_no_slots(self, driver):
        """step7_find_earliest_tee_time raises NoSuchElementException when no slots are available."""
        from selenium.common.exceptions import NoSuchElementException

        from pncc_tee_time.tee_time_booker import step7_find_earliest_tee_time

        driver.find_elements.return_value = []

        with pytest.raises(NoSuchElementException):
            step7_find_earliest_tee_time(driver)

    # ------------------------------------------------------------------
    # step10_verify_confirmation
    # ------------------------------------------------------------------

    def test_step10_returns_confirmation_text(self, driver):
        """step10_verify_confirmation returns the confirmation message text."""
        from pncc_tee_time.tee_time_booker import step10_verify_confirmation

        mock_elem = MagicMock()
        mock_elem.text = "Tee Time Received – Thank you!"

        with patch("pncc_tee_time.tee_time_booker.wait_for", return_value=mock_elem):
            result = step10_verify_confirmation(driver)

        assert "Tee Time Received" in result

    def test_step10_falls_back_to_body_keyword_match(self, driver):
        """step10_verify_confirmation falls back to body text when no selector matches."""
        from selenium.common.exceptions import TimeoutException

        from pncc_tee_time.tee_time_booker import step10_verify_confirmation

        body_mock = MagicMock()
        body_mock.text = "Your booking is CONFIRMED. Thank you for choosing PNCC!"

        with patch("pncc_tee_time.tee_time_booker.wait_for", side_effect=TimeoutException):
            driver.find_element.return_value = body_mock
            result = step10_verify_confirmation(driver)

        assert "confirmed" in result.lower() or "keyword" in result.lower()

    def test_step10_raises_when_no_confirmation(self, driver):
        """step10_verify_confirmation raises TimeoutException when no confirmation is found."""
        from selenium.common.exceptions import TimeoutException

        from pncc_tee_time.tee_time_booker import step10_verify_confirmation

        body_mock = MagicMock()
        body_mock.text = "Some unrelated page content"

        with patch("pncc_tee_time.tee_time_booker.wait_for", side_effect=TimeoutException):
            driver.find_element.return_value = body_mock
            with pytest.raises(TimeoutException):
                step10_verify_confirmation(driver)


# ---------------------------------------------------------------------------
# __main__.py – CLI entry point tests
# ---------------------------------------------------------------------------


class TestMain:
    """Unit tests for the __main__ entry point."""

    def test_main_exits_1_on_missing_credentials(self, monkeypatch):
        """main() returns exit code 1 when PNCC_USERNAME is not set."""
        monkeypatch.delenv("PNCC_USERNAME", raising=False)
        monkeypatch.delenv("PNCC_PASSWORD", raising=False)

        from pncc_tee_time.__main__ import main

        assert main() == 1

    def test_main_exits_0_on_success(self, monkeypatch):
        """main() returns exit code 0 when book_tee_time succeeds."""
        monkeypatch.setenv("PNCC_USERNAME", "u")
        monkeypatch.setenv("PNCC_PASSWORD", "p")
        monkeypatch.setenv("PNCC_TEE_DATE", "01/01/2025")
        monkeypatch.setenv("PNCC_HEADLESS", "true")

        with patch("pncc_tee_time.__main__.book_tee_time", return_value="Tee Time Received"):
            from pncc_tee_time.__main__ import main

            assert main() == 0

    def test_main_exits_1_on_booking_failure(self, monkeypatch):
        """main() returns exit code 1 when book_tee_time raises an exception."""
        monkeypatch.setenv("PNCC_USERNAME", "u")
        monkeypatch.setenv("PNCC_PASSWORD", "p")

        with patch("pncc_tee_time.__main__.book_tee_time", side_effect=RuntimeError("boom")):
            from pncc_tee_time.__main__ import main

            assert main() == 1
