"""Element interaction functions built on top of locators.py.

This module wraps common Selenium actions (click, type, wait, read text,
etc.) into small, reusable functions. Keeping interaction logic here
decouples the *how* of browser control from the *what* expressed in pages.py.

Typical functions:
    - click(driver, locator)              : Wait for an element and click it.
    - send_keys(driver, locator, text)    : Clear a field and type text.
    - get_text(driver, locator)           : Return an element's visible text.
    - wait_for_visible(driver, locator)   : Block until element is visible.
    - wait_for_clickable(driver, locator) : Block until element is clickable.

All functions accept a Selenium WebDriver instance as their first argument
and a locator tuple (from locators.py) as their second argument.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

_DEFAULT_TIMEOUT = 10


def wait_for_clickable(
    driver: WebDriver, locator: tuple, timeout: int = _DEFAULT_TIMEOUT
):
    """Wait until an element is visible and clickable, then return it.

    Uses Selenium's WebDriverWait with the element_to_be_clickable expected
    condition. This polls the DOM every 500ms until the element is both
    present in the DOM and in a state where it can receive a click (i.e. not
    hidden, disabled, or obscured by another element). If the condition is
    not met within `timeout` seconds a TimeoutException is raised.

    This is the foundation for click() and send_keys() — both call this
    function first to ensure the element is ready before interacting with it.

    Args:
        driver: An active Selenium WebDriver instance.
        locator: A (By.<strategy>, selector) tuple from locators.py.
        timeout: Maximum seconds to wait. Defaults to 10.

    Returns:
        The located WebElement once it is clickable.

    Raises:
        selenium.common.exceptions.TimeoutException: If the element does not
            become clickable within `timeout` seconds.
    """
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def click(driver: WebDriver, locator: tuple, timeout: int = _DEFAULT_TIMEOUT) -> None:
    """Wait for an element to be clickable and click it.

    Delegates to wait_for_clickable() to ensure the element is ready before
    attempting the click. This avoids ElementNotInteractableException errors
    that occur when clicking elements that exist in the DOM but are not yet
    visible or enabled (e.g. during a page transition or animation).

    Args:
        driver: An active Selenium WebDriver instance.
        locator: A (By.<strategy>, selector) tuple from locators.py.
        timeout: Maximum seconds to wait. Defaults to 10.

    Raises:
        selenium.common.exceptions.TimeoutException: If the element does not
            become clickable within `timeout` seconds.
    """
    wait_for_clickable(driver, locator, timeout).click()


def send_keys(
    driver: WebDriver, locator: tuple, text: str, timeout: int = _DEFAULT_TIMEOUT
) -> None:
    """Wait for an input element, click to focus it, clear it, and type text.

    Waits for the element to be visible (not necessarily "clickable") to
    handle masked or styled inputs that Selenium may not classify as
    clickable. Clicks the element first to ensure focus before typing.

    Args:
        driver: An active Selenium WebDriver instance.
        locator: A (By.<strategy>, selector) tuple from locators.py.
        text: The text to type into the element.
        timeout: Maximum seconds to wait. Defaults to 10.

    Raises:
        selenium.common.exceptions.TimeoutException: If the element does not
            become visible within `timeout` seconds.
    """
    element = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )
    element.click()
    element.clear()
    element.send_keys(text)


def wait_for_visible(
    driver: WebDriver, locator: tuple, timeout: int = _DEFAULT_TIMEOUT
):
    """Wait until an element is visible in the DOM, then return it.

    Uses visibility_of_element_located, which requires the element to be
    present and have non-zero dimensions.  Useful for waiting on panels that
    are refreshed via Ajax (e.g. the tee sheet time slot panel) where the
    element exists in the DOM but may be hidden while loading.

    Args:
        driver: An active Selenium WebDriver instance.
        locator: A (By.<strategy>, selector) tuple from locators.py.
        timeout: Maximum seconds to wait. Defaults to 10.

    Returns:
        The located WebElement once it is visible.

    Raises:
        selenium.common.exceptions.TimeoutException: If the element does not
            become visible within `timeout` seconds.
    """
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


def find_elements(
    driver: WebDriver, locator: tuple, timeout: int = _DEFAULT_TIMEOUT
) -> list:
    """Wait until at least one matching element is present, then return all.

    Uses presence_of_all_elements_located so it returns elements that are
    in the DOM even if not yet visible (e.g. hidden slot rows).  Callers
    that need visible-only elements should filter the result themselves.

    Args:
        driver: An active Selenium WebDriver instance.
        locator: A (By.<strategy>, selector) tuple from locators.py.
        timeout: Maximum seconds to wait. Defaults to 10.

    Returns:
        A list of WebElement objects matching the locator.

    Raises:
        selenium.common.exceptions.TimeoutException: If no matching elements
            appear within `timeout` seconds.
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(locator)
    )


def is_selected(
    driver: WebDriver, locator: tuple, timeout: int = _DEFAULT_TIMEOUT
) -> bool:
    """Return True if a checkbox or radio button element is currently selected.

    Waits for the element to be clickable via wait_for_clickable() before
    reading its state. This is used to check the current state of a checkbox
    before conditionally clicking it — for example, ensuring the Remember Me
    checkbox is only clicked if it is not already checked, to avoid toggling
    it off by accident.

    Args:
        driver: An active Selenium WebDriver instance.
        locator: A (By.<strategy>, selector) tuple from locators.py.
        timeout: Maximum seconds to wait for the element. Defaults to 10.

    Returns:
        True if the element is selected/checked, False otherwise.

    Raises:
        selenium.common.exceptions.TimeoutException: If the element does not
            become clickable within `timeout` seconds.
    """
    element = wait_for_clickable(driver, locator, timeout)
    return element.is_selected()


def click_by_js(driver: WebDriver, locator: tuple, timeout: int = _DEFAULT_TIMEOUT) -> None:  # noqa: E501
    """Click an element using JavaScript (handles onclick handlers reliably).

    Use this instead of click() if a button has a JavaScript onclick handler
    that standard Selenium clicks may not trigger reliably. For example,
    buttons with onclick="doLogin(...)" need JS clicks to ensure the handler
    fires.

    Args:
        driver: An active Selenium WebDriver instance.
        locator: A (By.<strategy>, selector) tuple from locators.py.
        timeout: Maximum seconds to wait. Defaults to 10.

    Raises:
        selenium.common.exceptions.TimeoutException: If the element does not
            become clickable within `timeout` seconds.
    """
    element = wait_for_clickable(driver, locator, timeout)
    driver.execute_script("arguments[0].click();", element)
