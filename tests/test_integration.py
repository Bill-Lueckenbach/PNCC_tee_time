"""Integration tests for the PNCC tee-time automation.

Unlike the per-module unit tests (test_base.py, test_elements.py, etc.),
these tests exercise multiple modules working together end-to-end against
a real browser and the live PNCC / McConnell Golf website.

Prerequisites:
    - ChromeDriver installed and on PATH.
    - A valid .env file at the project root containing:
          PNCC_USERNAME=<your username>
          PNCC_PASSWORD=<your password>

All integration tests are marked with @pytest.mark.smoke so they can be
run selectively without launching a browser during normal CI/unit runs::

    pytest -m smoke          # run only integration / smoke tests
    pytest -m "not smoke"    # run only unit tests
    pytest                   # run everything
"""

import os

import pytest
from dotenv import load_dotenv

from PNCC_tee_time import base, locators, pages

# ---------------------------------------------------------------------------
# Smoke tests  (real browser — run with: pytest -m smoke)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_open_login_page():
    """Launch a real Chrome browser and verify the login page loads."""
    # Arrange
    driver = base.create_driver(headless=True)
    expected_url = locators.LOGIN_URL

    try:
        # Act
        base.open_page(driver, locators.LOGIN_URL)

        # Assert
        assert locators.LOGIN_URL in driver.current_url, (
            f"{expected_url} not in {driver.current_url}"
        )
    finally:
        base.teardown(driver)


@pytest.mark.smoke
def test_smoke_login():
    """Log in with real credentials (headless) and verify redirect off the login page.

    Requires PNCC_USERNAME and PNCC_PASSWORD to be set in the .env file at
    the project root.
    """
    # Arrange
    load_dotenv()
    username = os.environ.get("PNCC_USERNAME", "")
    password = os.environ.get("PNCC_PASSWORD", "")
    if not username or not password:
        pytest.skip("PNCC_USERNAME / PNCC_PASSWORD not set in .env")

    driver = base.create_driver(headless=True)
    expected_url = locators.MEMBER_HOME_URL

    try:
        # Act
        base.open_page(driver, locators.LOGIN_URL)
        pages.login(driver, username, password)

        # Assert
        assert expected_url in driver.current_url, (
            f"{expected_url} not in {driver.current_url}"
        )
    finally:
        base.teardown(driver)

