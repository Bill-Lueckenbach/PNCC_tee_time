"""Unit tests for automation.py."""

import argparse

import pytest

from PNCC_tee_time.automation import argparse_setup

# ---------------------------------------------------------------------------
# argparse_setup
# ---------------------------------------------------------------------------


class TestArgparseSetup:
    """Tests for argparse_setup()."""

    def test_returns_argument_parser_with_expected_config(self):
        """Parser should have expected program metadata and help formatter."""
        # Arrange / Act
        parser = argparse_setup()

        # Assert
        assert isinstance(parser, argparse.ArgumentParser), (
            f"Expected ArgumentParser, got {type(parser).__name__}"
        )
        assert parser.prog == "PNCC_tee_time", (
            f"Expected parser.prog='PNCC_tee_time', got {parser.prog!r}"
        )
        assert parser.description == "Automate PNCC tee time booking.", (
            "Parser description mismatch. "
            f"Got: {parser.description!r}"
        )
        assert parser.formatter_class is argparse.RawTextHelpFormatter, (
            "Expected RawTextHelpFormatter so newline formatting is preserved "
            f"in help output, got {parser.formatter_class}"
        )

    def test_requires_tee_date_argument(self):
        """Parsing with no positional args should exit with argparse error."""
        # Arrange
        parser = argparse_setup()

        # Act / Assert
        with pytest.raises(SystemExit, match="2"):
            parser.parse_args([])

    def test_parses_tee_date_with_defaults(self):
        """When only tee_date is provided, optional positional defaults are used."""
        # Arrange
        parser = argparse_setup()

        # Act
        args = parser.parse_args(["today"])

        # Assert
        assert args.tee_date == "today", (
            f"Expected tee_date='today', got {args.tee_date!r}"
        )
        assert args.tee_time == "8am", (
            f"Expected default tee_time='8am', got {args.tee_time!r}"
        )
        assert args.players == ["Lueckenbach, Bill"], (
            "Expected default players=['Lueckenbach, Bill'], "
            f"got {args.players!r}"
        )

    def test_tee_time_lowercased_players_preserves_case(self):
        """tee_time is normalized to lowercase; players preserve original case."""
        # Arrange
        parser = argparse_setup()
        provided_tee_time = "9AM"
        provided_player = "LuEcKeNbAcH, Bill"

        # Act
        args = parser.parse_args(["tomorrow", provided_tee_time, provided_player])

        # Assert
        assert args.tee_date == "tomorrow", (
            f"Expected tee_date='tomorrow', got {args.tee_date!r}"
        )
        assert args.tee_time == provided_tee_time.lower(), (
            f"Expected tee_time to be lowercased to {provided_tee_time.lower()!r}, "
            f"got {args.tee_time!r}"
        )
        assert args.players == [provided_player], (
            f"Expected players to preserve case as {[provided_player]!r}, "
            f"got {args.players!r}"
        )

    def test_parses_up_to_four_players(self):
        """Parser should accept up to four player names as a list of strings."""
        # Arrange
        parser = argparse_setup()
        players = [
            "Lueckenbach, Bill",
            "Lueckenbach, Andrew",
            "Doe, Jane",
            "Doe, John",
        ]

        # Act
        args_with_four = parser.parse_args(["tomorrow", "8am", *players])
        args_with_none = parser.parse_args(["tomorrow", "8am"])

        # Assert
        assert args_with_four.players == players, (
            f"Expected players={players!r}, got {args_with_four.players!r}"
        )
        assert args_with_none.players == ["Lueckenbach, Bill"], (
            "Expected omitted players to default to ['Lueckenbach, Bill'], "
            f"got {args_with_none.players!r}"
        )

    def test_more_than_four_players_raises_parser_error(self):
        """Parser should reject more than four players with a clear error."""
        # Arrange
        parser = argparse_setup()
        too_many_players = [
            "Lueckenbach, Bill",
            "Lueckenbach, Andrew",
            "Doe, Jane",
            "Doe, John",
            "Smith, Alex",
        ]

        # Act / Assert
        with pytest.raises(SystemExit, match="2"):
            parser.parse_args(["tomorrow", "8am", *too_many_players])



