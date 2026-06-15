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
    - set_date(driver, date)
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
        Extract and return the display time label.
    - get_slot_players(slot)
        Extract and return the list of player names booked in a slot row.
    - set_tee_time(slot)
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
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from PNCC_tee_time import base, date_time_utils, elements, locators

logger = logging.getLogger(__name__)


def _normalize_tee_time_for_compare(time_str: str) -> str:
    """Return a canonical tee-time label for robust equality checks."""
    normalized = time_str.replace("\xa0", " ").strip().lower().replace(".", "")
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"\s*([ap]m)$", r"\1", normalized)

    parsed_time = date_time_utils.parse_single_time(normalized)
    hour_12 = parsed_time.strftime("%I").lstrip("0") or "0"
    return f"{hour_12}:{parsed_time.strftime('%M')} {parsed_time.strftime('%p')}"

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
def set_date(driver: WebDriver, date: dt.date) -> None:
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
    date_str = f"{date.month}/{date.day}/{date.year}"
    elements.send_keys(driver, locators.BOOKING_DATE, date_str)
    refresh_tee_sheet(driver)

    return None



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
    join_group: bool = False,
) -> list[WebElement]:
    """Return bookable slot rows with enough open spots.

    Queries the live DOM for rows explicitly marked as available.
    Each returned WebElement represents a tee time interval and can be passed
    to get_slot_time(), get_slot_players(), click_reserve_button(), or
    set_tee_time() for further inspection or reservation flow.

    Assumes the driver is already on the booking page with a date selected, so
    the tee sheet is loaded and ready to be queried.  
    
    Callers should handle the case where no slots are currently available (empty list) 
    gracefully, e.g. by retrying after a delay or notifying the user. 

    Note: The booking page uses Ajax to refresh available slots when a new
    date is selected, so the returned list may be empty if no slots are currently
    available for the chosen date.  Callers should handle the empty list case
    gracefully, e.g. by retrying after a delay or notifying the user.

     Args:
        driver: An active Selenium WebDriver instance with the tee sheet
                already loaded for the desired date.
        num_of_players: Number of players to book for. Only slots with at
            least this many open spots are returned.
        join_group: If False, only return slots with no players currently
            booked. This avoids joining an existing party and only returns
        
    Returns:
        A list of WebElement objects for bookable slots with at least
        `num_of_players` open spots. If join_group is False, 
        only returns slots that have no players currently booked,
        to avoid joining an existing party.
        Empty list if no slots are currently available.
    """

    #Set interim variable to hold number of desired number of spots.
    # This allows for looking for 4 spots when join_group is False 
    # and Num_of_players is less than 4.
    desired_open_spots = num_of_players if join_group else 4   
    
 
    # Wait briefly for available-slot rows to appear after the Ajax refresh.
    # This avoids a race where the panel is visible but rows are not yet rendered.
    try:
        #Look for BOOKING_AVAILABLE_SLOTS to determine if there are any bookable slots.

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
        slot_rows = []
    else:
        slot_rows = available_slots

    available_slots = []
    for slot in slot_rows:
        try:
            if get_num_of_open_spots_in_slot(slot) >= desired_open_spots:
                available_slots.append(slot)
        except (NoSuchElementException, StaleElementReferenceException) as exc:
            logger.debug("Skipping slot during open-spots filter: %s", exc)

    logger.info(f"get_available_slots() found {len(available_slots)} slots"
                f" with {num_of_players} or more open spots available."
    )

    return available_slots


def get_slot_time(slot: WebElement) -> str:
    """Return the display time string from a time slot WebElement.

    Finds the timeText span inside the given slot row and returns its text,
    stripped of extra whitespace.  The value will look like "9:30 AM".

    Args:
        slot: A WebElement for a single tee sheet slot row (as returned by
              get_available_slots()).

    Returns:
        The display time string for this slot, e.g. "9:30 AM".
        - time_str: The display time string for this slot, e.g. "9:30 AM".
            """
    # Get time text from the slot element. The raw text may contain newlines
    # or extra whitespace, so we split on newlines and strip whitespace to clean it up.
    raw_time_text = slot.find_element(*locators.BOOKING_SLOT_TIME_TEXT).text
    time_str = raw_time_text.split("\n")[0].strip()

    return time_str


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


