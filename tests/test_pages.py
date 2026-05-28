"""Unit tests for pages.py.

All tests mock the Selenium WebDriver and WebElement objects so no real
browser or website is required. Integration tests that exercise the full
booking workflow against a live browser live in test_integration.py.
"""

import datetime as dt
from unittest.mock import MagicMock, Mock, patch

import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)

from PNCC_tee_time import elements, locators, pages

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_driver():
    """Return a mock Selenium WebDriver."""
    return MagicMock()


@pytest.fixture
def mock_slot():
    """Return a mock WebElement representing a tee-time slot."""
    return MagicMock()


@pytest.fixture
def mock_element():
    """Return a generic mock WebElement."""
    return MagicMock()


# ---------------------------------------------------------------------------
# set_remember_me
# ---------------------------------------------------------------------------


class TestSetRememberMe:
    """Tests for set_remember_me()."""

    def test_set_remember_me_checked_when_enabled(self, mock_driver):
        """When enabled=True, should click checkbox if not already checked."""
        # Arrange
        mock_checkbox = MagicMock()
        mock_checkbox.is_selected.return_value = False
        mock_driver.find_elements.return_value = [mock_checkbox]

        # Act
        pages.set_remember_me(mock_driver, enabled=True)

        # Assert
        mock_driver.execute_script.assert_called_once()
        assert "arguments[0].click()" in mock_driver.execute_script.call_args[0][0]

    def test_set_remember_me_unchecked_when_disabled(self, mock_driver):
        """When enabled=False, should click checkbox if currently checked."""
        # Arrange
        mock_checkbox = MagicMock()
        mock_checkbox.is_selected.return_value = True
        mock_driver.find_elements.return_value = [mock_checkbox]

        # Act
        pages.set_remember_me(mock_driver, enabled=False)

        # Assert
        mock_driver.execute_script.assert_called_once()

    def test_set_remember_me_no_click_if_already_correct_state(self, mock_driver):
        """Should not click if checkbox is already in desired state."""
        # Arrange
        mock_checkbox = MagicMock()
        mock_checkbox.is_selected.return_value = True
        mock_driver.find_elements.return_value = [mock_checkbox]

        # Act
        pages.set_remember_me(mock_driver, enabled=True)

        # Assert
        mock_driver.execute_script.assert_not_called()

    def test_set_remember_me_handles_missing_checkbox(self, mock_driver):
        """Should return gracefully if Remember Me checkbox is not on page."""
        # Arrange
        mock_driver.find_elements.return_value = []

        # Act / Assert (should not raise)
        pages.set_remember_me(mock_driver, enabled=True)
        mock_driver.execute_script.assert_not_called()


# ---------------------------------------------------------------------------
# set_booking_date
# ---------------------------------------------------------------------------


class TestSetBookingDate:
    """Tests for set_booking_date()."""

    @patch("PNCC_tee_time.pages.elements.send_keys")
    def test_set_booking_date_formats_date_correctly(self, mock_send_keys, mock_driver):
        """Should format date as M/D/YYYY and send to the date input."""
        # Arrange
        test_date = dt.date(2026, 6, 15)

        # Act
        pages.set_booking_date(mock_driver, test_date)

        # Assert
        mock_send_keys.assert_called_once_with(
            mock_driver, locators.BOOKING_DATE, "6/15/2026"
        )

    @patch("PNCC_tee_time.pages.elements.send_keys")
    def test_set_booking_date_handles_single_digit_month_day(
        self, mock_send_keys, mock_driver
    ):
        """Should handle single-digit months and days without leading zeros."""
        # Arrange
        test_date = dt.date(2026, 1, 5)

        # Act
        pages.set_booking_date(mock_driver, test_date)

        # Assert
        mock_send_keys.assert_called_once_with(
            mock_driver, locators.BOOKING_DATE, "1/5/2026"
        )


# ---------------------------------------------------------------------------
# select_date
# ---------------------------------------------------------------------------


