"""High-level page automation functions for the PNCC tee-time booking flow.

Each function in this module represents a meaningful step in the end-to-end
workflow. They utilize the low-level helpers from base.py and elements.py
with the locators from locators.py to express what the automation does in
plain, readable terms.

Functions in this module:
    - login(driver, username, password, remember_me=True)
        Fill and submit the login form, then wait for page navigation to
        complete.
    - set_remember_me(driver, enabled)
        Toggle the Remember Me checkbox only when the current state differs
        from the desired state.
    - select_date(driver, date)
        Set the booking date and refresh the tee sheet so updated slots are
        visible.
    - prepare_booking_date(driver, date)
        Populate the booking date input field without triggering the tee-sheet
        refresh.
    - refresh_tee_sheet(driver)
        Click Update Tee Sheet and wait until slot panels are visible.
    - get_available_slots(driver, players=1)
        Return currently bookable slot row elements from the loaded tee sheet.
    - get_slot_time(slot)
        Extract and return the display time label and open spots from a slot row.
    - get_slot_players(slot)
        Extract and return the list of player names booked in a slot row.
    - select_time_slot(slot)
        Click the Reserve control inside a selected slot row.
    - navigate_and_select_tee_time(driver, date, preferred_times, players=1)
        Open the booking page, load the date, and reserve the first available
        slot matching preferred_times.

Functions are intentionally thin orchestration layers; complex waiting or
clicking logic lives in elements.py, not here.
"""

import datetime as dt
import logging
import re

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from PNCC_tee_time import base, elements, locators

logger = logging.getLogger(__name__)

# --- Login Page ---

def login(
    driver: WebDriver, username: str, password: str, *, remember_me: bool = True
) -> None:
    """Fill in and submit the PNCC login form.

    Assumes the driver is already on the login page (call
    base.open_page(driver, locators.LOGIN_URL) first).

    Args:
        driver:      An active Selenium WebDriver instance.
        username:    PNCC member username.
        password:    PNCC member password.
        remember_me: Check the Remember Me box if True. Defaults to True.
    """
    elements.send_keys(driver, locators.LOGIN_USERNAME, username)
    elements.send_keys(driver, locators.LOGIN_PASSWORD, password)

    set_remember_me(driver, enabled=remember_me)

    elements.click_by_js(driver, locators.LOGIN_SUBMIT)
    WebDriverWait(driver, 10).until(lambda d: locators.LOGIN_URL not in d.current_url)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def set_remember_me(driver: WebDriver, *, enabled: bool) -> None:
    """Set the Remember Me checkbox to the requested state.

    The checkbox is only clicked when its current selected state differs from
    the requested `enabled` value. This prevents accidental toggling when the
    page already reflects the desired state. Some login page variants do not
    render a Remember Me checkbox at all, so this helper treats the checkbox
    as optional and returns without error when it is absent.

    Args:
        driver: An active Selenium WebDriver instance.
        enabled: Desired checkbox state. True checks the box, False leaves it
                 unchecked.
    """
    checkboxes = driver.find_elements(*locators.LOGIN_REMEMBER_ME)
    if not checkboxes:
        return

    checkbox = checkboxes[0]
    is_checked = checkbox.is_selected()
    if is_checked != enabled:
        driver.execute_script("arguments[0].click();", checkbox)

# --- Booking Page ---
def select_date(driver: WebDriver, date: dt.date) -> None:
    """Set the booking date and refresh the tee sheet.

    Clears the date input, types the desired date in M/D/YYYY format, then
    clicks the Update Tee Sheet button to trigger an Ajax reload of the
    available time slots.  Waits for the time slot panel to be visible
    before returning so callers can immediately query the refreshed slots.

    Args:
        driver: An active Selenium WebDriver instance, already on the
                booking page.
        date:   Date object representing the desired booking date.

    Steps:
    [X] Clear the date input field to ensure no residual text interferes with typing.
    [X] Type the desired date string into the date input field.
    [X] Click the Update Tee Sheet button to trigger the page refresh.

    """
    elements.wait_for_clickable(driver, locators.BOOKING_DATE)
    set_booking_date(driver, date)
    refresh_tee_sheet(driver)

    # In DEBUG mode, emit a breadcrumb once the booking page is updated.
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Booking page was updated; continuing with slot selection.",
        )

    return None