def get_num_of_open_spots_in_slot(slot: WebElement) -> int:
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
        # Looking for  'NC_Reserved' or 'NC_ReservedToday1
        # and extracting the digit that indicates if the spot is occupied.
        # For example, 'NC_Reserved2' means spot 2 is occupied.
        match = re.search(r"NC_Reserved(?:Today)?(\d)", class_names)
        if match:
            # Add the digit from the class name to occupied spots
            occupied_spots += int(match.group(1))
            continue

        # Fallback: count player name elements if class name not found
        occupied_spots += len(
            reservation_block.find_elements(*locators.BOOKING_SLOT_PLAYER_NAME)
        )

    return max(0, 4 - occupied_spots)


def click_reserve_button(slot: WebElement) -> None:
    """Click the Reserve control for a slot to open the Make Tee Time form."""
    reserve_btn = slot.find_element(*locators.BOOKING_RESERVE_BTN)
    reserve_btn.click()


def _select_party_size(driver: WebDriver, player_count: int) -> None:
    """Set Party Size in the Make Tee Time popup from requested player count.

    The function maps player counts to expected labels (Single, Twosome,
    Threesome, Foursome), normalizes the requested count into the supported
    range 1..4, and applies the selection only when needed.

    Selection flow:
    1. Read current Party Size value and return early if already correct.
    2. Open the Telerik dropdown.
    3. Prefer visible options and click the first matching label.
    4. Retry once with JavaScript dropdown-open click if options are still hidden.

    Args:
        driver: Active Selenium WebDriver instance.
        player_count: Requested number of players.

    Raises:
        RuntimeError: If party size selection fails.
        ValueError: If player_count is not between 1 and 4 inclusive.
        TypeError: If player_count is not an integer.
        TypeError: If driver does not provide required WebDriver methods.

    """

    # Validate driver capabilities instead of strict type checks so tests can
    # use mocks while production still requires Selenium-like behavior.
    if not hasattr(driver, "find_element") or not hasattr(driver, "execute_script"):
        raise TypeError(
            "driver must provide Selenium WebDriver methods find_element "
            "and execute_script"
        )

    # Party-size mapping logic depends on exact numeric values. Reject non-int
    # values early (for example, "2" or 2.0) to keep behavior deterministic.
    if not isinstance(player_count, int):
        raise TypeError("player_count must be an integer")

    # The booking UI supports 1..4 players. Guard this boundary so callers get
    # a clear validation error instead of a confusing downstream mismatch.
    if player_count < 1 or player_count > 4:
        raise ValueError("player_count must be between 1 and 4 inclusive")

    desired_by_count = {
        1: ("single",),
        2: ("twosome",),
        3: ("threesome",),
        4: ("foursome",),
    }

    # Read current Party Size text as currently rendered in the popup form.
    try:
        party_size_input = driver.find_element(*locators.BOOK_TEE_TIME_PARTY_SIZE_INPUT)
    except NoSuchElementException as exc:
        if player_count == 1:
            logger.debug(
                "Party Size control not shown; assuming single-player default."
            )
            return
        raise RuntimeError(
            "Party Size control was not found for booking "
            f"(player_count={player_count})."
        ) from exc

    current_value_raw = party_size_input.get_attribute("value")

    current_value = (current_value_raw or "").strip().lower()
    if current_value in desired_by_count[player_count]:
        return

    # Open dropdown and fetch visible option rows.
    elements.click(driver, locators.BOOK_TEE_TIME_PARTY_SIZE_ARROW)
    options = elements.find_elements(
        driver,
        locators.BOOK_TEE_TIME_PARTY_SIZE_OPTIONS,
        timeout=5,
    )
    visible_options = [option for option in options if option.is_displayed()]

    # Telerik dropdowns can ignore a normal Selenium click when overlays or
    # focus state interfere. If no visible options appeared, retry once with
    # a JavaScript click on the arrow.
    if not visible_options:
        arrow = driver.find_element(*locators.BOOK_TEE_TIME_PARTY_SIZE_ARROW)
        driver.execute_script("arguments[0].click();", arrow)
        options = elements.find_elements(
            driver,
            locators.BOOK_TEE_TIME_PARTY_SIZE_OPTIONS,
            timeout=5,
        )
        visible_options = [option for option in options if option.is_displayed()]

    # Click first visible option that matches requested party size.
    for option in visible_options:
        option_text = option.text.strip().lower()
        if option_text in desired_by_count[player_count]:
            driver.execute_script("arguments[0].click();", option)
            return

    # Some Telerik states expose all labels but only mark one item as
    # "displayed". Fall back to all located options before failing.
    for option in options:
        if option in visible_options:
            continue
        option_text = option.text.strip().lower()
        if option_text in desired_by_count[player_count]:
            driver.execute_script("arguments[0].click();", option)
            return

    # Fail fast with context so caller can log/retry appropriately.
    available_labels = [option.text.strip() for option in options]
    visible_labels = [option.text.strip() for option in visible_options]
    raise RuntimeError(
        "Unable to select party size for "
        f"player count={player_count}. "
        f"visible_options={visible_labels}, all_options={available_labels}"
    )