class TestSelectDate:
    """Tests for select_date()."""

    @patch("PNCC_tee_time.pages.refresh_tee_sheet")
    @patch("PNCC_tee_time.pages.set_booking_date")
    @patch("PNCC_tee_time.pages.elements.wait_for_clickable")
    def test_select_date_waits_for_date_input(
        self,
        mock_wait_for_clickable,
        mock_set_booking_date,
        mock_refresh_tee_sheet,
        mock_driver,
    ):
        """Should wait for date input to be clickable before setting."""
        # Arrange
        test_date = dt.date(2026, 6, 15)
        mock_wait_for_clickable.return_value = MagicMock()

        # Act
        pages.select_date(mock_driver, test_date)

        # Assert
        mock_wait_for_clickable.assert_called_once_with(
            mock_driver, locators.BOOKING_DATE
        )

    @patch("PNCC_tee_time.pages.refresh_tee_sheet")
    @patch("PNCC_tee_time.pages.set_booking_date")
    @patch("PNCC_tee_time.pages.elements.wait_for_clickable")
    def test_select_date_calls_set_booking_date_and_refresh(
        self,
        mock_wait_for_clickable,
        mock_set_booking_date,
        mock_refresh_tee_sheet,
        mock_driver,
    ):
        """Should call set_booking_date and refresh_tee_sheet in order."""
        # Arrange
        test_date = dt.date(2026, 6, 15)

        # Act
        pages.select_date(mock_driver, test_date)

        # Assert
        mock_set_booking_date.assert_called_once_with(mock_driver, test_date)
        mock_refresh_tee_sheet.assert_called_once_with(mock_driver)


# ---------------------------------------------------------------------------
# refresh_tee_sheet
# ---------------------------------------------------------------------------


class TestRefreshTeeSheet:
    """Tests for refresh_tee_sheet()."""

    @patch("PNCC_tee_time.pages.elements.wait_for_visible")
    def test_refresh_tee_sheet_executes_javascript(
        self, mock_wait_for_visible, mock_driver
    ):
        """Should execute the RefreshTimes() JavaScript function."""
        # Arrange
        mock_wait_for_visible.return_value = MagicMock()

        # Act
        pages.refresh_tee_sheet(mock_driver)

        # Assert
        mock_driver.execute_script.assert_called_once()
        script = mock_driver.execute_script.call_args[0][0]
        assert "RefreshTimes" in script

    @patch("PNCC_tee_time.pages.elements.wait_for_visible")
    def test_refresh_tee_sheet_waits_for_ajax_panel(
        self, mock_wait_for_visible, mock_driver
    ):
        """Should wait for the Ajax panel to become visible."""
        # Arrange
        mock_wait_for_visible.return_value = MagicMock()

        # Act
        pages.refresh_tee_sheet(mock_driver)

        # Assert
        # First call should wait for AJAX panel
        first_call = mock_wait_for_visible.call_args_list[0]
        assert first_call[0][1] == locators.BOOKING_TIME_SLOT_AJAX_PANEL

    @patch("PNCC_tee_time.pages.elements.wait_for_visible")
    def test_refresh_tee_sheet_waits_for_slot_panel(
        self, mock_wait_for_visible, mock_driver
    ):
        """Should wait for the slot panel to become visible."""
        # Arrange
        mock_wait_for_visible.return_value = MagicMock()

        # Act
        pages.refresh_tee_sheet(mock_driver)

        # Assert
        # Second call should wait for slot panel
        second_call = mock_wait_for_visible.call_args_list[1]
        assert second_call[0][1] == locators.BOOKING_TIME_SLOT_PANEL


# ---------------------------------------------------------------------------
# get_available_slots
# ---------------------------------------------------------------------------


class TestGetAvailableSlots:
    """Tests for get_available_slots()."""

    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_returns_list(self, mock_find_elements, mock_driver):
        """Should return a list of WebElement objects."""
        # Arrange
        mock_slots = [MagicMock(), MagicMock(), MagicMock()]
        mock_find_elements.return_value = mock_slots

        # Act
        result = pages.get_available_slots(mock_driver)

        # Assert
        assert isinstance(result, list)
        assert result == mock_slots
        assert len(result) == 3

    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_returns_empty_when_none_available(
        self, mock_find_elements, mock_driver
    ):
        """Should return empty list when no slots available."""
        # Arrange
        mock_find_elements.return_value = []

        # Act
        result = pages.get_available_slots(mock_driver)

        # Assert
        assert result == []

    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_calls_find_elements_with_correct_locator(
        self, mock_find_elements, mock_driver
    ):
        """Should query the DOM using BOOKING_AVAILABLE_SLOTS locator."""
        # Arrange
        mock_find_elements.return_value = []

        # Act
        pages.get_available_slots(mock_driver)

        # Assert
        mock_find_elements.assert_called_once_with(
            mock_driver,
            locators.BOOKING_AVAILABLE_SLOTS,
            timeout=10,
        )

    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_returns_empty_on_wait_timeout(
        self, mock_find_elements, mock_driver
    ):
        """Should return empty list if available rows do not appear before timeout."""
        # Arrange
        mock_find_elements.side_effect = TimeoutException()

        # Act
        result = pages.get_available_slots(mock_driver)

        # Assert
        assert result == []


