"""Unit tests for pages.py.

All tests mock the Selenium WebDriver and WebElement objects so no real
browser or website is required. Integration tests that exercise the full
booking workflow against a live browser live in test_integration.py.
"""

import datetime as dt
from unittest.mock import MagicMock, patch

import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)

from PNCC_tee_time import locators, pages

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
# set_date
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
# set_date
# ---------------------------------------------------------------------------


class TestSelectDate:
    """Tests for set_date()."""

    @patch("PNCC_tee_time.pages.refresh_tee_sheet")
    @patch("PNCC_tee_time.pages.elements.send_keys")
    @patch("PNCC_tee_time.pages.elements.wait_for_clickable")
    def test_select_date_waits_for_date_input(
        self,
        mock_wait_for_clickable,
        mock_send_keys,
        mock_refresh_tee_sheet,
        mock_driver,
    ):
        """Should wait for date input to be clickable before setting."""
        # Arrange
        test_date = dt.date(2026, 6, 15)
        mock_wait_for_clickable.return_value = MagicMock()

        # Act
        pages.set_date(mock_driver, test_date)

        # Assert
        mock_wait_for_clickable.assert_called_once_with(
            mock_driver, locators.BOOKING_DATE
        )

    @patch("PNCC_tee_time.pages.refresh_tee_sheet")
    @patch("PNCC_tee_time.pages.elements.send_keys")
    @patch("PNCC_tee_time.pages.elements.wait_for_clickable")
    def test_select_date_calls_set_booking_date_and_refresh(
        self,
        mock_wait_for_clickable,
        mock_send_keys,
        mock_refresh_tee_sheet,
        mock_driver,
    ):
        """Should type the date and then refresh the tee sheet."""
        # Arrange
        test_date = dt.date(2026, 6, 15)

        # Act
        pages.set_date(mock_driver, test_date)

        # Assert
        mock_send_keys.assert_called_once_with(
            mock_driver,
            locators.BOOKING_DATE,
            "6/15/2026",
        )
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

    @patch("PNCC_tee_time.pages.get_num_of_open_spots_in_slot", return_value=4)
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_returns_list(
        self, mock_find_elements, mock_get_open_spots, mock_driver
    ):
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
        assert mock_get_open_spots.call_count == 3

    @patch("PNCC_tee_time.pages.get_num_of_open_spots_in_slot", return_value=0)
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_returns_empty_when_none_available(
        self, mock_find_elements, mock_get_open_spots, mock_driver
    ):
        """Should return empty list when no slots available."""
        # Arrange
        mock_find_elements.return_value = [MagicMock()]

        # Act
        result = pages.get_available_slots(mock_driver)

        # Assert
        assert result == []
        mock_get_open_spots.assert_called_once()

    @patch("PNCC_tee_time.pages.get_num_of_open_spots_in_slot", return_value=4)
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_calls_find_elements_with_correct_locator(
        self, mock_find_elements, mock_get_open_spots, mock_driver
    ):
        """Should query the DOM using BOOKING_AVAILABLE_SLOTS locator."""
        # Arrange
        mock_find_elements.return_value = [MagicMock()]

        # Act
        pages.get_available_slots(mock_driver)

        # Assert
        mock_find_elements.assert_called_once_with(
            mock_driver,
            locators.BOOKING_AVAILABLE_SLOTS,
            timeout=10,
        )
        mock_get_open_spots.assert_called_once()

    @patch("PNCC_tee_time.pages.get_num_of_open_spots_in_slot")
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_returns_empty_on_wait_timeout(
        self, mock_find_elements, mock_get_open_spots, mock_driver
    ):
        """Should return empty list if available rows do not appear before timeout."""
        # Arrange
        mock_find_elements.side_effect = TimeoutException()

        # Act
        result = pages.get_available_slots(mock_driver)

        # Assert
        assert result == []
        mock_get_open_spots.assert_not_called()

    @patch("PNCC_tee_time.pages.get_num_of_open_spots_in_slot")
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_get_available_slots_filters_by_num_of_players(
        self, mock_find_elements, mock_get_open_spots, mock_driver
    ):
        """Should keep slots with open spots >= num_of_players 
        when joining is allowed."""
        # Arrange
        slot1 = MagicMock()
        slot2 = MagicMock()
        slot3 = MagicMock()
        mock_find_elements.return_value = [slot1, slot2, slot3]
        mock_get_open_spots.side_effect = [1, 2, 4]

        # Act
        result = pages.get_available_slots(
            mock_driver,
            num_of_players=2,
            join_group=True,
        )

        # Assert
        assert result == [slot2, slot3]


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

        # Act
        time_str = pages.get_slot_time(mock_slot)

        # Assert
        assert time_str == "9:30 AM"

    def test_get_slot_time_strips_whitespace(self, mock_slot):
        """Should strip extra whitespace and newlines from time string."""
        # Arrange
        mock_time_element = MagicMock()
        mock_time_element.text = "  9:30 AM  \n  "
        mock_slot.find_element.return_value = mock_time_element

        # Act
        time_str = pages.get_slot_time(mock_slot)

        # Assert
        assert time_str == "9:30 AM"

    def test_get_slot_time_returns_string(self, mock_slot):
        """Should return the slot time as a string."""
        # Arrange
        mock_time_element = MagicMock()
        mock_time_element.text = "8:00 AM"
        mock_slot.find_element.return_value = mock_time_element

        # Act
        result = pages.get_slot_time(mock_slot)

        # Assert
        assert isinstance(result, str)
        assert result == "8:00 AM"

    def test_get_slot_time_calls_correct_locator(self, mock_slot):
        """Should use BOOKING_SLOT_TIME_TEXT locator to find time element."""
        # Arrange
        mock_time_element = MagicMock()
        mock_time_element.text = "10:00 AM"
        mock_slot.find_element.return_value = mock_time_element

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
# get_num_of_open_spots_in_slot
# ---------------------------------------------------------------------------