def _switch_to_form_iframe(driver: WebDriver) -> bool:
    """Switch driver context into the iframe that contains the booking form.

    The Make Tee Time popup is rendered inside an iframe on this page.
    Returns True if the driver was successfully switched into a frame
    containing booking form controls, False if no such frame was found.
    The caller is responsible for calling driver.switch_to.default_content()
    when done.
    """
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    logger.debug("Searching %d iframe(s) for booking form.", len(iframes))
    for i, iframe in enumerate(iframes):
        try:
            driver.switch_to.frame(iframe)
            if driver.find_elements(*locators.BOOK_TEE_TIME_PARTY_SIZE_INPUT):
                logger.debug("Booking form found in iframe %d.", i)
                return True
            # Also accept any drpPartySize input as confirmation.
            if driver.find_elements(
                By.CSS_SELECTOR,
                "input[id*='drpPartySize'][id$='_Input']",
            ):
                logger.debug(
                    "Booking form found in iframe %d via broad selector.", i
                )
                return True
            # Single-spot bookings can hide Party Size controls entirely.
            # Accept player name inputs as an alternate signal that this is
            # the active booking form iframe.
            if driver.find_elements(
                By.CSS_SELECTOR,
                "input[type='text'][id*='_PCombo_PlayerName_Input']",
            ):
                logger.debug(
                    "Booking form found in iframe %d via player input selector.", i
                )
                return True
        except Exception as exc:
            logger.debug("Could not inspect iframe %d: %s", i, exc)
        driver.switch_to.default_content()
    logger.debug("Booking form not found in any iframe.")
    return False


