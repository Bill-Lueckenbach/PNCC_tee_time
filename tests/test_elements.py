"""Unit tests for elements.py.

All tests mock the Selenium WebDriver and WebDriverWait objects to avoid
launching a real browser.
"""

from unittest.mock import MagicMock, patch

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from PNCC_tee_time import elements, locators

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_driver():
    """Return a mock Selenium WebDriver."""
    return MagicMock()


@pytest.fixture
def mock_element():
    """Return a mock WebElement."""
    return MagicMock()


@pytest.fixture
def mock_locator():
    """Return a sample locator tuple."""
    return locators.LOGIN_USERNAME


# ---------------------------------------------------------------------------
# wait_for_clickable
# ---------------------------------------------------------------------------


class TestWaitForClickable:
    """Tests for wait_for_clickable()."""

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_clickable_returns_element_when_clickable(
        self, mock_wait_class, mock_driver, mock_element, mock_locator
    ):
        """Should return the element once it becomes clickable."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait_instance

        # Act
        result = elements.wait_for_clickable(mock_driver, mock_locator)

        # Assert
        assert result is mock_element

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_clickable_calls_until_with_condition(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should call until() with an expected condition."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.wait_for_clickable(mock_driver, mock_locator)

        # Assert
        # Verify that until() was called with some condition (callable)
        assert mock_wait_instance.until.called
        condition = mock_wait_instance.until.call_args[0][0]
        assert callable(condition)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_clickable_uses_default_timeout(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should use default timeout of 10 seconds."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.wait_for_clickable(mock_driver, mock_locator)

        # Assert
        mock_wait_class.assert_called_once_with(mock_driver, 10)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_clickable_uses_custom_timeout(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should use custom timeout when provided."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance
        custom_timeout = 30

        # Act
        elements.wait_for_clickable(mock_driver, mock_locator, timeout=custom_timeout)

        # Assert
        mock_wait_class.assert_called_once_with(mock_driver, custom_timeout)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_clickable_raises_timeout_exception(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should raise TimeoutException if element doesn't become clickable."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.side_effect = TimeoutException()
        mock_wait_class.return_value = mock_wait_instance

        # Act / Assert
        with pytest.raises(TimeoutException):
            elements.wait_for_clickable(mock_driver, mock_locator)


# ---------------------------------------------------------------------------
# click
# ---------------------------------------------------------------------------


class TestClick:
    """Tests for click()."""

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_click_waits_for_element_to_be_clickable(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should wait for element to be clickable before clicking."""
        # Arrange
        mock_wait_for_clickable.return_value = mock_element

        # Act
        elements.click(mock_driver, mock_locator)

        # Assert
        mock_wait_for_clickable.assert_called_once_with(mock_driver, mock_locator, 10)

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_click_clicks_element(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should call click() on the element."""
        # Arrange
        mock_wait_for_clickable.return_value = mock_element

        # Act
        elements.click(mock_driver, mock_locator)

        # Assert
        mock_element.click.assert_called_once()

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_click_uses_custom_timeout(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should pass custom timeout to wait_for_clickable."""
        # Arrange
        mock_wait_for_clickable.return_value = mock_element
        custom_timeout = 20

        # Act
        elements.click(mock_driver, mock_locator, timeout=custom_timeout)

        # Assert
        mock_wait_for_clickable.assert_called_once_with(
            mock_driver, mock_locator, custom_timeout
        )


# ---------------------------------------------------------------------------
# send_keys
# ---------------------------------------------------------------------------


class TestSendKeys:
    """Tests for send_keys()."""

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_send_keys_waits_for_visibility(
        self, mock_wait_class, mock_driver, mock_element, mock_locator
    ):
        """Should wait for element to be visible before sending keys."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.send_keys(mock_driver, mock_locator, "test text")

        # Assert
        mock_wait_class.assert_called_once_with(mock_driver, 10)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_send_keys_clicks_element(
        self, mock_wait_class, mock_driver, mock_element, mock_locator
    ):
        """Should click the element to ensure focus."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.send_keys(mock_driver, mock_locator, "test text")

        # Assert
        mock_element.click.assert_called_once()

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_send_keys_clears_element(
        self, mock_wait_class, mock_driver, mock_element, mock_locator
    ):
        """Should clear the element before typing."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.send_keys(mock_driver, mock_locator, "test text")

        # Assert
        mock_element.clear.assert_called_once()

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_send_keys_types_text(
        self, mock_wait_class, mock_driver, mock_element, mock_locator
    ):
        """Should send the provided text to the element."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait_instance
        text_to_type = "MyPassword123"

        # Act
        elements.send_keys(mock_driver, mock_locator, text_to_type)

        # Assert
        mock_element.send_keys.assert_called_once_with(text_to_type)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_send_keys_uses_custom_timeout(
        self, mock_wait_class, mock_driver, mock_element, mock_locator
    ):
        """Should use custom timeout when provided."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait_instance
        custom_timeout = 15

        # Act
        elements.send_keys(mock_driver, mock_locator, "text", timeout=custom_timeout)

        # Assert
        mock_wait_class.assert_called_once_with(mock_driver, custom_timeout)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_send_keys_action_sequence(
        self, mock_wait_class, mock_driver, mock_element, mock_locator
    ):
        """Should perform click, clear, send_keys in correct sequence."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait_instance
        call_order = []

        mock_element.click.side_effect = lambda: call_order.append("click")
        mock_element.clear.side_effect = lambda: call_order.append("clear")
        mock_element.send_keys.side_effect = lambda x: call_order.append("send_keys")

        # Act
        elements.send_keys(mock_driver, mock_locator, "text")

        # Assert
        assert call_order == ["click", "clear", "send_keys"]


# ---------------------------------------------------------------------------
# wait_for_visible
# ---------------------------------------------------------------------------


class TestWaitForVisible:
    """Tests for wait_for_visible()."""

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_visible_returns_element_when_visible(
        self, mock_wait_class, mock_driver, mock_element, mock_locator
    ):
        """Should return the element once it becomes visible."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait_instance

        # Act
        result = elements.wait_for_visible(mock_driver, mock_locator)

        # Assert
        assert result is mock_element

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_visible_calls_until_with_condition(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should call until() with an expected condition."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.wait_for_visible(mock_driver, mock_locator)

        # Assert
        # Verify that until() was called with some condition (callable)
        assert mock_wait_instance.until.called
        condition = mock_wait_instance.until.call_args[0][0]
        assert callable(condition)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_visible_uses_default_timeout(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should use default timeout of 10 seconds."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.wait_for_visible(mock_driver, mock_locator)

        # Assert
        mock_wait_class.assert_called_once_with(mock_driver, 10)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_wait_for_visible_uses_custom_timeout(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should use custom timeout when provided."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance
        custom_timeout = 25

        # Act
        elements.wait_for_visible(mock_driver, mock_locator, timeout=custom_timeout)

        # Assert
        mock_wait_class.assert_called_once_with(mock_driver, custom_timeout)


# ---------------------------------------------------------------------------
# find_elements
# ---------------------------------------------------------------------------


class TestFindElements:
    """Tests for find_elements()."""

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_find_elements_returns_list_of_elements(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should return a list of WebElements."""
        # Arrange
        mock_elements = [MagicMock(), MagicMock()]
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_elements
        mock_wait_class.return_value = mock_wait_instance

        # Act
        result = elements.find_elements(mock_driver, mock_locator)

        # Assert
        assert result == mock_elements

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_find_elements_calls_until_with_condition(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should call until() with an expected condition."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.find_elements(mock_driver, mock_locator)

        # Assert
        # Verify that until() was called with some condition (callable)
        assert mock_wait_instance.until.called
        condition = mock_wait_instance.until.call_args[0][0]
        assert callable(condition)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_find_elements_uses_default_timeout(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should use default timeout of 10 seconds."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance

        # Act
        elements.find_elements(mock_driver, mock_locator)

        # Assert
        mock_wait_class.assert_called_once_with(mock_driver, 10)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_find_elements_uses_custom_timeout(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should use custom timeout when provided."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance
        custom_timeout = 20

        # Act
        elements.find_elements(mock_driver, mock_locator, timeout=custom_timeout)

        # Assert
        mock_wait_class.assert_called_once_with(mock_driver, custom_timeout)

    @patch("PNCC_tee_time.elements.WebDriverWait")
    def test_find_elements_raises_timeout_exception(
        self, mock_wait_class, mock_driver, mock_locator
    ):
        """Should raise TimeoutException if no elements found within timeout."""
        # Arrange
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.side_effect = TimeoutException()
        mock_wait_class.return_value = mock_wait_instance

        # Act / Assert
        with pytest.raises(TimeoutException):
            elements.find_elements(mock_driver, mock_locator)


# ---------------------------------------------------------------------------
# is_selected
# ---------------------------------------------------------------------------


class TestIsSelected:
    """Tests for is_selected()."""

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_is_selected_returns_true_when_selected(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should return True when element is selected."""
        # Arrange
        mock_element.is_selected.return_value = True
        mock_wait_for_clickable.return_value = mock_element

        # Act
        result = elements.is_selected(mock_driver, mock_locator)

        # Assert
        assert result is True

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_is_selected_returns_false_when_not_selected(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should return False when element is not selected."""
        # Arrange
        mock_element.is_selected.return_value = False
        mock_wait_for_clickable.return_value = mock_element

        # Act
        result = elements.is_selected(mock_driver, mock_locator)

        # Assert
        assert result is False

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_is_selected_waits_for_clickable(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should wait for element to be clickable before checking state."""
        # Arrange
        mock_wait_for_clickable.return_value = mock_element

        # Act
        elements.is_selected(mock_driver, mock_locator)

        # Assert
        mock_wait_for_clickable.assert_called_once_with(mock_driver, mock_locator, 10)

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_is_selected_uses_custom_timeout(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should use custom timeout when provided."""
        # Arrange
        mock_wait_for_clickable.return_value = mock_element
        custom_timeout = 15

        # Act
        elements.is_selected(mock_driver, mock_locator, timeout=custom_timeout)

        # Assert
        mock_wait_for_clickable.assert_called_once_with(
            mock_driver, mock_locator, custom_timeout
        )


# ---------------------------------------------------------------------------
# click_by_js
# ---------------------------------------------------------------------------


class TestClickByJs:
    """Tests for click_by_js()."""

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_click_by_js_waits_for_clickable(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should wait for element to be clickable before clicking."""
        # Arrange
        mock_wait_for_clickable.return_value = mock_element

        # Act
        elements.click_by_js(mock_driver, mock_locator)

        # Assert
        mock_wait_for_clickable.assert_called_once_with(mock_driver, mock_locator, 10)

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_click_by_js_executes_javascript_click(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should execute JavaScript click on the element."""
        # Arrange
        mock_wait_for_clickable.return_value = mock_element

        # Act
        elements.click_by_js(mock_driver, mock_locator)

        # Assert
        mock_driver.execute_script.assert_called_once()
        script = mock_driver.execute_script.call_args[0][0]
        assert "arguments[0].click()" in script
        assert mock_element == mock_driver.execute_script.call_args[0][1]

    @patch("PNCC_tee_time.elements.wait_for_clickable")
    def test_click_by_js_uses_custom_timeout(
        self, mock_wait_for_clickable, mock_driver, mock_element, mock_locator
    ):
        """Should use custom timeout when provided."""
        # Arrange
        mock_wait_for_clickable.return_value = mock_element
        custom_timeout = 18

        # Act
        elements.click_by_js(mock_driver, mock_locator, timeout=custom_timeout)

        # Assert
        mock_wait_for_clickable.assert_called_once_with(
            mock_driver, mock_locator, custom_timeout
        )