def set_booking_date(driver: WebDriver, date: dt.date) -> None:
    """Populate the booking date field without refreshing the tee sheet.

    Use this when pre-staging the page before the booking window opens.

    Args:
        driver: An active Selenium WebDriver instance, already on the
                booking page.
        date: Date object representing the desired booking date.
    """
    date_str = f"{date.month}/{date.day}/{date.year}"
    elements.send_keys(driver, locators.BOOKING_DATE, date_str)


def refresh_tee_sheet(driver: WebDriver) -> None:
    """Click Update Tee Sheet and wait for the tee slot panel to render.

    Args:
        driver: An active Selenium WebDriver instance, already on the
                booking page.
    """
    # The booking page's "Update Tee Sheet" control is wired to a global
    # JavaScript function named RefreshTimes(). On this Telerik/Ajax page,
    # Selenium's normal click flow can be unreliable due to dynamic overlays,
    # partial postbacks, and transient DOM state. Calling the function directly
    # avoids those timing issues while still triggering the exact site behavior.
    driver.execute_script("if (typeof RefreshTimes === 'function') { RefreshTimes(); }")

    # RefreshTimes() launches an asynchronous partial-page update. During the
    # update, the Ajax panel can be hidden/replaced and slot markup may be
    # incomplete. Wait for the wrapper first to ensure the async refresh cycle
    # has progressed far enough for slot content to be rendered.
    elements.wait_for_visible(driver, locators.BOOKING_TIME_SLOT_AJAX_PANEL)

    # Then wait for the inner slot panel itself. This second wait confirms that
    # the tee-sheet rows are visible and ready for downstream queries such as
    # get_available_slots() and get_slot_time().
    elements.wait_for_visible(driver, locators.BOOKING_TIME_SLOT_PANEL)