def _set_tee_time(
    driver: WebDriver,
    slot: WebElement,
    players: list[str],
    riding: bool = True,
) -> bool:
    """Click the Reserve button inside a given time slot element.

    Finds the clickable Reserve div within the slot and triggers it via
    JavaScript to ensure the site's onclick handler fires reliably.

    Then fills out the booking form with the given player names and riding option,
    and submits the form to attempt the reservation.

    Assumes the Date, Round, Course, and Time are populated from the slot element, 
    so only the party size, player names and riding option need to be set here.

    Note: The HTML uses Make Tee Time as the form title,
          but the screen name for the form is Book Tee Time.    

    Args:
          driver: Active Selenium WebDriver instance.
                  Needed to interact and wait for the Book Tee Time form 
                  that appears after clicking Reserve.
          slot: A WebElement for an available tee sheet slot row 
                (as returned by get_available_slots()).
          players: List of player names to book in this slot. Reserved for future use.
          riding: Whether this booking is for a riding slot. Reserved for future use.
    """
    # Click the Reserve button within this slot to start the booking process, 
    # and pull up the Book Tee Time form. 
    click_reserve_button(slot)

    # The booking form lives inside an iframe on this page. Switch into it
    # so all subsequent form interactions target the correct document context.
    in_iframe = _switch_to_form_iframe(driver)
    if not in_iframe:
        logger.info("Booking form was not found in any iframe.")
        return False

    try:
        # Wait for Party Size within the active form context (iframe when found).
        try:
            elements.wait_for_visible(
                driver,
                locators.BOOK_TEE_TIME_PARTY_SIZE_INPUT,
                timeout=10,
            )
        except TimeoutException:
            logger.debug(
                "Party Size control was not visible in time;" \
                " attempting selection anyway."
            )

        # Set the Party Size to match the number of requested players.
        try:
            _select_party_size(driver, len(players))
        except (RuntimeError, ValueError, TypeError, TimeoutException) as exc:
            logger.info("Unable to set party size for booking: %s", exc)
            return False

        # Fill player names into the booking form.
        try:
            _enter_player_names(driver, players)
        except RuntimeError as exc:
            logger.info("Unable to enter player names for booking: %s", exc)
            return False

        # Apply riding/cart preference when the form exposes that control.
        _set_riding_option(driver, riding)
    finally:
        if in_iframe:
            driver.switch_to.default_content()
            logger.debug("Switched back to default content after form interaction.")
        

    #[TODO] Click Make Tee Time to complete tee time.


    #[TODO] Confirm the booking was successful, 
    # e.g. by checking for a confirmation message or page.
    # and click to close confirmation dialog if needed.

    #[TODO] Handle booking errors, for example stale availability or
    #       form submission failures.

    _ = players
    return True


def _enter_player_names(driver: WebDriver, players: list[str]) -> None:
    """Populate player-name text inputs in the Make Tee Time form.

    Raises:
        RuntimeError: If there are fewer visible player inputs than names.
        ValueError: If any player name is not in the Player Pulldown list.
        TypeError: If players is not a list of strings.
    """
    if not players:
        return

    candidate_inputs = driver.find_elements(
        By.CSS_SELECTOR,
        "input[type='text'][id*='_PCombo_PlayerName_Input']",
    )
    # The popup can re-render after the party-size selection, so we avoid
    # keeping raw WebElement handles any longer than necessary.
    visible_input_ids: list[str] = []
    seen_ids: set[str] = set()
    for input_el in candidate_inputs:
        try:
            # Ignore rows that are hidden or disabled. These are often Telerik
            # template artifacts or off-screen duplicates that should not be
            # filled.
            if not input_el.is_displayed() or not input_el.is_enabled():
                continue
        except StaleElementReferenceException:
            # If the DOM is already mid-refresh, drop this handle and keep
            # scanning the remaining candidates instead of failing early.
            continue

        # Store the DOM id rather than the WebElement so we can re-query the
        # latest element just before typing into it.
        key = input_el.get_attribute("id") or str(id(input_el))
        if key in seen_ids:
            continue
        seen_ids.add(key)
        visible_input_ids.append(key)

    if len(visible_input_ids) < len(players):
        # Fail fast if the form does not expose enough usable rows for the
        # requested player list.
        raise RuntimeError(
            "Not enough visible player inputs for requested players "
            f"(requested={len(players)}, visible_inputs={len(visible_input_ids)})."
        )

    def _find_player_input_by_id(input_id: str) -> WebElement:
        # Re-scan the current DOM snapshot and pick the element whose id still
        # matches the row we identified earlier.
        matches = [
            input_el
            for input_el in driver.find_elements(
                By.CSS_SELECTOR,
                "input[type='text'][id*='_PCombo_PlayerName_Input']",
            )
            if (input_el.get_attribute("id") or "") == input_id
        ]
        if not matches:
            raise RuntimeError(f"Player input with id={input_id} was not found.")
        return matches[0]

    for index, player_name in enumerate(players):
        # Resolve the latest DOM element immediately before typing so a stale
        # handle from the previous refresh cannot break the fill step.
        input_id = visible_input_ids[index]
        input_el = _find_player_input_by_id(input_id)
        try:
            input_el.clear()
            input_el.send_keys(player_name)
        except StaleElementReferenceException:
            # A second refresh can happen between clear() and send_keys(); if
            # that occurs, re-find the row once and retry the write.
            logger.debug(
                "Player input %d went stale; re-finding and retrying once.",
                index + 1,
            )
            fresh_input = _find_player_input_by_id(input_id)
            fresh_input.clear()
            fresh_input.send_keys(player_name)


