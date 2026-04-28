from example.example import add


def test_add():
    """Test that add() returns the correct sum."""
    # Arrange
    a = 2
    b = 3
    expected = 5
    # Act
    result = add(a, b)
    error_message = f"Expected add({a}, {b}) to be {expected}, but got {result}."

    # Assert
    assert result == expected, error_message
