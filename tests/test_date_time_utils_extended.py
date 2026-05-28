"""Extended unit tests for date_time_utils.py.

Tests for parse_single_time(), get_request_date(), and get_tee_times().
"""

import datetime as dt

import pytest

from PNCC_tee_time.date_time_utils import (
    get_request_date,
    get_tee_times,
    parse_single_time,
)

# ---------------------------------------------------------------------------
# parse_single_time
# ---------------------------------------------------------------------------


class TestParseSingleTime:
    """Tests for parse_single_time()."""

    def test_parse_single_time_12_hour_am_format(self):
        """Should parse 12-hour AM format (e.g. '8am')."""
        # Act
        result = parse_single_time("8am")

        # Assert
        assert result == dt.time(hour=8, minute=0)

    def test_parse_single_time_12_hour_pm_format(self):
        """Should parse 12-hour PM format (e.g. '1pm')."""
        # Act
        result = parse_single_time("1pm")

        # Assert
        assert result == dt.time(hour=13, minute=0)

    def test_parse_single_time_12_hour_with_minutes_am(self):
        """Should parse 12-hour format with minutes (e.g. '8:30am')."""
        # Act
        result = parse_single_time("8:30am")

        # Assert
        assert result == dt.time(hour=8, minute=30)

    def test_parse_single_time_12_hour_with_minutes_pm(self):
        """Should parse 12-hour format with minutes (e.g. '2:45pm')."""
        # Act
        result = parse_single_time("2:45pm")

        # Assert
        assert result == dt.time(hour=14, minute=45)

    def test_parse_single_time_24_hour_format(self):
        """Should parse 24-hour format (e.g. '08:30')."""
        # Act
        result = parse_single_time("08:30")

        # Assert
        assert result == dt.time(hour=8, minute=30)

    def test_parse_single_time_24_hour_afternoon(self):
        """Should parse 24-hour format for afternoon (e.g. '16:00')."""
        # Act
        result = parse_single_time("16:00")

        # Assert
        assert result == dt.time(hour=16, minute=0)

    def test_parse_single_time_case_insensitive(self):
        """Should be case-insensitive (e.g. 'AM' or 'am')."""
        # Act
        result1 = parse_single_time("8AM")
        result2 = parse_single_time("8am")

        # Assert
        assert result1 == result2 == dt.time(hour=8, minute=0)

    def test_parse_single_time_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        # Act
        result = parse_single_time("  8:30am  ")

        # Assert
        assert result == dt.time(hour=8, minute=30)

    def test_parse_single_time_noon(self):
        """Should handle noon (12pm)."""
        # Act
        result = parse_single_time("12pm")

        # Assert
        assert result == dt.time(hour=12, minute=0)

    def test_parse_single_time_midnight(self):
        """Should handle midnight (12am)."""
        # Act
        result = parse_single_time("12am")

        # Assert
        assert result == dt.time(hour=0, minute=0)

    def test_parse_single_time_raises_on_non_string(self):
        """Should raise TypeError if input is not a string."""
        # Act / Assert
        with pytest.raises(TypeError, match="time_str must be a string"):
            parse_single_time(830) # type: ignore this is an error case test

    def test_parse_single_time_raises_on_empty_string(self):
        """Should raise ValueError if input is empty or whitespace-only."""
        # Act / Assert
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_single_time("")

        with pytest.raises(ValueError, match="cannot be empty"):
            parse_single_time("   ")

    def test_parse_single_time_raises_on_invalid_format(self):
        """Should raise ValueError for unrecognized time format."""
        # Act / Assert
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_single_time("25:00")

        with pytest.raises(ValueError, match="Invalid time format"):
            parse_single_time("abc")

        with pytest.raises(ValueError, match="Invalid time format"):
            parse_single_time("8:30:45am")


# ---------------------------------------------------------------------------
# get_request_date
# ---------------------------------------------------------------------------