def _set_riding_option(
    driver: WebDriver,
    riding: bool,
) -> None:
    """Apply riding/cart preference when a matching control exists.

    The booking form can vary by venue/configuration, so this helper is
    best-effort: if no recognizable control is found it logs and returns.
    """
    desired_label = "riding" if riding else "walking"

    # In the Book Tee Time form, transport is a Telerik combo per player row,
    # e.g. *_transport_oCombo_Input with matching *_Arrow and *_DropDown ids.
    transport_inputs = driver.find_elements(
        By.CSS_SELECTOR,
        "input[type='text'][id*='_transport_oCombo_Input']",
    )
    visible_inputs = [
        transport_input
        for transport_input in transport_inputs
        if transport_input.is_displayed() and transport_input.is_enabled()
    ]

    if not visible_inputs:
        logger.debug(
            "No riding control found in booking form; skipping riding preference."
        )
        return

    for transport_input in visible_inputs:
        current_value = (transport_input.get_attribute("value") or "").strip().lower()
        if current_value == desired_label:
            continue

        input_id = transport_input.get_attribute("id") or ""
        combo_prefix = input_id.removesuffix("_Input")
        if not combo_prefix:
            raise RuntimeError("Transport combo input is missing an id.")

        arrow_id = f"{combo_prefix}_Arrow"
        dropdown_id = f"{combo_prefix}_DropDown"

        try:
            arrow = driver.find_element(By.ID, arrow_id)
        except NoSuchElementException as exc:
            raise RuntimeError(
                f"Transport dropdown arrow not found for id={input_id}."
            ) from exc

        driver.execute_script("arguments[0].click();", arrow)

        try:
            option_elements = elements.find_elements(
                driver,
                (By.CSS_SELECTOR, f"#{dropdown_id} li.rcbItem"),
                timeout=5,
            )
        except TimeoutException as exc:
            raise RuntimeError(
                f"Transport options did not appear for id={input_id}."
            ) from exc

        selected_option = None
        for option in option_elements:
            if option.text.strip().lower() == desired_label:
                selected_option = option
                break

        if selected_option is None:
            available_options = [option.text.strip() for option in option_elements]
            raise RuntimeError(
                "Desired riding option was not available for transport combo "
                f"id={input_id}. desired={desired_label}, "
                f"available={available_options}"
            )

        driver.execute_script("arguments[0].click();", selected_option)



