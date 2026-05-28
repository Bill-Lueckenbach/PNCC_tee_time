"""Unit tests for date_time_utils.py."""

import datetime as dt

import pytest

from PNCC_tee_time.date_time_utils import (
    get_next_day_by_weekday,
    get_tee_date,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WEEKDAY_NAMES = [
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
]

# A fixed Monday to use as a stable start_date baseline.
# 2026-05-11 is a Monday.
MONDAY = dt.date(2026, 5, 11)
START_DATES_BY_NAME = {
    name: MONDAY + dt.timedelta(days=index)
    for index, name in enumerate(WEEKDAY_NAMES)
}

# Explicit expected offsets for each start weekday -> target weekday pair.
EXPECTED_DAYS_AHEAD = {
    "monday": {
        "monday": 7,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    },
    "tuesday": {
        "monday": 6,
        "tuesday": 7,
        "wednesday": 1,
        "thursday": 2,
        "friday": 3,
        "saturday": 4,
        "sunday": 5,
    },
    "wednesday": {
        "monday": 5,
        "tuesday": 6,
        "wednesday": 7,
        "thursday": 1,
        "friday": 2,
        "saturday": 3,
        "sunday": 4,
    },
    "thursday": {
        "monday": 4,
        "tuesday": 5,
        "wednesday": 6,
        "thursday": 7,
        "friday": 1,
        "saturday": 2,
        "sunday": 3,
    },
    "friday": {
        "monday": 3,
        "tuesday": 4,
        "wednesday": 5,
        "thursday": 6,
        "friday": 7,
        "saturday": 1,
        "sunday": 2,
    },
    "saturday": {
        "monday": 2,
        "tuesday": 3,
        "wednesday": 4,
        "thursday": 5,
        "friday": 6,
        "saturday": 7,
        "sunday": 1,
    },
    "sunday": {
        "monday": 1,
        "tuesday": 2,
        "wednesday": 3,
        "thursday": 4,
        "friday": 5,
        "saturday": 6,
        "sunday": 7,
    },
}


# ---------------------------------------------------------------------------
# get_next_day_by_weekday
# ---------------------------------------------------------------------------


class TestGetNextDayByWeekday:
    """Tests for get_next_day_by_weekday()."""

    @pytest.mark.parametrize("start_name", WEEKDAY_NAMES)
    @pytest.mark.parametrize("target_name", WEEKDAY_NAMES)
    def test_wraparound_for_every_start_day(self, start_name, target_name):
        """Validate exact day offsets for every start/target weekday pair."""
        # Arrange
        start = START_DATES_BY_NAME[start_name]
        expected_days_ahead = EXPECTED_DAYS_AHEAD[start_name][target_name]
        expected = start + dt.timedelta(days=expected_days_ahead)

        # Act
        result = get_next_day_by_weekday(target_name, start_date=start)

        # Assert
        assert result == expected, (
            f"From {start_name} ({start}), target '{target_name}' should be "
            f"{expected_days_ahead} days ahead ({expected}), got {result}"
        )

    def test_next_tuesday_from_monday(self):
        """Asking for Tuesday from a Monday should return the very next day."""
        # Arrange
        start = MONDAY  # Monday 2026-05-11
        expected = MONDAY + dt.timedelta(days=1)

        # Act
        result = get_next_day_by_weekday("Tuesday", start_date=start)

        # Assert
        assert result == expected, (
            f"Expected next Tuesday ({expected}) from Monday {start}, got {result}"
        )

    def test_next_sunday_from_monday(self):
        """Asking for Sunday from a Monday should return 6 days ahead."""
        # Arrange
        start = MONDAY
        expected = MONDAY + dt.timedelta(days=6)

        # Act
        result = get_next_day_by_weekday("Sunday", start_date=start)

        # Assert
        assert result == expected, (
            f"Expected next Sunday ({expected}) from Monday {start}, got {result}"
        )

    def test_same_weekday_returns_next_week(self):
        """Asking for Monday from a Monday should return 7 days ahead, not today."""
        # Arrange
        start = MONDAY
        expected = MONDAY + dt.timedelta(days=7)

        # Act
        result = get_next_day_by_weekday("Monday", start_date=start)

        # Assert
        assert result == expected, (
            f"Same weekday should jump 7 days ahead. Expected {expected}, got {result}"
        )

    def test_case_insensitive_upper(self):
        """Weekday names should be accepted in any case - all uppercase."""
        # Arrange
        start = MONDAY
        expected_weekday = 5  # Saturday

        # Act
        result = get_next_day_by_weekday("SATURDAY", start_date=start)

        # Assert
        assert result.weekday() == expected_weekday, (
            f"Expected weekday 5 (Saturday), got weekday {result.weekday()} ({result})"
        )

    def test_case_insensitive_mixed(self):
        """Weekday names should be accepted in any case - mixed case."""
        # Arrange
        start = MONDAY
        expected_weekday = 2  # Wednesday

        # Act
        result = get_next_day_by_weekday("wEdNeSdAy", start_date=start)

        # Assert
        assert result.weekday() == expected_weekday, (
            f"Expected weekday 2 (Wednesday), got weekday {result.weekday()} ({result})"
        )

    @pytest.mark.parametrize("name", WEEKDAY_NAMES)
    def test_all_weekday_names_return_correct_weekday(self, name):
        """Each weekday name should return a date with the matching weekday number."""
        # Arrange
        expected_weekday = WEEKDAY_NAMES.index(name)

        # Act
        result = get_next_day_by_weekday(name, start_date=MONDAY)

        # Assert
        assert result.weekday() == expected_weekday, (
            f"'{name}' should return weekday {expected_weekday}, "
            f"got weekday {result.weekday()} ({result})"
        )

    @pytest.mark.parametrize("name", WEEKDAY_NAMES)
    def test_result_is_always_in_the_future(self, name):
        """Result should always be strictly after start_date."""
        # Arrange
        start = MONDAY

        # Act
        result = get_next_day_by_weekday(name, start_date=start)

        # Assert
        assert result > start, (
            f"Result {result} for '{name}' should be after start_date {start}"
        )

    @pytest.mark.parametrize("name", WEEKDAY_NAMES)
    def test_result_is_within_7_days(self, name):
        """Result should never be more than 7 days ahead of start_date."""
        # Arrange
        start = MONDAY
        max_date = MONDAY + dt.timedelta(days=7)

        # Act
        result = get_next_day_by_weekday(name, start_date=start)

        # Assert
        assert result <= max_date, (
            f"Result {result} for '{name}' is more than 7 days after {start} "
            f"(max {max_date})"
        )

    def test_invalid_weekday_raises_value_error(self):
        """An unrecognized weekday name should raise ValueError."""
        # Arrange
        invalid_name = "Funday"

        # Act / Assert
        with pytest.raises(ValueError, match=invalid_name):
            get_next_day_by_weekday(invalid_name, start_date=MONDAY)

    def test_empty_string_raises_value_error(self):
        """An empty string should raise ValueError."""
        # Arrange
        invalid_name = ""

        # Act / Assert
        with pytest.raises(ValueError):
            get_next_day_by_weekday(invalid_name, start_date=MONDAY)

    def test_returns_date_type(self):
        """Return value should be a datetime.date instance."""
        # Arrange
        start = MONDAY

        # Act
        result = get_next_day_by_weekday("Friday", start_date=start)

        # Assert
        assert isinstance(result, dt.date), (
            f"Expected a dt.date instance, got {type(result).__name__}: {result!r}"
        )


# ---------------------------------------------------------------------------
# get_tee_date
# ---------------------------------------------------------------------------


class TestGetTeDate:
    """Tests for get_tee_date()."""

    def test_today_returns_today(self):
        """'Today' should return today's date."""
        # Arrange
        expected = dt.date.today()

        # Act
        result = get_tee_date("Today")

        # Assert
        assert result == expected, (
            f"Expected 'Today' to return {expected}, got {result}"
        )

    def test_today_case_insensitive_raises(self):
        """'TODAY' and 'today' should also return today's date."""
        # Arrange
        expected = dt.date.today()

        # Act
        result_upper = get_tee_date("TODAY")
        result_lower = get_tee_date("today")

        # Assert
        assert result_upper == expected, (
            f"Expected 'TODAY' to return {expected}, got {result_upper}"
        )
        assert result_lower == expected, (
            f"Expected 'today' to return {expected}, got {result_lower}"
        )

    def test_tomorrow_returns_next_day(self):
        """'Tomorrow' should return today + 1 day."""
        # Arrange
        expected = dt.date.today() + dt.timedelta(days=1)

        # Act
        result = get_tee_date("Tomorrow")

        # Assert
        assert result == expected, (
            f"Expected 'Tomorrow' to return {expected}, got {result}"
        )

    def test_tomorrow_case_insensitive(self):
        """'TOMORROW' should return the same result as 'Tomorrow'."""
        # Arrange
        expected = dt.date.today() + dt.timedelta(days=1)

        # Act
        result = get_tee_date("TOMORROW")

        # Assert
        assert result == expected, (
            f"Expected 'TOMORROW' to return {expected}, got {result}"
        )

    @pytest.mark.parametrize("name", WEEKDAY_NAMES)
    def test_weekday_name_returns_future_date(self, name):
        """A weekday name should return a future date on that weekday."""
        # Arrange
        today = dt.date.today()

        # Act
        result = get_tee_date(name.capitalize())

        # Assert
        assert result > today, (
            f"Expected '{name}' to return a future date, got {result}"
        )
        assert result.weekday() == WEEKDAY_NAMES.index(name), (
            f"Expected '{name}' to return weekday {WEEKDAY_NAMES.index(name)}, "
            f"got {result.weekday()} ({result})"
        )

    def test_date_dd_mm_yyyy_format(self):
        """DD-MM-YYYY format should be parsed correctly."""
        # Arrange
        expected = dt.date(2026, 6, 15)

        # Act
        result = get_tee_date("15-06-2026")

        # Assert
        assert result == expected, (
            f"Expected '15-06-2026' to return {expected}, got {result}"
        )

    def test_date_dd_mm_yy_format(self):
        """DD-MM-YY format should be parsed correctly."""
        # Arrange
        expected = dt.date(2026, 6, 15)

        # Act
        result = get_tee_date("15-06-26")

        # Assert
        assert result == expected, (
            f"Expected '15-06-26' to return {expected}, got {result}"
        )

    def test_date_slash_separator(self):
        """Slash separators (DD/MM/YYYY) should be accepted."""
        # Arrange
        expected = dt.date(2026, 6, 15)

        # Act
        result = get_tee_date("15/06/2026")

        # Assert
        assert result == expected, (
            f"Expected '15/06/2026' to return {expected}, got {result}"
        )

    def test_invalid_date_raises_value_error(self):
        """An unrecognized string should raise ValueError."""
        # Arrange
        invalid = "not-a-date"

        # Act / Assert
        with pytest.raises(ValueError):
            get_tee_date(invalid)

    def test_returns_date_type(self):
        """Return value should be a datetime.date instance."""
        # Arrange / Act
        result = get_tee_date("15-06-2026")

        # Assert
        assert isinstance(result, dt.date), (
            f"Expected dt.date, got {type(result).__name__}: {result!r}"
        )