# ---------------------------------------------------------------------------
# get_slot_time
# ---------------------------------------------------------------------------


class TestGetSlotTime:
    """Tests for get_slot_time()."""

    def test_get_slot_time_extracts_time_string(self, mock_slot):
        """Should extract and return the time display string."""
        # Arrange
        mock_time_element = MagicMock()
        mock_time_element.text = "9:30 AM"
        mock_slot.find_element.return_value = mock_time_element

        with patch("PNCC_tee_time.pages._get_open_spots_from_slot", return_value=2):
            # Act
            time_str, open_spots = pages.get_slot_time(mock_slot)

            # Assert
            assert time_str == "9:30 AM"
            assert open_spots == 2

    def test_get_slot_time_strips_whitespace(self, mock_slot):
        """Should strip extra whitespace and newlines from time string."""
        # Arrange
        mock_time_element = MagicMock()
        mock_time_element.text = "  9:30 AM  \n  "
        mock_slot.find_element.return_value = mock_time_element

        with patch("PNCC_tee_time.pages._get_open_spots_from_slot", return_value=1):
            # Act
            time_str, open_spots = pages.get_slot_time(mock_slot)

            # Assert
            assert time_str == "9:30 AM"

    def test_get_slot_time_returns_tuple_with_time_and_open_spots(self, mock_slot):
        """Should return tuple of (time_str, open_spots)."""
        # Arrange
        mock_time_element = MagicMock()
        mock_time_element.text = "8:00 AM"
        mock_slot.find_element.return_value = mock_time_element

        with patch("PNCC_tee_time.pages._get_open_spots_from_slot", return_value=3):
            # Act
            result = pages.get_slot_time(mock_slot)

            # Assert
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[0] == "8:00 AM"
            assert result[1] == 3

    def test_get_slot_time_calls_correct_locator(self, mock_slot):
        """Should use BOOKING_SLOT_TIME_TEXT locator to find time element."""
        # Arrange
        mock_time_element = MagicMock()
        mock_time_element.text = "10:00 AM"
        mock_slot.find_element.return_value = mock_time_element

        with patch("PNCC_tee_time.pages._get_open_spots_from_slot", return_value=4):
            # Act
            pages.get_slot_time(mock_slot)

            # Assert
            mock_slot.find_element.assert_called_with(*locators.BOOKING_SLOT_TIME_TEXT)


# ---------------------------------------------------------------------------
# get_slot_players
# ---------------------------------------------------------------------------