def get_available_slots(
    driver: WebDriver,
    num_of_players: int = 1,
) -> list[WebElement]:
    """Return all currently available (bookable) time slot elements
      from the loaded tee sheet.

    Queries the live DOM for rows explicitly marked as available.
    Each returned WebElement represents a tee time interval and can be passed
    to get_slot_time(), get_slot_players(), or select_time_slot() for further
    inspection or to make a reservation.

    Assumes the driver is already on the booking page with a date selected, so
    the tee sheet is loaded and ready to be queried.  
    
    Callers should handle the case where no slots are currently available (empty list) 
    gracefully, e.g. by retrying after a delay or notifying the user. 

    Note: The booking page uses Ajax to refresh available slots when a new
    date is selected, so the returned list may be empty if no slots are currently
    available for the chosen date.  Callers should handle the empty list case
    gracefully, e.g. by retrying after a delay or notifying the user.

    [TODO] Only return slots with n or more open slots 
           (e.g. for 2 players), which are indicated by a number in the slot's HTML.

    Args:
        driver: An active Selenium WebDriver instance with the tee sheet
                already loaded for the desired date.
        num_of_players: Number of players to book for. 
                 Only slots with at least this many open spots will be returned.
                 This is not currently implemented but reserved for future enhancement.
        

    Returns:
        A list of WebElement objects for bookable slots.  Empty list if
        no slots are currently available.
    """
    _ = num_of_players  # Reserved for future open-seat filtering.

    # Wait briefly for available-slot rows to appear after the Ajax refresh.
    # This avoids a race where the panel is visible but rows are not yet rendered.
    try:
        available_slots = elements.find_elements(
            driver,
            locators.BOOKING_AVAILABLE_SLOTS,
            timeout=10,
        )
    except TimeoutException as exc:
        logger.debug(
            "Timeout waiting for BOOKING_AVAILABLE_SLOTS (%s): %s",
            locators.BOOKING_AVAILABLE_SLOTS,
            exc,
        )

        # Fallback: wait for any slot rows, then keep only rows that have a
        # Reserve control. This handles markup variants where availability class
        # names differ from BOOKING_AVAILABLE_SLOTS.
        try:
            slot_rows = elements.find_elements(
                driver,
                locators.BOOKING_SLOT_TIME_ROW,
                timeout=3,
            )
        except TimeoutException as fallback_exc:
            logger.debug(
                "Timeout waiting for BOOKING_SLOT_TIME_ROW fallback (%s): %s",
                locators.BOOKING_SLOT_TIME_ROW,
                fallback_exc,
            )
            slot_rows = []

        available_slots = []
        for row in slot_rows:
            try:
                row.find_element(*locators.BOOKING_RESERVE_BTN)
                available_slots.append(row)
            except NoSuchElementException:
                continue
            except StaleElementReferenceException as stale_exc:
                logger.debug("Stale slot row during fallback scan: %s", stale_exc)

        logger.debug(
            "Fallback slot scan: total_rows=%d, bookable_rows=%d",
            len(slot_rows),
            len(available_slots),
        )
    logger.info(f"get_available_slots() found {len(available_slots)} slots")

    # Emit per-slot details only when DEBUG logging is enabled for this module.
    # Why guard this block?
    # - `get_slot_time()` and `get_slot_players()` perform additional 
    #    DOM lookups per slot.
    # - On dynamic/Ajax pages, extra element reads can add overhead.
    # - At INFO level, we only need the count above, not verbose diagnostics.
    if logger.isEnabledFor(logging.DEBUG):
        # `enumerate(..., start=1)` gives a human-friendly slot number for logs
        # ("slot 1", "slot 2", ...) instead of Python's default zero-based index.
        for index, slot in enumerate(available_slots, start=1):
            try:
                # Extract the display time and player info from this slot row.
                # This may fail transiently if the DOM updates between reads.
                time_str, open_spots = get_slot_time(slot)
                players = get_slot_players(slot)
                logger.debug("available slot %d: time=%s, open_spots=%d, players=%s",
                            index, time_str, open_spots, players)
            except (NoSuchElementException, StaleElementReferenceException) as exc:
                # Don't fail the full slot scan for one flaky row. Instead, log
                # a debug breadcrumb and continue processing the remaining slots.
                # - NoSuchElementException: expected time element not present.
                # - StaleElementReferenceException:
                #   element replaced during Ajax refresh.
                logger.debug("available slot %d: unable to read slot details (%s)", 
                             index, 
                             exc
                             )
    return available_slots


def get_slot_time(slot: WebElement) -> tuple[str, int]:
    """Return the display time string and number of open spots 
       from a time slot WebElement.

    Finds the timeText span inside the given slot row and returns its text,
    stripped of extra whitespace.  The value will look like "9:30 AM".

    Args:
        slot: A WebElement for a single tee sheet slot row (as returned by
              get_available_slots()).

    Returns:
        Tuple of (time_str, open_spots) where:
        - time_str: The display time string for this slot, e.g. "9:30 AM".
        - open_spots: The number of open player spots for this slot, as an integer.
    """
    # Get time text from the slot element. The raw text may contain newlines
    # or extra whitespace, so we split on newlines and strip whitespace to clean it up.
    raw_time_text = slot.find_element(*locators.BOOKING_SLOT_TIME_TEXT).text
    time_str = raw_time_text.split("\n")[0].strip()

    open_spots = _get_open_spots_from_slot(slot)

    return time_str, open_spots


