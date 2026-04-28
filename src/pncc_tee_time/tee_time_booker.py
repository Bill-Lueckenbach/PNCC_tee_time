"""PNCC Tee Time Booking Automation.

Automates the end-to-end flow of booking a tee time at Porter's Neck Country
Club (https://www.portersneckcountryclub.com/) using Google Chrome via
Selenium WebDriver.

Steps automated
---------------
1.  Open the club's website in Chrome.
2.  Click the LOGIN button.
3.  Fill in the username and password.
4.  Confirm "Remember Me" is checked, then click the Login button.
5.  Navigate to Golf → TEE TIME RESERVATION.
6.  Enter the desired date and click the UPDATE button.
7.  Find the earliest available open tee time.
8.  Fill in the Book Tee Time form.
9.  Click the Make Tee Time button.
10. Verify the confirmation / "Tee Time Received" message.

Usage
-----
Run directly as a module::

    python -m pncc_tee_time

Or import and call :func:`book_tee_time` programmatically.
"""

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SITE_URL = "https://www.portersneckcountryclub.com/"
DEFAULT_TIMEOUT = 20  # seconds to wait for elements

_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _ci_xpath(tag: str, keyword: str) -> str:
    """Return an XPath that matches *keyword* case-insensitively in element text.

    Args:
        tag (str): The HTML tag, e.g. ``"a"``, ``"button"``, or ``"*"``.
        keyword (str): The UPPER-CASE keyword to search for.

    Returns:
        str: An XPath expression string.
    """
    return f"//{tag}[contains(translate(text(),'{_LOWER}','{_UPPER}'),'{keyword}')]"


# ---------------------------------------------------------------------------
# Driver helpers
# ---------------------------------------------------------------------------