class TestGetRequestDate:
    """Tests for get_request_date()."""

    def test_get_request_date_today_raises_error(self):
        """Should raise error if tee_date is today."""
        # Arrange
        today = dt.date.today()

        # Act / Assert
        with pytest.raises(ValueError):
            get_request_date(today)

    def test_get_request_date_past_date_raises_error(self):
        """Should raise error if tee_date is in the past."""
        # Arrange
        yesterday = dt.date.today() - dt.timedelta(days=1)

        # Act / Assert
        with pytest.raises(ValueError):
            get_request_date(yesterday)

    def test_get_request_date_non_date_object_raises_error(self):
        """Should raise TypeError if tee_date is not a date object."""
        # Act / Assert
        with pytest.raises(TypeError, match="must be a datetime.date object"):
            get_request_date("2026-06-20") # type: ignore this is an error case test

    def test_get_request_date_saturday_three_days_before(self):
        """For Saturday tee dates 3+ days away, should request 3 days before."""
        # Arrange
        # Find next Saturday that's more than 3 days away
        today = dt.date.today()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        if days_until_saturday < 3:
            days_until_saturday += 7

        saturday = today + dt.timedelta(days=days_until_saturday)
        expected = saturday - dt.timedelta(days=3)

        # Act
        result = get_request_date(saturday)

        # Assert
        assert result == expected

    def test_get_request_date_sunday_four_days_before(self):
        """For Sunday tee dates 4+ days away, should request 4 days before."""
        # Arrange
        today = dt.date.today()
        days_until_sunday = (6 - today.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
        if days_until_sunday < 4:
            days_until_sunday += 7

        sunday = today + dt.timedelta(days=days_until_sunday)
        expected = sunday - dt.timedelta(days=4)

        # Act
        result = get_request_date(sunday)

        # Assert
        assert result == expected

    def test_get_request_date_weekday_seven_days_before(self):
        """For weekday tee dates 7+ days away, should request 7 days before."""
        # Arrange
        today = dt.date.today()
        # Use a Tuesday (weekday=1) that's 8 days away
        tuesday = today + dt.timedelta(days=8 - today.weekday() + 1)
        if tuesday.weekday() != 1:  # Ensure it's Tuesday
            tuesday = today + dt.timedelta(days=(1 - today.weekday()) % 7 + 7)

        expected = tuesday - dt.timedelta(days=7)

        # Act
        result = get_request_date(tuesday)

        # Assert
        assert result == expected

    def test_get_request_date_close_date_returns_today(self):
        """For near-term bookings, should return today."""
        # Arrange
        tomorrow = dt.date.today() + dt.timedelta(days=1)

        # Act
        result = get_request_date(tomorrow)

        # Assert
        assert result == dt.date.today()


# ---------------------------------------------------------------------------
# get_tee_times
# ---------------------------------------------------------------------------


class TestGetTeeTimes:
    """Tests for get_tee_times()."""

    def test_get_tee_times_single_time_returns_range_to_4pm(self):
        """Single time should return all 10-minute slots from that time to 4pm."""
        # Act
        result = get_tee_times("8am")

        # Assert
        assert len(result) > 0
        assert result[0] == "8:00 AM"
        assert result[-1] == "4:00 PM"

    def test_get_tee_times_time_range(self):
        """Time range should return slots between start and end."""
        # Act
        result = get_tee_times("8am-10am")

        # Assert
        assert len(result) == 13  # 8:00 to 10:00 in 10-min intervals
        assert result[0] == "8:00 AM"
        assert result[-1] == "10:00 AM"

    def test_get_tee_times_10_minute_intervals(self):
        """Should generate 10-minute intervals."""
        # Act
        result = get_tee_times("8am-8:30am")

        # Assert
        # 8:00, 8:10, 8:20, 8:30 = 4 slots
        assert len(result) == 4
        assert result == ["8:00 AM", "8:10 AM", "8:20 AM", "8:30 AM"]

    def test_get_tee_times_24_hour_format(self):
        """Should handle 24-hour format."""
        # Act
        result = get_tee_times("08:00-10:00")

        # Assert
        assert len(result) > 0
        assert result[0] == "8:00 AM"
        assert result[-1] == "10:00 AM"

    def test_get_tee_times_with_minutes(self):
        """Should handle times with minutes (e.g. 8:30am)."""
        # Act
        result = get_tee_times("8:30am")

        # Assert
        assert result[0] == "8:30 AM"

    def test_get_tee_times_case_insensitive(self):
        """Should be case-insensitive."""
        # Act
        result1 = get_tee_times("8AM-10AM")
        result2 = get_tee_times("8am-10am")

        # Assert
        assert result1 == result2

    def test_get_tee_times_raises_on_non_string(self):
        """Should raise TypeError if input is not a string."""
        # Act / Assert
        with pytest.raises(TypeError, match="tee_time_str must be a string"):
            get_tee_times(830) # type: ignore this is an error case test

    def test_get_tee_times_raises_on_empty_string(self):
        """Should raise ValueError on empty string."""
        # Act / Assert
        with pytest.raises(ValueError):
            get_tee_times("")

    def test_get_tee_times_raises_on_invalid_range_format(self):
        """Should raise ValueError if range has more than 2 parts."""
        # Act / Assert
        with pytest.raises(ValueError, match="Invalid time range format"):
            get_tee_times("8am-10am-12pm")

    def test_get_tee_times_raises_if_first_time_after_last(self):
        """Should raise ValueError if first time >= last time."""
        # Act / Assert
        with pytest.raises(ValueError, match="First time must be earlier"):
            get_tee_times("10am-8am")

        with pytest.raises(ValueError, match="First time must be earlier"):
            get_tee_times("8am-8am")

    def test_get_tee_times_raises_if_outside_booking_window(self):
        """Should raise ValueError if times outside 8am-4pm window."""
        # Act / Assert
        with pytest.raises(ValueError, match="must be between 8:00 AM and 4:00 PM"):
            get_tee_times("7am-9am")

        with pytest.raises(ValueError, match="must be between 8:00 AM and 4:00 PM"):
            get_tee_times("3pm-5pm")

    def test_get_tee_times_boundary_8am(self):
        """Should allow 8:00 AM as start time."""
        # Act
        result = get_tee_times("8am-9am")

        # Assert
        assert result[0] == "8:00 AM"

    def test_get_tee_times_boundary_4pm(self):
        """Should allow 4:00 PM as end time."""
        # Act
        result = get_tee_times("3pm")

        # Assert
        assert result[-1] == "4:00 PM"