class TestGetNumOfOpenSpotsInSlot:
    """Tests for get_num_of_open_spots_in_slot()."""

    def test_get_open_spots_returns_4_when_no_reservations(self, mock_slot):
        """Should return 4 open spots when no reservation blocks found."""
        # Arrange
        mock_slot.find_elements.return_value = []

        # Act
        result = pages.get_num_of_open_spots_in_slot(mock_slot)

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
        result = pages.get_num_of_open_spots_in_slot(mock_slot)

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
        result = pages.get_num_of_open_spots_in_slot(mock_slot)

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
        result = pages.get_num_of_open_spots_in_slot(mock_slot)

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
        result = pages.get_num_of_open_spots_in_slot(mock_slot)

        # Assert
        assert result == 0

    def test_get_open_spots_never_goes_negative(self, mock_slot):
        """Should return 0 (not negative) if reservation count exceeds 4."""
        # Arrange
        mock_res_block = MagicMock()
        mock_res_block.get_attribute.return_value = "NC_Reserved5"  # Invalid but handle
        mock_res_block.find_elements.return_value = []
        mock_slot.find_elements.return_value = [mock_res_block]

        # Act
        result = pages.get_num_of_open_spots_in_slot(mock_slot)

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
        result = pages.get_num_of_open_spots_in_slot(mock_slot)

        # Assert
        assert result == 1  # 4 - 2 - 1 = 1 open


# ---------------------------------------------------------------------------
# click_reserve_button
# ---------------------------------------------------------------------------


class TestSelectTimeSlot:
    """Tests for click_reserve_button()."""

    def test_select_time_slot_finds_reserve_button(self, mock_slot):
        """Should find the reserve button within the slot."""
        # Arrange
        mock_reserve_btn = MagicMock()
        mock_slot.find_element.return_value = mock_reserve_btn

        # Act
        pages.click_reserve_button(mock_slot)

        # Assert
        mock_slot.find_element.assert_called_once_with(*locators.BOOKING_RESERVE_BTN)

    def test_select_time_slot_clicks_reserve_button(self, mock_slot):
        """Should click the reserve button."""
        # Arrange
        mock_reserve_btn = MagicMock()
        mock_slot.find_element.return_value = mock_reserve_btn

        # Act
        pages.click_reserve_button(mock_slot)

        # Assert
        mock_reserve_btn.click.assert_called_once()

