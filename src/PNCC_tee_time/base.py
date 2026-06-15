"""Core Selenium WebDriver setup and shared helper functions.

This module is responsible for initialising the browser driver and providing
low-level utility functions that every other module in the package depends on.

Functions in this module:
    - _move_window_to_right_monitor(driver)
        Best-effort Windows-only helper that moves the browser window to a
        secondary monitor and maximizes it when multiple monitors are present.

    - create_driver(headless=False, page_load_timeout=30)
        Creates and returns a configured Chrome WebDriver instance with
        standard options (maximised window, notifications disabled), optional
        headless mode, and a page-load timeout.

    - open_page(driver, url)
        Navigates the provided driver to any supplied URL. Callers typically
        pass URLs defined in locators.py.

    - teardown(driver)
        Closes the browser and ends the WebDriver session, releasing Selenium
        resources.

All functions here should be stateless or accept the driver as a parameter
so they remain easy to test and reuse.
"""

import ctypes
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver


def _move_window_to_right_monitor(driver: WebDriver) -> None:
    """Move and maximize the browser on the right monitor when available.

    This is a best-effort Windows-only helper. If monitor detection fails,
    it silently falls back to default browser placement.
    """
    if sys.platform != "win32":
        return

    try:
        user32 = ctypes.windll.user32
        monitor_count = user32.GetSystemMetrics(80)  # SM_CMONITORS
        if monitor_count < 2:
            return

        primary_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        driver.set_window_position(primary_width, 0)
        driver.maximize_window()
    except Exception:
        # Keep driver setup resilient if monitor APIs are unavailable.
        return


def create_driver(*, headless: bool = False, page_load_timeout: int = 30) -> WebDriver:
    """Create and return a configured Chrome WebDriver instance.

    Args:
        headless: Run Chrome in headless mode (no visible window).
                  Note driver is headless, not the page itself. 
                  Defaults to False.
        page_load_timeout: Seconds to wait for a page to load before
                           raising a TimeoutException. Defaults to 30.

    Returns:
        A Selenium Chrome WebDriver ready for use.

    [TODO] Switch to an Undetected ChromeDriver
            import undetected_chromedriver as uc
            # It initializes exactly like regular webdriver
            driver = uc.Chrome()
            driver.get('https://example.com')

            Google Search
                I am using selenium python to login into a website, 
                how do i block the website from detecting selenium?
        
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.set_page_load_timeout(page_load_timeout)
    if not headless:
        _move_window_to_right_monitor(driver)
    return driver


def open_page(driver: WebDriver, url: str) -> None:
    """Navigate to the supplied URL.

    driver.get() blocks until the page is fully loaded (or timeout), so no
    explicit wait is needed after this call.

    Args:
        driver: An active Selenium WebDriver instance.
        url: The absolute URL to open.
    """
    driver.get(url)


def teardown(driver: WebDriver,) -> None:
    """Quit the WebDriver and close all associated browser windows.

    Args:
        driver: An active Selenium WebDriver instance.
    """
    driver.quit()