class TestGetSlotPlayers:
    """Tests for get_slot_players()."""

    def test_get_slot_players_returns_empty_list_when_no_players(self, mock_slot):
        """Should return empty list when no player entries found."""
        # Arrange
        mock_slot.find_elements.return_value = []

        # Act
        result = pages.get_slot_players(mock_slot)

        # Assert
        assert result == []

    def test_get_slot_players_extracts_player_names(self, mock_slot):
        """Should extract player names from player entries."""
        # Arrange
        mock_player1 = MagicMock()
        mock_player2 = MagicMock()
        mock_name_elem1 = MagicMock()
        mock_name_elem1.text = "Lueckenbach, Bill"
        mock_name_elem2 = MagicMock()
        mock_name_elem2.text = "Doe, Jane"

        mock_player1.find_element.return_value = mock_name_elem1
        mock_player2.find_element.return_value = mock_name_elem2
        mock_slot.find_elements.return_value = [mock_player1, mock_player2]

        # Act
        result = pages.get_slot_players(mock_slot)

        # Assert
        assert result == ["Lueckenbach, Bill", "Doe, Jane"]

    def test_get_slot_players_skips_empty_names(self, mock_slot):
        """Should skip player entries that don't have a name."""
        # Arrange
        mock_player1 = MagicMock()
        mock_player2 = MagicMock()
        mock_name_elem = MagicMock()
        mock_name_elem.text = "Smith, Alex"

        mock_player1.find_element.side_effect = NoSuchElementException()
        mock_player2.find_element.return_value = mock_name_elem
        mock_slot.find_elements.return_value = [mock_player1, mock_player2]

        # Act
        result = pages.get_slot_players(mock_slot)

        # Assert
        assert result == ["Smith, Alex"]

    def test_get_slot_players_handles_stale_element(self, mock_slot):
        """Should handle StaleElementReferenceException gracefully."""
        # Arrange
        mock_slot.find_elements.side_effect = StaleElementReferenceException()

        # Act
        result = pages.get_slot_players(mock_slot)

        # Assert
        assert result == []

    def test_get_slot_players_uses_correct_locator(self, mock_slot):
        """Should use BOOKING_SLOT_PLAYER_ENTRY locator."""
        # Arrange
        mock_slot.find_elements.return_value = []

        # Act
        pages.get_slot_players(mock_slot)

        # Assert
        mock_slot.find_elements.assert_called_with(*locators.BOOKING_SLOT_PLAYER_ENTRY)


# ---------------------------------------------------------------------------
# _get_open_spots_from_slot
# ---------------------------------------------------------------------------


class TestGetOpenSpotsFromSlot:
    """Tests for _get_open_spots_from_slot()."""

    def test_get_open_spots_returns_4_when_no_reservations(self, mock_slot):
        """Should return 4 open spots when no reservation blocks found."""
        # Arrange
        mock_slot.find_elements.return_value = []

        # Act
        result = pages._get_open_spots_from_slot(mock_slot)

        # Assert
        assert result == 4

    def test_get_open_spots_parses_reservation_class_nc_reserved(self, mock_slot):
        """Should parse NC_Reserved class to extract occupied spots."""
        # Arrange
        mock_res_block = MagicMock()
        mock_res_block.get_attribute.return_value = "NC_Reserved2"
        mock_res_block.find_elements.return_value = []
        mock_slot.find_elements.return_value = [mock_res_block]

        # Act
        result = pages._get_open_spots_from_slot(mock_slot)

        # Assert
        assert result == 2  # 4 - 2 = 2 open

    def test_get_open_spots_parses_reservation_class_nc_reserved_today(self, mock_slot):
        """Should parse NC_ReservedToday class to extract occupied spots."""
        # Arrange
        mock_res_block = MagicMock()
        mock_res_block.get_attribute.return_value = "NC_ReservedToday3"
        mock_res_block.find_elements.return_value = []
        mock_slot.find_elements.return_value = [mock_res_block]

        # Act
        result = pages._get_open_spots_from_slot(mock_slot)

        # Assert
        assert result == 1  # 4 - 3 = 1 open

    def test_get_open_spots_counts_player_names_when_no_class_match(self, mock_slot):
        """Should count player entries when reservation class doesn't match."""
        # Arrange
        mock_res_block = MagicMock()
        mock_res_block.get_attribute.return_value = "someOtherClass"
        mock_player1 = MagicMock()
        mock_player2 = MagicMock()
        mock_res_block.find_elements.return_value = [mock_player1, mock_player2]
        mock_slot.find_elements.return_value = [mock_res_block]

        # Act
        result = pages._get_open_spots_from_slot(mock_slot)

        # Assert
        assert result == 2  # 4 - 2 = 2 open

    def test_get_open_spots_returns_zero_when_full(self, mock_slot):
        """Should return 0 when all 4 spots are occupied."""
        # Arrange
        mock_res_block = MagicMock()
        mock_res_block.get_attribute.return_value = "NC_Reserved4"
        mock_res_block.find_elements.return_value = []
        mock_slot.find_elements.return_value = [mock_res_block]

        # Act
        result = pages._get_open_spots_from_slot(mock_slot)

        # Assert
        assert result == 0

    def test_get_open_spots_never_goes_negative(self, mock_slot):
        """Should return 0 (not negative) if reservation count exceeds 4."""
        # Arrange
        mock_res_block = MagicMock()
        mock_res_block.get_attribute.return_value = "NC_Reserved5"  # Invalid but handle it
        mock_res_block.find_elements.return_value = []
        mock_slot.find_elements.return_value = [mock_res_block]

        # Act
        result = pages._get_open_spots_from_slot(mock_slot)

        # Assert
        assert result == 0

    def test_get_open_spots_sums_multiple_reservation_blocks(self, mock_slot):
        """Should sum occupied spots across multiple reservation blocks."""
        # Arrange
        mock_res_block1 = MagicMock()
        mock_res_block1.get_attribute.return_value = "NC_Reserved2"
        mock_res_block1.find_elements.return_value = []
        mock_res_block2 = MagicMock()
        mock_res_block2.get_attribute.return_value = "NC_Reserved1"
        mock_res_block2.find_elements.return_value = []
        mock_slot.find_elements.return_value = [mock_res_block1, mock_res_block2]

        # Act
        result = pages._get_open_spots_from_slot(mock_slot)

        # Assert
        assert result == 1  # 4 - 2 - 1 = 1 open