class TestSelectPartySize:
    """Tests for _select_party_size()."""

    def test_select_party_size_missing_input_is_allowed_for_single_player(
        self, mock_driver
    ):
        """Should allow single-player booking when Party Size is absent."""
        mock_driver.find_element.side_effect = NoSuchElementException()
        mock_driver.find_elements.return_value = []

        pages._select_party_size(mock_driver, 1)

    def test_select_party_size_missing_input_raises_for_multi_player(
        self, mock_driver
    ):
        """Should fail when Party Size control is absent for multi-player booking."""
        mock_driver.find_element.side_effect = NoSuchElementException()
        mock_driver.find_elements.return_value = []

        with pytest.raises(RuntimeError, match="Party Size control was not found"):
            pages._select_party_size(mock_driver, 2)

    @patch("PNCC_tee_time.pages.elements.click")
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_select_party_size_skips_when_current_value_matches(
        self, mock_find_elements, mock_click, mock_driver
    ):
        """Should not open dropdown if current value already matches target."""
        # Arrange
        input_el = MagicMock()
        input_el.get_attribute.return_value = "Foursome"
        mock_driver.find_element.return_value = input_el

        # Act
        pages._select_party_size(mock_driver, 4)

        # Assert
        mock_click.assert_not_called()
        mock_find_elements.assert_not_called()

    @patch("PNCC_tee_time.pages.elements.click")
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_select_party_size_selects_matching_option(
        self, mock_find_elements, mock_click, mock_driver
    ):
        """Should open the party-size dropdown and click the matching item."""
        # Arrange
        input_el = MagicMock()
        input_el.get_attribute.return_value = "Foursome"
        mock_driver.find_element.return_value = input_el

        twosome_option = MagicMock()
        twosome_option.text = "Twosome"
        twosome_option.is_displayed.return_value = True
        foursome_option = MagicMock()
        foursome_option.text = "Foursome"
        foursome_option.is_displayed.return_value = True
        mock_find_elements.return_value = [foursome_option, twosome_option]

        # Act
        pages._select_party_size(mock_driver, 2)

        # Assert
        mock_click.assert_called_once_with(
            mock_driver,
            locators.BOOK_TEE_TIME_PARTY_SIZE_ARROW,
        )
        mock_find_elements.assert_called_once_with(
            mock_driver,
            locators.BOOK_TEE_TIME_PARTY_SIZE_OPTIONS,
            timeout=5,
        )
        mock_driver.execute_script.assert_called_once_with(
            "arguments[0].click();",
            twosome_option,
        )

    @patch("PNCC_tee_time.pages.elements.click")
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_select_party_size_retries_open_with_js_when_no_visible_options(
        self, mock_find_elements, mock_click, mock_driver
    ):
        """Should JS-click the arrow if first dropdown open has no visible options."""
        # Arrange
        input_el = MagicMock()
        input_el.get_attribute.return_value = "Foursome"
        mock_driver.find_element.return_value = input_el

        hidden_option = MagicMock()
        hidden_option.text = "Twosome"
        hidden_option.is_displayed.return_value = False

        visible_option = MagicMock()
        visible_option.text = "Twosome"
        visible_option.is_displayed.return_value = True

        mock_find_elements.side_effect = [[hidden_option], [visible_option]]

        # Act
        pages._select_party_size(mock_driver, 2)

        # Assert
        assert mock_find_elements.call_count == 2
        assert mock_driver.execute_script.call_count == 2
        first_script_call = mock_driver.execute_script.call_args_list[0]
        second_script_call = mock_driver.execute_script.call_args_list[1]
        assert first_script_call.args[0] == "arguments[0].click();"
        assert second_script_call.args[0] == "arguments[0].click();"
        assert second_script_call.args[1] == visible_option

    @patch("PNCC_tee_time.pages.elements.click")
    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_select_party_size_raises_when_no_matching_option(
        self, mock_find_elements, mock_click, mock_driver
    ):
        """Should raise RuntimeError if dropdown does not contain target size."""
        # Arrange
        input_el = MagicMock()
        input_el.get_attribute.return_value = "Foursome"
        mock_driver.find_element.return_value = input_el

        only_option = MagicMock()
        only_option.text = "Foursome"
        mock_find_elements.return_value = [only_option]

        # Act / Assert
        with pytest.raises(RuntimeError, match="Unable to select party size"):
            pages._select_party_size(mock_driver, 2)


