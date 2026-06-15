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


@patch("PNCC_tee_time.base.webdriver.Chrome")
@patch("PNCC_tee_time.base.Service")
def test_create_driver_moves_to_right_monitor_on_windows_dual_display(
    mock_service, mock_chrome
):
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    with patch("PNCC_tee_time.base.sys.platform", "win32"):
        with patch("PNCC_tee_time.base.ctypes") as mock_ctypes:
            user32 = mock_ctypes.windll.user32

            def _metrics(index):
                if index == 80:  # SM_CMONITORS
                    return 2
                if index == 0:  # SM_CXSCREEN
                    return 1920
                return 0

            user32.GetSystemMetrics.side_effect = _metrics

            # Act
            base.create_driver()

    # Assert
    mock_driver.set_window_position.assert_called_once_with(1920, 0)
    mock_driver.maximize_window.assert_called_once()


@patch("PNCC_tee_time.base.webdriver.Chrome")
@patch("PNCC_tee_time.base.Service")
def test_create_driver_does_not_move_window_on_single_display(
    mock_service, mock_chrome
):
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    with patch("PNCC_tee_time.base.sys.platform", "win32"):
        with patch("PNCC_tee_time.base.ctypes") as mock_ctypes:
            user32 = mock_ctypes.windll.user32

            def _metrics(index):
                if index == 80:  # SM_CMONITORS
                    return 1
                if index == 0:  # SM_CXSCREEN
                    return 1920
                return 0

            user32.GetSystemMetrics.side_effect = _metrics

            # Act
            base.create_driver()

    # Assert
    mock_driver.set_window_position.assert_not_called()
    mock_driver.maximize_window.assert_not_called()


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



