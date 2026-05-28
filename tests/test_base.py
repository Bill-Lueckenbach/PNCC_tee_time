"""Unit tests for base.py.

All tests mock the Selenium WebDriver so no real browser is launched.
Smoke / integration tests that require a live browser live in test_integration.py.
"""

from unittest.mock import MagicMock, patch

from PNCC_tee_time import base, locators

# ---------------------------------------------------------------------------
# create_driver
# ---------------------------------------------------------------------------


@patch("PNCC_tee_time.base.webdriver.Chrome")
@patch("PNCC_tee_time.base.Service")
def test_create_driver_returns_driver(mock_service, mock_chrome):
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    # Act
    driver = base.create_driver()

    # Assert
    assert driver is mock_driver, (
        "create_driver() should return the Chrome WebDriver instance it creates."
    )


@patch("PNCC_tee_time.base.webdriver.Chrome")
@patch("PNCC_tee_time.base.Service")
def test_create_driver_sets_page_load_timeout_default(mock_service, mock_chrome):
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    # Act
    base.create_driver()

    # Assert
    mock_driver.set_page_load_timeout.assert_called_once_with(30)


@patch("PNCC_tee_time.base.webdriver.Chrome")
@patch("PNCC_tee_time.base.Service")
def test_create_driver_sets_custom_page_load_timeout(mock_service, mock_chrome):
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    # Act
    base.create_driver(page_load_timeout=60)

    # Assert
    mock_driver.set_page_load_timeout.assert_called_once_with(60)


@patch("PNCC_tee_time.base.webdriver.Chrome")
@patch("PNCC_tee_time.base.Service")
def test_create_driver_headless_adds_argument(mock_service, mock_chrome):
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    with patch("PNCC_tee_time.base.Options") as mock_options_cls:
        mock_options = MagicMock()
        mock_options_cls.return_value = mock_options

        # Act
        base.create_driver(headless=True)

        # Assert
        calls = [c.args[0] for c in mock_options.add_argument.call_args_list]
        assert "--headless=new" in calls, (
            "create_driver(headless=True) should add the Chrome headless argument."
        )


@patch("PNCC_tee_time.base.webdriver.Chrome")
@patch("PNCC_tee_time.base.Service")
def test_create_driver_not_headless_omits_headless_argument(mock_service, mock_chrome):
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    with patch("PNCC_tee_time.base.Options") as mock_options_cls:
        mock_options = MagicMock()
        mock_options_cls.return_value = mock_options

        # Act
        base.create_driver(headless=False)

        # Assert
        calls = [c.args[0] for c in mock_options.add_argument.call_args_list]
        assert "--headless=new" not in calls, (
            "create_driver(headless=False) should not add the Chrome headless argument."
        )


@patch("PNCC_tee_time.base.webdriver.Chrome")
@patch("PNCC_tee_time.base.Service")
def test_create_driver_always_adds_standard_arguments(mock_service, mock_chrome):
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    with patch("PNCC_tee_time.base.Options") as mock_options_cls:
        mock_options = MagicMock()
        mock_options_cls.return_value = mock_options

        # Act
        base.create_driver()

        # Assert
        calls = [c.args[0] for c in mock_options.add_argument.call_args_list]
        assert "--start-maximized" in calls, (
            "create_driver() should always request a maximized Chrome window."
        )
        assert "--disable-notifications" in calls, (
            "create_driver() should always disable browser notifications."
        )


# ---------------------------------------------------------------------------
# open_page
# ---------------------------------------------------------------------------


def test_open_page_calls_get_with_given_url():
    # Arrange
    mock_driver = MagicMock()
    url = locators.LOGIN_URL

    # Act
    base.open_page(mock_driver, url)

    # Assert
    mock_driver.get.assert_called_once_with(url)


# ---------------------------------------------------------------------------
# teardown
# ---------------------------------------------------------------------------


def test_teardown_calls_quit():
    # Arrange
    mock_driver = MagicMock()

    # Act
    base.teardown(mock_driver)

    # Assert
    mock_driver.quit.assert_called_once()