# ---------------------------------------------------------------------------
# select_time_slot
# ---------------------------------------------------------------------------


class TestSelectTimeSlot:
    """Tests for select_time_slot()."""

    def test_select_time_slot_finds_reserve_button(self, mock_slot):
        """Should find the reserve button within the slot."""
        # Arrange
        mock_reserve_btn = MagicMock()
        mock_slot.find_element.return_value = mock_reserve_btn

        # Act
        pages.select_time_slot(mock_slot)

        # Assert
        mock_slot.find_element.assert_called_once_with(*locators.BOOKING_RESERVE_BTN)

    def test_select_time_slot_clicks_reserve_button(self, mock_slot):
        """Should click the reserve button."""
        # Arrange
        mock_reserve_btn = MagicMock()
        mock_slot.find_element.return_value = mock_reserve_btn

        # Act
        pages.select_time_slot(mock_slot)

        # Assert
        mock_reserve_btn.click.assert_called_once()


# ---------------------------------------------------------------------------
# navigate_and_select_tee_time
# ---------------------------------------------------------------------------


class TestNavigateAndSelectTeeTime:
    """Tests for navigate_and_select_tee_time()."""

    @patch("PNCC_tee_time.pages.select_date")
    @patch("PNCC_tee_time.pages.base.open_page")
    def test_navigate_and_select_tee_time_opens_booking_page(
        self, mock_open_page, mock_select_date, mock_driver
    ):
        """Should navigate to the booking URL."""
        # Arrange
        test_date = dt.date(2026, 6, 20)
        preferred_times = ["8:00 AM", "8:10 AM"]
        players = ["Lueckenbach, Bill"]

        # Act
        result = pages.navigate_and_select_tee_time(
            mock_driver, test_date, preferred_times, players
        )

        # Assert
        mock_open_page.assert_called_once_with(mock_driver, locators.BOOKING_URL)

    @patch("PNCC_tee_time.pages.select_date")
    @patch("PNCC_tee_time.pages.base.open_page")
    def test_navigate_and_select_tee_time_selects_date(
        self, mock_open_page, mock_select_date, mock_driver
    ):
        """Should call select_date with the provided date."""
        # Arrange
        test_date = dt.date(2026, 6, 20)
        preferred_times = ["8:00 AM"]
        players = ["Lueckenbach, Bill"]

        # Act
        pages.navigate_and_select_tee_time(mock_driver, test_date, preferred_times, players)

        # Assert
        mock_select_date.assert_called_once_with(mock_driver, test_date)

    @patch("PNCC_tee_time.pages.select_date")
    @patch("PNCC_tee_time.pages.base.open_page")
    def test_navigate_and_select_tee_time_returns_false_when_incomplete(
        self, mock_open_page, mock_select_date, mock_driver
    ):
        """Should return False (function is incomplete with TODO sections)."""
        # Arrange
        test_date = dt.date(2026, 6, 20)
        preferred_times = ["8:00 AM"]
        players = ["Lueckenbach, Bill"]

        # Act
        result = pages.navigate_and_select_tee_time(
            mock_driver, test_date, preferred_times, players
        )

        # Assert
        assert result is False