def build_driver(headless: bool = False) -> webdriver.Chrome:
    """Create and return a configured Chrome WebDriver instance.

    Args:
        headless (bool): When True, Chrome runs without a visible window.

    Returns:
        webdriver.Chrome: A ready-to-use Chrome driver.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1440,900")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(5)
    return driver


def wait_for(driver: webdriver.Chrome, by: str, value: str, timeout: int = DEFAULT_TIMEOUT):
    """Wait until an element is visible and return it.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.
        by (str): A ``selenium.webdriver.common.by.By`` locator strategy.
        value (str): The locator value.
        timeout (int): Maximum seconds to wait.

    Returns:
        selenium.webdriver.remote.webelement.WebElement: The located element.

    Raises:
        TimeoutException: If the element is not found within *timeout* seconds.
    """
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


def wait_clickable(driver: webdriver.Chrome, by: str, value: str, timeout: int = DEFAULT_TIMEOUT):
    """Wait until an element is clickable and return it.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.
        by (str): A ``selenium.webdriver.common.by.By`` locator strategy.
        value (str): The locator value.
        timeout (int): Maximum seconds to wait.

    Returns:
        selenium.webdriver.remote.webelement.WebElement: The located element.

    Raises:
        TimeoutException: If the element is not clickable within *timeout* seconds.
    """
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )


# ---------------------------------------------------------------------------
# Step implementations
# ---------------------------------------------------------------------------


def step1_open_website(driver: webdriver.Chrome) -> None:
    """Step 1 – Open https://www.portersneckcountryclub.com/ in Chrome.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.
    """
    logger.info("Step 1: Opening %s", SITE_URL)
    driver.get(SITE_URL)
    # Wait for the page body to be present
    wait_for(driver, By.TAG_NAME, "body")
    logger.info("  ✓ Website loaded: %s", driver.title)


def step2_click_login(driver: webdriver.Chrome) -> None:
    """Step 2 – Click the LOGIN link/button in the site navigation.

    The function tries several common selectors used by club management
    platforms to locate the login element.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.

    Raises:
        NoSuchElementException: If no LOGIN element can be found.
    """
    logger.info("Step 2: Clicking LOGIN")

    # Try common selectors in priority order
    selectors = [
        (By.LINK_TEXT, "LOGIN"),
        (By.LINK_TEXT, "Login"),
        (By.LINK_TEXT, "Log In"),
        (By.LINK_TEXT, "MEMBER LOGIN"),
        (By.LINK_TEXT, "Member Login"),
        (By.PARTIAL_LINK_TEXT, "LOGIN"),
        (By.PARTIAL_LINK_TEXT, "Login"),
        (By.CSS_SELECTOR, "a[href*='login']"),
        (By.CSS_SELECTOR, "a[href*='Login']"),
        (By.CSS_SELECTOR, ".login-link"),
        (By.CSS_SELECTOR, "#login-link"),
        (By.XPATH, _ci_xpath("a", "LOGIN")),
    ]

    for by, value in selectors:
        try:
            element = wait_clickable(driver, by, value, timeout=5)
            element.click()
            logger.info("  ✓ Clicked LOGIN using selector (%s, %r)", by, value)
            time.sleep(1)
            return
        except (TimeoutException, NoSuchElementException):
            continue

    raise NoSuchElementException("Could not locate a LOGIN button/link on the page.")


def step3_fill_credentials(driver: webdriver.Chrome, username: str, password: str) -> None:
    """Step 3 – Fill in the username and password fields.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.
        username (str): The member login username / email.
        password (str): The member login password.

    Raises:
        TimeoutException: If the login form does not appear within the timeout.
    """
    logger.info("Step 3: Filling in credentials")

    # Username / email field
    username_selectors = [
        (By.ID, "username"),
        (By.ID, "email"),
        (By.ID, "user_email"),
        (By.NAME, "username"),
        (By.NAME, "email"),
        (By.NAME, "user[email]"),
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[placeholder*='sername']"),
        (By.CSS_SELECTOR, "input[placeholder*='mail']"),
        (By.XPATH, "//input[@type='text' and (contains(@id,'user') or contains(@name,'user'))]"),
    ]

    username_field = None
    for by, value in username_selectors:
        try:
            username_field = wait_for(driver, by, value, timeout=10)
            break
        except (TimeoutException, NoSuchElementException):
            continue

    if username_field is None:
        raise NoSuchElementException("Could not locate the username/email field on the login form.")

    username_field.clear()
    username_field.send_keys(username)
    logger.info("  ✓ Username entered")

    # Password field
    password_selectors = [
        (By.ID, "password"),
        (By.NAME, "password"),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.XPATH, "//input[@type='password']"),
    ]

    password_field = None
    for by, value in password_selectors:
        try:
            password_field = wait_for(driver, by, value, timeout=5)
            break
        except (TimeoutException, NoSuchElementException):
            continue

    if password_field is None:
        raise NoSuchElementException("Could not locate the password field on the login form.")

    password_field.clear()
    password_field.send_keys(password)
    logger.info("  ✓ Password entered")


def step4_ensure_remember_me_and_login(driver: webdriver.Chrome) -> None:
    """Step 4 – Verify "Remember Me" is checked and click the Login button.

    If the "Remember Me" checkbox exists but is unchecked, it will be
    checked before clicking Login.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.

    Raises:
        NoSuchElementException: If the Login submit button cannot be found.
    """
    logger.info("Step 4: Checking 'Remember Me' and clicking Login")

    # --- Remember Me checkbox ---
    remember_selectors = [
        (By.ID, "rememberMe"),
        (By.ID, "remember_me"),
        (By.NAME, "rememberMe"),
        (By.NAME, "remember_me"),
        (By.CSS_SELECTOR, "input[type='checkbox']"),
        (By.XPATH, "//input[@type='checkbox' and (contains(@id,'emember') or contains(@name,'emember'))]"),
    ]

    for by, value in remember_selectors:
        try:
            checkbox = driver.find_element(by, value)
            if not checkbox.is_selected():
                checkbox.click()
                logger.info("  ✓ 'Remember Me' checkbox checked")
            else:
                logger.info("  ✓ 'Remember Me' already checked")
            break
        except NoSuchElementException:
            continue
    else:
        logger.info("  ! 'Remember Me' checkbox not found – skipping")

    # --- Login / Submit button ---
    submit_selectors = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, _ci_xpath("button", "LOGIN")),
        (By.XPATH, "//input[@type='submit']"),
        (By.XPATH, _ci_xpath("button", "LOG IN")),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.XPATH, _ci_xpath("button", "SIGN IN")),
    ]

    for by, value in submit_selectors:
        try:
            btn = wait_clickable(driver, by, value, timeout=5)
            btn.click()
            logger.info("  ✓ Login button clicked")
            time.sleep(2)
            return
        except (TimeoutException, NoSuchElementException):
            continue

    raise NoSuchElementException("Could not locate the Login submit button.")


def step5_navigate_to_tee_time(driver: webdriver.Chrome) -> None:
    """Step 5 – Select Golf → TEE TIME RESERVATION from the top navigation.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.

    Raises:
        NoSuchElementException: If the TEE TIME RESERVATION link cannot be found.
    """
    logger.info("Step 5: Navigating to Golf > TEE TIME RESERVATION")

    # First try to hover over the Golf menu item to reveal the dropdown
    golf_selectors = [
        (By.LINK_TEXT, "GOLF"),
        (By.LINK_TEXT, "Golf"),
        (By.PARTIAL_LINK_TEXT, "GOLF"),
        (By.PARTIAL_LINK_TEXT, "Golf"),
        (By.XPATH, _ci_xpath("a", "GOLF")),
    ]

    golf_menu = None
    for by, value in golf_selectors:
        try:
            golf_menu = wait_clickable(driver, by, value, timeout=10)
            break
        except (TimeoutException, NoSuchElementException):
            continue

    if golf_menu:
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).move_to_element(golf_menu).perform()
        logger.info("  ✓ Hovered over Golf menu")
        time.sleep(1)

    # Now click the TEE TIME RESERVATION link
    tee_time_selectors = [
        (By.LINK_TEXT, "TEE TIME RESERVATION"),
        (By.LINK_TEXT, "Tee Time Reservation"),
        (By.LINK_TEXT, "TEE TIMES"),
        (By.LINK_TEXT, "Tee Times"),
        (By.PARTIAL_LINK_TEXT, "TEE TIME"),
        (By.PARTIAL_LINK_TEXT, "Tee Time"),
        (By.XPATH, _ci_xpath("a", "TEE TIME")),
    ]

    for by, value in tee_time_selectors:
        try:
            link = wait_clickable(driver, by, value, timeout=10)
            link.click()
            logger.info("  ✓ Clicked TEE TIME RESERVATION")
            time.sleep(2)
            return
        except (TimeoutException, NoSuchElementException):
            continue

    raise NoSuchElementException(
        "Could not locate the TEE TIME RESERVATION link in the Golf dropdown menu."
    )


def step6_select_date_and_update(driver: webdriver.Chrome, tee_date: str) -> None:
    """Step 6 – Enter the desired tee time date and click the UPDATE button.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.
        tee_date (str): Date in MM/DD/YYYY format.

    Raises:
        NoSuchElementException: If the date field or UPDATE button cannot be found.
    """
    logger.info("Step 6: Selecting date %s and clicking UPDATE", tee_date)

    # Date input field
    date_selectors = [
        (By.ID, "teeTimeDate"),
        (By.NAME, "teeTimeDate"),
        (By.ID, "date"),
        (By.NAME, "date"),
        (By.CSS_SELECTOR, "input[type='date']"),
        (By.CSS_SELECTOR, "input[name*='date']"),
        (By.CSS_SELECTOR, "input[id*='date']"),
        (By.XPATH, "//input[contains(@id,'ate') or contains(@name,'ate') or @type='date']"),
    ]

    date_field = None
    for by, value in date_selectors:
        try:
            date_field = wait_for(driver, by, value, timeout=10)
            break
        except (TimeoutException, NoSuchElementException):
            continue

    if date_field is None:
        raise NoSuchElementException("Could not locate the date input field on the tee time page.")

    # Clear and set the date using JavaScript to handle datepicker widgets
    driver.execute_script("arguments[0].value = '';", date_field)
    date_field.clear()
    date_field.send_keys(tee_date)
    logger.info("  ✓ Date entered: %s", tee_date)

    # UPDATE button
    update_selectors = [
        (By.CSS_SELECTOR, "input[type='submit'][value='UPDATE']"),
        (By.CSS_SELECTOR, "input[type='submit'][value='Update']"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//input[@value='UPDATE' or @value='Update']"),
        (By.XPATH, _ci_xpath("button", "UPDATE")),
        (By.XPATH, _ci_xpath("a", "UPDATE")),
    ]

    for by, value in update_selectors:
        try:
            btn = wait_clickable(driver, by, value, timeout=5)
            btn.click()
            logger.info("  ✓ UPDATE button clicked")
            time.sleep(2)
            return
        except (TimeoutException, NoSuchElementException):
            continue

    raise NoSuchElementException("Could not locate the UPDATE button on the tee time page.")


def step7_find_earliest_tee_time(driver: webdriver.Chrome) -> str:
    """Step 7 – Find and return the earliest available open tee time.

    Scans the tee time listing page for available slots and returns the
    text/value of the earliest one, then clicks it.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.

    Returns:
        str: The text description of the earliest available tee time slot.

    Raises:
        NoSuchElementException: If no available tee time slots are found.
    """
    logger.info("Step 7: Finding earliest available tee time")
    time.sleep(1)

    # Common patterns for available tee time links / buttons
    available_selectors = [
        (By.CSS_SELECTOR, "a.available"),
        (By.CSS_SELECTOR, "td.available a"),
        (By.CSS_SELECTOR, ".tee-time-slot:not(.unavailable) a"),
        (By.CSS_SELECTOR, ".open a"),
        (By.CSS_SELECTOR, "a.teeTimeOpen"),
        (By.XPATH, "//a[contains(@class,'available') and not(contains(@class,'unavailable'))]"),
        (By.XPATH, "//a[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'BOOK')]"),
        (By.XPATH, "//input[@type='submit' and (contains(@value,'Book') or contains(@value,'BOOK'))]"),
        (By.XPATH, "//a[contains(@href,'book') or contains(@href,'reserve')]"),
    ]

    slots = []
    for by, value in available_selectors:
        try:
            found = driver.find_elements(by, value)
            if found:
                slots = found
                logger.info("  ✓ Found %d available slot(s) using (%s, %r)", len(found), by, value)
                break
        except NoSuchElementException:
            continue

    if not slots:
        raise NoSuchElementException(
            "No available tee time slots found on the page. "
            "Try a different date or check the website manually."
        )

    earliest = slots[0]
    slot_text = earliest.text or earliest.get_attribute("value") or "Unknown time"
    logger.info("  ✓ Earliest available slot: %s", slot_text)
    earliest.click()
    time.sleep(1)
    return slot_text


def step8_fill_booking_form(driver: webdriver.Chrome, num_players: str) -> None:
    """Step 8 – Fill in the Book Tee Time form.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.
        num_players (str): Number of players as a string (e.g. "2").

    Raises:
        TimeoutException: If the booking form does not load in time.
    """
    logger.info("Step 8: Filling in Book Tee Time form")
    time.sleep(1)

    # Number of players dropdown / select
    players_selectors = [
        (By.ID, "numberOfPlayers"),
        (By.NAME, "numberOfPlayers"),
        (By.ID, "numPlayers"),
        (By.NAME, "numPlayers"),
        (By.ID, "players"),
        (By.NAME, "players"),
        (By.XPATH, "//select[contains(@id,'layer') or contains(@name,'layer')]"),
        (By.CSS_SELECTOR, "select[name*='player']"),
        (By.CSS_SELECTOR, "select[id*='player']"),
    ]

    for by, value in players_selectors:
        try:
            from selenium.webdriver.support.ui import Select
            select_el = driver.find_element(by, value)
            sel = Select(select_el)
            sel.select_by_value(num_players)
            logger.info("  ✓ Number of players set to %s", num_players)
            break
        except (NoSuchElementException, Exception):
            continue
    else:
        logger.info("  ! Number of players field not found – skipping")

    # Additional form fields may vary by site; we wait for the form to be ready
    logger.info("  ✓ Booking form filled")


def step9_click_make_tee_time(driver: webdriver.Chrome) -> None:
    """Step 9 – Click the "Make Tee Time" (or equivalent submit) button.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.

    Raises:
        NoSuchElementException: If the submit button cannot be found.
    """
    logger.info("Step 9: Clicking Make Tee Time button")

    submit_selectors = [
        (By.XPATH, "//input[@value='Make Tee Time']"),
        (By.XPATH, _ci_xpath("button", "MAKE TEE TIME")),
        (By.XPATH, "//input[contains(@value,'Make Tee Time') or contains(@value,'MAKE TEE TIME')]"),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, _ci_xpath("button", "RESERVE")),
        (By.XPATH, "//input[@type='submit']"),
    ]

    for by, value in submit_selectors:
        try:
            btn = wait_clickable(driver, by, value, timeout=10)
            btn.click()
            logger.info("  ✓ Make Tee Time button clicked")
            time.sleep(2)
            return
        except (TimeoutException, NoSuchElementException):
            continue

    raise NoSuchElementException("Could not locate the Make Tee Time submit button.")


def step10_verify_confirmation(driver: webdriver.Chrome) -> str:
    """Step 10 – Verify the "Tee Time Received" confirmation message.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.

    Returns:
        str: The confirmation message text that was found on the page.

    Raises:
        TimeoutException: If no confirmation message appears within the timeout.
    """
    logger.info("Step 10: Verifying confirmation message")
    time.sleep(1)

    # Look for common confirmation message patterns
    confirmation_selectors = [
        (By.XPATH, _ci_xpath("*", "TEE TIME RECEIVED")),
        (By.XPATH, _ci_xpath("*", "CONFIRMATION")),
        (By.XPATH, _ci_xpath("*", "CONFIRMED")),
        (By.XPATH, _ci_xpath("*", "BOOKING RECEIVED")),
        (By.XPATH, _ci_xpath("*", "RESERVED")),
        (By.XPATH, _ci_xpath("*", "THANK YOU")),
        (By.CSS_SELECTOR, ".confirmation"),
        (By.CSS_SELECTOR, ".success"),
        (By.CSS_SELECTOR, ".alert-success"),
        (By.ID, "confirmation"),
    ]

    for by, value in confirmation_selectors:
        try:
            element = wait_for(driver, by, value, timeout=15)
            message = element.text.strip()
            logger.info("  ✓ Confirmation message found: %r", message)
            return message
        except (TimeoutException, NoSuchElementException):
            continue

    # Fall back: check the page title or URL for confirmation cues
    page_text = driver.find_element(By.TAG_NAME, "body").text.upper()
    if any(kw in page_text for kw in ("TEE TIME RECEIVED", "CONFIRMED", "CONFIRMATION", "RESERVED", "THANK YOU")):
        logger.info("  ✓ Confirmation keyword found in page body")
        return "Tee time confirmed (keyword match)"

    raise TimeoutException(
        "No confirmation message found after clicking Make Tee Time. "
        "Please verify the booking manually on the website."
    )


# ---------------------------------------------------------------------------
# Main orchestration function
# ---------------------------------------------------------------------------


def book_tee_time(
    username: str,
    password: str,
    tee_date: str,
    num_players: str = "1",
    headless: bool = False,
) -> str:
    """Run the full 10-step tee time booking automation.

    Args:
        username (str): PNCC member username / email.
        password (str): PNCC member password.
        tee_date (str): Desired tee time date in MM/DD/YYYY format.
        num_players (str): Number of players (``"1"`` – ``"4"``).
        headless (bool): Run Chrome without a visible window when True.

    Returns:
        str: The confirmation message returned by :func:`step10_verify_confirmation`.

    Raises:
        Exception: Any Selenium exception encountered during automation stops the
            run and the driver is safely closed before re-raising.
    """
    driver = build_driver(headless=headless)
    try:
        step1_open_website(driver)
        step2_click_login(driver)
        step3_fill_credentials(driver, username, password)
        step4_ensure_remember_me_and_login(driver)
        step5_navigate_to_tee_time(driver)
        step6_select_date_and_update(driver, tee_date)
        step7_find_earliest_tee_time(driver)
        step8_fill_booking_form(driver, num_players)
        step9_click_make_tee_time(driver)
        confirmation = step10_verify_confirmation(driver)
        return confirmation
    finally:
        driver.quit()