def get_slot_players(slot: WebElement) -> list[str]:
    """Return a list of player names currently booked in a time slot.

    Scans the slot's party info area for all player entries and extracts
    the full name of each player.

    Args:
        slot: A WebElement for a single tee sheet slot row (as returned by
              get_available_slots()).

    Returns:
        A list of player name strings. Empty list if no players are booked
        in this slot.
    """
    player_names = []
    try:
        # Find all player entries within this slot
        player_entries = slot.find_elements(*locators.BOOKING_SLOT_PLAYER_ENTRY)
        for entry in player_entries:
            try:
                # Extract the full name from within this player entry
                name_element = entry.find_element(*locators.BOOKING_SLOT_FULL_NAME)
                name = name_element.text.strip()
                if name:  # Only add non-empty names
                    player_names.append(name)
            except NoSuchElementException:
                # This player entry doesn't have a full name (e.g., open slot)
                pass
    except (NoSuchElementException, StaleElementReferenceException) as exc:
        # Player info not found or DOM changed during read
        logger.debug("Unable to read player names from slot: %s", exc)

    return player_names


def _get_open_spots_from_slot(slot: WebElement) -> int:
    """Infer the remaining open spots from the rendered reservation groups.

        The ``slot`` argument is one tee-time row element from the booking page.
        In the inspected markup, that row is a ``div.tsSection.timeslotJQ`` wrapper
        containing a ``div.block.Slot`` subtree. Inside that subtree are:

        - a time cell with ``span.timeText`` and ``span.startTee``;
        - an action cell with the ``div.openTee`` reserve/request control;
        - a party/occupancy area with ``div.partyinfo``;
        - one or more player entries rendered as ``div.NC_MemberPlayer.playerJQ``
            or ``div.NC_GuestPlayer.playerJQ``;
        - each player entry containing ``div.playerName.noPlayerSelect``,
            ``span.fullName``, and a ``span.cancelTrashButton`` remove control.

        The page does not expose a dedicated open-spots text field. Instead, each
        reservation block uses a class like ``NC_Reserved2`` or
        ``NC_ReservedToday1`` to indicate how many player positions are already
        occupied. This helper reads those reservation blocks and converts them into
        the number of remaining open spots.
    """
    reservation_blocks = slot.find_elements(*locators.BOOKING_SLOT_RESERVATION)
    if not reservation_blocks:
        return 4

    occupied_spots = 0
    for reservation_block in reservation_blocks:
        class_names = reservation_block.get_attribute("class") or ""
        match = re.search(r"NC_Reserved(?:Today)?(\d)", class_names)
        if match:
            occupied_spots += int(match.group(1))
            continue

        occupied_spots += len(
            reservation_block.find_elements(*locators.BOOKING_SLOT_PLAYER_NAME)
        )

    return max(0, 4 - occupied_spots)


def select_time_slot(slot: WebElement) -> None:
    """Click the Reserve button inside a given time slot element.

    Finds the clickable Reserve div within the slot and triggers it via
    JavaScript to ensure the site's onclick handler fires reliably.

    Args:
        slot: A WebElement for an available tee sheet slot row (as returned
              by get_available_slots()).
    """
    reserve_btn = slot.find_element(*locators.BOOKING_RESERVE_BTN)
    reserve_btn.click()


