"""
date_time_utils.py
------------------
Helpers for date parsing, normalization, and booking request scheduling for 
PNCC tee time automation.

Functions:
    get_next_day_by_weekday(): Returns the next date for a given weekday name after 
                               a start date.
    get_tee_date(): Parses a date string (e.g. "Today", weekday, or date) 
                    into a datetime.date object.
    get_request_date(): Determines when to attempt the booking request based on the 
                        tee date.
    get_tee_times(): Parses a time string into a list of tee time strings in the format 
                     expected by the booking system.
"""

import datetime as dt
import logging

logger = logging.getLogger(__name__)


def parse_single_time(time_str: str) -> dt.time:
    """Parse a single time string into a datetime.time object.

    Accepted formats:
        - HHam / HHpm (e.g. "8am", "12pm")
        - HH:MMam / HH:MMpm (e.g. "8:30am")
        - HH:MM 24-hour format (e.g. "08:30", "16:00")

    Args:
        time_str: Time-only string to parse.

    Returns:
        Parsed datetime.time value.

    Raises:
        TypeError: If time_str is not a string.
        ValueError: If time_str does not match a supported format.
    """
    if not isinstance(time_str, str):
        raise TypeError("time_str must be a string.")

    normalized = time_str.strip().lower()
    if not normalized:
        raise ValueError("time_str cannot be empty.")

    formats = ("%I%p", "%I:%M%p", "%H:%M")
    for fmt in formats:
        try:
            return dt.datetime.strptime(normalized, fmt).time()
        except ValueError:
            continue

    raise ValueError(
        "Invalid time format. Accepted formats: HHam, HH:MMam, or HH:MM (24-hour)."
    )

def get_next_day_by_weekday(weekday_name: str, start_date: dt.date) -> dt.date:
    """Return the next date that falls on the specified weekday.

    Args:
        weekday_name: Name of the weekday (e.g. "Monday", "Tuesday", etc.).
        start_date: The date from which to start searching.

    Returns:
        A datetime.date object representing the next date that matches 
        the specified weekday.

    Raises:
        ValueError: If the input weekday name is not valid.
    """
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    weekday_name_lower = weekday_name.lower()
    if weekday_name_lower not in weekdays:
        raise ValueError(f"{weekday_name} is not a valid weekday.")
    target_weekday = weekdays[weekday_name_lower]
    if target_weekday == start_date.weekday():
        days_ahead = 7  # If the target day is today, return the same day next week
    else:
        days_ahead = (target_weekday - start_date.weekday() + 7) % 7
    return start_date + dt.timedelta(days=days_ahead)

def get_tee_date(date_str: str) -> dt.date:
    """Convert a date string into a datetime.date object.

    Accepts formats: "Today", "Tomorrow", weekday name, 
                      MM-DD-YY, MM-DD-YYYY, MM/DD/YY, MM/DD/YYYY.
    """
    today = dt.date.today()
    date_str = date_str.lower()
    if date_str == "today":
        return today
    elif date_str == "tomorrow":
        return today + dt.timedelta(days=1)
    elif date_str in (["monday", "tuesday", "wednesday", "thursday", "friday", 
                       "saturday", "sunday"]):
        return get_next_day_by_weekday(date_str, today)
    else:
        date_str = date_str.replace("/", "-")
        try:
            return dt.datetime.strptime(date_str, "%d-%m-%y").date()
        except ValueError:
            try:
                return dt.datetime.strptime(date_str, "%d-%m-%Y").date()
            except ValueError as err:
                raise ValueError(f"{date_str} is not a valid date format.") from err

def get_request_date(tee_date: dt.date) -> dt.date:
    """Determine the appropriate request date based on the tee_date.

    Returns the date on which to attempt the booking request.
    """
    today = dt.date.today()
    if not isinstance(tee_date, dt.date):
        raise TypeError("tee_date must be a datetime.date object.")
    if tee_date <= today:
        if tee_date == today:
            logger.warning("Tee time is today. Please call the Proshop to schedule.")
            print("Tee time is today. Please call the Proshop to schedule.")
        raise ValueError
    tee_day_of_week = tee_date.weekday()
    if tee_day_of_week == 5:  # Saturday
        if tee_date - today >= dt.timedelta(days=3):
            return tee_date - dt.timedelta(days=3)
        else:
            return today
    elif tee_day_of_week == 6:  # Sunday
        if tee_date - today >= dt.timedelta(days=4):
            return tee_date - dt.timedelta(days=4)
        else:
            return today
    elif tee_date - today > dt.timedelta(days=7):
        return tee_date - dt.timedelta(days=7)
    else:
        return today
def get_tee_times(tee_time_str: str) -> list[str]:
    """ Preferred tee time.\n'
        Accepted formats:\n'


    Args:
        tee_time_str (str): User Requested tee time in one of the accepted formats:
                            "HHam-HHam"   "8am-1pm"
                            "HH:MM-HH:MM" "08:00-13:00"
                            "HHam"        "8am"  is treated as earliest tee_time
                                                 after 08:00 and should return
                                                 ["8:00 AM", "8:10 AM", ...] up to 4pm.
                            "HH:MM"       "8:00" is treated as earliest tee_time
                                                 after 08:00 and should return
                                                 ["8:00 AM", "8:10 AM", ...] up to 4pm.

    Returns:
        list[str]: A list of tee time strings in the format expected by the booking 
                    system. (e.g. ["8:00 AM", "8:10 AM", "8:20 AM"])
    
    Raises:
        ValueError: If the input string is not in a recognized format or contains 
                    invalid time values.
        TypeError: If the input is not a string.
    """
    if not isinstance(tee_time_str, str):
        raise TypeError("tee_time_str must be a string.")

    
    # Initialize variables to hold the first and last times in the range
    first_time = NotImplemented
    last_time = NotImplemented

    # Normalize the input string by stripping whitespace and converting to lowercase
    tee_time_str = tee_time_str.strip().lower()

    # If the string contains a hyphen, we assume it's a range of times
    if "-" in tee_time_str:
        # Split the string into two parts and parse each part as a single time
        parts = tee_time_str.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid time range format: {tee_time_str}")
        first_time_str, last_time_str = parts
        #validate that both parts are in a valid time format and 
        # parse them into datetime.time objects
        first_time = parse_single_time(first_time_str)
        last_time = parse_single_time(last_time_str)
        if first_time >= last_time:
            raise ValueError(f"First time must be earlier than last time in range: "
                             f"{tee_time_str}") 
        elif (first_time < dt.time(hour=8, minute=0) or 
              last_time > dt.time(hour=16, minute=0)):
            raise ValueError(f"Tee times must be between 8:00 AM and 4:00 PM:"
                              f"{tee_time_str}")
    else:
        # If no hyphen, treat it as a single time and set last time to 4:00 PM
        first_time = parse_single_time(tee_time_str)
        last_time = dt.time(hour=16, minute=0)  # 4:00 PM   

    # Convert first_time and last_time to datetime.time objects so we can use
    #     - datetime arithmetic to generate the list of tee times.
    #     - use strftime to format the output strings to correct format (e.g. "8:00 AM")

    first_time_dt = dt.datetime.combine(dt.date.today(), first_time)
    last_time_dt = dt.datetime.combine(dt.date.today(), last_time)  

    # Generate the list of tee times in 10-minute intervals 
    # between first_time and last_time
    tee_times = []
    current_time = first_time_dt
    while current_time <= last_time_dt:
        tee_times.append(current_time.strftime("%#I:%M %p"))
        current_time += dt.timedelta(minutes=10)

    return tee_times