def get_slot(
    available_slots: list[WebElement],
    preferred_times: list[str],
    join_group: bool = False,
) -> WebElement | None:
    """Loop through available slots and return the WebElement of the first matching slot

    `join_group` is reserved for future group-booking behavior.

    Args:
        available_slots list[WebElement]: Snapshot list of candidate slot row elements
                                          with enough open spots, as returned 
                                          by get_available_slots().
        preferred_times list[str]: Ordered list of preferred tee-time strings.
        join_group bool: True join a group if no empty slots match preferred_times.
                         False only consider empty slots that match preferred_times.
                         Defaults to False for booking tee times with out other players.

    Returns:
        The first matching WebElement, or None if no preferred slot is found.
    """


    
    preferred_times_normalized = {
        _normalize_tee_time_for_compare(preferred_time)
        for preferred_time in preferred_times
    }

    slot_count = len(available_slots)

    # Iterate through slot indexes using a stable list snapshot.
    #
    # Why index-based iteration instead of iterating over `available_slots` directly?
    # - `available_slots` is a snapshot list of WebElement handles.
    # - On this Ajax page, those handles can go stale between loop iterations.
    # - If a handle goes stale, we can refresh `available_slots` once and retry the
    #   same index from the new snapshot.
    #
    # We still use the original `slot_count` so this remains a single, bounded
    # pass through the initially observed slot list.
    for index in range(slot_count):
        # If the list shrank after a partial refresh, this index may no longer
        # exist. Skip it and keep scanning remaining indexes.
        if index >= len(available_slots):
            logger.debug(
                "Slot %d: no longer present in refreshed slot list", index + 1
            )
            continue

        # Resolve the slot from the current snapshot, then read time/open-spots.
        slot = available_slots[index]
        try:
            time_str = get_slot_time(slot)
            open_spots = get_num_of_open_spots_in_slot(slot)
        except (NoSuchElementException, StaleElementReferenceException) as exc:
            # Keep find_slot scan-only: skip unstable rows and let the caller
            # decide whether to perform a second full re-fetch pass.
            logger.debug(
                "Slot %d: unable to read slot details (%s)", index + 1, exc
            )
            continue

        if logger.isEnabledFor(logging.DEBUG):
            time_str_normalized = _normalize_tee_time_for_compare(time_str)
            logger.debug(
                "Slot %d: time=%s, open_spots=%d",
                index + 1,
                time_str,
                open_spots,
            )
            logger.debug(
                (
                    "Slot %d match check: slot_time=%r normalized=%r "
                    "in preferred_times=%s -> %s"
                ),
                index + 1,
                time_str,
                time_str_normalized,
                preferred_times,
                time_str_normalized in preferred_times_normalized,
            )

        # Attempt booking on the first slot whose display time appears in the
        # preferred time list. This preserves existing "first match wins" behavior.
        if _normalize_tee_time_for_compare(time_str) in preferred_times_normalized:
            return slot

    return None


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
        tee_date:        Datetime object representing the desired tee time date.
        preferred_times: Ordered list of time strings to try, e.g.
                         ["9:00 AM", "9:10 AM", "9:20 AM"].  The first
                         match found on the tee sheet is booked.
        players:         Player names to book. The slot search requires at
                 least len(players) open spots.

    Returns:
        True if a tee time was selected, False if none were available.
    """
    # Navigate to the booking page
    base.open_page(driver, locators.BOOKING_URL)

    # Set the desired date and refresh the tee sheet.
    set_date(driver, tee_date)

    # Look for the first available slot that matches one of the preferred times.
    # Start with one DOM snapshot and only refresh it when a stale read occurs.
    available_slots = get_available_slots(driver, num_of_players=len(players))
    logger.info("Initial scan found %d available slots for %d player(s).",
                len(available_slots), len(players)
    )          
    slot = get_slot(
        available_slots,
        preferred_times=preferred_times,
        join_group=False,
    )
    if slot is not None:
        logger.info("Initial scan found preferred slot at: %s", get_slot_time(slot))

    # One bounded retry pass: re-fetch the slot snapshot once and re-scan.
    if slot is None:
        logger.debug("No preferred slot found on first pass; refreshing slots once.")
        available_slots = get_available_slots(driver, num_of_players=len(players))
        slot = get_slot(
            available_slots,
            preferred_times=preferred_times,
            join_group=False,
        )

    if slot is None:
        logger.info("No preferred tee times were available to select.")
        return False
    
    # We found a preferred slot.
    if logger.isEnabledFor(logging.DEBUG):
        time_str = get_slot_time(slot)
        open_spots = get_num_of_open_spots_in_slot(slot)
        logger.debug(
            "Attempting to reserve slot at %s with %d open spots",
            time_str,
            open_spots,
        )


    #Fill out the booking form with player names and riding option, then submit.
    booking_started = _set_tee_time(driver, slot, players, riding=True)
    if not booking_started:
        logger.info("Unable to open Make Tee Time form after selecting slot.")
    return booking_started



    

    # [TODO] Find first available slot and click the reserve button for that slot.
        #[X] Implement a helper to get the available time slots
        #[X] Implement a helper to determine if 
        #    any of the available time slots match the preferred times.
        #[X] Look for blank time slots that match the preferred times.
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