# ---------------------------------------------------------------------------
# set_tee_time
# ---------------------------------------------------------------------------


class TestSetTeeTime:
    """Tests for set_tee_time()."""

    @patch("PNCC_tee_time.pages._switch_to_form_iframe", return_value=False)
    @patch("PNCC_tee_time.pages.click_reserve_button")
    def test_set_tee_time_returns_false_when_form_iframe_not_found(
        self,
        mock_click_reserve_button,
        mock_switch_to_form_iframe,
        mock_driver,
        mock_slot,
    ):
        """Should return False when the booking form iframe cannot be found."""
        # Arrange
        players = ["Lueckenbach, Bill"]

        # Act
        result = pages._set_tee_time(mock_driver, mock_slot, players, riding=True)

        # Assert
        mock_click_reserve_button.assert_called_once_with(mock_slot)
        mock_switch_to_form_iframe.assert_called_once_with(mock_driver)
        assert result is False

    @patch("PNCC_tee_time.pages._switch_to_form_iframe", return_value=True)
    @patch("PNCC_tee_time.pages._set_riding_option")
    @patch("PNCC_tee_time.pages._enter_player_names")
    @patch("PNCC_tee_time.pages._select_party_size")
    @patch("PNCC_tee_time.pages.elements.wait_for_visible")
    @patch("PNCC_tee_time.pages.click_reserve_button")
    def test_set_tee_time_waits_for_booking_form(
        self,
        mock_click_reserve_button,
        mock_wait_for_visible,
        mock_select_party_size,
        mock_enter_player_names,
        mock_set_riding_option,
        mock_switch_to_form_iframe,
        mock_driver,
        mock_slot,
    ):
        """Should wait for Book Tee Time form after clicking Reserve."""
        # Arrange
        players = ["Lueckenbach, Bill"]

        # Act
        result = pages._set_tee_time(mock_driver, mock_slot, players, riding=True)

        # Assert
        mock_click_reserve_button.assert_called_once_with(mock_slot)
        mock_switch_to_form_iframe.assert_called_once_with(mock_driver)
        mock_wait_for_visible.assert_called_once_with(
            mock_driver,
            locators.BOOK_TEE_TIME_PARTY_SIZE_INPUT,
            timeout=10,
        )
        mock_select_party_size.assert_called_once_with(mock_driver, len(players))
        mock_enter_player_names.assert_called_once()
        assert mock_enter_player_names.call_args[0][0] == mock_driver
        assert mock_enter_player_names.call_args[0][1] == players
        mock_set_riding_option.assert_called_once_with(
            mock_driver,
            True,
        )
        assert result is True

    @patch("PNCC_tee_time.pages._switch_to_form_iframe", return_value=True)
    @patch("PNCC_tee_time.pages._set_riding_option")
    @patch("PNCC_tee_time.pages._enter_player_names")
    @patch("PNCC_tee_time.pages._select_party_size")
    @patch("PNCC_tee_time.pages.elements.wait_for_visible")
    @patch("PNCC_tee_time.pages.click_reserve_button")
    def test_set_tee_time_continues_when_party_size_wait_times_out(
        self,
        mock_click_reserve_button,
        mock_wait_for_visible,
        mock_select_party_size,
        mock_enter_player_names,
        mock_set_riding_option,
        mock_switch_to_form_iframe,
        mock_driver,
        mock_slot,
    ):
        """Should continue booking flow even when Party Size wait times out."""
        # Arrange
        players = ["Lueckenbach, Bill"]
        mock_wait_for_visible.side_effect = TimeoutException()
        # Act
        result = pages._set_tee_time(mock_driver, mock_slot, players, riding=False)

        # Assert
        mock_click_reserve_button.assert_called_once_with(mock_slot)
        mock_switch_to_form_iframe.assert_called_once_with(mock_driver)
        mock_wait_for_visible.assert_called_once_with(
            mock_driver,
            locators.BOOK_TEE_TIME_PARTY_SIZE_INPUT,
            timeout=10,
        )
        mock_select_party_size.assert_called_once_with(mock_driver, len(players))
        mock_enter_player_names.assert_called_once()
        mock_set_riding_option.assert_called_once_with(mock_driver, False)
        assert result is True