def navigate_and_select_tee_time(
    driver: WebDriver,
    tee_date: dt.date,
    preferred_times: list[str],
    players: list[str],
) -> bool:
    """Navigate to the booking page, load a date, and book the first preferred slot.

    Orchestrates the full sequence: open the booking page, set the date,
    wait for the tee sheet to load, then iterate through available slots
    looking for the first match against `preferred_times`.  If a match is
    found the Reserve button is clicked and True is returned.  If none of
    the preferred times are available, returns False without clicking.

    Args:
        driver:          An active Selenium WebDriver instance.
        date:            Datetime object representing the desired tee time date.
        preferred_times: Ordered list of time strings to try, e.g.
                         ["9:00 AM", "9:10 AM", "9:20 AM"].  The first
                         match found on the tee sheet is booked.
        players:         Minimum player count requirement. Current
                         implementation accepts but does not yet filter by
                         open-seat count.

    Returns:
        True if a tee time was selected, False if none were available.
    """
    # Navigate to the booking page
    base.open_page(driver, locators.BOOKING_URL)

    # Set the desired date and refresh the tee sheet.
    select_date(driver, tee_date)

    # Look for the first available slot that matches one of the preferred times.
    # Start with one live DOM snapshot and only refresh it when a stale read occurs.
    live_slots = get_available_slots(driver, num_of_players=len(players))
    slot_count = len(live_slots)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Available slots after loading date %s:", tee_date)

    # [TODO] Filter available_slots by num_of_players once open-spot parsing is 
    # implemented.

    # Iterate through slot indexes using a stable list snapshot.
    #
    # Why index-based iteration instead of iterating over `live_slots` directly?
    # - `live_slots` is a snapshot list of WebElement handles.
    # - On this Ajax page, those handles can go stale between loop iterations.
    # - If a handle goes stale, we can refresh `live_slots` once and retry the
    #   same index from the new snapshot.
    #
    # We still use the original `slot_count` so this remains a single, bounded
    # pass through the initially observed slot list.
    for index in range(slot_count):
        try:
            # If the list shrank after a partial refresh, this index may no longer
            # exist. Skip it and keep scanning remaining indexes.
            if index >= len(live_slots):
                logger.debug(
                    "Slot %d: no longer present in refreshed slot list", index + 1
                )
                continue

            # Resolve the slot from the current snapshot, then read time/open-spots.
            slot = live_slots[index]
            time_str, open_spots = get_slot_time(slot)
        except (NoSuchElementException, StaleElementReferenceException):
            # One immediate retry with a fresh element reference often recovers
            # from transient stale rows during partial-page updates.
            try:
                # Refresh the slot snapshot, then retry the same index.
                live_slots = get_available_slots(
                    driver,
                    num_of_players=len(players),
                )

                # The slot may have disappeared between attempts.
                if index >= len(live_slots):
                    logger.debug(
                        "Slot %d: no longer present after stale retry", index + 1
                    )
                    continue

                # Retry read using the freshly resolved slot handle.
                slot = live_slots[index]
                time_str, open_spots = get_slot_time(slot)
            except (NoSuchElementException, StaleElementReferenceException) as exc:
                # If the retry fails too, treat this row as unstable and continue
                # to the next slot rather than aborting the full booking scan.
                logger.debug(
                    "Slot %d: unable to read slot details (%s)", index + 1, exc
                )
                continue

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Slot %d: time=%s, open_spots=%d",
                         index + 1, time_str, open_spots)

        # Attempt booking on the first slot whose display time appears in the
        # preferred time list. This preserves existing "first match wins" behavior.
        if time_str in preferred_times:
            logger.info("Attempting to reserve slot at %s with %d open spots",
                        time_str, open_spots)
            select_time_slot(slot)
            logger.info("Selected preferred tee time: %s\n"
                        "with %d open spots.", 
                        time_str, 
                        open_spots
                        )
            return True

    logger.info("No preferred tee times were available to select.")

    

    # [TODO] Find first available slot and click the reserve button for that slot.
        #[X] Implement a helper to get the available time slots
        #[X] Implement a helper to determine if 
        #    any of the available time slots match the preferred times.
        #[ ] Look for blank time slots that match the preferred times.
        #[ ] (future) If no blank time slots are available, check for 
        #    time slot with enough player slots available.
        #[ ] Implement a helper to click the Reserve button 
        #     for the first matching time slot.

    # [TODO] Enter Party Size and Player Names into the booking form and press
    # Make tee Time button.
        #[ ] Implement a helper function to fill out the booking 
        #    tee time form
        #[ ] Implement a helper function to submit the 
        #    booking form and handle Tee Time Received window.
        #[ ] Implement a helper function that verifies 
        #    the tee time was booked successfully.
        #[ ] (future) Implement error handling for cases where preferred time slots
        #  are not available, or where the booking form submission fails.




    return False