class TestSetRidingOption:
    """Tests for _set_riding_option()."""

    @patch("PNCC_tee_time.pages.elements.find_elements")
    def test_set_riding_option_selects_walking_when_current_is_riding(
        self, mock_find_elements, mock_driver
    ):
        """Should open transport dropdown and select Walking option."""
        # Arrange
        transport_input = MagicMock()
        transport_input.is_displayed.return_value = True
        transport_input.is_enabled.return_value = True
        transport_input.get_attribute.side_effect = (
            lambda name: {
                "id": "ctl00_ctrl_MakeTeeTime_P2_transport_oCombo_Input",
                "value": "Riding",
            }.get(name, "")
        )
        mock_driver.find_elements.return_value = [transport_input]

        arrow = MagicMock()
        mock_driver.find_element.return_value = arrow

        riding_option = MagicMock()
        riding_option.text = "Riding"
        walking_option = MagicMock()
        walking_option.text = "Walking"
        mock_find_elements.return_value = [riding_option, walking_option]

        # Act
        pages._set_riding_option(mock_driver, riding=False)

        # Assert
        mock_driver.find_element.assert_called_once_with(
            pages.By.ID,
            "ctl00_ctrl_MakeTeeTime_P2_transport_oCombo_Arrow",
        )
        mock_find_elements.assert_called_once_with(
            mock_driver,
            (
                pages.By.CSS_SELECTOR,
                "#ctl00_ctrl_MakeTeeTime_P2_transport_oCombo_DropDown li.rcbItem",
            ),
            timeout=5,
        )
        assert mock_driver.execute_script.call_count == 2
        assert mock_driver.execute_script.call_args_list[0].args[1] == arrow
        assert mock_driver.execute_script.call_args_list[1].args[1] == walking_option

    def test_set_riding_option_noops_when_no_transport_inputs(self, mock_driver):
        """Should return without error when transport controls are absent."""
        # Arrange
        mock_driver.find_elements.return_value = []

        # Act
        pages._set_riding_option(mock_driver, riding=True)

        # Assert
        mock_driver.execute_script.assert_not_called()

    @patch("PNCC_tee_time.pages._switch_to_form_iframe", return_value=True)
    @patch("PNCC_tee_time.pages._set_riding_option")
    @patch("PNCC_tee_time.pages._enter_player_names")
    @patch("PNCC_tee_time.pages._select_party_size")
    @patch("PNCC_tee_time.pages.elements.wait_for_visible")
    @patch("PNCC_tee_time.pages.click_reserve_button")
    def test_set_tee_time_returns_false_when_party_size_cannot_be_set(
        self,
        mock_click_reserve_button,
        mock_wait_for_visible,
        mock_select_party_size,
        mock_enter_player_names,
        mock_set_riding_option,
        mock_switch_to_form_iframe,
        mock_driver,
        mock_slot,
    ):
        """Should return False if selecting party size fails."""
        # Arrange
        players = ["Lueckenbach, Bill", "Lueckenbach, Andrew"]
        mock_select_party_size.side_effect = RuntimeError("party-size failed")

        # Act
        result = pages._set_tee_time(mock_driver, mock_slot, players, riding=True)

        # Assert
        mock_click_reserve_button.assert_called_once_with(mock_slot)
        mock_switch_to_form_iframe.assert_called_once_with(mock_driver)
        mock_wait_for_visible.assert_called_once_with(
            mock_driver,
            locators.BOOK_TEE_TIME_PARTY_SIZE_INPUT,
            timeout=10,
        )
        mock_select_party_size.assert_called_once_with(mock_driver, len(players))
        mock_enter_player_names.assert_not_called()
        mock_set_riding_option.assert_not_called()
        assert result is False

    @patch("PNCC_tee_time.pages._switch_to_form_iframe", return_value=True)
    @patch("PNCC_tee_time.pages._set_riding_option")
    @patch("PNCC_tee_time.pages._enter_player_names")
    @patch("PNCC_tee_time.pages._select_party_size")
    @patch("PNCC_tee_time.pages.elements.wait_for_visible")
    @patch("PNCC_tee_time.pages.click_reserve_button")
    def test_set_tee_time_returns_false_when_player_names_cannot_be_entered(
        self,
        mock_click_reserve_button,
        mock_wait_for_visible,
        mock_select_party_size,
        mock_enter_player_names,
        mock_set_riding_option,
        mock_switch_to_form_iframe,
        mock_driver,
        mock_slot,
    ):
        """Should return False if entering player names fails."""
        # Arrange
        players = ["Lueckenbach, Bill", "Lueckenbach, Andrew"]
        mock_enter_player_names.side_effect = RuntimeError("player inputs missing")

        # Act
        result = pages._set_tee_time(mock_driver, mock_slot, players, riding=True)

        # Assert
        mock_click_reserve_button.assert_called_once_with(mock_slot)
        mock_switch_to_form_iframe.assert_called_once_with(mock_driver)
        mock_wait_for_visible.assert_called_once_with(
            mock_driver,
            locators.BOOK_TEE_TIME_PARTY_SIZE_INPUT,
            timeout=10,
        )
        mock_select_party_size.assert_called_once_with(mock_driver, len(players))
        mock_enter_player_names.assert_called_once_with(
            mock_driver,
            players,
        )
        mock_set_riding_option.assert_not_called()
        assert result is False


# ---------------------------------------------------------------------------
# navigate_and_select_tee_time
# ---------------------------------------------------------------------------


class TestNavigateAndSelectTeeTime:
    """Tests for navigate_and_select_tee_time()."""

    @patch("PNCC_tee_time.pages.get_slot", return_value=None)
    @patch("PNCC_tee_time.pages.get_available_slots", return_value=[])
    @patch("PNCC_tee_time.pages.set_date")
    @patch("PNCC_tee_time.pages.base.open_page")
    def test_navigate_and_select_tee_time_opens_booking_page(
        self,
        mock_open_page,
        mock_set_date,
        mock_get_available_slots,
        mock_get_slot,
        mock_driver,
    ):
        """Should navigate to the booking URL."""
        # Arrange
        test_date = dt.date(2026, 6, 20)
        preferred_times = ["8:00 AM", "8:10 AM"]
        players = ["Lueckenbach, Bill"]

        # Act
        pages.navigate_and_select_tee_time(
            mock_driver, test_date, preferred_times, players
        )

        # Assert
        mock_open_page.assert_called_once_with(mock_driver, locators.BOOKING_URL)

    @patch("PNCC_tee_time.pages.get_slot", return_value=None)
    @patch("PNCC_tee_time.pages.get_available_slots", return_value=[])
    @patch("PNCC_tee_time.pages.set_date")
    @patch("PNCC_tee_time.pages.base.open_page")
    def test_navigate_and_select_tee_time_selects_date(
        self,
        mock_open_page,
        mock_set_date,
        mock_get_available_slots,
        mock_get_slot,
        mock_driver,
    ):
        """Should call set_date with the provided date."""
        # Arrange
        test_date = dt.date(2026, 6, 20)
        preferred_times = ["8:00 AM"]
        players = ["Lueckenbach, Bill"]

        # Act
        pages.navigate_and_select_tee_time(mock_driver,
                                            test_date, 
                                            preferred_times, 
                                            players,
        )
        # Assert
        mock_set_date.assert_called_once_with(mock_driver, test_date)

    @patch("PNCC_tee_time.pages.get_slot", return_value=None)
    @patch("PNCC_tee_time.pages.get_available_slots", return_value=[])
    @patch("PNCC_tee_time.pages.set_date")
    @patch("PNCC_tee_time.pages.base.open_page")
    def test_navigate_and_select_tee_time_returns_false_when_incomplete(
        self,
        mock_open_page,
        mock_set_date,
        mock_get_available_slots,
        mock_get_slot,
        mock_driver,
    ):
        """Should return False when no preferred slot is found."""
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
